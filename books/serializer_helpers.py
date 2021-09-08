import copy
import json


def change_authors_format_from_data(data: dict):
    """
    Since AuthorSerializer needs data in dictionary format and the data coming is in list format, therefore this
        function converts it into dictionary format
    """
    converted_data = copy.deepcopy(data)
    author_data = data.get('authors', [])
    if type(author_data) == str:
        author_data = json.loads(author_data)

    converted_authors = [{"name": author} for author in author_data]
    converted_data['authors'] = converted_authors
    return converted_data
