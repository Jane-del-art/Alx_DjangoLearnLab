# Gunicorn Configuration File for HTTPS Django Deployment
# Save as: gunicorn_config.py

import multiprocessing

# Server socket
bind = "127.0.0.1:8000"  # Listen on localhost, proxy through Nginx
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = 'django_library_project'

# Logging
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'info'

# SSL Configuration (if running Gunicorn with SSL directly)
# ssl_version = 2  # TLS 1.2
# certfile = '/path/to/certificate.crt'
# keyfile = '/path/to/private.key'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# Server hooks
def post_fork(server, worker):
    server.log.info("Worker %s spawned", worker.pid)

def pre_fork(server, worker):
    pass

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal")