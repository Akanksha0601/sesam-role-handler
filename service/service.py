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
available_roles = portal_api + '/subscriptions/' + node_subscription + '/available-roles'
pipe_permissions = node_api + '/permissions/pipes/'
pipes = node_api + '/pipes'
system_permissions = node_api + '/permissions/systems/'
systems = node_api + '/systems'
member_roles = portal_api + '/subscriptions/' + node_subscription + '/members/'

headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + jwt}


def get_available_roles():
    logger.info("fetching available roles ...")

    url = available_roles
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

    url = pipes
    response = requests.request("GET", url, headers=headers)
    logger.debug(f"url:{url} {response}")

    return response


def get_member_roles(user_id, email):
    logger.info(f"fetching roles for user: {email} with user_id: {user_id} ...")

    url = member_roles + user_id
    response = requests.request("GET", url, headers=headers)
    logger.debug(f"url:{url} {response}")

    return response


def set_pipe_permissions(role_id, pipe_id):
    logger.info("setting pipe permissions ...")
    
    logger.info (f"adding role(s) {role_id} on pipe {pipe_id}")
    url = pipe_permissions + pipe_id
    payload = f"[[\"allow_all\", {json.dumps(role_id)}, []]]"
    logger.debug(f"payload:{payload}")
    response = requests.request("PUT", url, data=payload, headers=headers)
    logger.debug (f"url:{url} {response}")

    return response


if __name__ == '__main__':

    # fetch all available roles
    roles = json.loads(get_available_roles().text)

    # isolate custom roles
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
        
        response = json.loads(get_member_roles(user_id, email).text)
        member_roles = response['roles']

        # keep only creator's custom roles
        member_custom_roles = []

        for role in member_roles:
            if role in available_custom_roles:
                member_custom_roles.append(role)

        # set creator's custom roles on pipe
        if member_custom_roles:
            set_pipe_permissions(member_custom_roles, pipe_id)
