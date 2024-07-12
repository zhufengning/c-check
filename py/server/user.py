import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from kvdb import encrypt_data, decrypt_data


def user_check(user, passwd):
    try:
        if (
            decrypt_data(os.path.join("users", user), f"{user}.hello", passwd)
            == "hello"
        ):
            return True
    finally:
        return False


def user_create(user, passwd):
    try:
        encrypt_data(os.path.join("users", user), f"{user}.hello", passwd, "hello")
        return True
    finally:
        return False


def user_delete(user, passwd):
    try:
        if (
            decrypt_data(os.path.join("users", user), f"{user}.hello", passwd)
            == "hello"
        ):
            os.remove(os.path.join("users", user))
        return True
    finally:
        return False
