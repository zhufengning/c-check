import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from kvdb import encrypt_data, decrypt_data, remove_data


def user_check(user, passwd):
    try:
        if (
            decrypt_data(os.path.join("users", user), f"{user}.hello", passwd)
            == "hello"
        ):
            return True
    except Exception as e:
        print(e)
        return False


def user_create(user, passwd):
    try:
        if (user_check(user, passwd)):
            return False
        encrypt_data(os.path.join("users", user), f"{user}.hello", passwd, "hello")
        return True
    except Exception as e:
        print(e)
        return False


def user_delete(user, passwd):
    try:
        remove_data(os.path.join("users", user), f"{user}.hello", passwd)
        return True
    except Exception as e:
        print(e)
        return False
