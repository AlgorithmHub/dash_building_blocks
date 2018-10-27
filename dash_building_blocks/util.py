import random
import string

def generate_random_string(size):
    """Generate a pseudo-random alphanumerical string.

    :param size int: The number of characters in the string.
    :return: The pseudo-random alphanumerical string.
    """
    random_char = lambda: random.choice(string.ascii_letters + string.digits)
    return ''.join([random_char() for _ in range(size)])

def camelify(name, delims=None):
    """Convert *name* to 
    `camelCase <https://en.wikipedia.org/wiki/Camel_case>`_.
    ::

        >> camelify('hello-world')
        'helloWorld'

    :param name str: The string to be converted.
    :param delims list(str): The list of delims that identify where\
    the camel "humps" occur.
    :return: The converted string.
    """
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
    """Convert *name* from `camelCase 
    <https://en.wikipedia.org/wiki/Camel_case>`_ to a non-camel version
    delimited by *delim*.
    ::

        >> decamelify('HelloWorld')
        'hello-world'

    :param name str: The string to be converted.
    :param delim str: The delimiting string.
    :return: The converted string.
    """
    chars = [name[0].lower()]
    
    for c in name[1:]:
        if c == c.upper():
            chars.append(delim)
            chars.append(c.lower())
        else:
            chars.append(c)
            
    return ''.join(chars)