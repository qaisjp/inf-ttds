
[Source](https://www.inf.ed.ac.uk/teaching/courses/tts/labs/lab0.html "Permalink to Text Technologies for Data Science: LAB 0")

# Text Technologies for Data Science: Lab 0

![skip navigation][1]

How to read a text file from hard-disk. This lab is optional for those who are not fully confident about their programming skills. There is nothing specific to be done in this lab more than reading a text file from HD word by word, which is the most basic skill you need to have to be able to take the course.

### Programming languages

* You need to have Perl or Python on your machine (you still can use something else) if you prefer.
* If you are using Dice, then you should have them there. Check with demonstrators how to run them.

### Download a sample text file

* Download the following file, which has the text of the Bible: [link][2]

### Skills to do with the file

You need to be confident with the following skills with any programming language when dealing with a text file:

* Reading and Writing into text files
* Reading text by word, and calling functions to process word if required (e.g. lower case word letters)
* Regular expressions would be very useful to know

### Useful tips

Python Tutorials: you can check one of these tutorials:

**Useful Shell Commands**
Print frequency of unique terms in a given collection:

- `cat text.file | tr " " "n" | tr "A-Z" "a-z" | sort | uniq -c | sort -n > terms.freq`
- `cat text.file | perl -p -e "s/[^w]+/n/g" | tr "A-Z" "a-z" | sort | uniq -c | sort -n > terms.freq`

**All Unix Shell Commands for Windows**:

- download: [here][3]
- unzip the directory at a decent location on your drive (e.g. c: or c:program files)
- add the path to the "bin" directory to your Windows path: ([example][4])

Unless explicitly stated otherwise, all material is copyright © The University of Edinburgh

[1]: https://www.inf.ed.ac.uk/images/spacer.gif
[2]: http://www.gutenberg.org/cache/epub/10/pg10.txt
[3]: https://www.inf.ed.ac.uk/lab1/UnxUpdates.zip
[4]: https://www.java.com/en/download/help/path.xml
[5]: https://www.inf.ed.ac.uk/about/webmaster.html
[6]: https://www.inf.ed.ac.uk/about/cookies.html
