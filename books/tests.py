import datetime

from django.test import TestCase

from books.external_api_adapter import get_external_books, api_adapter
from books.helpers import format_and_wrap_data
from books.models import Book, Author
from books.serializer_helpers import change_authors_format_from_data
from books.serializers import BookSerializer


def create_book_object(author: list, name='Book 2', isbn='4846616-11', release_date='2020-07-02', number_of_pages=8):
    if not author:
        author = ['Hatim', 'Hasan']

    book_object = Book.objects.create(
        name=name,
        isbn=isbn,
        release_date=datetime.datetime.strptime(release_date, "%Y-%m-%d").date(),
        number_of_pages=number_of_pages,
    )

    for name in author:
        author_object = Author.objects.create(name=name)
        book_object.authors.add(author_object)
    return book_object


def check_authors(book_instance: Book, authors: list) -> bool:
    if book_instance.authors.count() != len(authors):
        return False

    book_authors = [author.name for author in book_instance.authors.all()]
    return True if len(set(book_authors).union(authors)) == len(authors) else False


class BookTestCase(TestCase):

    def test_book_object_serialization(self):
        book_object = create_book_object(name='Test Book', author=['Hatim', 'Hussain'])

        serializer = BookSerializer(book_object)
        serialized_data = serializer.data

        print(serialized_data)
        self.assertEqual(serialized_data['name'], 'Test Book')
        self.assertEqual(serialized_data['release_date'], '2020-07-02')
        print(serialized_data['authors'])
        self.assertEqual(serialized_data['authors'], ['Hatim', 'Hussain'])

    def test_data_conversion_to_book_object(self):
        data = {
            "name": "Clean Code Book",
            "authors": ["Hatim", "Bob Martin"],
            "isbn": "123-45",
            "release_date": "2020-01-01",
            "number_of_pages": 7,
        }
        data = change_authors_format_from_data(data)

        serializer = BookSerializer(data=data)

        valid_serialization = serializer.is_valid()
        if not valid_serialization:
            print(serializer.errors)
        self.assertTrue(valid_serialization)
        book_object = serializer.save()

        self.assertEqual(book_object.name, data['name'])
        self.assertTrue(check_authors(book_object, [author['name'] for author in data['authors']]))

    def test_external_books_api(self):
        api_status, details = get_external_books(name='A Game of Thrones')

        serializer = BookSerializer(data=api_adapter(details), many=True)
        valid_serialization = serializer.is_valid()
        if not valid_serialization:
            print(serializer.errors)
        self.assertTrue(valid_serialization)

        self.assertEqual({
                "status_code": 200,
                "status": "success",
                "data": [
                    {
                        "name": "A Game of Thrones",
                        "isbn": "978-0553103540",
                        "publisher": "Bantam Books",
                        "number_of_pages": 694,
                        "country": "United States",
                        "release_date": "1996-08-01",
                        "authors": [
                            "George R. R. Martin"
                        ]
                    }
                ]
            }, format_and_wrap_data(api_status, 'success', serializer.to_representation(data=api_adapter(details))))

    def test_update_book_details(self):
        # creating book
        book_instance = create_book_object(author=['Ben', 'Martin'])

        change_authors_data = change_authors_format_from_data({
            "authors": ["Hatim", "Hasan"]
        })
        
        # updating authors
        serializer = BookSerializer(book_instance, data=change_authors_data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertTrue(check_authors(book_instance, ['Hatim', 'Hasan']))
        self.assertEqual(book_instance.isbn, "4846616-11")
        self.assertEqual(book_instance.number_of_pages, 8)
        self.assertEqual(book_instance.publisher, '')
        
        # now updating only publisher and number of pages
        update_book_details = change_authors_format_from_data({
            "publisher": "Disney",
            "number_of_pages": "100"
        })

        serializer = BookSerializer(book_instance, data=update_book_details, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(book_instance.publisher, "Disney")
        self.assertEqual(book_instance.name, "Book 2")
        self.assertEqual(book_instance.number_of_pages, 100)
        self.assertTrue(check_authors(book_instance, ['Hatim', 'Hasan']))
