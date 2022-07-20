import logging
import os
import sys


def create_logger(name=__name__):
    log = logging.getLogger(name)
    if os.environ.get("DEBUG") and int(os.environ.get("DEBUG")) == 1:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log
