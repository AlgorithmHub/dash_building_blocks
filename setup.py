from dash_building_blocks import __version__
from setuptools import setup

def readme():
    with open('README.md') as readme_file:
        return readme_file.read()

configuration = {
    'name' : 'dash_building_blocks',
    'version': __version__,
    'description' : 'Lightweight Auxiliary Framework for Writing Object-Oriented Dash Code.',
    'long_description' : readme(),
    'long_description_content_type' : 'text/markdown',
    'classifiers' : [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3 :: Only',
    ],
    'keywords' : 'dash object-oriented-programming',
    'url' : 'http://github.com/AlgorithmHub/dash_buildin_blocks',
    'maintainer' : 'Marco de Lannoy Kobayashi',
    'maintainer_email' : 'mdlkdev@gmail.com',
    'license' : 'MIT',
    'packages' : ['dash_building_blocks'],
    'install_requires': [
        'dash >= 0.22.0',
        'dash-html-components',
        'dash-core-components'
    ],
    'ext_modules' : [],
    'cmdclass' : {},
    'test_suite' : 'dash_building_blocks.tests',
    'tests_require' : [],
    'data_files' : ()
    }

setup(**configuration)