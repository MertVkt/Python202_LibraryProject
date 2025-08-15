import pytest
import json
import os
import tempfile
from models import Book, Library


class TestBook:
    def test_book_creation(self):
        book = Book("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565")
        assert book.title == "The Great Gatsby"
        assert book.author == "F. Scott Fitzgerald"
        assert book.isbn == "9780743273565"
    
    def test_book_str(self):
        book = Book("1984", "George Orwell", "9780451524935")
        expected = "1984 by George Orwell (ISBN: 9780451524935)"
        assert str(book) == expected
    
    def test_book_to_dict(self):
        book = Book("To Kill a Mockingbird", "Harper Lee", "9780061120084")
        expected = {
            'title': 'To Kill a Mockingbird',
            'author': 'Harper Lee',
            'isbn': '9780061120084'
        }
        assert book.to_dict() == expected


class TestLibrary:
    def setup_method(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.library = Library(self.temp_file.name)
    
    def teardown_method(self):
        # Clean up the temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_library_initialization_new_file(self):
        # Test with non-existent file
        temp_file = tempfile.NamedTemporaryFile(delete=True)
        temp_filename = temp_file.name
        temp_file.close()  # This deletes the file
        
        library = Library(temp_filename)
        assert library.filename == temp_filename
        assert len(library.books) == 0
        
        # Clean up
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)
    
    def test_library_add_book(self):
        book = Book("The Catcher in the Rye", "J.D. Salinger", "9780316769174")
        self.library.add_book(book)
        
        assert len(self.library.books) == 1
        assert self.library.books[0].title == "The Catcher in the Rye"
        assert self.library.books[0].author == "J.D. Salinger"
        assert self.library.books[0].isbn == "9780316769174"
    
    def test_library_add_duplicate_book(self):
        book1 = Book("Dune", "Frank Herbert", "9780441172719")
        book2 = Book("Dune Messiah", "Frank Herbert", "9780441172719")  # Same ISBN
        
        self.library.add_book(book1)
        with pytest.raises(ValueError, match="Book with ISBN 9780441172719 already exists"):
            self.library.add_book(book2)
    
    def test_library_remove_book(self):
        book = Book("Brave New World", "Aldous Huxley", "9780060850524")
        self.library.add_book(book)
        
        assert len(self.library.books) == 1
        result = self.library.remove_book("9780060850524")
        assert result is True
        assert len(self.library.books) == 0
    
    def test_library_remove_nonexistent_book(self):
        result = self.library.remove_book("9999999999999")
        assert result is False
    
    def test_library_list_books(self):
        book1 = Book("Pride and Prejudice", "Jane Austen", "9780141439518")
        book2 = Book("Jane Eyre", "Charlotte Brontë", "9780141441146")
        
        self.library.add_book(book1)
        self.library.add_book(book2)
        
        books = self.library.list_books()
        assert len(books) == 2
        
        # Ensure it returns a copy
        books.clear()
        assert len(self.library.books) == 2
    
    def test_library_find_book(self):
        book = Book("The Lord of the Rings", "J.R.R. Tolkien", "9780544003415")
        self.library.add_book(book)
        
        found_book = self.library.find_book("9780544003415")
        assert found_book is not None
        assert found_book.title == "The Lord of the Rings"
        
        not_found = self.library.find_book("9999999999999")
        assert not_found is None
    
    def test_library_save_load(self):
        book1 = Book("Moby Dick", "Herman Melville", "9780142437247")
        book2 = Book("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565")
        
        self.library.add_book(book1)
        self.library.add_book(book2)
        
        # Create a new library instance with the same file
        new_library = Library(self.temp_file.name)
        
        assert len(new_library.books) == 2
        assert new_library.books[0].title == "Moby Dick"
        assert new_library.books[1].title == "The Great Gatsby"
    
    def test_library_load_corrupted_file(self):
        # Write invalid JSON to the file
        with open(self.temp_file.name, 'w') as f:
            f.write("invalid json content")
        
        library = Library(self.temp_file.name)
        assert len(library.books) == 0  # Should handle corrupted file gracefully
    
    def test_library_load_missing_fields(self):
        # Write JSON with missing fields
        invalid_data = [{"title": "Test", "author": "Test"}]  # Missing ISBN
        with open(self.temp_file.name, 'w') as f:
            json.dump(invalid_data, f)
        
        library = Library(self.temp_file.name)
        assert len(library.books) == 0  # Should handle missing fields gracefully
    
    def test_library_save_error_handling(self):
        # Test save error by using an invalid path
        invalid_library = Library("/invalid/path/that/doesnt/exist.json")
        book = Book("Test", "Test", "123")
        
        # This should raise an IOError
        invalid_library.books.append(book)
        with pytest.raises(IOError):
            invalid_library.save_books()