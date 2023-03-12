from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class StripCharFieldsMixin:
    def clean(self):
        print('Обрееезка')
        for field in self._meta.fields:
            if isinstance(field, models.CharField):
                value = getattr(self, field.name)
                if value:
                    setattr(self, field.name, value.strip())


# Create your models here.
class Artist(models.Model, StripCharFieldsMixin):
    class Meta:
        verbose_name = 'Artist'
        verbose_name_plural = 'Artists'

    name = models.CharField(verbose_name='name', max_length=255, null=False, blank=False, unique=True)

    def __str__(self):
        return self.name


class Album(models.Model, StripCharFieldsMixin):
    class Meta:
        verbose_name = 'Album'
        verbose_name_plural = 'Albums'
        unique_together = ('artist', 'name')

    name = models.CharField(verbose_name='name', max_length=255, null=False, blank=False)
    artist = models.ForeignKey('Artist', related_name='albums', on_delete=models.CASCADE, null=False, blank=False)
    # recorded sound of a human voice was conducted on April 9, 1860
    year = models.SmallIntegerField(verbose_name='Release year', validators=[MinValueValidator(1860),
                                                                             MaxValueValidator(
                                                                                 limit_value=timezone.now().year)])

    def __str__(self):
        return self.name


class Track(models.Model, StripCharFieldsMixin):
    class Meta:
        verbose_name = 'Track'
        verbose_name_plural = 'Tracks'

    name = models.CharField(verbose_name='name', max_length=255, null=False, blank=False)
    artist = models.ForeignKey('Artist', related_name='tracks', on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.name


class AlbumTrack(models.Model, StripCharFieldsMixin):
    class Meta:
        verbose_name = 'Album Track'
        verbose_name_plural = 'Album Tracks'
        unique_together = ('album', 'order')

    order = models.SmallIntegerField(null=False, blank=False, validators=[MinValueValidator(1)])
    track = models.ForeignKey('Track', related_name='album_track', on_delete=models.CASCADE, null=False)
    album = models.ForeignKey('Album', related_name='tracks', on_delete=models.CASCADE, null=False)

    def __str__(self):
        return str(self.track)
