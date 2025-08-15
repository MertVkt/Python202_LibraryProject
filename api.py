from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from models import Library, Book


# Pydantic models for API
class BookResponse(BaseModel):
    title: str
    author: str
    isbn: str


class ISBNRequest(BaseModel):
    isbn: str


class ErrorResponse(BaseModel):
    error: str
    message: str


# Initialize FastAPI app
app = FastAPI(
    title="Library Management System",
    description="A modern library management system with book search and management features",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Library
library = Library()


@app.get("/books", response_model=List[BookResponse])
async def get_all_books():
    """Get all books in the library"""
    try:
        books = library.list_books()
        return [BookResponse(title=book.title, author=book.author, isbn=book.isbn) 
                for book in books]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/books", response_model=BookResponse)
async def add_book_by_isbn(isbn_request: ISBNRequest):
    """Add a book by ISBN using Open Library API"""
    try:
        book = library.add_book_by_isbn(isbn_request.isbn)
        return BookResponse(title=book.title, author=book.author, isbn=book.isbn)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/books/{isbn}", response_model=BookResponse)
async def get_book_by_isbn(isbn: str):
    """Get a specific book by ISBN"""
    try:
        book = library.find_book(isbn)
        if book is None:
            raise HTTPException(status_code=404, detail=f"Book with ISBN {isbn} not found")
        
        return BookResponse(title=book.title, author=book.author, isbn=book.isbn)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/books/{isbn}")
async def delete_book(isbn: str):
    """Delete a book by ISBN"""
    try:
        success = library.remove_book(isbn)
        if not success:
            raise HTTPException(status_code=404, detail=f"Book with ISBN {isbn} not found")
        
        return {"message": f"Book with ISBN {isbn} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return HTTPException(status_code=400, detail=str(exc))


@app.exception_handler(ConnectionError)
async def connection_error_handler(request, exc):
    return HTTPException(status_code=503, detail=f"Service unavailable: {str(exc)}")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if library can be accessed
        book_count = len(library.list_books())
        return {
            "status": "healthy",
            "message": "Library Management System is running",
            "book_count": book_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Library Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }