import copy
import datetime

import requests

from Ice_and_Fire.settings import ICE_AND_FIRE_BOOK_QUERY_ENDPOINT
from books.serializer_helpers import change_authors_format_from_data


def get_external_books(name: str = None, from_release_date: str = None, to_release_date: str = None) -> tuple:
    """
    External API Endpoint to get books from the given parameters
    Returns:
        tuple: (status code, response as json)
    """
    if name is None and from_release_date is None and to_release_date is None:
        return 400, "No parameters provided for search"

    # forming query context
    query_params = {}
    name is not None and query_params.update({"name": name})
    from_release_date is not None and query_params.update({"fromReleaseDate": from_release_date})
    to_release_date is not None and query_params.update({"toReleaseDate": to_release_date})

    resp = requests.get(ICE_AND_FIRE_BOOK_QUERY_ENDPOINT, query_params)
    return resp.status_code, resp.json()


def api_adapter(book_list: list):
    """
    Adapts the api output so that it can be fed to serializer
    """
    new_book_list = []
    # deepcopy to not mutate original data, instead return a new copy of updated data
    book_list = copy.deepcopy(book_list)

    for book in book_list:
        # changing key names for serializer
        book['number_of_pages'] = book['numberOfPages']
        book['release_date'] = datetime.datetime.strptime(book['released'], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")

        # now popping old keys
        book.pop('numberOfPages')
        book.pop('released')

        book = change_authors_format_from_data(book)
        new_book_list.append(book)

    return new_book_list
