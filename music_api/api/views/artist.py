from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .paginators import Paginator
from ..models import Artist
from ..serializers import ArtistSerializer
from .mixins import AutoManySerializerMixin


class ArtistViewSet(AutoManySerializerMixin, viewsets.ModelViewSet):

    serializer_class = ArtistSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    queryset = Artist.objects.annotate(albums_count=Count('albums', distinct=True),
                                       tracks_count=Count('tracks', distinct=True)).all()
    pagination_class = Paginator
