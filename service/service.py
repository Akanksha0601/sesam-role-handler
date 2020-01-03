#!/usr/bin/env python3

import requests
import os
import json
from sesamutils import sesam_logger, Dotdictify
import schedule
import time

# fetch env vars
jwt = os.environ.get('JWT')
node_api = os.environ.get('NODE_API')
node_subscription = os.environ.get('NODE_SUBSCRIPTION')
portal_api = os.environ.get('PORTAL_API')
schedule_interval = int(os.environ.get('SCHEDULE_INTERVAL', 60))  # default 60 seconds

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

    return json.loads(response.text)


def isolate_custom_roles(roles):
    custom_roles = []

    for role in roles:
        if role['is-custom-role']:
            custom_roles.append(role['id'])

    return custom_roles


def get_member_roles(user_id, email):
    logger.debug(f"fetching roles for user: {email} with user_id: {user_id} ...")

    url = member_roles_api + user_id
    response = requests.request("GET", url, headers=headers)
    logger.debug(f"url:{url} {response}")

    return json.loads(response.text)["roles"]


def get_pipes():
    logger.info("fetching pipes ...")

    url = pipes_api
    response = requests.request("GET", url, headers=headers)
    logger.debug(f"url:{url} {response}")

    return json.loads(response.text)


def get_systems():
    logger.info("fetching systems...")

    url = systems_api
    response = requests.request("GET", url, headers=headers)
    logger.debug(f"url:{url} {response}")

    return json.loads(response.text)


def set_permissions(role_id, object_id, object_type, scope="allow_all", permissions=[]):
    logger.debug("setting permissions ...")

    logger.info(f"adding role(s) {role_id} on {object_id}")

    url = f"{permissions_api}{object_type}/{object_id}"
    payload = f"[[\"{scope}\", {json.dumps(role_id)}, {json.dumps(permissions)}]]"
    logger.debug(f"payload:{payload}")

    response = requests.request("PUT", url, data=payload, headers=headers)
    logger.debug(f"url:{url} {response}")

    return response


if __name__ == '__main__':

    def run():
        roles = get_available_roles()
        available_custom_roles = isolate_custom_roles(roles)

        # handle pipe permissions
        pipes = get_pipes()

        # fetch pipe creators
        pipe_creators = {}

        for p in pipes:
            pipe = Dotdictify(p)
            pipe_creators[pipe._id] = pipe.config.audit.created_by

        # fetch pipe creator's roles
        for pipe_id in pipe_creators:
            email = pipe_creators[pipe_id].email
            user_id = pipe_creators[pipe_id].user_id

            member_roles = get_member_roles(user_id, email)

            # keep only creator's custom roles
            member_custom_roles = []

            for role in member_roles:
                if role in available_custom_roles:
                    member_custom_roles.append(role)

            # set creator's custom roles on pipe
            if member_custom_roles:
                set_permissions(member_custom_roles, pipe_id, object_type="pipes")

        # handle system permissions
        systems = get_systems()

        # fetch system creators
        system_creator_dict = {}

        for s in systems:
            system = Dotdictify(s)
            if system.config.audit:
                system_creator_dict[system._id] = system.config.audit.created_by

        # fetch system creator's roles
        for sys_id in system_creator_dict:
            email = system_creator_dict[sys_id].email
            user_id = system_creator_dict[sys_id].user_id

            member_roles = get_member_roles(user_id, email)

            # keep only creator's custom roles
            member_custom_roles = []

            for role in member_roles:
                if role in available_custom_roles:
                    member_custom_roles.append(role)

            # set creator's custom roles on system
            if member_custom_roles:
                set_permissions(member_custom_roles, sys_id, object_type="systems")

        logger.info("All done. Have a nice day!")
        logger.info(f"Waiting {str(schedule_interval)} seconds...")


logger.info(f"Running every {str(schedule_interval)} seconds...")
schedule.every(schedule_interval).seconds.do(run)

while True:
    # check for pending jobs every second
    schedule.run_pending()
    time.sleep(1)
