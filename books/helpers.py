import collections

from books.models import Author, Book


def format_and_wrap_data(status_code: int, status: str, data=None):
    print(data)
    data_to_send = {
        "status_code": status_code,
        "status": status,
    }
    data is not None and data_to_send.update({"data": data})
    return data_to_send


def get_author(author_obj: collections.OrderedDict) -> Author:
    """
    Creates author with the author_obj if it does not exist already, else returns an already existing author
    Returns an author object
    """
    query = Author.objects.filter(name=author_obj.get('name'))
    if query.exists():
        return query[0]
    
    return Author.objects.create(name=author_obj.get('name'))


def add_authors(instance: Book, authors: list) -> Book:
    """
    Removes existing authors and updates it with the given list of authors
    """
    instance.authors.set([])
    print(authors)
    for author in authors:
        author_obj = get_author(author)
        instance.authors.add(author_obj)
    return instance
