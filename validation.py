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



def validate_review(data):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object."

    reviewer = data.get("reviewer")
    rating = data.get("rating")
    comment = data.get("comment")


    if not isinstance(reviewer, str):
        return None, "Reviewer name must be a string."

    reviewer = reviewer.strip()

    if not reviewer or len(reviewer) > 100:
        return None, "Reviewer name must be 1-100 characters."


    if type(rating) is not int or not 1 <= rating <= 5:
        return None, "Rating must be an integer from 1 to 5."


    if not isinstance(comment, str):
        return None, "Comment must be a string."

    comment = comment.strip()

    if not comment or len(comment) > 1000:
        return None, "Comment must be 1-1000 characters."

    cleaned_review = {
        "reviewer": reviewer,
        "rating": rating,
        "comment": comment
    }

    return cleaned_review, None
