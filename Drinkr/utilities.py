
import random, string

MAX_ATTEMPTS = 10

def random_room_key():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))


def isNoneOrEmptyOrSpace(string):
    return string is None or string.isspace() or string == ""