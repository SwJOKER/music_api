from rest_framework import serializers

from .track import AlbumTrackSerializer
from .mixins import ContextUtilsMixin
from ..models import Album


class ArtistAlbumRetrieveSerializer(serializers.ModelSerializer):
    tracks_count = serializers.IntegerField(read_only=True, default=0)
    tracks = AlbumTrackSerializer(read_only=True, many=True)

    class Meta:
        model = Album
        fields = ['name', 'year', 'tracks_count', 'tracks']
        depth = 1


class AlbumRetrieveSerializer(ArtistAlbumRetrieveSerializer):
    artist_id = serializers.IntegerField(write_only=True, required=True)
    artist_name = serializers.CharField(read_only=True, source='artist.name')

    class Meta:
        model = Album
        fields = ArtistAlbumRetrieveSerializer.Meta.fields + ['artist_name', 'artist_id']
        depth = 1


class ArtistAlbumSerializer(serializers.ModelSerializer, ContextUtilsMixin):
    tracks_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Album
        fields = ['id', 'name', 'year', 'tracks_count']
        depth = 1

    def validate(self, attrs):
        attrs.update({'artist_id': self.get_artist_id()})
        return attrs


class AlbumSerializer(ArtistAlbumSerializer):
    artist_id = serializers.IntegerField(write_only=True, required=True)
    artist_name = serializers.CharField(read_only=True, source='artist.name')

    class Meta:
        model = Album
        fields = ['id', 'name', 'year', 'artist_name', 'artist_id', 'tracks_count']
        depth = 1
