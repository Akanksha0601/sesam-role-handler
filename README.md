# sesam-role-handler
[![Build Status](https://travis-ci.org/sesam-community/sesam-role-handler.svg?branch=master)](https://travis-ci.org/sesam-community/sesam-role-handler)

TODO: Sensible ms description goes here.

## Environment variables

`JWT` - JSON Web Token granting access to the sesam node instance

`LOG_LEVEL` - Default 'INFO'. Ref: https://docs.python.org/3/howto/logging.html#logging-levels

`NODE_API` - base url to the sesam node instance api (ex: "https://abcd1234.sesam.cloud/api")

`NODE_SUBSCRIPTION` - subscription id of the sesam node instance

`PORTAL_API` - base url to the sesam portal (https://portal.sesam.io/api)

`SCHEDULE_INTERVAL` - number of seconds to wait before next run

## Usage

TODO: Usage description goes here.

## Example System Config
```
{
  "_id": "sesam-role-handler-service",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "JWT": "$SECRET(JWT)",
      "LOG_LEVEL": "INFO",
      "NODE": "https://abcd1234.sesam.cloud/api",
      "NODE_SUBSCRIPTION": "abcdefg...",
      "PORTAL_API": "https://portal.sesam.io/api"
    },
    "image": "sesamcommunity/sesam-role-handler:latest",
    "port": 5000
  }
}
```
