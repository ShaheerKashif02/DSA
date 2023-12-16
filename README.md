# Github Documentation

This code performs various operations on JSON files in a given directory, including lemmatizing and removing stopwords from the "title" and "content" fields, building a lexicon and inverted and forward indexes for each file, and implementing a search function that returns a list of relevant documents for a given query. 

## Dependencies

This code requires the following modules to be installed:

•	json: a built-in Python module for working with JSON data.

•	os: a built-in Python module for interacting with the operating system.

•	math: a built-in Python module for mathematical operations.

•	nltk: a natural language processing library for Python.

•	multiprocessing: a module for concurrent execution of Python code.

•	PyQt5: a GUI framework for Python.

•	webbrowser: a built-in Python module for launching web browsers.

•	PySide2: a GUI framework for Python.

## File Structure

The code defines the following variables and functions:

•	lemmatizer: an instance of the WordNetLemmatizer class from nltk, used to lemmatize words.

•	Stopwords: a list of English stopwords from nltk.

•	path: the current working directory.

•	directory: the path to the "Uncleaned" directory, which is located within the current working directory.

•	folder: a list of filenames that end with ".json" in the "Uncleaned" directory.

•	ProcessFile: a class that initializes a filename and directory, and has methods to build a lexicon, inverted index, and forward index for a JSON file, and to run the process of building these indexes.

•	search: a function that takes in a query and the lexicon, inverted index, and forward index of a JSON file, and returns a list of relevant documents for the given query.

## Operations

The ProcessFile class has the following methods:

### __init__(self, filename, directory)

This method initializes a ProcessFile object with the following attributes:

•	filename: the name of the JSON file to be processed.

•	directory: the directory where the JSON file is located.

•	lexicon: an empty list that will hold the lexicon for the JSON file.

•	inv_index: an empty list that will hold the inverted index for the JSON file.

•	fwd_index: an empty list that will hold the forward index for the JSON file.

### run(self)

This method performs the following operations on the JSON file specified in the filename attribute:

1.	Opens the file and loads the data into a variable.
2.	Loops through the data and performs the following operations on each entry.
3.	Tokenizes and lemmatizes the "title" field, removing any non-alphanumeric characters and stopwords.
4.	Tokenizes and lemmatizes the "content" field, removing any non-alphanumeric characters and stopwords.
5.	Creates a set of unique words from the "title" and "content" fields and adds it to the lexicon attribute.
6.	Creates an inverted index of the words in the entry, with the keys being the words and the values being a list of tuples containing the document ID, the hit count for the word in the document, and a boolean indicating whether the word appears in the "title" field. This inverted index is added to the inv_index attribute.
7.	Creates a forward index of the words in the entry, with the keys being the document IDs and the values being a sorted list of the words in the document. This forward index is added to the fwd_index attribute.
8. Returns the lexicon, inv_index, and fwd_index attributes as a list.

### The Search Function has the Following Parameters:

•	query: a string representing the search query.

•	lexicon: the lexicon of a JSON file.

•	inv_index: the inverted index of a JSON file.

•	fwd_index: the forward index of a JSON file.

It performs the following operations:

1.	Tokenizes and lemmatizes the query, removing any non-alphanumeric characters and stopwords.
2.	Removes any words from the query that are not in the lexicon.
3.	If the modified query is empty, returns an empty list.
4.	Gets the lists of document IDs and hit counts for each word in the query from the inv_index.
5.	Finds the intersection of the lists to get the IDs of the documents that contain any of the words in the query.
6.	Calculates the importance of each word in the query by summing the hit counts of each word in the documents where it appears, with a higher importance given to words that appear in the "title" field.
7.	Sorts the words in the query by importance.
8.	Initializes an empty list results to store the relevant documents.
9.	Loops through the documents identified in step 5 and performs the following operations:
10.	Calculates the score for the document by summing the importance of the words in the query that appear in the document.
11.	Adds a tuple containing the document ID and score to results.
12.	Sorts results in descending order by score and returns it.

## Additional notes

The code also includes a few lines of code related to PyQt5 and PySide2, which are GUI frameworks for Python. These create a QtWidgets class for the simple and interactive GUI, and define a function that opens the listed URLs in the default web browser. 

The main function executes and compiles the indexes and lexicon for all files, and multiprocessing is used to do said processing concurrently.

