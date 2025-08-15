import json
import os
import httpx
from typing import List, Optional, Dict


class Book:
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn
    
    def __str__(self) -> str:
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn
        }


class Library:
    def __init__(self, filename: str = 'library.json'):
        self.filename = filename
        self.books: List[Book] = []
        self.load_books()
    
    def add_book(self, book: Book) -> None:
        if self.find_book(book.isbn) is not None:
            raise ValueError(f"Book with ISBN {book.isbn} already exists")
        self.books.append(book)
        self.save_books()
    
    def remove_book(self, isbn: str) -> bool:
        for i, book in enumerate(self.books):
            if book.isbn == isbn:
                self.books.pop(i)
                self.save_books()
                return True
        return False
    
    def list_books(self) -> List[Book]:
        return self.books.copy()
    
    def find_book(self, isbn: str) -> Optional[Book]:
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None
    
    def load_books(self) -> None:
        if not os.path.exists(self.filename):
            self.books = []
            return
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.books = [
                    Book(book_data['title'], book_data['author'], book_data['isbn'])
                    for book_data in data
                ]
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            self.books = []
    
    def save_books(self) -> None:
        try:
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump([book.to_dict() for book in self.books], file, indent=2, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"Failed to save books to {self.filename}: {e}")
    
    def add_book_by_isbn(self, isbn: str) -> Book:
        # Check if book already exists
        existing_book = self.find_book(isbn)
        if existing_book is not None:
            raise ValueError(f"Book with ISBN {isbn} already exists")
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"https://openlibrary.org/isbn/{isbn}.json")
                
                if response.status_code == 404:
                    raise ValueError(f"Book with ISBN {isbn} not found")
                
                response.raise_for_status()
                book_data = response.json()
                
                # Extract title
                title = book_data.get('title', 'Unknown Title')
                
                # Extract authors - they can be in different formats
                authors = []
                if 'authors' in book_data:
                    for author_ref in book_data['authors']:
                        if isinstance(author_ref, dict) and 'key' in author_ref:
                            # Fetch author details
                            author_response = client.get(f"https://openlibrary.org{author_ref['key']}.json")
                            if author_response.status_code == 200:
                                author_data = author_response.json()
                                authors.append(author_data.get('name', 'Unknown Author'))
                
                # If no authors found or extraction failed, use a default
                if not authors:
                    authors = ['Unknown Author']
                
                # Combine author names
                author = ', '.join(authors)
                
                # Create and add book
                book = Book(title, author, isbn)
                self.add_book(book)
                return book
        
        except httpx.TimeoutException:
            raise ConnectionError("Request timed out while fetching book information")
        except httpx.ConnectError:
            raise ConnectionError("Failed to connect to Open Library API")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Book with ISBN {isbn} not found")
            else:
                raise ConnectionError(f"HTTP error occurred: {e.response.status_code}")
        except json.JSONDecodeError:
            raise ValueError("Invalid response format from Open Library API")
        except ValueError:
            # Re-raise ValueError exceptions (like "Book not found")
            raise
        except Exception as e:
            raise ConnectionError(f"Unexpected error occurred: {e}")