from rest_framework import serializers

from books.helpers import add_authors
from books.models import Book, Author


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'
        extra_kwargs = {
            'name': {'validators': []}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        return representation.pop('name')


class BookSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True, max_length=100)
    isbn = serializers.CharField(required=True, max_length=100)
    publisher = serializers.CharField(required=False, default='', max_length=100)
    number_of_pages = serializers.IntegerField(required=True)
    country = serializers.CharField(required=False, default='', max_length=100)
    release_date = serializers.DateField(format='iso-8601', input_formats=["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"])
    authors = AuthorSerializer(many=True, required=True)

    def create(self, validated_data):
        print(f"{validated_data = }")
        authors = validated_data.pop('authors', [])

        print("Authors found:", authors)
        book_object = Book.objects.create(**validated_data)

        book_object = add_authors(book_object, authors)
        
        book_object.save()
        return book_object

    def update(self, instance: Book, validated_data) -> Book:
        instance.name = validated_data.get('name', instance.name)
        instance.publisher = validated_data.get('publisher', instance.publisher)
        instance.release_date = validated_data.get('release_date', instance.release_date)
        instance.isbn = validated_data.get('isbn', instance.isbn)
        instance.country = validated_data.get('country', instance.country)
        instance.number_of_pages = validated_data.get('number_of_pages', instance.number_of_pages)

        new_authors = validated_data.get('authors', [])
        
        if len(new_authors):
            instance = add_authors(instance, new_authors)

        instance.save()
        return instance
