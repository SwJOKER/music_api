from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from . import swagger
from .views import AlbumViewSet, TrackViewSet, ArtistViewSet, AlbumTrackViewSet, ArtistTrackViewSet, ArtistAlbumViewSet
from django.urls import include, path, re_path

router = routers.DefaultRouter()

router.register(r'artists', ArtistViewSet, basename='artists')
router.register(r'tracks', TrackViewSet, basename='tracks')
router.register(r'albums', AlbumViewSet, basename='albums')

albums_router = NestedSimpleRouter(router, r'artists', lookup='artists')
albums_router.register(r'albums', ArtistAlbumViewSet, basename='artist_albums')

artist_tracks_router = NestedSimpleRouter(router, r'artists', lookup='artists')
artist_tracks_router.register(r'tracks', ArtistTrackViewSet, basename='artist_tracks')

album_tracks_router = NestedSimpleRouter(router, r'albums', lookup='albums')
album_tracks_router.register(r'tracks', AlbumTrackViewSet, basename='album_tracks')

artist_album_tracks_router = NestedSimpleRouter(albums_router, r'albums', lookup='artist_albums')
artist_album_tracks_router.register(r'tracks', AlbumTrackViewSet, basename='artist_album_tracks')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(albums_router.urls)),
    path('', include(artist_tracks_router.urls)),
    path('', include(artist_album_tracks_router.urls)),
    path('', include(album_tracks_router.urls)),
    path('', include(swagger)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
