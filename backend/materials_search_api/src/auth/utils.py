from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        ph.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False


def needs_rehash(password_hash: str) -> bool:
    return ph.check_needs_rehash(password_hash)
