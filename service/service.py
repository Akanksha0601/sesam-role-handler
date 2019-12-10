#!/usr/bin/env python3

import requests
import os
import json
from sesamutils import sesam_logger, Dotdictify

# fetch env vars
jwt = os.environ.get('JWT')
node_api = os.environ.get('NODE_API')
node_subscription = os.environ.get('NODE_SUBSCRIPTION')
portal_api = os.environ.get('PORTAL_API')

# set logging
logger = sesam_logger('sesam-role-handler', timestamp=True)

# API urls
available_roles_api = portal_api + '/subscriptions/' + node_subscription + '/available-roles'
pipes_api = node_api + '/pipes'
systems_api = node_api + '/systems'
member_roles_api = portal_api + '/subscriptions/' + node_subscription + '/members/'
permissions_api = node_api + '/permissions/'

headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + jwt}


def get_available_roles():
    logger.info("fetching available roles ...")

    url = available_roles_api
    response = requests.request("GET", url, headers=headers)
    logger.debug(f"url:{url} {response}")

    return response


def isolate_custom_roles(roles):
    custom_roles = []

    for role in roles:
        if role['is-custom-role']:
            custom_roles.append(role['id'])

    return custom_roles


def get_pipes():
    logger.info("fetching pipes ...")

    url = pipes_api
    response = requests.request("GET", url, headers=headers)
    logger.debug(f"url:{url} {response}")

    return response


def get_member_roles(user_id, email):
    logger.info(f"fetching roles for user: {email} with user_id: {user_id} ...")

    url = member_roles_api + user_id
    response = requests.request("GET", url, headers=headers)
    logger.debug(f"url:{url} {response}")

    return response.text


def set_permissions(role_id, object_id, object_type, scope="allow_all", permissions=[]):
    logger.info("setting object permissions ...")

    logger.info(f"adding role(s) {role_id} on {object_id}")
    url = f"{permissions_api}{object_type}/{object_id}"
    payload = f"[[\"{scope}\", {json.dumps(role_id)}, {permissions}]]"
    logger.debug(f"payload:{payload}")
    response = requests.request("PUT", url, data=payload, headers=headers)
    #response = 'foo'
    logger.debug(f"url:{url} {response}")

    return response


# system functions
def get_systems():
    logger.info("fetching systems...")

    url = systems_api
    response = requests.request("GET", url, headers=headers)
    logger.debug(f"url:{url} {response}")
    return response


if __name__ == '__main__':

    # fetch all available roles in subscription
    roles = json.loads(get_available_roles().text)

    # isolate custom roles in subscription
    available_custom_roles = isolate_custom_roles(roles)

    # fetch all pipes
    pipes = json.loads(get_pipes().text)

    # fetch pipe creators
    pipe_creator_dict = {}

    for p in pipes:
        pipe = Dotdictify(p)
        pipe_creator_dict[pipe._id] = pipe.config.audit.created_by

    # fetch pipe creator's roles
    for pipe_id in pipe_creator_dict:
        email = pipe_creator_dict[pipe_id].email
        user_id = pipe_creator_dict[pipe_id].user_id

        response = json.loads(get_member_roles(user_id, email))
        member_roles = response["roles"]

        # keep only creator's custom roles
        member_custom_roles = []

        for role in member_roles:
            if role in available_custom_roles:
                member_custom_roles.append(role)

        # set creator's custom roles on pipe
        if member_custom_roles:
            set_permissions(member_custom_roles, pipe_id, object_type="pipes")

    # fetch all systems
    system_list = json.loads(get_systems().text)

    # fetch system creators
    system_creator_dict = {}

    for s in system_list:
        system = Dotdictify(s)
        if system.config.audit:
            system_creator_dict[system._id] = system.config.audit.created_by

    # fetch system creator's roles
    for sys_id in system_creator_dict:
        email = system_creator_dict[sys_id].email
        user_id = system_creator_dict[sys_id].user_id
        response = json.loads(get_member_roles(user_id, email))
        member_roles = response["roles"]

        # keep only creator's custom roles
        member_custom_roles = []

        for role in member_roles:
            if role in available_custom_roles:
                member_custom_roles.append(role)

        # set creator's custom roles on system
        if member_custom_roles:
            set_permissions(member_custom_roles, sys_id, object_type="systems")
