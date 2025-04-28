# The Task
# First Fetch all ISBNs that exist
# Second Use Pandas to manipulate the dataset and get the information you need
# Third log the answers and make sure you see everything

# install the dependencies: Requests,Pandas

# 1. How many different books are in the list?
# 2. What is the book with the most number of different ISBNs?
# 3. How many books don’t have a goodreads id?
# 4. How many books have more than one author?
# 5. What is the number of books published per publisher?
# 6. What is the median number of pages for books in this list?
# 7. What is the month with the most number of published books?
# 8. What is/are the longest word/s that appear/s either in a book’s description or in the first
# sentence of a book? In which book (title) it appears?
# 9. What was the last book published in the list?
# 10. What is the year of the most updated entry in the list?
# 11. What is the title of the second published book for the author with the highest number of
# different titles in the list?
# 12. What is the pair of (publisher, author) with the highest number of books published?
# Finally put the files into a Zip File
# ISBNs are essentially book identifiers and different editions of a book will have different ids. So
# the same book (text) can be represented by more than one ISBN. We consider books with
# different ISBN identifiers but with the same title value to be the same book.
import requests
import pandas as pd 
API_ENDPOINT = "https://openlibrary.org/api/books"


df = pd.read_csv('books-isbns.txt',header=None,names=['isbn'])
available_books = []
unavailable_books = []
for isbn in df['isbn']:
    params = {
        'bibkeys': f'ISBN:{isbn}',
        'format': 'json',
        'jscmd': 'data'
    }
    try:
        response = requests.get(API_ENDPOINT, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            key = f"ISBN:{isbn}"

            if key in data:
                available_books.append(data[key])
            else:
                print(f"No data found for ISBN: {isbn}")
                unavailable_books.append(data[key])
        else:
            print(f'Failed to fetch data for ISBN: {isbn} - Status Code: {response.status_code}')
    except Exception as e:
        print(f"Error fetching ISBN {isbn}: {e}")


if available_books:
    books_df = pd.DataFrame(results)
    books_df.to_csv('fetched_books.csv', index=False)
    print(books_df.head())
else:
    print("No valid data fetched.")



# test = requests.get('https://openlibrary.org/api/books?bibkeys=ISBN:9780316134262,format=json&jscmd=data',timeout=2)
# print(test.text)
# var _OLBookInfo = {"ISBN:9780316134262": {"url": "https://openlibrary.org/books/OL44242367M/Deadline", "key": "/books/OL44242367M", "title": "Deadline", "authors": [{"url": "https://openlibrary.org/authors/OL6807570A/Seanan_McGuire", "name": "Seanan McGuire"}], "pagination": "624", "identifiers": {"isbn_13": ["9780316134262"], "openlibrary": ["OL44242367M"]}, "publishers": [{"name": "Orbit"}], "publish_date": "2011"}};