import json
from enum import Enum

from django.db.models import Prefetch
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import APIException

from .models import Album, Artist, Track, AlbumTrack
from .utils import query_debugger

# set parent as default value for foreign key
class ContextUtilsMixin:

    @property
    def request_kwargs(self):
        return self.context.get('request').parser_context.get('kwargs')

    @property
    def current_basename(self):
        return self.context['request'].parser_context.get('view').basename

    def get_defined_album_id(self):
        if self.current_basename.endswith('albums') and self.request_kwargs.get('pk'):
            return self.request_kwargs.get('pk')
        try:
            return next(value for key, value in self.request_kwargs.items() if key.endswith('albums_pk'))
        except StopIteration:
            return None

    def get_defined_artist_id(self):
        if self.current_basename.endswith('artists') and self.request_kwargs.get('pk'):
            return self.request_kwargs.get('pk')
        try:
            return next(value for key, value in self.request_kwargs.items() if key.endswith('artist_pk'))
        except StopIteration:
            return None


class TrackSerializer(serializers.ModelSerializer, ContextUtilsMixin):
    albums = serializers.SerializerMethodField()
    artist_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Track
        fields = ['id', 'name', 'artist', 'albums', 'artist_id']
        depth = 1

    # albums from album tracks related to track
    def get_albums(self, instance):
        albums = {}
        for item in instance.album_track.all():
            album = item.album
            albums.update({album.id: {'id': album.id, 'name': album.name}})
        return [album for album in albums.values()]

    # take artist_pk from request if possible
    def validate(self, attrs):
        if artist_id := self.get_defined_artist_id():
            attrs.update({'artist_id': artist_id})
        return attrs

    # delete fields which defined in url
    def get_fields(self):
        fields = super().get_fields()
        if self.current_basename != 'tracks':
            if self.get_defined_artist_id():
                fields.pop('artist_id')
            if self.get_defined_album_id():
                fields.pop('albums')
        return fields

    # hide artist data if it exists in request
    # hide id if retrieve request
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if self.get_defined_artist_id():
            rep.pop('artist')
        if self.current_basename.endswith('tracks') and self.request_kwargs.get('pk'):
            rep.pop('id')
        return rep


class AlbumTrackSerializer(serializers.ModelSerializer, ContextUtilsMixin):
    name = serializers.CharField(source='track.name', read_only=True)
    track_id = serializers.IntegerField(write_only=False, required=False)

    class Meta:
        model = AlbumTrack
        fields = ['order', 'track_id', 'name']
        extra_kwargs = {
            'order': {'required': False},
        }

    @property
    def album_tracks_queryset(self):
        if not hasattr(self, '_album_tracks_queryset'):
            self._album_tracks_queryset = AlbumTrack.objects.filter(album=self.get_defined_album_id()).order_by('-order').all()
        return self._album_tracks_queryset


    def get_max_order(self):
        if queryset := self.album_tracks_queryset:
            max_order = queryset.first().order + 1
        else:
            max_order = 1
        return max_order

    def update_tracks_order(self, new_item_order):
        queryset = self.album_tracks_queryset.filter(order__gte=new_item_order)
        updating = []
        for album_track in queryset:
            album_track.order = album_track.order + 1
            updating.append(album_track)
        queryset.bulk_update(updating, ['order'])

    @query_debugger
    def validate(self, attrs):
        if track_id := attrs.get('track_id'):
            try:
                Track.objects.filter(artist=self.get_defined_artist_id()).get(pk=track_id)
            except Track.DoesNotExist:
                raise serializers.ValidationError('track_id: Track Not Found')
        max_order = self.get_max_order()
        if order_value := attrs.get('order'):
            if order_value > max_order:
                raise serializers.ValidationError(f'order: max order is {max_order}')
            elif order_value < max_order:
                self.update_tracks_order(order_value)
        else:
            attrs.update({'order': max_order})
        attrs.update({'album_id': self.get_defined_album_id()})
        return attrs

    # I wanted to implement feature that provides creating AlbumTrack without parental Track id, through search by name
    # and if it not exists, create a new one. But i thought it was a bad idea and could make space for errors.
    # In any case I left it here.

    # def create(self, validated_data):
    #     track_name = validated_data.pop('track').get('name').strip()
    #     artist_pk = self.request_kwargs.get('artists_pk')
    #     if track_name and artist_pk and not validated_data.get('id'):
    #         prefetch = Prefetch('track_set', queryset=Track.objects.filter(name__iexact=track_name))
    #         artist = Artist.objects.filter(pk=artist_pk).prefetch_related(prefetch)[0]
    #         if track_set := artist.track_set.all():
    #             track = track_set[0]
    #         else:
    #             track = artist.track_set.create(name=track_name)
    #         validated_data.update({'track_id': track.id})
    #     try:
    #         instance = super().create(validated_data)
    #     except TypeError as e:
    #         if track is not None:
    #             track.delete()
    #             raise e
    #     return instance


class AlbumSerializer(serializers.ModelSerializer, ContextUtilsMixin):
    tracks = serializers.SerializerMethodField()
    tracks_count = serializers.SerializerMethodField()
    artist_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Album
        fields = ['id', 'name', 'year', 'artist', 'tracks', 'artist_id', 'tracks_count']
        depth = 1

    def get_tracks_count(self, instance):
        return instance.tracks_count

    def get_tracks(self, instance):
        tracks = instance.tracks.all().order_by('order')
        return AlbumTrackSerializer(tracks, many=True).data

    def validate(self, attrs):
        if artist_id := self.get_defined_artist_id():
            attrs.update({'artist_id': artist_id})
        return attrs

    def get_fields(self):
        fields = super().get_fields()
        if self.get_defined_artist_id():
            fields.pop('artist_id')
        return fields

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        match self.current_basename.endswith('albums'), self.request_kwargs.get('pk'):
            case True, None:
                rep.pop('tracks')
            case _:
                rep.pop('tracks_count')
        if self.get_defined_artist_id():
            rep.pop('artist')
        return rep


class ArtistSerializer(serializers.ModelSerializer):
    tracks_count = serializers.SerializerMethodField()
    albums_count = serializers.SerializerMethodField()
    class Meta:
        model = Artist
        fields = ['id', 'name', 'tracks_count', 'albums_count']

    @query_debugger
    def get_tracks_count(self, instance):
        if hasattr(instance, 'tracks_count'):
            return instance.tracks_count
        return 0

    @query_debugger
    def get_albums_count(self, instance):
        if hasattr(instance, 'albums_count'):
            return instance.albums_count
        return 0




