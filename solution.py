# Import libraries
import os
import requests
import pandas as pd
import calendar
import string

# Create the API Endpoint Variable
API_ENDPOINT = "https://openlibrary.org/api/books"

# Create local file variable
LOCAL_FILE = "fetched_books.csv"

# To keep the task in one file we check if the fetched_books.csv is created if so we go to the solutions part if not we run the code that fetches the data and creates the file
if os.path.exists(LOCAL_FILE):
    books_df = pd.read_csv(LOCAL_FILE)
else:
    # Get all the isbns from the text file we got
    df = pd.read_csv("books-isbns.txt", header=None, names=["isbn"])
    # Create an array for the raw books before putting them into a dataframe
    raw_books = []
    # Create an array for all fields so we can flatten the data
    all_possible_fields = set()
    # Create an array for unavailable books to also make sure we have that data
    unavailable_books = []
    # Create a loop to loop over all the isbn numbers we got from the text file
    for isbn in df["isbn"]:
        # Create the parameters for the URL dynamically
        params = {"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"}

        try:
            # Send a get request to fetch each book based on the isbn and parameters
            response = requests.get(API_ENDPOINT, params=params, timeout=2)
            response.raise_for_status()
            # Fetch the data in json format
            data = response.json()
            # Create the key variable to get each book the API returns each book as a dictionary where the key is ISBN:isbn and the value inside is the book data
            key = f"ISBN:{isbn}"
            # Check if the key exists inside our data to make sure which book exists and which does not
            if key in data:
                book = data[key]
                # If the book exists we add it to the raw_books array
                raw_books.append(book)

                # We then get all the keys which are the fields of the books so we can make sure we get all available fields for the books
                all_possible_fields.update(book.keys())

            else:
                # We add the unavailable books to the unavailable_books array
                print(f"No data for ISBN: {isbn}")
                unavailable_books.append(isbn)
        except (requests.RequestException, Exception) as e:
            # In case the attempt to fetch the book fails we add that book to the unavailable_books array as well
            print(f"Error fetching ISBN {isbn}: {e}")
            unavailable_books.append(isbn)

    # Now that we fetched the books and found all the available fields we create a flattened_books array to generate a clean and organized csv file
    flattened_books = []

    # We loop over our raw_books which we fetched, this way it's much quicker
    for book in raw_books:
        # For each book we create a dictionary to hold the book after being flattened
        flat = {}

        # We check the book to see which fields it has and pass None for those it does not have from the fields
        for field in all_possible_fields:
            value = book.get(field)

            # We check if the value in the book for a field is a list
            if isinstance(value, list):
                # Clean up: Make sure if the field is a dictionary list (like authors, subjects) we pull 'name' fields; else cleanly join list into string
                if all(isinstance(item, dict) and "name" in item for item in value):
                    flat[field] = "; ".join(item["name"] for item in value)
                else:
                    flat[field] = "; ".join(
                        str(item).strip("'\"") for item in value
                    )  # Clean: strip messy quotes inside list items

            # We then check if the field is a dictionary
            elif isinstance(value, dict):
                # Clean up: If it's a dict (like cover, identifiers), we flatten keys nicely into field_subfield format
                for k, v in value.items():
                    clean_key = f"{field}_{k}"
                    if isinstance(v, list):
                        flat[clean_key] = "; ".join(
                            str(i).strip("'\"") for i in v
                        )  # Clean: handle lists inside dictionaries too
                    else:
                        flat[clean_key] = v

            else:
                # Primitive value (string, int, etc.)
                flat[field] = value

        flattened_books.append(flat)

    # Save the now flattened books into a dataFrame object then save them to our csv file
    books_df = pd.DataFrame(flattened_books)
    books_df.to_csv("fetched_books.csv", index=False)


# 1. How many different books are in the list?

# We take the titles of all the books and remove the duplicates then print the amount of books
titles = books_df["title"]
unique_titles = titles.drop_duplicates()
print(f"There are {unique_titles.count()} different books in the list")


# 2. What is the book with the most number of different ISBNs?

# We need to group the books by title then count how many rows have the same title , then find the one with most rows and that is the one with most ISBNs

# we create a series of books based on titles and the value for each is the amount of rows for that title
isbn_count = books_df.groupby("title").size()

# We sort the series from highest amount to the lowest
sort_count = isbn_count.sort_values(ascending=False)

# We get the title of the first book in our series
top_title = sort_count.index[0]

# We save the value of the first title which in this case amount of rows
top_count = sort_count.iloc[0]

print(
    f"The book with the most different ISBNs is '{top_title}' with {top_count} editions."
)

# 3. How many books don’t have a goodreads id?


# The field for goodreads is called identifiers_goodreads so we save it in a variable
goodreads_ids = books_df["identifiers_goodreads"]

# We now use the isna method to find all the NaN values
missing_goodreads = goodreads_ids.isna()

# We get the sum of the books without the goodreads ID
count_missing = missing_goodreads.sum()

