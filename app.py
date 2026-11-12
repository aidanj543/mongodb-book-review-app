from flask import Flask, jsonify, request
from pymongo.errors import PyMongoError

from database import books_collection
from validation import validate_book


app = Flask(__name__)


def serialize_book(book):
    return {
        "id": str(book["_id"]),
        "title": book["title"],
        "author": book["author"],
        "genre": book["genre"]
    }

@app.route("/")
def home():
    return "Welcome to the Book Review App!"


@app.route("/api/books", methods = ["GET"])
def get_books():

    try:
        books = []

        for book in books_collection.find():
            books.append(serialize_book(book))

        return jsonify(books), 200

    except PyMongoError:
        return jsonify({
            "error": "Unable to retrieve books"
        }), 503


@app.route("/api/books", methods=["POST"])
def add_book():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json"
        }), 415

    data = request.get_json(silent = True)

    cleaned_book, error = validate_book(data)

    if error: return jsonify({'error': error}), 400

    try:
        result = books_collection.insert_one(cleaned_book)

        new_book = {
            "id": str(result.inserted_id),
            "title": cleaned_book["title"],
            "author": cleaned_book["author"],
            "genre": cleaned_book["genre"]
        }

        return jsonify({
            "message": "Book added successfully",
            "book": new_book
        }), 201

    except PyMongoError:
        return jsonify({
            "error": "unable to save the book"
        }), 503

if __name__ == "__main__":
    app.run(debug=True, port = 5001)
