import re

import pytz

EMAIL_ADDRESS = "test@smail.nju.edu.cn"
EMAIL_PASSWORD = "A_SECRET_KEY_HERE"
SMTP_SERVER = "smtp.exmail.qq.com"
SMTP_PORT = 465

EDITOR_LIST = ["editor1", "editor2", "111"]
ADMIN_LIST = ["admin", "222", "111"]
LINK_REGEX = re.compile(
    r"(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)?)")


FILE_PATH = 'static/uploads'

# 创建时区对象
utc_tz = pytz.UTC
SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')
