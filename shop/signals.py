from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .cache import invalidate_catalog_cache
from .models import Author, Book, Category, Publisher


@receiver([post_save, post_delete], sender=Book)
def invalidate_book_cache(sender, instance, **kwargs):
    invalidate_catalog_cache(book_id=instance.pk)


@receiver(m2m_changed, sender=Book.author.through)
@receiver(m2m_changed, sender=Book.category.through)
def invalidate_book_m2m_cache(sender, instance, **kwargs):
    if kwargs.get('action') in {'post_add', 'post_remove', 'post_clear'}:
        invalidate_catalog_cache(book_id=instance.pk)


@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=Author)
@receiver([post_save, post_delete], sender=Publisher)
def invalidate_related_catalog_cache(sender, instance, **kwargs):
    invalidate_catalog_cache()
