from __future__ import unicode_literals
import multiprocessing

bind = "unix:/opt/projects/{{ project_name }}/src/gunicorn.sock"
workers = 4
errorlog = "/opt/projects/{{ project_name }}/logs/gunicorn_error.log"
loglevel = "error"
proc_name = "{{ project_name }}"
