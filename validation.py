REQUIRED_FIELDS = ("title", "author", "genre")


def validate_book(data):
    if not isinstance(data, dict):
        return None, "Request must be in JSON"

    cleaned_book = {}

    for field in REQUIRED_FIELDS:
        value = data.get(field)

        if not isinstance(value, str):
            return None, f"{field} must be a string"

        value = value.strip()

        if not value:
            return None, f"{field} can't be empty"

        if len(value)>200:
            return None, f'{field} cannot exceed 200 characters'

        cleaned_book[field] = value

    return cleaned_book, None