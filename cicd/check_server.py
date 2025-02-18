from functools import wraps
import json
import logging
import os
import platform
import time

import requests
from requests.auth import HTTPBasicAuth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

MAX_ATTEMPTS = 30
WAIT_TIME = 15


def block_until_server_is_ok(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        check_count = 1
        while True:
            logger.info(f"Check {check_count}")
            if func(*args, **kwargs):
                logger.info(f"Server ready!")
                break
            if check_count == MAX_ATTEMPTS:
                logger.info(f"Failed after {MAX_ATTEMPTS} attempts. Quitting...")
                raise ConnectionError
            logger.info(f"Check {check_count} failed. Waiting {WAIT_TIME} seconds...")
            check_count = check_count + 1
            time.sleep(WAIT_TIME)

    return wrapper


def get_user_agent():
    python_implementation = platform.python_implementation()
    python_version = platform.python_version()
    os_version = platform.platform()
    user_agent = f"check_server.py {python_implementation}/{python_version} ({os_version})"
    return user_agent


@block_until_server_is_ok
def check_status(url: str, auth_header: HTTPBasicAuth) -> bool:
    try:
        response = requests.get(
            url + "/Health/v2.svc/",
            auth=auth_header,
            headers={
                "User-Agent": get_user_agent(),
            },
        )
    except requests.exceptions.RequestException as e:
        # This generally won't happen in normal operation. But if a RequestException happens we want
        # to make sure we handle it and try again.
        # If MI isn't running we'll generally get a 5xx status from the gateway instead, which is
        # handled below.
        logger.error(e)
        return False
    logger.info(f"Received {response.status_code} response.")
    if response.status_code != 200:
        return False

    content = json.loads(response.content)
    for check in content["HealthChecks"]:
        if check["Name"] == "Database Check" and check["Status"] == "Ok":
            logger.info(f"All databases loaded.")
            return True
    logger.info(f"All databases not loaded.")
    return False


def warm_up_bas(url: str, auth_header: HTTPBasicAuth) -> None:
    response = requests.get(
        url + "/BomAnalytics/v1.svc/yaml",
        auth=auth_header,
        headers={
            "User-Agent": get_user_agent(),
        },
    )
    logger.info(f"Received {response.status_code} response.")


if __name__ == "__main__":
    sl_url = os.getenv("TEST_SL_URL")
    username = os.getenv("TEST_USER")
    password = os.getenv("TEST_PASS")
    auth = HTTPBasicAuth(username, password)

    logger.info("Checking Granta MI server status")
    check_status(sl_url, auth)

    logger.info("Warming up BoM Analytics Services")
    warm_up_bas(sl_url, auth)
