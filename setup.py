from __future__ import absolute_import
import re
import ast
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('ui_driver/_version.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

with open('requirements.txt') as f:
    requirements = [line for line in f.read().splitlines() if line]

setup(
    name='uidriver',
    description='ui auto test framework cli',
    version=version,
    author='CHNJX',
    author_email='chaozhourose@gmail.com',
    url='https://github.com/CHNJX/uiauto-driver',
    packages=['ui_driver','ui_driver.utils'],
    package_data={'templates': ['ui_driver/templates/*']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'udf=ui_driver:cmd'
        ]
    },
    install_requires=requirements,
    tests_require=['pytest'],
)
