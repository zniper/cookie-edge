"""
Does the following:

1. Generates and saves random secret key
2. Removes the taskapp if celery isn't going to be used
3. Removes the .idea directory if PyCharm isn't going to be used
4. Copy files from /docs/ to {{ cookiecutter.project_slug }}/docs/

    TODO: this might have to be moved to a pre_gen_hook

A portion of this code was adopted from Django's standard crypto functions and
utilities, specifically:
    https://github.com/django/django/blob/master/django/utils/crypto.py
"""
from __future__ import print_function

import json
from distutils.version import StrictVersion, LooseVersion

import os
import random
import re
import shutil

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

# Get the root project directory
PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)

# Use the system PRNG if possible
try:
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False

sample_env_file = os.path.join(
    PROJECT_DIRECTORY,
    'src',
    '{{ cookiecutter.project_slug }}',
    '.env.sample'
)


def get_random_string(
    length=50,
    allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789!@#%^&*(-_=+)'):
    """
    Returns a securely generated random string.
    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit value. log_2((26+26+10)^12) =~ 71 bits
    """
    if using_sysrandom:
        return ''.join(random.choice(allowed_chars) for i in range(length))
    print(
        "Cookiecutter Django couldn't find a secure pseudo-random number "
        "generator on your system. Please change change your SECRET_KEY "
        "variables in {{ cookiecutter.project_slug }}/.env.sample manually."
    )
    return "CHANGEME!!"


def replace_file_placeholder(file_path, placeholder, value):
    """Replace a placeholder in a file with given value."""
    # Open file
    with open(file_path) as f:
        file_ = f.read()

    # Do replace
    file_ = file_.replace(placeholder, value, 1)

    # Write the results to the locals.py module
    with open(file_path, 'w') as f:
        f.write(file_)


def set_secret_key(env_file):
    # Generate a SECRET_KEY that matches the Django standard
    SECRET_KEY = get_random_string()
    # Call replace placeholder function
    replace_file_placeholder(env_file, "NOT.THIS.SECRET", SECRET_KEY)


def make_secret_key():
    """Generates and saves random secret key to .env.sample"""
    # .env.example file
    set_secret_key(sample_env_file)


def remove_task_app():
    """Removes the taskapp if celery isn't going to be used"""
    # Determine the local_setting_file_location
    task_app_location = os.path.join(
        PROJECT_DIRECTORY,
        'src',
        'taskapp'
    )
    shutil.rmtree(task_app_location)


def set_database_url():
    """Set DATABASE_URL environment variable in .env.sample file"""
    database_url = "{{ cookiecutter.database_engine }}://" \
                   "{{ cookiecutter.database_user }}:" \
                   "{{ cookiecutter.database_password }}@" \
                   "{{ cookiecutter.database_host }}:" \
                   "{{ cookiecutter.database_port }}/" \
                   "{{ cookiecutter.database_name }}"
    if '{{ cookiecutter.database_engine }}'.lower() == "sqlite":
        database_url = "{{ cookiecutter.database_engine }}:///" \
                       "{{ cookiecutter.database_name }}"

    replace_file_placeholder(sample_env_file, "SET_DATABASE_URL_HERE",
                             database_url)


class MyLooseVersion(LooseVersion):
    """Override the version components list to avoid comparation between int
    and str.

    For example: [2, 0, 2] vs [2, 0, 'rc', 2].

    """
    def parse(self, vstring):
        super().parse(vstring)
        self.version = list(filter(lambda x:isinstance(x, int), self.version))


def get_latest_version(package):
    """Returns the latest version of package from Pypi."""
    url = "https://pypi.python.org/pypi/{}/json".format(package)
    data = urlopen(url).read()
    if isinstance(data, bytes):
        data = data.decode("utf-8", "ignore")
    try:
        data = json.loads(data)
    except ValueError as ex:
        return None
    versions = sorted(map(str, data["releases"].keys()), key=MyLooseVersion,
                  reverse=True)
    return versions[0] if versions else None


def dump_requirement_versions():
    """Check the latest version of package and set to requirements.txt.

    This will be apply to packages without version only.

    """
    req_files = ["base.txt", "development.txt", "production.txt"]
    try:
        import requirements
    except ImportError as ex:
        print("Please install 'requirements-parser' to make "
              "dump requirement versions feature run properly.")
        return
    # Parse requirements
    print("Dumping requirement versions, it might take a few minutes...")
    for req_file in req_files:
        replacements = {}
        file_path = os.path.join(PROJECT_DIRECTORY, "requirements", req_file)
        with open(file_path, "r") as file_handler:
            reqs = [req for req in requirements.parse(file_handler)]
            for req in reqs:
                #Check if requirement will be fetched from Pypi or not.
                if req.line == req.name:
                    #Check latest version of this package in Pypi
                    version = get_latest_version(req.line)
                    if version:
                        replacements[req.line] = "{0}=={1}\n".format(
                            req.line,
                            version
                        )
        if replacements:
            #Replace file content
            with open(file_path, "r") as file_handler:
                lines = file_handler.readlines()
                for idx, line in enumerate(lines):
                    if line.strip() in replacements:
                        lines[idx] = replacements[line.strip()]
            with open(file_path, "w") as file_handler:
                file_handler.write("".join(lines))


def create_env_file():
    """Create a new .env file from .env.sample file."""
    env_file = os.path.join(
        PROJECT_DIRECTORY,
        'src',
        '{{ cookiecutter.project_slug }}',
        '.env'
    )
    shutil.copy(sample_env_file, env_file)


# 1. Generates and saves random secret key
make_secret_key()

# 2. Removes the taskapp if celery isn't going to be used
if '{{ cookiecutter.use_celery }}'.lower() == 'n':
    remove_task_app()

# 3. Set DATABASE_URL in .env.sample file
set_database_url()

# 4. Set versions for requirements
if '{{ cookiecutter.dump_requirement_versions }}'.lower() == 'y':
    dump_requirement_versions()

# 5. Create .env file from .env.sample file
create_env_file()