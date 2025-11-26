from os import getenv

from dotenv import load_dotenv

from backend.const import ENV_DEBUG_MODE

# load envs
load_dotenv()


# debug
DEBUG_MODE = bool(getenv(ENV_DEBUG_MODE))
