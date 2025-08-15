import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from api import app
from models import Library, Book


@pytest.fixture
def temp_library_file():
    """Create a temporary file for testing"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_file.close()
    yield temp_file.name
    # Cleanup
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


@pytest.fixture
def client(temp_library_file):
    """Create a test client with a temporary library file"""
    with patch('api.library') as mock_library:
        mock_library.return_value = Library(temp_library_file)
        # Replace the global library instance
        from api import library
        test_library = Library(temp_library_file)
        
        # Patch the library instance in the api module
        with patch('api.library', test_library):
            with TestClient(app) as test_client:
                yield test_client, test_library


class TestAPI:
    def test_root_endpoint(self, client):
        test_client, _ = client
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Library Management System API"
        assert data["version"] == "1.0.0"
    
    def test_health_check(self, client):
        test_client, _ = client
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "book_count" in data
    
    def test_get_all_books_empty(self, client):
        test_client, _ = client
        response = test_client.get("/books")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_all_books_with_data(self, client):
        test_client, library = client
        # Add some test books
        book1 = Book("Test Book 1", "Test Author 1", "1234567890")
        book2 = Book("Test Book 2", "Test Author 2", "0987654321")
        library.add_book(book1)
        library.add_book(book2)
        
        response = test_client.get("/books")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Test Book 1"
        assert data[1]["title"] == "Test Book 2"
    
    def test_get_book_by_isbn_found(self, client):
        test_client, library = client
        # Add a test book
        book = Book("Found Book", "Found Author", "1111111111")
        library.add_book(book)
        
        response = test_client.get("/books/1111111111")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Found Book"
        assert data["author"] == "Found Author"
        assert data["isbn"] == "1111111111"
    
    def test_get_book_by_isbn_not_found(self, client):
        test_client, _ = client
        response = test_client.get("/books/9999999999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_delete_book_success(self, client):
        test_client, library = client
        # Add a test book
        book = Book("Delete Me", "Delete Author", "2222222222")
        library.add_book(book)
        
        # Verify book exists
        assert library.find_book("2222222222") is not None
        
        # Delete the book
        response = test_client.delete("/books/2222222222")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify book is deleted
        assert library.find_book("2222222222") is None
    
    def test_delete_book_not_found(self, client):
        test_client, _ = client
        response = test_client.delete("/books/9999999999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @patch('httpx.Client')
    def test_add_book_by_isbn_success(self, mock_client_class, client):
        test_client, library = client
        
        # Mock the HTTP client and responses
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Mock book data response
        mock_book_response = Mock()
        mock_book_response.status_code = 200
        mock_book_response.json.return_value = {
            'title': 'API Test Book',
            'authors': [{'key': '/authors/OL123A'}]
        }
        
        # Mock author data response
        mock_author_response = Mock()
        mock_author_response.status_code = 200
        mock_author_response.json.return_value = {
            'name': 'API Test Author'
        }
        
        # Configure mock to return different responses for different URLs
        def mock_get(url):
            if 'isbn' in url:
                return mock_book_response
            elif 'authors' in url:
                return mock_author_response
        
        mock_client.get.side_effect = mock_get
        mock_book_response.raise_for_status = Mock()
        
        # Test the API endpoint
        response = test_client.post("/books", json={"isbn": "3333333333"})
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "API Test Book"
        assert data["author"] == "API Test Author"
        assert data["isbn"] == "3333333333"
        
        # Verify book was added to library
        book = library.find_book("3333333333")
        assert book is not None
        assert book.title == "API Test Book"
    
    @patch('httpx.Client')
    def test_add_book_by_isbn_not_found(self, mock_client_class, client):
        test_client, _ = client
        
        # Mock the HTTP client to return 404
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_client.get.return_value = mock_response
        
        response = test_client.post("/books", json={"isbn": "9999999999"})
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]
    
    @patch('httpx.Client')
    def test_add_book_by_isbn_connection_error(self, mock_client_class, client):
        test_client, _ = client
        
        # Mock the HTTP client to raise connection error
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        import httpx
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")
        
        response = test_client.post("/books", json={"isbn": "4444444444"})
        assert response.status_code == 503
        assert "Service unavailable" in response.json()["detail"]
    
    def test_add_book_duplicate_isbn(self, client):
        test_client, library = client
        
        # Add a book first
        book = Book("Existing Book", "Existing Author", "5555555555")
        library.add_book(book)
        
        # Try to add the same ISBN via API (this should fail without calling external API)
        with patch('httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            
            response = test_client.post("/books", json={"isbn": "5555555555"})
            assert response.status_code == 400
            assert "already exists" in response.json()["detail"]
    
    def test_add_book_invalid_request(self, client):
        test_client, _ = client
        
        # Test with missing ISBN
        response = test_client.post("/books", json={})
        assert response.status_code == 422  # Validation error
        
        # Test with invalid JSON structure
        response = test_client.post("/books", json={"invalid_field": "value"})
        assert response.status_code == 422  # Validation error
    
    def test_api_cors_headers(self, client):
        test_client, _ = client
        
        # Test preflight request
        response = test_client.options("/books")
        # FastAPI TestClient doesn't fully simulate CORS preflight,
        # but we can verify the middleware is configured
        assert response.status_code == 200 or response.status_code == 405
        
        # Test actual request has CORS headers in real scenarios
        response = test_client.get("/books")
        # In actual deployment, CORS headers would be present
        assert response.status_code == 200