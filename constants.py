from dotenv import (
    load_dotenv,
    find_dotenv,
)
import os
load_dotenv(find_dotenv())

ADMIN_LIST = "adminList"
USER_LIST = "userList"
BIND_LIST = "bindList"
NAME = "name"
OVERLAP = "overlap"
PERMISSION_DENIED_MESSAGE = "你沒有權限使用該指令"
COMMAND_NOT_AVAILABLE_MESSAGE = "該指令無法在此使用"
USER_NOT_BOUND_MESSAGE = "你尚未綁定使用者姓名"
PASSWORD = os.environ.get("PASSWORD")
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")
