from django.db import transaction
from django.db.models import F
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import AlbumTrack


def update_album_order(queryset, step):
    queryset = queryset.select_for_update()
    with transaction.atomic():
        for album_track in queryset:
            album_track.order = F('order') + step
            album_track.save(update_fields=['order'])


@receiver(pre_save, sender=AlbumTrack)
def update_order_increase(sender, instance: AlbumTrack, **kwargs):
    pre_save.disconnect(update_order_increase, sender=sender)
    queryset = AlbumTrack.objects.filter(album=instance.album_id, order__gte=instance.order).order_by('-order')
    update_album_order(queryset, 1)
    pre_save.connect(update_order_increase, sender=sender)


@receiver(post_delete, sender=AlbumTrack)
def update_order_decrease(sender, instance: AlbumTrack, **kwargs):
    pre_save.disconnect(update_order_increase, sender=sender)
    queryset = AlbumTrack.objects.filter(album=instance.album_id, order__gt=instance.order).order_by('order')
    update_album_order(queryset, -1)
    pre_save.connect(update_order_increase, sender=sender)
