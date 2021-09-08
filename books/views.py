from django.db.models import QuerySet
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from books.external_api_adapter import get_external_books, api_adapter
from books.helpers import format_and_wrap_data
from books.models import Book
from books.serializer_helpers import change_authors_format_from_data
from books.serializers import BookSerializer


class ExternalBooks(APIView):

    def get(self, request, format=None):
        book_name = request.GET.get('name', None)

        api_status, details = get_external_books(name=book_name)

        # if api request was not success
        if api_status != status.HTTP_200_OK:
            return Response(format_and_wrap_data(api_status, details), status=api_status)

        serializer = BookSerializer(data=api_adapter(details), many=True)
        if serializer.is_valid():
            external_books = serializer.to_representation(data=api_adapter(details))
            return Response(format_and_wrap_data(200, 'success', external_books), status.HTTP_200_OK)

        return Response(format_and_wrap_data(status.HTTP_400_BAD_REQUEST, serializer.errors),
                        status.HTTP_400_BAD_REQUEST)


# @api_view(['GET', 'POST'])
class BookList(APIView):
    """
    List all books, or create a new book
    """
    def get_book_queryset(self, query_data) -> QuerySet:
        search_dictionary = {}
        'name' in query_data.keys() and search_dictionary.update({'name': query_data['name']})
        'country' in query_data.keys() and search_dictionary.update({'country': query_data['country']})
        'publisher' in query_data.keys() and search_dictionary.update({'publisher': query_data['publisher']})
        'release_date' in query_data.keys() and search_dictionary.update({
            'release_date__year': query_data['release_date']})
        
        return Book.objects.filter(**search_dictionary)

    def get(self, request, format=None):
        books = self.get_book_queryset(query_data=request.GET)
        serializer = BookSerializer(books, many=True)
        return Response(format_and_wrap_data(200, 'success', serializer.data))

    def post(self, request, format=None):
        serializer = BookSerializer(data=change_authors_format_from_data(request.data))
        if serializer.is_valid():
            serializer.save()
            return Response(format_and_wrap_data(status.HTTP_201_CREATED, 'success', serializer.data),
                            status=status.HTTP_201_CREATED)
        return Response(format_and_wrap_data(status.HTTP_400_BAD_REQUEST, serializer.errors),
                        status=status.HTTP_400_BAD_REQUEST)


# @api_view(['PATCH', 'DELETE'])
class BookUpdate(APIView):

    def get_book(self, pk):
        try:
            return Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        book = self.get_book(pk)
        serializer = BookSerializer(book)

        return Response(format_and_wrap_data(200, 'success', data=serializer.data))

    def delete(self, request, pk, format=None):
        book = self.get_book(pk)
        message = f"The book {book.name} was deleted successfully."
        book.delete()
        
        response_data = format_and_wrap_data(204, 'success', [])
        response_data['message'] = message
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk, format=None):
        book = self.get_book(pk)
        message = f"The book {book.name} was updated successfully."
        serializer = BookSerializer(book, data=change_authors_format_from_data(request.data), partial=True)

        if serializer.is_valid():
            serializer.save()
            response_data = format_and_wrap_data(200, "success", serializer.data)
            response_data['message'] = message
            return Response(response_data, status=200)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
