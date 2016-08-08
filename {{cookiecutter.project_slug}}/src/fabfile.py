"""
Starter fabfile for deploying the {{cookiecutter.project_slug}} project.

Change all the things marked CHANGEME. Other things can be left at their
defaults if you are happy with the default layout.
"""

import posixpath

from fabric.api import run, local, env, settings, cd, task, sudo
from fabric.contrib.files import exists
from fabric.operations import _prefix_commands, _prefix_env_vars
#from fabric.decorators import runs_once
#from fabric.context_managers import cd, lcd, settings, hide

# CHANGEME
env.hosts = ['user@host:22']
env.code_dir = '/path/to/src/dir'
env.project_dir = '/path/to/project/dir'
env.static_root = '/path/to/static/root'
env.virtualenv = '/path/to/virtual/env'
env.code_repo = 'git@bitbucket.org:repo.git'
env.django_settings_module = '{{cookiecutter.project_slug}}.settings'

# Python version
PYTHON_BIN = "python2.7"
PYTHON_PREFIX = ""  # e.g. /usr/local  Use "" for automatic
PYTHON_FULL_PATH = "%s/bin/%s" % (PYTHON_PREFIX, PYTHON_BIN) if PYTHON_PREFIX \
    else PYTHON_BIN


def virtualenv(venv_dir):
    """
    Context manager that establishes a virtualenv to use.
    """
    return settings(venv=venv_dir)


def run_venv(command, **kwargs):
    """
    Runs a command in a virtualenv (which has been specified using
    the virtualenv context manager
    """
    run("source %s/bin/activate" % env.virtualenv + " && " + command, **kwargs)


def install_dependencies():
    ensure_virtualenv()
    with virtualenv(env.virtualenv):
        with cd(env.code_dir):
            run_venv("pip install -r ../requirements/production.txt")


def collect_static():
    ensure_virtualenv()
    with virtualenv(env.virtualenv):
        with cd(env.code_dir):
            run_venv("python manage.py collectstatic --no-input")


def ensure_virtualenv():
    if exists(env.virtualenv):
        return

    with cd(env.code_dir):
        run("virtualenv --no-site-packages --python=%s %s" %
            (PYTHON_BIN, env.virtualenv))
        run("echo %s > %s/lib/%s/site-packages/projectsource.pth" %
            (env.project_dir, env.virtualenv, PYTHON_BIN))


def ensure_src_dir():
    if not exists(env.code_dir):
        run("mkdir -p %s" % env.project_dir)
    with cd(env.project_dir):
        if not exists(posixpath.join(env.project_dir, '.git')):
            run('git clone %s .' % env.code_repo)


@task
def push_sources():
    """
    Push source code to server
    """
    ensure_src_dir()
    local('git push origin master')
    with cd(env.code_dir):
        run('git pull origin master')


@task
def run_tests():
    """ Runs the Django test suite as is.  """
    local("./manage.py test")


@task
def version():
    """ Show last commit to the deployed repo. """
    with cd(env.code_dir):
        run('git log -1')


@task
def uname():
    """ Prints information about the host. """
    run("uname -a")


@task
def webserver_restart():
    """
    Restarts the webserver that is running the Django instance
    """
    with cd(env.code_dir):
        run('bash ./bin/uwsgi.sh')


@task
def first_deployment_mode():
    """
    Use before first deployment to switch on fake south migrations.
    """
    env.initial_deploy = True


@task
def update_database(app=None):
    """
    Update the database (run the migrations)
    Usage: fab update_database:app_name
    """
    with virtualenv(env.virtualenv):
        with cd(env.code_dir):
            if getattr(env, 'initial_deploy', False):
                run_venv("./manage.py migrate --noinput")
            else:
                if app:
                    run_venv("./manage.py migrate %s --noinput" % app)
                else:
                    run_venv("./manage.py migrate --noinput")


@task
def sshagent_run(cmd):
    """
    Helper function.
    Runs a command with SSH agent forwarding enabled.

    Note:: Fabric (and paramiko) can't forward your SSH agent.
    This helper uses your system's ssh to do so.
    """
    # Handle context manager modifications
    wrapped_cmd = _prefix_commands(_prefix_env_vars(cmd), 'remote')
    try:
        host, port = env.host_string.split(':')
        return local(
            "ssh -p %s -A %s@%s '%s'" % (port, env.user, host, wrapped_cmd)
        )
    except ValueError:
        return local(
            "ssh -A %s@%s '%s'" % (env.user, env.host_string, wrapped_cmd)
        )


@task
def deploy():
    """
    Deploy the project.
    """
    # with settings(warn_only=True):
    #    webserver_stop()
    push_sources()
    install_dependencies()
    collect_static()
    update_database()
    webserver_restart()
