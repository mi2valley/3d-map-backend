from logging import getLogger
from sys import version

from backend.util import log

LOG = getLogger(__name__)


async def start_up() -> None:
    log.init()
    LOG.info("Starting up...")
    LOG.info(f"Python version: {version}")
    LOG.info("Start up completed")


def shut_down() -> None:
    LOG.info("Shutdown...")
    LOG.info("Shutdown Complete")
