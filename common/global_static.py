import re

import pytz

LINK_REGEX = re.compile(
    r"(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)?)")

UPLOAD_FILE_PATH = 'static/uploads'

# 创建时区对象
GLOBAL_TIMEZONE = pytz.timezone('Asia/Shanghai')

