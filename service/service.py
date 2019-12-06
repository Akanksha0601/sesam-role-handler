#!/usr/bin/env python3

import requests
import os
import json
from sesamutils import sesam_logger

# fetch env vars
jwt = os.environ.get('JWT')
node_api = os.environ.get('NODE_API')
node_subscription = os.environ.get('NODE_SUBSCRIPTION')
portal_api = os.environ.get('PORTAL_API')|

# set logging
logger = sesam_logger('sesam-role-handler', timestamp=True)

# API urls
available_roles = portal_api + '/subscriptions/' + node_subscription + '/available-roles'
#pipes_collection = node_api + '/permissions/pipes-collection'
pipe_permissions = node_api + '/permissions/pipes/'
pipes = node_api + '/pipes'
#system_collection = node_api + '/permissions/systems-collection'
system_permissions = node_api + '/permissions/systems/'
systems = node_api + '/systems'
member_roles = portal_api + '/subscriptions/' + node_subscription + '/members/'

headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + jwt}


def get_available_roles():
    logger.info("fetching available roles...")

    url = available_roles

    response = requests.request("GET", url, headers=headers)
    return response


def get_pipes():
    logger.info("fetching pipes...")

    url = pipes

    response = requests.request("GET", url, headers=headers)
    return response


def get_creator_roles(user_id):
    logger.info("fetching roles for user_id {user_id}...")

    url = member_roles + user_id
    logger.debug("url: {url}")

    response = requests.request("GET", url, headers=headers)
    return response


def set_pipe_permissions(role_id, pipe_id):
    logger.info("setting pipe permissions...")

    url = pipe_permissions + pipe_id
    logger.debug("url: {url}")
    payload = "[[\"allow_all\"," + json.dumps(role_id) + ",[]]]"
    logger.debug("payload: {payload}")

    # response = requests.request("PUT", url, data=payload, headers=headers)
    response = "foo"
    return response


# fetch all available roles
roles = json.loads(get_available_roles().text)

# isolate custom roles
available_custom_roles = []

for role in roles:
    if role['is-custom-role']:
        available_custom_roles.append(role['id'])

# fetch all pipes
json_pipe_list = get_pipes().text
pipe_list = json.loads(json_pipe_list)

# fetch pipe creators
pipe_creator_dict = {}

for pipe in pipe_list:
    pipe_creator_dict[pipe['_id']] = pipe['config']['audit']['created_by']['user_id']


# fetch creator's roles and keep only custom roles
for pipe_id in pipe_creator_dict:
    user_id = pipe_creator_dict[pipe_id]
    response = json.loads(get_creator_roles(user_id).text)
    user_roles = response['roles']

    custom_user_roles = []

    for role in user_roles:
        if role in available_custom_roles:
            custom_user_roles.append(role)

#    print(custom_user_roles)

    if custom_user_roles:
        print(set_pipe_permissions(custom_user_roles, pipe_id))
