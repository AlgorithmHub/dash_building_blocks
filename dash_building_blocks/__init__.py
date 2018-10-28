__project__ = 'dash_building_blocks'
__version__ = '0.1.1'

try:
    from .base import Block, Store
    from .core import *
# required to import __version__ from setup.py
#   before dependencies are installed
except ImportError as error:
    # print(error.__class__.__name__ + ": " + error)
    pass
