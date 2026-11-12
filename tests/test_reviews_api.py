
import pytest
from bson import ObjectId
from unittest.mock import patch, MagicMock

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def mock_database():
    with patch("app.books_collection") as books:
        with patch("app.reviews_collection") as reviews:
            yield books, reviews


@pytest.fixture
def book_id():
    return ObjectId()


def test_add_valid_review(client, mock_database, book_id):
    books, reviews = mock_database

    books.find_one.return_value = {
        "_id": book_id,
        "title": "The Hobbit"
    }

    reviews.insert_one.return_value = MagicMock(
        inserted_id=ObjectId()
    )

    response = client.post(
        f"/api/books/{book_id}/reviews",
        json={
            "reviewer": "Aidan",
            "rating": 5,
            "comment": "Amazing book!"
        }
    )

    assert response.status_code == 201
    assert response.json["review"]["rating"] == 5

    saved = reviews.insert_one.call_args.args[0]
    assert saved["book_id"] == book_id


@pytest.mark.parametrize("rating", [0, 6, -1, 4.5, "5", True])
def test_invalid_rating(
    client, mock_database, book_id, rating
):
    books, reviews = mock_database

    response = client.post(
        f"/api/books/{book_id}/reviews",
        json={
            "reviewer": "Aidan",
            "rating": rating,
            "comment": "Good book"
        }
    )

    assert response.status_code == 400
    reviews.insert_one.assert_not_called()


def test_missing_comment(client, mock_database, book_id):
    books, reviews = mock_database

    response = client.post(
        f"/api/books/{book_id}/reviews",
        json={
            "reviewer": "Aidan",
            "rating": 5
        }
    )

    assert response.status_code == 400
    reviews.insert_one.assert_not_called()


def test_invalid_book_id(client, mock_database):
    response = client.post(
        "/api/books/not-a-valid-id/reviews",
        json={
            "reviewer": "Aidan",
            "rating": 5,
            "comment": "Great!"
        }
    )

    assert response.status_code == 400


def test_book_not_found(client, mock_database, book_id):
    books, reviews = mock_database

    books.find_one.return_value = None

    response = client.post(
        f"/api/books/{book_id}/reviews",
        json={
            "reviewer": "Aidan",
            "rating": 5,
            "comment": "Great!"
        }
    )

    assert response.status_code == 404
    reviews.insert_one.assert_not_called()


def test_get_reviews_and_average(
    client, mock_database, book_id
):
    books, reviews = mock_database

    books.find_one.return_value = {
        "_id": book_id,
        "title": "The Hobbit"
    }

    reviews.find.return_value = [
        {
            "_id": ObjectId(),
            "book_id": book_id,
            "reviewer": "Aidan",
            "rating": 5,
            "comment": "Amazing!"
        },
        {
            "_id": ObjectId(),
            "book_id": book_id,
            "reviewer": "Mia",
            "rating": 4,
            "comment": "Great!"
        },
        {
            "_id": ObjectId(),
            "book_id": book_id,
            "reviewer": "Alex",
            "rating": 3,
            "comment": "Good!"
        }
    ]

    response = client.get(
        f"/api/books/{book_id}/reviews"
    )

    assert response.status_code == 200
    assert response.json["review_count"] == 3
    assert response.json["average_rating"] == 4.0

    reviews.find.assert_called_once_with({
        "book_id": book_id
    })


def test_get_no_reviews(client, mock_database, book_id):
    books, reviews = mock_database

    books.find_one.return_value = {
        "_id": book_id,
        "title": "The Hobbit"
    }

    reviews.find.return_value = []

    response = client.get(
        f"/api/books/{book_id}/reviews"
    )

    assert response.status_code == 200
    assert response.json["reviews"] == []
    assert response.json["review_count"] == 0
    assert response.json["average_rating"] is None


def test_get_reviews_invalid_id(client, mock_database):
    response = client.get(
        "/api/books/invalid-id/reviews"
    )

    assert response.status_code == 400


def test_get_reviews_book_not_found(
    client, mock_database, book_id
):
    books, reviews = mock_database
    books.find_one.return_value = None

    response = client.get(
        f"/api/books/{book_id}/reviews"
    )

    assert response.status_code == 404
    reviews.find.assert_not_called()
