from django.contrib import admin

from .forms import AlbumsTrackForm
from .models import Artist, Album, Track, AlbumTrack


# Register your models here.

class TrackInline(admin.TabularInline):
    extra = 1
    model = AlbumTrack
   # form = AlbumsTrackForm
    show_change_link = True

@admin.register(Artist)
class AuthorAdmin(admin.ModelAdmin):
    fields = ['name']


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    fields = ['name', 'artist', 'year']
  #  inlines = [TrackInline]


@admin.register(AlbumTrack)
class AlbumsTrackAdmin(admin.ModelAdmin):
 #   form = AlbumsTrackForm
    fields = ['album', 'track', 'order']


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
 #   form = AlbumsTrackForm
    fields = ['name', 'artist']