print(f"There are {count_missing} books without a Goodreads ID.")


# 4. How many books have more than one author?


# we get the authors series
authors = books_df["authors"]

# check for multiple authors using the str contains method make sure none values don't break the code
check_multiple_authors = authors.str.contains(";", na=False)

# get the amount of books with multiple authors
count_multiple_authors = check_multiple_authors.sum()

print(f"There are {count_multiple_authors} books with more than one author.")


# 5. What is the number of books published per publisher?

# Get the publishers series remove null values
publishers = books_df["publishers"].dropna()

# Split the publishers in case there are multiple publishers for one book
publishers_split = publishers.str.split(";")

# We use the explode method to make each publisher into one row
publishers_exploded = publishers_split.explode()

# strip them so that we can clear any whitespace around the publishers name to avoid repetetive values and turn to lowercase
publishers_exploded = publishers_exploded.str.lower()
publishers_exploded = publishers_exploded.str.strip()

# Count the amount of books per publisher
publisher_counts = publishers_exploded.value_counts()

# I created another csv file to hold the values since there are 211 entries
publisher_counts.to_csv("publishers_counts.csv", header=["books_published"])


# Now a problem arises since some publishers are the same but named differently hence I map out the publishers which are the same and created another csv file to hold the filtered publishers and their amounts, although in a real world situation I would use a library like fuzzywuzzy but that would be more useful if we had over 100k entries so I simply used the chatGPT to give me the perfect mapping for this

publisher_mapping = {
    # HarperCollins and variants
    "harper collins": "harpercollins",
    "harper collins publishers": "harpercollins",
    "harper collins paperbacks": "harpercollins",
    "harper collins usa": "harpercollins",
    "harper collins/voyager": "harpercollins",
    "harper collins uk": "harpercollins",
    "harper collins publisher": "harpercollins",
    "harper collins.india": "harpercollins",
    "harper  collins": "harpercollins",
    "harper collins 0 pub": "harpercollins",
    "harperchildren's audio": "harpercollins",
    "harper children's audio": "harpercollins",
    "harpercollins publishers": "harpercollins",
    "harpercollins publishers limited": "harpercollins",
    "harpercollinschildrensbooks": "harpercollins",
    "harpercollins childrens books": "harpercollins",
    "harpercollins pub.": "harpercollins",
    "harpercollins pub ltd": "harpercollins",
    "harpercollins audio": "harpercollins",
    "harpercollins, publishers": "harpercollins",
    "harper voyager harper collins publishers": "voyager",  # shifted to voyager
    # Voyager
    "voyager / harper collins": "voyager",
    "voyager / harpercollins": "voyager",
    "brand: harper voyager": "voyager",
    "livros da voyager (reino unido) e spectra (eua)": "voyager",
    "voyager": "voyager",
    "harper voyager": "voyager",
    "harpervoyager": "voyager",
    # Random House
    "random house uk ltd (a division of random house group)": "random house",
    "random house us": "random house",
    "random house export editions": "random house",
    "random house audio": "random house",
    "random house publishing group": "random house",
    # Penguin
    "penguin books": "penguin",
    "penguin books, limited": "penguin",
    "penguin books ltd": "penguin",
    "penguin": "penguin",
    "penguin random house": "penguin random house",
    "penguin random house llc.": "penguin random house",
    "penguin adult hc/tr": "penguin",
    # Putnam
    "putnam pub group": "putnam",
    "putnam": "putnam",
    "putnam adult": "putnam",
    "g.p. putnam's sons": "putnam",
    # Berkley
    "berkley pub. corp.": "berkley",
    "berkley pub. co. , distributed by putnam": "berkley",
    "berkley pub. corp. : distributed by putnam": "berkley",
    "berkley pub. co. : distributed by putnam": "berkley",
    "berkley publications": "berkley",
    "berkley": "berkley",
    # Ballantine
    "ballantine books": "ballantine",
    "ballantine del rey": "ballantine",
    "ballatine books": "ballantine",
    # Del Rey
    "del rey": "del rey",
    "del rey books": "del rey",
    "brand: del rey": "del rey",
    # Orbit
    "orbit science fiction": "orbit",
    "orbit": "orbit",
    # Sidgwick & Jackson
    "sidgwick and jackson": "sidgwick & jackson",
    "sidgwick & jackson ltd": "sidgwick & jackson",
    "sidg. & j": "sidgwick & jackson",
    "sidgwick & jackson": "sidgwick & jackson",
}

publishers_exploded = publishers_exploded.replace(publisher_mapping)
publisher_counts = publishers_exploded.value_counts()
publisher_counts.to_csv(
    "publishers_counts_mapped.csv", header=["books_published_mapped"]
)


# 6. What is the median number of pages for books in this list?

# First we get the number of pages series and remove NaN values
number_of_pages = books_df["number_of_pages"].dropna()

# We then use the median method to get the median number of pages
median_pages = number_of_pages.median()

print(f"The median number of pages is {median_pages}.")


# 7. What is the month with the most number of published books?

