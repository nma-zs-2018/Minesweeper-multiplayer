.PHONY: all
all: pull build collectstatic migrate run
local: build collectstatic migrate run

# Pulls git
pull:
	git pull

# Build containers
# Images are automatically fetched, if necessary, from docker hub
build:
	docker-compose build

# Collects the static files into STATIC_ROOT https://docs.djangoproject.com/en/2.0/ref/contrib/staticfiles/
collectstatic:
	docker-compose run --rm web python manage.py collectstatic --noinput

# Start a new web container to run migrations
# Use --rm to remove the container when the command completes
migrate:
	docker-compose run --rm web python manage.py migrate

# Run everything in the background with -d
run:
	docker-compose up -d

# Stop docker containers
stop:
	docker-compose down