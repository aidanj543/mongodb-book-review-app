
const bookForm = document.getElementById("book-form");
const bookMessage = document.getElementById("book-message");
const booksContainer = document.getElementById("books-container");
const booksStatus = document.getElementById("books-status");
const refreshButton = document.getElementById("refresh-btn");



function makeElement(tag, text, className = "") {
    const element = document.createElement(tag);
    element.textContent = text;

    if (className) {
        element.className = className;
    }

    return element;
}



function showMessage(element, text, isError = false) {
    element.textContent = text;
    element.className = isError
        ? "message error"
        : "message success";
}



async function apiRequest(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.error || `Request failed: ${response.status}`
        );
    }

    return data;
}



async function loadBooks() {
    booksContainer.replaceChildren();
    booksStatus.textContent = "Loading books...";

    try {
        const books = await apiRequest("/api/books");

        if (books.length === 0) {
            booksStatus.textContent =
                "No books yet. Add your first book!";
            return;
        }

        const results = await Promise.allSettled(
            books.map(async (book) => {
                const details = await apiRequest(
                    `/api/books/${book.id}/reviews`
                );

                return { book, details };
            })
        );

        booksStatus.textContent = `${books.length} book(s) found.`;

        results.forEach((result, index) => {
            if (result.status === "fulfilled") {
                const { book, details } = result.value;
                renderBook(book, details);
            } else {
                const book = books[index];

                renderBook(book, {
                    reviews: [],
                    review_count: 0,
                    average_rating: null
                });

                console.error(
                    "Could not load ratings:",
                    result.reason
                );
            }
        });

    } catch (error) {
        showMessage(booksStatus, error.message, true);
    }
}



function renderBook(book, details) {
    const card = document.createElement("article");
    card.className = "book-card";

    const icon = makeElement("div", "📖", "book-icon");

    const title = makeElement("h3", book.title);

    const author = makeElement(
        "p",
        `By ${book.author}`,
        "book-author"
    );

    const genre = makeElement(
        "p",
        book.genre,
        "book-genre"
    );

    const ratingText =
        details.average_rating === null
            ? "Not rated yet"
            : `⭐ ${details.average_rating.toFixed(2)} / 5`;

    const rating = makeElement(
        "p",
        `${ratingText} (${details.review_count} reviews)`,
        "rating"
    );

    const reviewButton = makeElement(
        "button",
        "View Reviews",
        "secondary-btn"
    );

    reviewButton.type = "button";

    const reviewPanel = document.createElement("div");
    reviewPanel.className = "review-panel";
    reviewPanel.hidden = true;


    reviewButton.addEventListener("click", () => {
        reviewPanel.hidden = !reviewPanel.hidden;
        reviewButton.textContent = reviewPanel.hidden
            ? "View Reviews"
            : "Hide Reviews";
    });

    const reviewHeading = makeElement(
        "h4",
        "Reader Reviews"
    );

    reviewPanel.appendChild(reviewHeading);

    if (details.reviews.length === 0) {
        reviewPanel.appendChild(
            makeElement("p", "No reviews yet.")
        );
    }

    details.reviews.forEach((review) => {
        const reviewItem = document.createElement("div");
        reviewItem.className = "review-item";

        reviewItem.appendChild(
            makeElement(
                "strong",
                `${review.reviewer} — ${review.rating}/5 stars`
            )
        );

        reviewItem.appendChild(
            makeElement("p", review.comment)
        );

        reviewPanel.appendChild(reviewItem);
    });


    const form = createReviewForm(book.id);
    reviewPanel.appendChild(form);

    card.append(
        icon,
        title,
        author,
        genre,
        rating,
        reviewButton,
        reviewPanel
    );

    booksContainer.appendChild(card);
}



function createReviewForm(bookId) {
    const form = document.createElement("form");
    form.className = "review-form";

    const heading = makeElement("h4", "Write a Review");

    const name = document.createElement("input");
    name.placeholder = "Your name";
    name.setAttribute("aria-label", "Your name");
    name.required = true;
    name.maxLength = 100;

    const rating = document.createElement("select");
    rating.setAttribute("aria-label", "Rating");

    for (let i = 1; i <= 5; i++) {
        const option = document.createElement("option");
        option.value = String(i);
        option.textContent = `${i} Star${i > 1 ? "s" : ""}`;
        rating.appendChild(option);
    }

    rating.value = "5";

    const comment = document.createElement("textarea");
    comment.placeholder = "Your review...";
    comment.setAttribute("aria-label", "Review comment");
    comment.required = true;
    comment.maxLength = 1000;
    comment.rows = 3;

    const submitButton = makeElement(
        "button",
        "Submit Review",
        "primary-btn"
    );

    submitButton.type = "submit";

    const message = makeElement("p", "", "message");
    message.setAttribute("role", "status");
    message.setAttribute("aria-live", "polite");

    form.append(
        heading,
        name,
        rating,
        comment,
        submitButton,
        message
    );


    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const review = {
            reviewer: name.value.trim(),
            rating: Number(rating.value),
            comment: comment.value.trim()
        };

        submitButton.disabled = true;

        try {
            await apiRequest(
                `/api/books/${bookId}/reviews`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(review)
                }
            );

            showMessage(message, "Review submitted!");
            form.reset();


            await loadBooks();

        } catch (error) {
            showMessage(message, error.message, true);

        } finally {
            submitButton.disabled = false;
        }
    });

    return form;
}



bookForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const book = {
        title: document.getElementById("book-title")
            .value.trim(),

        author: document.getElementById("book-author")
            .value.trim(),

        genre: document.getElementById("book-genre")
            .value.trim()
    };

    const submitButton = bookForm.querySelector(
        'button[type="submit"]'
    );

    submitButton.disabled = true;

    try {
        await apiRequest("/api/books", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(book)
        });

        showMessage(bookMessage, "Book added successfully!");

        bookForm.reset();
        await loadBooks();

    } catch (error) {
        showMessage(bookMessage, error.message, true);

    } finally {
        submitButton.disabled = false;
    }
});



refreshButton.addEventListener("click", loadBooks);



loadBooks();