# Get the published dates series , convert to real dates and remove NaT values
published_dates = pd.to_datetime(books_df["publish_date"], errors="coerce").dropna()

# Extract the months into a series
months = published_dates.dt.month

# Get the amount of books per month
month_counts = months.value_counts()

# Get the month with the most books
top_month = month_counts.idxmax()

# Get the amount of books in that month
top_month_count = month_counts.max()

# Get the month name instead of just the number
month_name = calendar.month_name[top_month]

print(
    f"The month with the most published books is {month_name} with {top_month_count} books."
)


# 8. What is/are the longest word/s that appear/s either in a book’s description or in the first sentence of a book? In which book (title) it appears?


# Looking at the fields for the books there is no description so we willl go with excerpts which usually include the first line or paragraph of the book , and remove the null values
excerpts = books_df["excerpts"].dropna()

# Create a longest word variable and title of the longest work book to keep track and compare the string
longest_word = ""
book_title_of_longest = ""

for idx, excerpt_raw in excerpts.items():
    try:
        # check if the string returned from the excerpt is a dictionary or not and turn it into a dictionary if it is
        if isinstance(excerpt_raw, str):
            excerpt_parsed = eval(excerpt_raw)
        else:
            excerpt_parsed = excerpt_raw

        # get the value of the text inside whether its a list or dictionary or if it's nothing return an empty string
        if isinstance(excerpt_parsed, list) and len(excerpt_parsed) > 0:
            text = excerpt_parsed[0].get("text", "")
        elif isinstance(excerpt_parsed, dict):
            text = excerpt_parsed.get("text", "")
        else:
            text = ""

        # Split the returned text
        words = text.split()

        # clean the split strings
        cleaned_words = [word.strip(string.punctuation) for word in words]

        # compare the words returned by length to get the longest word
        for word in cleaned_words:
            if len(word) > len(longest_word):
                longest_word = word
                book_title_of_longest = books_df.loc[idx, "title"]

    except Exception as e:
        pass


print(
    f"The longest word is '{longest_word}' It appears in the book titled '{book_title_of_longest}'"
)


# 9. What was the last book published in the list?

# fetch the latest date for the log to be clearer
latest_date = published_dates.max()

# First off we return the published_dates variable we used earlier and use idxmax method to find the highest value in that series
latest_date_index = published_dates.idxmax()

# we then use the locate method with the index we got and ask for the title of the value in that index
latest_book_title = books_df.loc[latest_date_index, "title"]

print(f"The last book published is '{latest_book_title}' on {latest_date.date()}.")


# 10. What is the year of the most updated entry in the list?

# here we simply that the latest_date we got from the previous question and log the year of that entry
latest_year = latest_date.year

print(f"The year of the most updated entry is {latest_year}.")

# 11. What is the title of the second published book for the author with the highest number of different titles in the list?

# we will first split the authors in all books if there are multiple authors
books_df["authors_split"] = books_df["authors"].dropna().str.split(";")

# We then convert each one into a row
books_exploded = books_df.explode("authors_split")

# we then group by author and count unique titles
author_title_counts = books_exploded.groupby("authors_split")["title"].nunique()

# finally we get the top author using idxmax method
top_author = author_title_counts.idxmax()

# We now filter the books by the top author , we use copy to make sure we don't edit the original dataFrame but rather just the copy we need for the task at hand
top_author_books = books_exploded[books_exploded["authors_split"] == top_author].copy()


# we convert the publish date into a datetime object that gives us a real date
top_author_books.loc[:, "publish_date_parsed"] = pd.to_datetime(
    top_author_books["publish_date"], errors="coerce"
)


# we then sort the books by the publish date
top_author_books_sorted = top_author_books.sort_values("publish_date_parsed")

# we then locate based on index the second book's title
second_book_title = top_author_books_sorted.iloc[1]["title"]
print(f"The second published book for '{top_author}' is '{second_book_title}'.")


# 12. What is the pair of (publisher, author) with the highest number of books published?

# first off we have to split the authors and publishers and remove null values
books_df["authors_split"] = books_df["authors"].dropna().str.split(";")
books_df["publishers_split"] = books_df["publishers"].dropna().str.split(";")

# now we create one row that has one author one publisher and one title each so we can find the highest number of combination between all three
books_exploded_authors = books_df.explode("authors_split")
books_exploded = books_exploded_authors.explode("publishers_split")

# we will also strip any whitespace to make sure there are no values that mismatch because of it
books_exploded["authors_split"] = books_exploded["authors_split"].str.strip()
books_exploded["publishers_split"] = books_exploded["publishers_split"].str.strip()

# we then group them by the authors and publishers for each book
pair_counts = books_exploded.groupby(["publishers_split", "authors_split"]).size()

# using the idxmax method we get the highest pair and the max method to get the number of books
top_pair = pair_counts.idxmax()
top_pair_count = pair_counts.max()

print(
    f"The top (publisher, author) pair is {top_pair} with {top_pair_count} books published together."
)
