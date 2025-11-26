from pathlib import Path

# common
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# logging
LOG_FORMAT = "[%(process)d][%(levelname)s][%(name)s] %(message)s"

# encoding
UTF8 = "utf-8"

# version
VERSION = "0.1.0"

# debug
ENV_DEBUG_MODE = "DEBUG"


# openapi
TAG_METADATA = "Metadata"
TAG_USER = "User"
TAG_SECURITY = "Security"


# security
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 5
SECRET_KEY = "thaL3ha5uPhoo8ooTheigh6Boohaip4UZoh6zah1Hee9GierKeeX3einaethei9I"  # TODO: Replace to your random value
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 4

# pre-defined user
USER = "my_user"  # TODO: Replace to your random value

# TODO: Replace to your random value using '/src/notebooks/password.ipynb'. Current is hash of 'my_password'
HASHED_PASSWORD = "$2b$12$BfGx1OmuCya9aHRA9UflQeLvJQkDllOaIvulURK45zWehUUzaAh5a"
