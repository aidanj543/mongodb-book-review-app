from database import books_collection

book = {
    "title": "1984",
    "author": "George Orwell",
    "genre": "Dystopian",
}

result = books_collection.insert_one(book)

print("Book inserted successfully with ID:", result.inserted_id)