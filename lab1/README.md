
[Source](https://www.inf.ed.ac.uk/teaching/courses/tts/labs/lab1.html "Permalink to Text Technologies for Data Science: LAB 1")

# Text Technologies for Data Science: Lab 1

![skip navigation][1]

Based on lecture 3 and 4

## Preprocessing

* You need to have Perl or Python on your machine (you still can use something else).
* Download the following files:
    - Collection 1 --> Bible: [link][2]
    - Collection 2 --> Wikipedia abstracts: [link][3]
* Write code to do the following:
    - **Tokenisation**: convert text into tokens with no puncituations
    - **Case folding**: make all text into lower case
    - **Stopping**: remove English [stop words][4]
    - **Normalisation**: Porter stemmer at least. You can try other stemmers as well. You can get Porter stemmer in [Perl][5] or [Python][6], or you can use [Snowball Stemmer][7] for multiple languages.
* Print new files for collection 1 and 2 after preprocessing.
* Discuss with your colleagues, what kind of modifications in preprocessing could be applied. For example:
    - Additional words/terms to be filtered outline
    - Special tokenisation
    - Additional normalisation to some terms

## Text Laws

For each of the two collections,

* Print the unique terms with frequency, then plot them in a log-log graph. Report with your friends what you notice on Zipf's law
* Plot the distribution of the first digit in frequences obtained and observe Beford's law. Try again while neglecting the one digit frequencies (frequencies less than 10), and check if the law still applies.
* Plot the growth of vocabulary while you go through the collection and observe Heap's law. Try to fit the law to you graph and report the best fitting _k_ and _b_ constants.
Advice on how to implement:
    - read text file term by term. count _n_ (the number of terms read).
    - save new terms in a hash as you go in reading the file. With each new term update the vocabulray size _v_.
    - print the values of _n_ and _v_ every while. Plot _n_ vs _v_ at the end.
    - try to fit an equation _v = k.n^b_. Report best fitting _k_ and _b_.

### Useful tips

**Print frequency of unique terms in a given collection**:
- `cat text.file | tr " " "n" | tr "A-Z" "a-z" | sort | uniq -c | sort -n > terms.freq`
- `cat text.file | perl -p -e "s/[^w]+/n/g" | tr "A-Z" "a-z" | sort | uniq -c | sort -n > terms.freq`

**All Unix Shell Commands for Windows**:
- download: [here][8]
- unzip the directory at a decent location on your drive (e.g. c: or c:program files)
- add the path to the "bin" directory to your Windows path: ([example][9])

Unless explicitly stated otherwise, all material is copyright © The University of Edinburgh

[1]: https://www.inf.ed.ac.uk/images/spacer.gif
[2]: http://www.gutenberg.org/cache/epub/10/pg10.txt
[3]: https://www.inf.ed.ac.uk/lab1/abstracts.wiki.txt.gz
[4]: http://members.unine.ch/jacques.savoy/clef/index.html
[5]: https://www.inf.ed.ac.uk/lab1/Porter.pm
[6]: https://pypi.python.org/pypi/stemming/1.0
[7]: http://snowball.tartarus.org/
[8]: https://www.inf.ed.ac.uk/lab1/UnxUpdates.zip
[9]: https://www.java.com/en/download/help/path.xml
[10]: https://www.inf.ed.ac.uk/about/webmaster.html
[11]: https://www.inf.ed.ac.uk/about/cookies.html
