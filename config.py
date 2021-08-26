from utils.secret import *

# if test mode, the bot will be switched to a test bot
TEST_MODE = False

TOKEN = load_token(TEST_MODE)

# the error will be sent to admin
ADMIN = load_secret('admin')

# the maximum number of subscriptions for a user
JOB_LIMIT = 3

# if true, only authorized users can use /subscribe and /mysub
REQUIRE_AUTH = True

AUTHORIZED_USERS = load_secrets('authorized_users')
