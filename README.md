# Music Catalog API

Music Catalog.<br>
Django REST application.<br>
Includes swagger.

## Quick start

There are two docker configurations:
- debug
- production

### Debug

Uses django debug server.<br>
Every start flushes DB, makes migrations and creates superuser 'admin' with the same password.<br>
It needed for making edit queries, because as default permissions set to IsAuthenticatedOrReadOnly

Start docker:
```
docker-compose -f docker-compose.yml up -d --build
```
Port: 8000

### Production

Uses kubernates + nginx.<br>

Start
```
docker-compose -f docker-compose.prod.yml up -d --build
```
On first start required to make migrations and collect static files:
```
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear 
```

For create and edit objects in additional requires create superuser:
```
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser 
```
Port: 1337

## Swagger

Swagger will be avaiable by link:
```
https://127.0.0.1:8000/swagger-ui
```

## Additional information

### Work with AlbumTrack

Album tracks input
```
  {
    "order": int,
    "id": int,
    "name": string
  }
```

For create AlbumTrack required one of the fields:
- id
- name

ID is a identificator of existing artist's track. <br>

'name' is name for new track, creating together with AlbumTrack. <br>
Not checks for exist, may be duplicates. Be aware.<br>
AlbumTrack has not editing possibility. Only deleting. 

If track with defined in request order exists, then it will release the place and order in album will be updated.
If order is not defined it assigns automatically.