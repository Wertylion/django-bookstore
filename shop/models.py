from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Publisher(models.Model):
    name = models.CharField(_('name'), max_length=100)
    address = models.CharField(_('address'), max_length=100)
    city = models.CharField(_('city'), max_length=100)
    state_province = models.CharField(_('state/province'), max_length=100)
    country = models.CharField(_('country'), max_length=100)
    website = models.URLField(_('website'), max_length=100)

    class Meta:
        verbose_name = _('publisher')
        verbose_name_plural = _('publishers')

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(_('name'), max_length=100)
    email = models.EmailField(_('email'), max_length=100)
    bio = models.TextField(_('bio'))

    class Meta:
        verbose_name = _('author')
        verbose_name_plural = _('authors')

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True, null=True, blank=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(_('title'), max_length=100)
    author = models.ManyToManyField(Author, verbose_name=_('authors'))
    category = models.ManyToManyField(Category, verbose_name=_('categories'))
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(_('added at'), auto_now_add=True)
    published_year = models.IntegerField(_('published year'))
    amount = models.IntegerField(_('amount'))
    available = models.BooleanField(_('available'), default=True)
    publisher = models.ForeignKey(Publisher, verbose_name=_('publisher'), on_delete=models.CASCADE)
    # ВИПРАВЛЕНО: decimal_places=2 але max_digits=3 — це дозволяє максимум 9.99
    # Для рейтингу (наприклад 4.75) краще max_digits=4
    calculated_average = models.DecimalField(_('average rating'), max_digits=4, decimal_places=2, default=0)

    class Meta:
        verbose_name = _('book')
        verbose_name_plural = _('books')

    def __str__(self):
        return self.title


class Rating(models.Model):
    book = models.ForeignKey(Book, verbose_name=_('book'), on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE)
    rating = models.IntegerField(_('rating'))
    feedback = models.TextField(_('feedback'))

    class Meta:
        verbose_name = _('rating')
        verbose_name_plural = _('ratings')

    def __str__(self):
        return f'{self.book.title} — {self.user.username}: {self.rating}'
