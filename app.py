from flask import Flask, jsonify, request
from pymongo.errors import PyMongoError

from bson import ObjectId
from bson.errors import InvalidId

from database import books_collection, reviews_collection
from validation import validate_book, validate_review


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



@app.route("/api/books/<book_id>/reviews", methods=["POST"])
def add_review(book_id):
    try:
        object_id = ObjectId(book_id)
    except (InvalidId, TypeError):
        return jsonify({
            "error": "Invalid book ID"
        }), 400

    if not request.is_json:
        return jsonify({
            "error":"Content-Type must be in JSON"
        }), 415

    data = request.get_json(silent=True)

    cleaned_review, error = validate_review(data)

    if error:
        return jsonify({
            "error": error
        }), 400


    try:
        book = books_collection.find_one({
            "_id": object_id
        })

        if book is None:
            return jsonify({
                "error": "Book not found"
            }), 404

        review = {
            "book_id": object_id,
            **cleaned_review
        }

        result = reviews_collection.insert_one(review)

        new_review = {
            "id": str(result.inserted_id),
            "book_id": book_id,
            "reviewer": cleaned_review["reviewer"],
            "rating": cleaned_review["rating"],
            "comment": cleaned_review["comment"]
        }

        return jsonify({
            "message": "Review submitted",
            "review": new_review
        }), 201

    except PyMongoError:
        return jsonify({
            "error": "unable to save review"
        }), 503




@app.route("/api/books/<book_id>/reviews", methods=["GET"])
def get_reviews(book_id):

    try:
        object_id = ObjectId(book_id)
    except (InvalidId, TypeError):
        return jsonify({
            "error": "Invalid book ID."
        }), 400

    try:
        book = books_collection.find_one({
            "_id": object_id
        })

        if book is None:
            return jsonify({
                "error": "Book not found."
            }), 404

        reviews = []

        for review in reviews_collection.find({
            "book_id": object_id
        }):
            reviews.append({
                "id": str(review["_id"]),
                "book_id": str(review["book_id"]),
                "reviewer": review["reviewer"],
                "rating": review["rating"],
                "comment": review["comment"]
            })

        review_count = len(reviews)

        if review_count > 0:
            total_rating = sum(
                review["rating"] for review in reviews
            )

            average_rating = round(
                total_rating / review_count, 2
            )
        else:
            average_rating = None

        return jsonify({
            "book_id": book_id,
            "book_title": book["title"],
            "reviews": reviews,
            "review_count": review_count,
            "average_rating": average_rating
        }), 200

    except PyMongoError:
        return jsonify({
            "error": "Unable to retrieve reviews."
        }), 503


if __name__ == "__main__":
    app.run(debug=True, port = 5001)
