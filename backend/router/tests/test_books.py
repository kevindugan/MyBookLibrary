
from uuid import uuid3, NAMESPACE_OID
from json import dumps

from ...models import BooksTB, CategoriesTB

def test_list_books_all(db_session, helpers):
    db_session.add_all([
        CategoriesTB(cat_id="CAT001000", cat_path="Category|Sub Category"),
        CategoriesTB(cat_id="CAT002000", cat_path="Category|Other Sub Category"),
    ])
    db_session.commit()
    id_list = [uuid3(NAMESPACE_OID, f"test {it}") for it in range(3)]
    db_session.add_all([
        BooksTB(title="Book 1", author="Someone", category="1", id=id_list[0]),
        BooksTB(title="Book 2", author="Someone", category="2", id=id_list[1]),
        BooksTB(title="Other Book", author="Someone Else", category="2", id=id_list[2]),
    ])
    db_session.commit()
    
    client = helpers.get_client(db_session)
    
    # List all endpoint
    response = client.get("/api/v1/books/list")
    assert response.status_code == 200
    assert response.json() == {
        "result": [
            {"unique_id": str(id_list[0]), "title": "Book 1", "author": "Someone", "category": "Category / Sub Category", "cover_art": None, "isbn": None},
            {"unique_id": str(id_list[1]), "title": "Book 2", "author": "Someone", "category": "Category / Other Sub Category", "cover_art": None, "isbn": None},
            {"unique_id": str(id_list[2]), "title": "Other Book", "author": "Someone Else", "category": "Category / Other Sub Category", "cover_art": None, "isbn": None},
        ]
    }
    
def test_list_books_limit(db_session, helpers):
    db_session.add_all([
        CategoriesTB(cat_id="CAT001000", cat_path="Category|Sub Category"),
        CategoriesTB(cat_id="CAT002000", cat_path="Category|Other Sub Category"),
    ])
    db_session.commit()
    id_list = [uuid3(NAMESPACE_OID, f"test {it}") for it in range(6)]
    db_session.add_all([
        BooksTB(title="Book 1", author="Someone", category="1", id=id_list[0]),
        BooksTB(title="Book 2", author="Someone", category="2", id=id_list[1]),
        BooksTB(title="Other Book", author="Someone Else", category="2", id=id_list[2]),
        BooksTB(title="Other Book 1", author="Someone Else", category="2", id=id_list[3]),
        BooksTB(title="Book 2", author="Someone", category="1", id=id_list[4]),
        BooksTB(title="Other Book", author="Someone Else", category="2", id=id_list[5]),
    ])
    db_session.commit()
    
    client = helpers.get_client(db_session)
    
    # List all endpoint
    response = client.get("/api/v1/books/list?limit=2")
    assert response.status_code == 200
    assert response.json() == {
        "result": [
            {"unique_id": str(id_list[0]), "title": "Book 1", "author": "Someone", "category": "Category / Sub Category", "cover_art": None, "isbn": None},
            {"unique_id": str(id_list[1]), "title": "Book 2", "author": "Someone", "category": "Category / Other Sub Category", "cover_art": None, "isbn": None},
        ]
    }
    
    # Test Offset
    # response = client.get("/api/v1/books/list?limit=2&page=2")
    # assert response.status_code == 200
    # assert response.json() == {
    #     "result": [
    #         {"unique_id": str(id_list[4]), "title": "Book 2", "author": "Someone", "category": "Category / Sub Category", "cover_art": None, "isbn": None},
    #         {"unique_id": str(id_list[5]), "title": "Other Book", "author": "Someone Else", "category": "Category / Other Sub Category", "cover_art": None, "isbn": None}
    #     ]
    # }

def test_list_books_with_cover(db_session, helpers):
    db_session.add_all([
        CategoriesTB(cat_id="CAT001000", cat_path="Category|Sub Category"),
        CategoriesTB(cat_id="CAT002000", cat_path="Category|Other Sub Category"),
    ])
    db_session.commit()
    id_list = [uuid3(NAMESPACE_OID, f"test {it}") for it in range(3)]
    db_session.add_all([
        BooksTB(title="Book 1", author="Someone", category="1", id=id_list[0]),
        BooksTB(title="Book 2", author="Someone", category="2", id=id_list[1], cover_art="data:image/jpg;base64,/9j/4AAQSkZJRgABAQ"),
        BooksTB(title="Other Book", author="Someone Else", category="2", id=id_list[2], cover_art="data:image/jpg;base64,/9j/4AAQSjZJqgABAQ"),
    ])
    db_session.commit()
    
    client = helpers.get_client(db_session)
    
    # List all, some have cover
    response = client.get("/api/v1/books/list")
    assert response.status_code == 200
    assert response.json() == {
        "result": [
            {"cover_art": None, "unique_id": str(id_list[0]), "title": "Book 1", "author": "Someone", "category": "Category / Sub Category", "isbn": None},
            {"cover_art": "data:image/jpg;base64,/9j/4AAQSkZJRgABAQ", "unique_id": str(id_list[1]), "title": "Book 2", "author": "Someone", "category": "Category / Other Sub Category", "isbn": None},
            {"cover_art": "data:image/jpg;base64,/9j/4AAQSjZJqgABAQ", "unique_id": str(id_list[2]), "title": "Other Book", "author": "Someone Else", "category": "Category / Other Sub Category", "isbn": None},
        ]
    }
    
