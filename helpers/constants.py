from enum import Enum

email_regex = r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,4})+$"

class Role(str, Enum):
    admin = "admin"
    user = "user"
