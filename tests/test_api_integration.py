import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
import json
import httpx
from models import Library, Book


class TestAPIIntegration:
    def setup_method(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.library = Library(self.temp_file.name)
    
    def teardown_method(self):
        # Clean up the temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    @patch('httpx.Client')
    def test_fetch_book_from_api(self, mock_client_class):
        # Mock the HTTP client and responses
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Mock book data response
        mock_book_response = Mock()
        mock_book_response.status_code = 200
        mock_book_response.json.return_value = {
            'title': 'The Great Gatsby',
            'authors': [{'key': '/authors/OL123A'}]
        }
        
        # Mock author data response
        mock_author_response = Mock()
        mock_author_response.status_code = 200
        mock_author_response.json.return_value = {
            'name': 'F. Scott Fitzgerald'
        }
        
        # Configure mock to return different responses for different URLs
        def mock_get(url):
            if 'isbn' in url:
                return mock_book_response
            elif 'authors' in url:
                return mock_author_response
        
        mock_client.get.side_effect = mock_get
        mock_book_response.raise_for_status = Mock()
        
        # Test the method
        isbn = '9780743273565'
        book = self.library.add_book_by_isbn(isbn)
        
        # Verify the results
        assert book.title == 'The Great Gatsby'
        assert book.author == 'F. Scott Fitzgerald'
        assert book.isbn == isbn
        assert len(self.library.books) == 1
        
        # Verify API calls were made
        assert mock_client.get.call_count == 2
        mock_client.get.assert_any_call(f"https://openlibrary.org/isbn/{isbn}.json")
        mock_client.get.assert_any_call("https://openlibrary.org/authors/OL123A.json")
    
    @patch('httpx.Client')
    def test_invalid_isbn(self, mock_client_class):
        # Mock the HTTP client
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_client.get.return_value = mock_response
        
        # Test invalid ISBN
        with pytest.raises(ValueError, match="Book with ISBN 9999999999999 not found"):
            self.library.add_book_by_isbn('9999999999999')
    
    @patch('httpx.Client')
    def test_network_error(self, mock_client_class):
        # Mock the HTTP client to raise a connection error
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")
        
        # Test network error
        with pytest.raises(ConnectionError, match="Failed to connect to Open Library API"):
            self.library.add_book_by_isbn('9780743273565')
    
    @patch('httpx.Client')
    def test_timeout_error(self, mock_client_class):
        # Mock the HTTP client to raise a timeout error
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        mock_client.get.side_effect = httpx.TimeoutException("Request timed out")
        
        # Test timeout error
        with pytest.raises(ConnectionError, match="Request timed out while fetching book information"):
            self.library.add_book_by_isbn('9780743273565')
    
    @patch('httpx.Client')
    def test_http_error(self, mock_client_class):
        # Mock the HTTP client
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_client.get.return_value = mock_response
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=mock_response
        )
        
        # Test HTTP error
        with pytest.raises(ConnectionError, match="HTTP error occurred: 500"):
            self.library.add_book_by_isbn('9780743273565')
    
    @patch('httpx.Client')
    def test_invalid_json_response(self, mock_client_class):
        # Mock the HTTP client
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status = Mock()
        mock_client.get.return_value = mock_response
        
        # Test invalid JSON response
        with pytest.raises(ValueError, match="Invalid response format from Open Library API"):
            self.library.add_book_by_isbn('9780743273565')
    
    @patch('httpx.Client')
    def test_book_without_authors(self, mock_client_class):
        # Mock the HTTP client
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Mock book data response without authors
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'title': 'Unknown Author Book'
        }
        mock_response.raise_for_status = Mock()
        mock_client.get.return_value = mock_response
        
        # Test book without authors
        isbn = '9780000000000'
        book = self.library.add_book_by_isbn(isbn)
        
        assert book.title == 'Unknown Author Book'
        assert book.author == 'Unknown Author'
        assert book.isbn == isbn
    
    @patch('httpx.Client')
    def test_author_fetch_failure(self, mock_client_class):
        # Mock the HTTP client
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Mock book data response
        mock_book_response = Mock()
        mock_book_response.status_code = 200
        mock_book_response.json.return_value = {
            'title': 'Test Book',
            'authors': [{'key': '/authors/OL123A'}]
        }
        mock_book_response.raise_for_status = Mock()
        
        # Mock failed author response
        mock_author_response = Mock()
        mock_author_response.status_code = 404
        
        # Configure mock to return different responses
        def mock_get(url):
            if 'isbn' in url:
                return mock_book_response
            elif 'authors' in url:
                return mock_author_response
        
        mock_client.get.side_effect = mock_get
        
        # Test author fetch failure
        isbn = '9780000000001'
        book = self.library.add_book_by_isbn(isbn)
        
        assert book.title == 'Test Book'
        assert book.author == 'Unknown Author'
        assert book.isbn == isbn
    
    @patch('httpx.Client')
    def test_duplicate_isbn_api(self, mock_client_class):
        # First add a book manually
        existing_book = Book("Existing Book", "Existing Author", "9780743273565")
        self.library.add_book(existing_book)
        
        # Try to add the same ISBN via API
        with pytest.raises(ValueError, match="Book with ISBN 9780743273565 already exists"):
            self.library.add_book_by_isbn("9780743273565")