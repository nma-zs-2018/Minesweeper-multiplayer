.PHONY: all
all: pull build collectstatic run
local: build collectstatic run

# Pulls git
pull:
	git pull

# Build containers
# Images are automatically fetched, if necessary, from docker hub
build:
	docker-compose build

# Collects the static files into STATIC_ROOT https://docs.djangoproject.com/en/2.0/ref/contrib/staticfiles/
collectstatic:
	docker-compose run --rm web python manage.py collectstatic --noinput --clear

# Run everything in the background with -d
run:
	docker-compose up -d

# Stop docker containers
stop:
	docker-compose down