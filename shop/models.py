from django.db import models

# Create your models here.
class Publisher(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    website = models.URLField(max_length=100)
    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    bio = models.TextField()
    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ManyToManyField(Author)
    category = models.ManyToManyField(Category)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
    published_year = models.IntegerField()
    amount = models.IntegerField()
    available = models.BooleanField(default=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    calculated_average = models.DecimalField(max_digits=3, decimal_places=2)
    def __str__(self):
        return self.title

class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(Author, on_delete=models.CASCADE)
    rating = models.IntegerField()
    feedback = models.TextField()
