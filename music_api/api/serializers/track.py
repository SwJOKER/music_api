from django.db.models import Prefetch
from rest_framework import serializers
from rest_framework.fields import empty

from .mixins import ContextUtilsMixin
from ..models import Track, AlbumTrack, Album


class ArtistTrackSerializer(serializers.ModelSerializer, ContextUtilsMixin):
    albums = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = ['id', 'name', 'albums']
        depth = 1

    def validate(self, attrs):
        if artist_id := self.get_artist_id():
            attrs.update({'artist_id': artist_id})
        return attrs

    def get_albums(self, instance):
        albums = {}
        for item in instance.album_track.all():
            album = item.album
            albums.update({album.id: {'id': album.id, 'name': album.name}})
        return [album for album in albums.values()]


class ArtistTrackRetrieveSerializer(ArtistTrackSerializer):
    class Meta:
        model = Track
        fields = ['name', 'albums']
        depth = 1


class TrackRetrieveSerializer(ArtistTrackRetrieveSerializer):
    artist_name = serializers.CharField(source='artist.name', read_only=True)
    artist_id = serializers.IntegerField()

    class Meta:
        model = Track
        fields = ArtistTrackRetrieveSerializer.Meta.fields + ['artist_id', 'artist_name']
        depth = 1


class TrackSerializer(ArtistTrackSerializer):
    artist_name = serializers.CharField(source='artist.name', read_only=True)
    artist_id = serializers.IntegerField()

    class Meta:
        model = Track
        fields = ArtistTrackSerializer.Meta.fields + ['artist_id', 'artist_name']
        depth = 1


class AlbumTrackSerializer(serializers.ModelSerializer, ContextUtilsMixin):
    name = serializers.CharField(source='track.name', read_only=False, required=False)
    id = serializers.IntegerField(source='track_id', required=False)

    class Meta:
        model = AlbumTrack
        fields = ['order', 'id', 'name']
        extra_kwargs = {
            'order': {'required': False},
        }

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data is not empty and not instance:
            prefetch = Prefetch('tracks', queryset=AlbumTrack.objects.filter(album=self.get_album_id()).
                                select_related('track').order_by('-order'))

            self._album = Album.objects.filter(pk=self.get_album_id()).prefetch_related(prefetch)[0]
            if isinstance(self.initial_data, list):
                orders = [x.get('order') for x in self.initial_data]
                if any(orders) and not all(orders):
                    raise serializers.ValidationError('Order must be at all tracks or at no one at all')
                if not any(orders):
                    start_order = self._album.tracks.first().order + 1 if self._album.tracks.first() else 1
                    for order, track in enumerate(self.initial_data, start=start_order):
                        track.update({'order': order})
                new_objects_count = len(self.initial_data)
            else:
                new_objects_count = 1
            if queryset := self._album.tracks.all():
                self._max_order = queryset.first().order + new_objects_count
            else:
                self._max_order = new_objects_count

    def to_representation(self, instance):
        return super().to_representation(instance)

    def fill_track_data(self, track):
        track.update({'artist_id': self._album.artist.id})

    def validate(self, attrs):
        track_id = attrs.get('track_id')
        track = attrs.get('track')
        if not track and not track_id:
            raise serializers.ValidationError('name, id: one of variables must be defined')
        if track_id and track:
            raise serializers.ValidationError('name, id: only one variable allowed. Name for create, '
                                              'track id for add existing track')
        if track_id:
            try:
                self._album.tracks.get(pk=track_id)
            except Track.DoesNotExist:
                raise serializers.ValidationError('id: Track Not Found')
        else:
            self.fill_track_data(track)
        if order_value := attrs.get('order'):
            if order_value > self._max_order:
                raise serializers.ValidationError(f'order: max order is {self._max_order}')
        else:
            attrs.update({'order': self._max_order})
        attrs.update({'album_id': self._album.id})
        attrs.update({'artist_id': self._album.artist_id})
        return attrs

    def create(self, validated_data):
        if validated_data.get('track_id'):
            obj = AlbumTrack.objects.create(**validated_data)
        else:
            track_data = validated_data.pop('track')
            track = Track.objects.create(**track_data)
            obj = AlbumTrack.objects.create(track=track, **validated_data)
        return obj
