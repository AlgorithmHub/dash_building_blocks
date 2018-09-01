from setuptools import setup

def readme():
    with open('README.md') as readme_file:
        return readme_file.read()

configuration = {
    'name' : 'dash_building_blocks',
    'version': '0.0.1',
    'description' : 'Lightweight Auxiliary Framework for Writing Object-Oriented Dash Code.',
    'long_description' : readme(),
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
    'url' : 'http://github.com/marcodlk/dash_building_blocks', #TODO: move to AlgorithmHub
    'maintainer' : 'Marco de Lannoy Kobayashi',
    'maintainer_email' : 'mdlkdev@gmail.com',
    'license' : 'MIT',
    'packages' : ['dash_building_blocks'],
    'install_requires': ['dash >= 0.22.0'],
    'ext_modules' : [],
    'cmdclass' : {},
    'test_suite' : '',
    'tests_require' : [],
    'data_files' : ()
    }

setup(**configuration)