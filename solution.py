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

API_ENDPOINT = "https://openlibrary.org/isbn/"
data_set = requests.get(API_ENDPOINT, timeout=2)
print(data_set)
