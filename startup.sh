#! /bin/bash

# Start service
jupyter notebook --generate-config --allow-root
supervisord -c /etc/supervisor/supervisord.conf