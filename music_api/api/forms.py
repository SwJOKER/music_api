from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField

from .models import AlbumTrack, Track


class UpperCaseField(CharField):
    def clean(self, value):
        try:
            return Track.objects.get(name__iexact=value.lower())
        except:
            raise ValidationError

class AlbumsTrackForm(ModelForm):
    track = CharField(max_length=255, required=True)
    class Meta:
        model = AlbumTrack
        fields = '__all__'


    def save(self, commit=True):
        print(self.instance)
        instance = super().save(commit)
        print(instance)
        return instance
