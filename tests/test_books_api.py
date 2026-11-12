
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
def mock_books():
    with patch("app.books_collection") as collection:
        yield collection


def test_get_books(client, mock_books):
    mock_books.find.return_value = [
        {
            "_id": ObjectId(),
            "title": "1984",
            "author": "George Orwell",
            "genre": "Dystopian Fiction"
        }
    ]

    response = client.get("/api/books")

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["title"] == "1984"


def test_get_empty_books(client, mock_books):
    mock_books.find.return_value = []

    response = client.get("/api/books")

    assert response.status_code == 200
    assert response.json == []


def test_add_valid_book(client, mock_books):
    mock_books.insert_one.return_value = MagicMock(
        inserted_id=ObjectId()
    )

    response = client.post("/api/books", json={
        "title": "Dune",
        "author": "Frank Herbert",
        "genre": "Science Fiction"
    })

    assert response.status_code == 201
    assert response.json["book"]["title"] == "Dune"
    mock_books.insert_one.assert_called_once()


def test_add_book_missing_title(client, mock_books):
    response = client.post("/api/books", json={
        "author": "Frank Herbert",
        "genre": "Science Fiction"
    })

    assert response.status_code == 400
    assert "title" in response.json["error"]
    mock_books.insert_one.assert_not_called()


def test_add_book_empty_title(client, mock_books):
    response = client.post("/api/books", json={
        "title": "   ",
        "author": "Frank Herbert",
        "genre": "Science Fiction"
    })

    assert response.status_code == 400
    mock_books.insert_one.assert_not_called()


def test_add_book_invalid_type(client, mock_books):
    response = client.post("/api/books", json={
        "title": 123,
        "author": "Frank Herbert",
        "genre": "Science Fiction"
    })

    assert response.status_code == 400
    mock_books.insert_one.assert_not_called()


def test_add_book_not_json(client, mock_books):
    response = client.post(
        "/api/books",
        data="hello",
        content_type="text/plain"
    )

    assert response.status_code == 415
    mock_books.insert_one.assert_not_called()


def test_add_book_trims_spaces(client, mock_books):
    mock_books.insert_one.return_value = MagicMock(
        inserted_id=ObjectId()
    )

    response = client.post("/api/books", json={
        "title": "  Dune  ",
        "author": " Frank Herbert ",
        "genre": " Science Fiction "
    })

    assert response.status_code == 201
    assert response.json["book"]["title"] == "Dune"

    saved_book = mock_books.insert_one.call_args.args[0]
    assert saved_book["author"] == "Frank Herbert"
