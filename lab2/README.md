
[Source](https://www.inf.ed.ac.uk/teaching/courses/tts/labs/lab2.html "Permalink to Text Technologies for Data Science: LAB 2")

# Text Technologies for Data Science: Lab 2

Based on lecture 5

## Preprocessing

* You need to have Perl or Python on your machine (you still can use something else).
* Download the following file: [link][9], which contains:
    - Collection 1: 5 sample 1-line-documents used in lecture 5.
    - Collection 2: 1000 sample news articles.

    _Note 1:_ there are two versions of the files, XML and TXT. You are free to use the one you want for the lab. However, it worth noting that XML format is the more standard one in TREC IR test collections.

    _Note 2:_ for the news articles collection, please include the headline of the article to the index.

    _Note 3:_ these are very small collections just for experimentation
* Be sure that you have your preprocessing module ready (revise: [lab 1][10]), then apply it to the collections.

    _if you didn't have it done, then at least get the tokeniser and casefolding ready for this lab_
* Implement positional inverted index. You need to save the following information in terms inverted lists:
    - term (pre-processed) and its document frequency (optional)
    - list of documents where this term occured
    - for each document, list of positions where the term occured within the document
* Print output in a text file for visualisation. Example output [here][11] (_examples didn't apply stopping or stemming_)

    _in practice (for assignment), you might save in a more effecient format (e.g. binary files)._
* Please check the output inverted index when enable/disable the following:
    - stopping
    - stemming

## Running search on index

* Build a module that allows the following:
    - load index into memory
    - apply Boolean search (AND, OR, and NOT)
    - apply phrase search
    - apply proximity search
* Run the following queries in the following [file][12], and report the list of retrieved documents for each query. Discuss your results with your colleagues and try to find where is the problem if there are difference in answers.
* Think of the following:
    - If the index is very large, what would be the best way to save the index, and how it should be loaded into memory for search later?
    - What if the number of document is very large, and terms appears in documents 100000001 to 10010000. Is there a more effecient way to save document numbers? (read on Delta Encoding).

Unless explicitly stated otherwise, all material is copyright © The University of Edinburgh

[9]: https://www.inf.ed.ac.uk/teaching/courses/tts/labs/lab2/collections.zip
[10]: https://www.inf.ed.ac.uk/teaching/courses/tts/labs/lab1.html
[11]: https://www.inf.ed.ac.uk/teaching/courses/tts/labs/lab2/Index.zip
[12]: https://www.inf.ed.ac.uk/teaching/courses/tts/labs/lab2/queries.lab2.txt