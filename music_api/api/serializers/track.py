from django.db.models import Prefetch
from rest_framework import serializers
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

    def to_representation(self, instance):
        return super().to_representation(instance)

    @property
    def album(self):
        prefetch = Prefetch('tracks', queryset=AlbumTrack.objects.select_related('track').order_by('-order'))
        if not hasattr(self, '_album'):
            self._album = Album.objects.filter(pk=self.get_album_id()).prefetch_related(prefetch)[0]
        return self._album

    def get_max_order(self):
        if not hasattr(self, '_max_order'):
            if queryset := self.album.tracks.all():
                self._max_order = queryset.first().order + 1
            else:
                self._max_order = 1
        return self._max_order

    def increase_max_order(self):
        if not hasattr(self, '_max_order'):
            self._max_order = self._max_order + 1

    def update_tracks_order(self, new_item_order):
        queryset = self.album.tracks.filter(order__gte=new_item_order)
        updating = []
        for album_track in queryset:
            album_track.order = album_track.order + 1
            updating.append(album_track)
        queryset.bulk_update(updating, ['order'])

    def fill_track_data(self, track):
        track.update({'artist_id': self.album.id})

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
                self.album.tracks.get(pk=track_id)
            except Track.DoesNotExist:
                raise serializers.ValidationError('id: Track Not Found')
        else:
            self.fill_track_data(track)
        max_order = self.get_max_order()
        if order_value := attrs.get('order'):
            if order_value > max_order:
                raise serializers.ValidationError(f'order: max order is {max_order}')
        attrs.update({'album_id': self.album.id})
        return attrs

    def create(self, validated_data):
        order = validated_data.get('order')
        if not order:
            order = self.get_max_order()
        else:
            if order < self.get_max_order():
                self.update_tracks_order(order)
        validated_data.update({'order': order})
        if validated_data.get('track_id'):
            obj = AlbumTrack.objects.create(**validated_data)
        else:
            track_data = validated_data.pop('track')
            track = Track.objects.create(**track_data)
            obj = AlbumTrack.objects.create(track=track, **validated_data)
        self.increase_max_order()
        return obj