def test_list_books_with_isbn(db_session, helpers):
    db_session.add_all([
        CategoriesTB(cat_id="CAT001000", cat_path="Category|Sub Category"),
        CategoriesTB(cat_id="CAT002000", cat_path="Category|Other Sub Category"),
    ])
    db_session.commit()
    id_list = [uuid3(NAMESPACE_OID, f"test {it}") for it in range(3)]
    db_session.add_all([
        BooksTB(title="Book 1", author="Someone", id=id_list[0]),
        BooksTB(title="Book 2", author="Someone", category="2", id=id_list[1], isbn="9780534349417"),
        BooksTB(title="Other Book", author="Someone Else", category="2", id=id_list[2], isbn="9780534349517"),
    ])
    db_session.commit()
    
    client = helpers.get_client(db_session)
    
    # List all, some have cover
    response = client.get("/api/v1/books/list")
    assert response.status_code == 200
    assert response.json() == {
        "result": [
            {"isbn": "9780534349417", "unique_id": str(id_list[1]), "title": "Book 2", "author": "Someone", "category": "Category / Other Sub Category", "cover_art": None},
            {"isbn": "9780534349517", "unique_id": str(id_list[2]), "title": "Other Book", "author": "Someone Else", "category": "Category / Other Sub Category", "cover_art": None},
            {"isbn": None, "unique_id": str(id_list[0]), "title": "Book 1", "author": "Someone", "category": None, "cover_art": None},
        ]
    }
    
    
def test_list_books_by_category(db_session, helpers):
    db_session.add_all([
        CategoriesTB(cat_id="CAT001000", cat_path="Category|Sub Category"),
        CategoriesTB(cat_id="CAT002000", cat_path="Category|Other Sub Category"),
    ])
    db_session.commit()
    id_list = [uuid3(NAMESPACE_OID, f"test {it}") for it in range(5)]
    db_session.add_all([
        BooksTB(title="Other Book", author="New Someone", category="2", id=id_list[0]),
        BooksTB(title="Book 1", author="Someone", category="2", id=id_list[1]),
        BooksTB(title="Book 2", author="Someone", category="1", id=id_list[2]),
        BooksTB(title="A Book 2", author="Someone", category="1", id=id_list[3]),
        BooksTB(title="No Cat", author="Unknown", id=id_list[4])
    ])
    db_session.commit()
    
    client = helpers.get_client(db_session)
    
    # List all books, ordered by category,author,title
    response = client.get("/api/v1/books/list-by-category")
    assert response.status_code == 200
    assert response.json() == {
        "result": [
            {"unique_id": str(id_list[3]), "title": "A Book 2", "author": "Someone", "category": "Category / Sub Category", "cover_art": None, "isbn": None},
            {"unique_id": str(id_list[2]), "title": "Book 2", "author": "Someone", "category": "Category / Sub Category", "cover_art": None, "isbn": None},
            {"unique_id": str(id_list[0]), "title": "Other Book", "author": "New Someone", "category": "Category / Other Sub Category", "cover_art": None, "isbn": None},
            {"unique_id": str(id_list[1]), "title": "Book 1", "author": "Someone", "category": "Category / Other Sub Category", "cover_art": None, "isbn": None},
        ]
    }

def test_add_new_book(db_session, helpers):
    db_session.add_all([
        CategoriesTB(cat_id="CAT001000", cat_path="Category|Sub Category"),
        CategoriesTB(cat_id="CAT002000", cat_path="Category|Other Sub Category"),
    ])
    db_session.commit()
    
    client = helpers.get_client(db_session)
    
    # Verify that books are empty
    response = client.get("/api/v1/books/list")
    assert response.status_code == 200
    assert response.json() == {"result": []}
    
    # Add new book
    newBook = {
        "title": "New Book Title",
        "author": "Someone New",
        "category": "CAT002000",
        "isbn": "9780534349417"
    }
    post_response = client.post("/api/v1/books/add", json=newBook)
    assert post_response.status_code == 200, post_response.text
    assert post_response.json()["title"] == newBook["title"]
    assert post_response.json()["author"] == newBook["author"]
    assert post_response.json()["category"] == newBook["category"]
    assert "id" in post_response.json()
    
    # Check that book was added to database
    get_response = client.get("/api/v1/books/list")
    assert get_response.status_code == 200
    assert len(get_response.json()["result"]) == 1
    book_response = get_response.json()["result"][0]
    assert book_response["title"] == newBook["title"]
    assert book_response["author"] == newBook["author"]
    assert book_response["category"] == "Category / Other Sub Category"
    assert "unique_id" in book_response
    assert book_response["unique_id"] == post_response.json()["id"]
