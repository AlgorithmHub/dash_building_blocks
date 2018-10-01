import random
import string

def generate_random_string(size):
    random_char = lambda: random.choice(string.ascii_letters + string.digits)
    return ''.join([random_char() for _ in range(size)])