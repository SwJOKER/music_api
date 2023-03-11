from django.db.models import Count, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import APIException

from .mixins import AutoManySerializerMixin, DiscreteRetrieveSerializerMixin
from .paginators import Paginator
from ..models import Album, Artist, AlbumTrack
from ..serializers import AlbumSerializer, AlbumRetrieveSerializer, ArtistAlbumSerializer, ArtistAlbumRetrieveSerializer


class AlbumViewSet(AutoManySerializerMixin, DiscreteRetrieveSerializerMixin, viewsets.ModelViewSet):
    serializer_class = AlbumSerializer
    retrieve_serializer_class = AlbumRetrieveSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['artist__name', 'year', 'name']
    pagination_class = Paginator

    def get_queryset(self):
        prefetch_tracks = Prefetch('tracks', queryset=AlbumTrack.objects.select_related('track').order_by('order'))
        queryset = Album.objects.prefetch_related(prefetch_tracks)
        queryset = queryset.annotate(tracks_count=Count('tracks')).order_by('-id')
        return queryset


class ArtistAlbumViewSet(AutoManySerializerMixin, DiscreteRetrieveSerializerMixin, viewsets.ModelViewSet):
    serializer_class = ArtistAlbumSerializer
    retrieve_serializer_class = ArtistAlbumRetrieveSerializer

    def get_queryset(self):
        kwargs = self.request.parser_context.get('kwargs')
        artist_pk = kwargs.get('artists_pk')
        if getattr(self, 'swagger_fake_view', False):
            return Album.objects.prefetch_related('tracks')
        if not Artist.objects.filter(pk=artist_pk).exists():
            raise APIException('Artist not found')
        prefetch_tracks = Prefetch('tracks', queryset=AlbumTrack.objects.select_related('track').order_by('order'))
        queryset = Album.objects.filter(artist_id=artist_pk).prefetch_related(prefetch_tracks)
        return queryset.annotate(tracks_count=Count('tracks')).order_by('-id')
