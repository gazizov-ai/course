# itc-education
````
uv sync

source .venv/bin/activate
````
REDIS
(В РАЗНЫХ ТЕРМИНАЛАХ)

````
redis-server

celery -A config worker -l info