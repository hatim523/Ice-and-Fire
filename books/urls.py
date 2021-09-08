from django.urls import path

from . import views

app_name = "books"

urlpatterns = [
    path('external-books', views.ExternalBooks.as_view(), name='external-books'),

    path('v1/books', views.BookList.as_view(), name='books'),
    path('v1/books/<int:pk>', views.BookUpdate.as_view(), name='book-update'),
]
