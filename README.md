# cinema
Django API example

## Installation
Create .env file with following variables:
```
# Database name. Used in settings.DATABASES.default
POSTGRES_DB_NAME=postgres

# Postgres user name. Used in settings.DATABASES.default
POSTGRES_USER=postgres

# Postgres user's password. Used in settings.DATABASES.default
POSTGRES_PASSWORD=)9T'gje6`N7*t'Ne

# Django secret key
DJANGO_SECRET_KEY='nuu)9f_$pd4pamy85k7vs(5uoxrvg9a-s#o6j#tbs$uhu#auu)'

```  

Run containers in detached mode (-d)
```
docker-compose up -d api
```

Apply migrations
```
docker-compose exec api python manage.py migrate
```

Create superuser (email required)
```
docker-compose exec api python manage.py createsuperuser
```

## Run tests
```
docker-compose exec api ./manage.py test
```