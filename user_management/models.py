from django.db import models

class DeliveryAddress(models.Model):
    post_code = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    branch = models.CharField(max_length=50)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)

class LastView (models.Model):
    book = models.ForeignKey('shop.Book', on_delete=models.CASCADE)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)