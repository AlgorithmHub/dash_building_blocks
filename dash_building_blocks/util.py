import random
import string

def generate_random_string(size):
    random_char = lambda: random.choice(string.ascii_letters + string.digits)
    return ''.join([random_char() for _ in range(size)])

def camelify(name, delims=None):
    
    delims = delims or ['-', '_']
    chars = []
    headsup = False
    
    for c in name:
        if headsup:
            chars.append(c.upper())
            headsup = False
        elif c in delims:
            headsup = True
        else:
            chars.append(c)
            
    return ''.join(chars)

            
def decamelify(name, delim='-'):
    
    chars = [name[0].lower()]
    
    for c in name[1:]:
        if c == c.upper():
            chars.append(delim)
            chars.append(c.lower())
        else:
            chars.append(c)
            
    return ''.join(chars)