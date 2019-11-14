# cinema
Django API example

## Installation
Run containers in detached mode (-d)
```
docker-compose up -d api
```

Apply migrations
```
docker exec -ti cinema_api_1 python manage.py migrate
```

Create superuser (email required)
```
docker exec -ti cinema_api_1 python manage.py createsuperuser
```