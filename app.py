from flask import Flask, jsonify
from database import books_collection

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to the Book Review App!"


@app.route("/api/books", methods = ["GET"])
def get_books():

    books = []

    for book in books_collection.find():
        books.append({
            "id": str(book["_id"]),
            "title": book["title"],
            "author": book["author"],
            "genre": book["genre"]
        })

    return jsonify(books)

if __name__ == "__main__":
    app.run(debug=True)
