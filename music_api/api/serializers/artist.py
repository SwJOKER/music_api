from rest_framework import serializers

from ..models import Artist


class ArtistSerializer(serializers.ModelSerializer):
    tracks_count = serializers.IntegerField(read_only=True, default=0)
    albums_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Artist
        fields = ['id', 'name', 'tracks_count', 'albums_count']
