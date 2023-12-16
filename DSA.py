#importing libraries
import json
import os
from math import ceil

import nltk
from nltk import wordpunct_tokenize, WordNetLemmatizer
from nltk.corpus import stopwords
from multiprocessing import Pool, cpu_count
from PyQt5 import QtWidgets
import webbrowser
from PySide2.QtCore import Qt
import time

#lemmatizing words
#nltk.download('all')

lemmatizer = WordNetLemmatizer()
Stopwords = stopwords.words("english")
path = os.getcwd()
directory = os.path.join(path, "Uncleaned")
folder = [f for f in os.listdir(directory) if f.endswith(".json")]

class ProcessFile:
    
    def __init__(myuwuobject, filename, directory):
        myuwuobject.filename = filename
        myuwuobject.directory = directory
        myuwuobject.lexicon = []
        myuwuobject.inv_index = []
        myuwuobject.fwd_index = []
    
    def run(myuwuobject):
        start_time = time.perf_counter()
        f = os.path.join(myuwuobject.directory, myuwuobject.filename)
        with open(f, 'r') as File:
            data = json.load(File)
            for i in data:
                lexx = set()
                inv = {}
                fwd = {}
                i["title"] = wordpunct_tokenize(i["title"])
                i["title"] = [lemmatizer.lemmatize(x.lower()) for x in i["title"] if (x.isalnum() and x.lower() not in Stopwords)]
                i["content"] = wordpunct_tokenize(i["content"])
                i["content"] = [lemmatizer.lemmatize(x.lower()) for x in i["content"] if (x.isalnum() and x.lower() not in Stopwords)]
                # Add the words from the title and content fields to the lexicon
                fwd[i["url"]] = fwd.get(i["url"], []) + sorted([word for word in (i["title"]+i["content"])])
                lexx.update(i["title"]+i["content"])
                for word in lexx:
                    is_in_title = word in i["title"]
                    inv[word] = inv.get(word, []) + [(i["url"], (i["title"]+i["content"]).count(word), is_in_title)]
                myuwuobject.lexicon.append(lexx)
                myuwuobject.fwd_index.append(fwd)
                myuwuobject.inv_index.append(inv)
        end_time = time.perf_counter()
        print(f"Indexing completed in {end_time - start_time:.2f} seconds")
        return [myuwuobject.lexicon, myuwuobject.inv_index, myuwuobject.fwd_index]

#Searching function
def search(query, lexicon, inv_index, fwd_index):
    start_time = time.perf_counter()
    # Tokenize and lemmatize the query
    query = wordpunct_tokenize(query)
    query = [lemmatizer.lemmatize(x.lower()) for x in query if (x.isalnum() and x.lower() not in Stopwords)]
    for word in query:
        if (word not in lexicon):
            query.remove(word)
    if (len(query)==0):
        return []
    # Get the lists of document IDs and hit counts for each word in the query from the inverted index
    doc_hit_lists = [inv_index[word] for word in query]

    # Find the intersection of the lists to get the IDs of the documents that contain any of the words in the query
    docs = set()
    for doc_hit_list in doc_hit_lists:
        docs |= set(doc_hit_list)

    # Calculate the importance of each word in the query
    word_importance = {}
    for word in query:
        word_importance[word] = 0
        for doc_hit in doc_hit_lists:
            for doc, hit, is_in_title in doc_hit:
                if doc in docs:
                    word_importance[word] += hit * (2 if is_in_title else 1)

    # Sort the words in the query by importance
    sorted_query = sorted(query, key=lambda word: word_importance[word], reverse=True)

    # Get the lists of words for each document from the forward index
    word_lists = [fwd_index[doc_id[0]] for doc_id in docs]

    # Find the intersection of the lists to get the words that are common to all the documents
    words = set()
    for word_list in word_lists:
        words |= set(word_list)

    # Sort the documents by the number of hits for the most important word in the query (Ranking)
    try:
        sorted_docs = sorted(docs, key=lambda doc_id: inv_index[sorted_query[0]][doc_id[1]], reverse=True)  
        # Modify the ranking of the documents based on the number of query words they contain
        sorted_docs = [(doc, len(set(fwd_index[doc[0]]) & set(query))) for doc in sorted_docs]
        sorted_docs = sorted(sorted_docs, key=lambda qcount: qcount[1], reverse=True)
        # Return the top 30 documents
        sorted_docs = [doc[0][0] for doc in sorted_docs[:30]]
        end_time = time.perf_counter()
        print(f"Search completed in {end_time - start_time:.2f} seconds")
        return sorted_docs
    except: 
        return []

class SearchWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
#Window for query in tkinter
    def init_ui(self):
        self.query_label = QtWidgets.QLabel("Enter query:", self)
        self.query_input = QtWidgets.QLineEdit(self)
        self.search_button = QtWidgets.QPushButton("Search", self)
        self.results_label = QtWidgets.QLabel("Results:", self)
        self.results_list = QtWidgets.QListWidget(self)
        self.addfile_button = QtWidgets.QPushButton("Add New File", self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.addfile_button)
        layout.addWidget(self.query_label)
        layout.addWidget(self.query_input)
        layout.addWidget(self.search_button)
        layout.addWidget(self.results_label)
        layout.addWidget(self.results_list)
        self.addfile_button.clicked.connect(self.addfile)
        self.search_button.clicked.connect(self.on_search)
        self.results_list.itemDoubleClicked.connect(self.onDoubleClick)
        self.setWindowTitle("Search")
        self.setGeometry(300, 300, 300, 300)
        #Function to add a file
    def addfile(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select File to Add", "", "All Files (*);;JSON Files (*.json)", options=options)
        if file_name:
            updateIndexes(file_name, lexicon, inv_index, fwd_index)
        
    def setUrls(self, urls):
        # Clear the results list
        self.results_list.clear()    
        # Add the URLs to the list widget
        for url in set(urls):
            item = QtWidgets.QListWidgetItem(url)
            item.setData(Qt.UserRole, url)
            self.results_list.addItem(item)

    def on_search(self):
        # Get the query from the input field
        query = self.query_input.text()
        # Search for the query and get the top 30 results
        results = search(query, lexicon, inv_index, fwd_index)
        self.setUrls(results)

    def onDoubleClick(self, item):
        # Get the URL from the item
        url = item.data(Qt.UserRole)
        # Open the URL in the default web browser
        webbrowser.open(url)        

def updateIndexes(file, lexicon, inv_index, fwd_index):
    lexicon = set(lexicon)
    lex = []
    Inv = []
    Fwd = []
    f = os.path.join(directory, file)
    with open(f, 'r') as File:
        data = json.load(File)
        for i in data:
            lexx = set()
            inv = {}
            fwd = {}
            i["title"] = wordpunct_tokenize(i["title"])
            i["title"] = [lemmatizer.lemmatize(x.lower()) for x in i["title"] if (x.isalnum() and x.lower() not in Stopwords)]
            i["content"] = wordpunct_tokenize(i["content"])
            i["content"] = [lemmatizer.lemmatize(x.lower()) for x in i["content"] if (x.isalnum() and x.lower() not in Stopwords)]
            # Add the words from the title and content fields to the lexicon
            fwd[i["url"]] = fwd.get(i["url"], []) + sorted([word for word in (i["title"]+i["content"])])
            lexx.update(i["title"]+i["content"])
            for word in lexx:
                is_in_title = word in i["title"]
                inv[word] = inv.get(word, []) + [(i["url"], (i["title"]+i["content"]).count(word), is_in_title)]
            lex.append(lexx)
            Fwd.append(fwd)
            Inv.append(inv)
    for i in lex:
        lexicon.update(i)   
    for i in Inv:
        for key, value in i.items():
            # Modify the inv_index to store a list of lists containing the document link, number of hits and importance check
            inv_index.setdefault(key, []).extend(value)
    for i in Fwd:
        fwd_index.update(i) 
    lexicon = list(lexicon)
#Main
if __name__ == '__main__':
    
    lexicon = set()
    inv_index = {}
    fwd_index = {}
    objects = []
    workers = cpu_count()-1
    if workers == 0:
        workers = 1
    p = Pool(workers)
    for i in range(len(folder)):
        objects.append(ProcessFile(folder[i], directory))
    chunk = ceil(len(objects)/workers)
    if chunk == 0:
        chunk = 1
    proc = p.imap_unordered(ProcessFile.run, objects, chunk)
    p.close()
    p.join()
    for p in proc:
        for i in p[0]:
            lexicon.update(i)
        for i in p[1]:
            for key, value in i.items():
                # Modify the inv_index to store a list of lists containing the document ID, number of hits and importance check
                inv_index.setdefault(key, []).extend(value)
        for j in p[2]:
            fwd_index.update(j)
    lexicon = list(sorted(lexicon))
    inv_index = dict(sorted(inv_index.items()))
    fwd_index = dict(sorted(fwd_index.items()))
    app = QtWidgets.QApplication([])
    window = SearchWindow()
    window.show()
    app.exec_()
    