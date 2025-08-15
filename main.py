from models import Book, Library


def display_menu():
    print("\n" + "="*50)
    print("        LIBRARY MANAGEMENT SYSTEM")
    print("="*50)
    print("1. Add Book")
    print("2. Remove Book")
    print("3. List All Books")
    print("4. Search Book")
    print("5. Exit")
    print("="*50)


def add_book(library: Library):
    print("\n--- Add New Book ---")
    print("Choose an option:")
    print("1. Manual entry")
    print("2. ISBN lookup (automatic)")
    
    try:
        choice = input("Enter your choice (1-2): ").strip()
        
        if choice == '1':
            # Manual entry
            title = input("Enter book title: ").strip()
            if not title:
                print("Error: Title cannot be empty")
                return
            
            author = input("Enter book author: ").strip()
            if not author:
                print("Error: Author cannot be empty")
                return
            
            isbn = input("Enter book ISBN: ").strip()
            if not isbn:
                print("Error: ISBN cannot be empty")
                return
            
            book = Book(title, author, isbn)
            library.add_book(book)
            print(f"Success: Book '{title}' added successfully!")
        
        elif choice == '2':
            # ISBN lookup
            isbn = input("Enter book ISBN: ").strip()
            if not isbn:
                print("Error: ISBN cannot be empty")
                return
            
            print("Looking up book information...")
            book = library.add_book_by_isbn(isbn)
            print(f"Success: Book '{book.title}' by {book.author} added successfully!")
        
        else:
            print("Invalid choice! Please enter 1 or 2.")
    
    except ValueError as e:
        print(f"Error: {e}")
    except ConnectionError as e:
        print(f"Network Error: {e}")
        print("Please check your internet connection or try again later.")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")


def remove_book(library: Library):
    print("\n--- Remove Book ---")
    try:
        isbn = input("Enter ISBN of book to remove: ").strip()
        if not isbn:
            print("Error: ISBN cannot be empty")
            return
        
        if library.remove_book(isbn):
            print(f"Success: Book with ISBN {isbn} removed successfully!")
        else:
            print(f"Error: No book found with ISBN {isbn}")
    
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")


def list_books(library: Library):
    print("\n--- All Books ---")
    try:
        books = library.list_books()
        if not books:
            print("No books in the library.")
            return
        
        print(f"Total books: {len(books)}")
        print("-" * 60)
        for i, book in enumerate(books, 1):
            print(f"{i}. {book}")
    
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")


def search_book(library: Library):
    print("\n--- Search Book ---")
    try:
        isbn = input("Enter ISBN to search: ").strip()
        if not isbn:
            print("Error: ISBN cannot be empty")
            return
        
        book = library.find_book(isbn)
        if book:
            print(f"Found: {book}")
        else:
            print(f"No book found with ISBN {isbn}")
    
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")


def main():
    print("Initializing Library Management System...")
    try:
        library = Library()
        print("Library loaded successfully!")
    except Exception as e:
        print(f"Error initializing library: {e}")
        return
    
    while True:
        try:
            display_menu()
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                add_book(library)
            elif choice == '2':
                remove_book(library)
            elif choice == '3':
                list_books(library)
            elif choice == '4':
                search_book(library)
            elif choice == '5':
                print("Thank you for using Library Management System!")
                break
            else:
                print("Invalid choice! Please enter a number between 1-5.")
        
        except KeyboardInterrupt:
            print("\n\nExiting Library Management System...")
            break
        except EOFError:
            print("\n\nExiting Library Management System...")
            break
        except Exception as e:
            print(f"Error: An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()