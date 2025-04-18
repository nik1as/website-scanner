import re

HTML_COMMENT_REGEX = re.compile(r"<!--(.*?)-->", re.DOTALL)
EMAIL_REGEX = re.compile(
    r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}", re.IGNORECASE)
