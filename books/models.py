from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=200, primary_key=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=100)
    isbn = models.CharField(max_length=100)
    number_of_pages = models.IntegerField()
    country = models.CharField(max_length=100)
    release_date = models.DateField()
    publisher = models.CharField(max_length=100)
    authors = models.ManyToManyField(Author)
