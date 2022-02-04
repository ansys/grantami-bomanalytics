import requests
from requests.auth import HTTPBasicAuth
import os
import json
import time
from functools import wraps
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

MAX_ATTEMPTS = 30
WAIT_TIME = 5


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
                logger.info(f"Failed after 30 attempts. Quitting...")
                raise ConnectionError
            logger.info(f"Check {check_count} failed. Waiting 5 seconds...")
            check_count = check_count + 1
            time.sleep(WAIT_TIME)
    return wrapper


@block_until_server_is_ok
def check_status(url: str, auth_header: HTTPBasicAuth) -> bool:
    try:
        response = requests.get(url + "/Health/v2.svc/", auth=auth_header)
    except requests.exceptions.RequestException:
        # This generally won't happen in normal operation. But if a RequestException happens we want to make sure we
        # handle it and try again.
        # If MI isn't running we'll generally get a 5xx status from the gateway instead, which is handled below.
        return False
    logger.info(f"Received {response.status_code} response.")
    if response.status_code != 200:
        return False

    content = json.loads(response.content)
    for check in content['HealthChecks']:
        if check['Name'] == 'Database Check' and check['Status'] == 'Ok':
            logger.info(f"All databases loaded.")
            return True
        else:
            logger.info(f"All databases not loaded.")
    return False


if __name__ == "__main__":
    sl_url = os.getenv("TEST_SL_URL")
    username = os.getenv("TEST_USER")
    password = os.getenv("TEST_PASS")

    logger.info(f"Checking if Granta MI server is ready for requests")
    auth = HTTPBasicAuth(username, password)
    check_status(sl_url, auth)
