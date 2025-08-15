# Library Management System

A comprehensive library management system built with Python, featuring both command-line interface and REST API capabilities. This project demonstrates modern Python development practices including object-oriented programming, external API integration, and web API development with FastAPI.

## 🚀 Features

- **Command-Line Interface**: Interactive terminal-based book management
- **REST API**: Full-featured web API with OpenAPI/Swagger documentation
- **External API Integration**: Automatic book information retrieval from Open Library
- **Data Persistence**: JSON-based storage system
- **Comprehensive Testing**: Full test coverage with pytest
- **Error Handling**: Robust error handling for network and data issues

## 📋 Requirements

- Python 3.8 or higher
- pip package manager

## 🛠 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/shenmali/Python202_LibraryProject.git
   cd Python202_LibraryProject
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage

### Command-Line Interface

Run the interactive terminal application:

```bash
python main.py
```

**Available operations:**
- **Add Book**: Manual entry or automatic ISBN lookup
- **Remove Book**: Delete books by ISBN
- **List Books**: Display all books in the library
- **Search Book**: Find books by ISBN
- **Exit**: Close the application

### REST API

Start the FastAPI server:

```bash
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`

**Interactive documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/books` | List all books |
| POST | `/books` | Add book by ISBN |
| GET | `/books/{isbn}` | Get specific book |
| DELETE | `/books/{isbn}` | Delete book |

### API Examples

**List all books:**
```bash
curl -X GET "http://localhost:8000/books"
```

**Add a book by ISBN:**
```bash
curl -X POST "http://localhost:8000/books" \
     -H "Content-Type: application/json" \
     -d '{"isbn": "9780743273565"}'
```

**Get a specific book:**
```bash
curl -X GET "http://localhost:8000/books/9780743273565"
```

**Delete a book:**
```bash
curl -X DELETE "http://localhost:8000/books/9780743273565"
```

## 🧪 Testing

Run all tests:

```bash
pytest tests/ -v
```

Run tests with coverage:

```bash
pytest tests/ --cov=. --cov-report=html
```

**Test Structure:**
- `tests/test_models.py`: Core functionality tests
- `tests/test_api_integration.py`: External API integration tests
- `tests/test_api.py`: FastAPI endpoint tests

## 📁 Project Structure

```
library-management-system/
│
├── models.py              # Book and Library classes
├── main.py               # Command-line interface
├── api.py                # FastAPI web application
├── requirements.txt      # Project dependencies
├── .gitignore           # Git ignore rules
│
├── tests/               # Test suite
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_api_integration.py
│   └── test_api.py
│
└── library.json         # Data storage (auto-generated)
```

## 🔧 Core Components

### Book Class
Represents individual books with title, author, and ISBN properties.

### Library Class
Manages the book collection with the following capabilities:
- Add/remove books
- Search functionality
- JSON persistence
- External API integration

### CLI Application
Interactive command-line interface with menu-driven operations.

### FastAPI Application
RESTful web API with:
- Pydantic models for validation
- Comprehensive error handling
- CORS support
- Automatic OpenAPI documentation

## 🌐 External Integration

The system integrates with the [Open Library API](https://openlibrary.org/developers/api) to automatically fetch book information:

- **Endpoint**: `https://openlibrary.org/isbn/{isbn}.json`
- **Features**: Automatic title and author retrieval
- **Error Handling**: Network timeouts, invalid ISBNs, connection errors

## 🔍 Example Usage Scenarios

### Adding Books via CLI
1. Run `python main.py`
2. Select "1" for Add Book
3. Choose between manual entry or ISBN lookup
4. For ISBN lookup, enter: `9780743273565` (The Great Gatsby)

### Using the API
1. Start server: `uvicorn api:app --reload`
2. Visit `http://localhost:8000/docs`
3. Try the "POST /books" endpoint with ISBN `9780451524935` (1984)

## 🛡 Error Handling

The system includes comprehensive error handling for:
- Invalid ISBN formats
- Network connectivity issues
- API timeouts and failures
- Duplicate book entries
- File system errors
- Invalid JSON data

## 🧰 Technologies Used

- **Python 3.8+**: Core programming language
- **FastAPI**: Modern web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **httpx**: Async HTTP client for external API calls
- **pytest**: Testing framework
- **uvicorn**: ASGI server for FastAPI

## 📊 Features Overview

| Feature | CLI | API | Description |
|---------|-----|-----|-------------|
| Add Books | ✅ | ✅ | Manual entry and ISBN lookup |
| Remove Books | ✅ | ✅ | Delete by ISBN |
| List Books | ✅ | ✅ | Display all books |
| Search Books | ✅ | ✅ | Find by ISBN |
| Data Persistence | ✅ | ✅ | JSON file storage |
| External API | ✅ | ✅ | Open Library integration |
| Error Handling | ✅ | ✅ | Comprehensive error management |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📝 Development Notes

- The application uses JSON for data persistence
- Book data is automatically saved after each operation
- ISBN validation relies on Open Library API responses
- All external API calls include timeout handling
- Tests use mocking for external API calls

## 🔮 Future Enhancements

- Database integration (SQLite/PostgreSQL)
- User authentication and authorization
- Book categories and tags
- Advanced search functionality
- Book borrowing/lending system
- Web frontend interface
- Docker containerization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Built with Python and FastAPI for educational purposes.**