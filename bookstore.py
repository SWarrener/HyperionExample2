import sqlite3

#========The beginning of the class==========
class Book:
    '''
    A class to represent a book.

    Attributes:
        id (int): The numeric id code of the book
        title (string): The title of the book
        author (string): The author of the book
        quantity (int): The quantity of stock of the book

    Methods:
        get_id(self):
            Returns the id of the book as a string
        
        __str__(self):
            Provides neat printable string for the book object
    '''

    def __init__(self, id_, title, author, quantity):
        '''
        Constructor for the Book object

            Parameters:
                id (int): The numeric id code of the book
                title (string): The title of the book
                author (string): The author of the book
                quantity (int): The quantity of stock of the book

        '''
        self.id = id_
        self.title = title
        self.author = author
        self.quantity = quantity

    def get_id(self):
        '''Returns the id of the book as a string'''
        return str(self.id)

    def __str__(self):
        '''Provides neat printable string for the book object'''
        return (f"{self.title}, by {self.author}."
                f" Quantity: {self.quantity}. Product id: {self.id}")


#==========Functions outside the class==============
def get_quantity(string):
    '''
    Gets and validates a value for quantity
    
    Parameters:
        String for displaying in input field
    
    Returns:
        Int representing quantity of book in stock
    '''
    while True:
        try:
            new_quantity = int(input(string))
            if new_quantity > 0: #  Negative quantity makes no sense
                return new_quantity
            print("Please enter a positive value")
        except ValueError:
            print("Please enter a numeric value")

def print_books():
    '''
    Gets all the books from the db and prints them
    
    Returns:
        List of book objects.
    '''
    cursor.execute('''SELECT * FROM book''')
    book_list = [Book(*data) for data in cursor]
    for book in book_list:
        print(book)
    return book_list

def delete_book():
    '''Allows the user to delete a book from the database'''
    book_list = print_books()
    if book_list is None:
        print("There are no books in the database, please add some")
        return
    cursor.execute('''SELECT id FROM book''')
    cursor.row_factory = lambda cursor, row: row[0]
    id_list = tuple(map(str, cursor.fetchall()))
    cursor.row_factory = None
    while True:
        if (choice := input("Enter the id of the book you wish to "
                            "delete, or 'c' to cancel ")).lower() in id_list:
            cursor.execute('''DELETE FROM book WHERE id=?''', (int(choice),))
            db.commit()
            for book in book_list:
                if book.get_id() == choice:
                    print(f"Deleting {book}")
                    break
            return
        if choice == 'c':
            return
        print("Please enter a valid book id, or 'c' to cancel.")

def update_book():
    '''Allows the user to update a book from the database'''
    book_list = print_books()
    if book_list is None:
        print("There are no books in the database, please add some")
        return
    cursor.execute('''SELECT id FROM book''')
    cursor.row_factory = lambda cursor, row: row[0]
    id_list = tuple(map(str, cursor.fetchall()))
    cursor.row_factory = None
    while True:
        if (choice := input("Enter the id of the book you wish to "
                            "edit, or 'c' to cancel ")).lower() in id_list:
            cursor.execute("SELECT * FROM book WHERE id=?", (int(choice),))
            book_data = list(cursor.fetchone())
            print(book_data)
            if (new_title := input("Enter the new title, or leave "
                              "blank to keep title ")).strip() != '':
                book_data[1] = new_title
            if (new_author := input("Enter the new author, or leave "
                              "blank to keep author ")).strip() != '':
                book_data[2] = new_author
            book_data[3] = get_quantity("Enter the new quantity of the book ")
            cursor.execute('''UPDATE book SET title = ?, author = ?,
                           quantity = ? WHERE id = ?''',
                           (*tuple(book_data[1:]), int(choice)))
            db.commit()
            return
        if choice == 'c':
            return
        print("Please enter a valid book id, or 'c' to cancel.")

def add_book():
    '''Allows the user to add a new book to the database'''
    cursor.execute('''SELECT MAX(id) FROM book''')
    new_id = cursor.fetchone()[0] + 1
    while True: #  This section ensures there are no repeated books
        new_title = input("Enter the title of the new book ").strip()
        new_author = input("Enter the author of the new book ").strip()
        cursor.execute('''SELECT * FROM book WHERE title = ? COLLATE NOCASE
                       AND author = ? COLLATE NOCASE''',
                       (new_title, new_author))
        if not cursor.fetchone():
            break
        print("There is already an entry with that author and title. "
              "Please enter a different combination")
    new_quantity = get_quantity("Enter the quantity of the book ")
    cursor.execute('''INSERT INTO book VALUES(?,?,?,?)''',
                   (new_id, new_title, new_author, new_quantity))
    db.commit()

def search_book():
    '''Searches for specific book'''
    search = input("Please enter the title of the "
                   "book you are searching for ").lower()
    cursor.execute("SELECT * FROM book WHERE title = ? COLLATE NOCASE",
                       (search,))
    result = cursor.fetchall()
    if result:
        for book in result:
            print(Book(*book))
    else:
        print("There are no books with that title")

def prepare_db():
    '''Creates the database table and appends starting data'''
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book (id INT PRIMARY KEY, title TEXT,
                                        author TEXT, quantity int)
        ''')
    book_data = [
        (3001, "A Tale of Two Cities", "Charles Dickens", 30),
        (3002, "Harry Potter and the Philosopher's Stone", "J.K Rowling", 40),
        (3003, "The Lion, the Witch and the Wardrobe", "C.S Lewis", 25),
        (3004, "The Lord of the Rings", "J.R.R Tolkien", 37),
        (3005, "Alice in Wonderland", "Lewis Carroll", 12)
    ]
    try:
        cursor.executemany('''INSERT INTO book VALUES(?,?,?,?)''', book_data)
    except sqlite3.IntegrityError:
        pass
    db.commit()

#==========Main Menu=============
# Creates the db and other initial sqlite set up
db = sqlite3.connect('ebookstore.db')
cursor = db.cursor()

prepare_db()

# Displays a menu to the user to allow them to pick which of the above
# functions they would like to perform
while True:

    menu = input("Select one of the following options:\n"
                 "a - Add a new book\n"
                 "u - Update a book\n"
                 "d - Delete a book\n"
                 "s - Search for a specific book\n"
                 "e - Exit\n"
                 ":").lower()

    if menu == 'a':
        add_book()

    elif menu == 'u':
        update_book()

    elif menu == 'd':
        delete_book()

    elif menu == 's':
        search_book()

    elif menu == 'e':
        print('Goodbye!!!')
        exit()

    else:
        print("Please enter a valid option")
