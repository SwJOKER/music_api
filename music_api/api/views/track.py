from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from .mixins import AutoManySerializerMixin, DiscreteRetrieveSerializerMixin
from .paginators import Paginator
from ..models import AlbumTrack, Artist, Track, Album
from ..serializers import ArtistTrackSerializer, TrackSerializer, AlbumTrackSerializer, ArtistTrackRetrieveSerializer
from ..utils import query_debugger


class ArtistTrackViewSet(AutoManySerializerMixin, DiscreteRetrieveSerializerMixin, viewsets.ModelViewSet):
    serializer_class = ArtistTrackSerializer
    retrieve_serializer_class = ArtistTrackRetrieveSerializer

    def get_queryset(self):
        prefetch = Prefetch('album_track', queryset=AlbumTrack.objects.select_related('album'))
        artist_pk = self.request.parser_context.get('kwargs').get('artists_pk')
        if getattr(self, 'swagger_fake_view', False):
            return Track.objects.prefetch_related(prefetch).order_by('-id')
        if artist_pk and not Artist.objects.filter(pk=artist_pk).exists():
            raise APIException('Artist not found')
        queryset = Track.objects.filter(artist=artist_pk).prefetch_related(prefetch).order_by('-id')
        return queryset


class TrackViewSet(AutoManySerializerMixin, viewsets.ModelViewSet):

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['artist__name', 'name']
    serializer_class = TrackSerializer
    pagination_class = Paginator

    def get_queryset(self):
        prefetch = Prefetch('album_track', queryset=AlbumTrack.objects.select_related('album'))
        queryset = Track.objects.prefetch_related(prefetch).order_by('-id').all()
        return queryset


class AlbumTrackViewSet(AutoManySerializerMixin, viewsets.ModelViewSet):

    serializer_class = AlbumTrackSerializer
    lookup_field = 'order'
    http_method_names = ['get', 'post', 'delete', 'head', 'options', 'trace']

    def destroy(self, request, *args, **kwargs):
        order = self.request.parser_context.get('kwargs').get('order')
        queryset = self.get_queryset().filter(order__gt=order)
        response = super().destroy(request, *args, **kwargs)
        print(response.status_code)
        if response.status_code == 204:
            print('asdf')
            update_obj = []
            for item in queryset:
                item.order = item.order - 1
                update_obj.append(item)
            queryset.bulk_update(update_obj, ['order'])
        return response

    def get_queryset(self):
        kwargs = self.request.parser_context.get('kwargs')
        album_pk = next(value for key, value in kwargs.items() if key.endswith('albums_pk'))
        artist_pk = self.request.parser_context.get('kwargs').get('artists_pk')
        if getattr(self, 'swagger_fake_view', False):
            return AlbumTrack.objects.select_related('track', 'album').order_by('order')
        if album_pk and not Album.objects.filter(pk=album_pk).exists():
            raise APIException('Album not found')
        if artist_pk and not Artist.objects.filter(pk=artist_pk).exists():
            raise APIException('Artist not found')
        queryset = AlbumTrack.objects.filter(album=album_pk).select_related('track', 'album').order_by('order')
        return queryset
