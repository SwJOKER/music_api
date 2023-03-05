import django_filters.rest_framework
from django.db.models import Prefetch, Count
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.exceptions import APIException
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import AlbumSerializer, AlbumTrackSerializer, TrackSerializer, query_debugger, ArtistSerializer
from .models import Album, Artist, Track, AlbumTrack


class Paginator(PageNumberPagination):
    page_size = 200


class AutoManySerializerMixin:

    def create(self, request, *args, **kwargs):
        many = True if isinstance(request.data, list) else False
        serializer = self.get_serializer(data=request.data, many=many)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AlbumViewSet(AutoManySerializerMixin, viewsets.ModelViewSet):

    serializer_class = AlbumSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['artist__name', 'year', 'name']

    def get_queryset(self):
        kwargs = self.request.parser_context.get('kwargs')
        artist_pk = kwargs.get('artists_pk')
        if artist_pk:
            self.pagination_class = None
            queryset = Album.objects.filter(artist_id=artist_pk).prefetch_related('tracks')
        else:
            self.pagination_class = Paginator
            queryset = Album.objects.prefetch_related('tracks')
        queryset = queryset.annotate(tracks_count=Count('tracks')).order_by('-id')
        return queryset


class ArtistViewSet(AutoManySerializerMixin, viewsets.ModelViewSet):

    serializer_class = ArtistSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    queryset = Artist.objects.annotate(albums_count=Count('albums', distinct=True), tracks_count=Count('tracks', distinct=True)).all()
    pagination_class = Paginator


class TrackViewSet(AutoManySerializerMixin, viewsets.ModelViewSet):

    serializer_class = TrackSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['artist', 'name']

    def get_queryset(self):
        prefetch = Prefetch('album_track', queryset=AlbumTrack.objects.select_related('album'))
        if self.basename == 'tracks':
            self.pagination_class = Paginator
            queryset = Track.objects.prefetch_related(prefetch).order_by('-id').all()
        else:
            self.pagination_class = None
            artist_pk = self.request.parser_context.get('kwargs').get('artists_pk')
            try:
                queryset = Track.objects.filter(artist=artist_pk).prefetch_related(prefetch).order_by('-id')
            except Artist.DoesNotExist:
                raise APIException("Artist not found")
            if not queryset:
                raise APIException("No tracks yet")
        return queryset


class AlbumTrackViewSet(viewsets.ModelViewSet, AutoManySerializerMixin):

    serializer_class = AlbumTrackSerializer
    lookup_field = 'order'

    def get_queryset(self):
        kwargs = self.request.parser_context.get('kwargs')
        album_pk = next(value for key, value in kwargs.items() if key.endswith('albums_pk'))
        queryset = AlbumTrack.objects.filter(album=album_pk).select_related('track', 'album').order_by('order')
        return queryset