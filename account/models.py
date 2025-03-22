
from django.contrib.auth.models import User
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    img = models.ImageField(upload_to='products/', null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE)
  
    def __str__(self):
        
        return self.name

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')