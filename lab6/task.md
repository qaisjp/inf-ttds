::: {#banner}
[![skip navigation](/images/spacer.gif){width="1"
height="1"}](#main){.skiplink}

+-----------------------------------------------------------------------+
| +:--------------------+:--------------------+---------------------+   |
| | ![The University of | ![School of         | ::: {align="left"}  |   |
| | Edinburgh](/images/ | Informatics](/image | [![](/images/arrow. |   |
| | crest.jpg){#logo    | s/title.jpg){#colle | gif){width="16"     |   |
| | width="84"          | getitle             | height="11"}](http: |   |
| | height="84"}        | width="479"         | //www.ed.ac.uk){.he |   |
| |                     | height="84"}        | adertext}[Universit |   |
| |                     |                     | y                   |   |
| |                     |                     | Homepage](http://ww |   |
| |                     |                     | w.ed.ac.uk){.header |   |
| |                     |                     | text}\              |   |
| |                     |                     | [![](/images/arrow. |   |
| |                     |                     | gif){width="16"     |   |
| |                     |                     | height="11"}](/){.h |   |
| |                     |                     | eadertext}[School   |   |
| |                     |                     | Homepage](/){.heade |   |
| |                     |                     | rtext}\             |   |
| |                     |                     | [![](/images/arrow. |   |
| |                     |                     | gif){width="16"     |   |
| |                     |                     | height="11"}](/abou |   |
| |                     |                     | t/contact.html){.he |   |
| |                     |                     | adertext}[School    |   |
| |                     |                     | Contacts](/about/co |   |
| |                     |                     | ntact.html){.header |   |
| |                     |                     | text}\              |   |
| |                     |                     | [![](/images/arrow. |   |
| |                     |                     | gif){width="16"     |   |
| |                     |                     | height="11"}](/sear |   |
| |                     |                     | ch/){.headertext}[S |   |
| |                     |                     | chool               |   |
| |                     |                     | Search](/search/){. |   |
| |                     |                     | headertext}\        |   |
| |                     |                     | ![](/images/spacer. |   |
| |                     |                     | gif){width="212"    |   |
| |                     |                     | height="1"}         |   |
| |                     |                     | :::                 |   |
| +---------------------+---------------------+---------------------+   |
+-----------------------------------------------------------------------+
:::

::: {#container}
[]{#main}

Lab 6 and 7
===========

Based on lectures 13 and 14

In these labs you will build a text classification model for classifying
tweets into 14 different categories

Please finish at least the first part of the lab in Lab 6, and the
remaining in Lab 7.

Build a text classifier
-----------------------

-   Download the following **[file](lab6/tweetsclassification.zip)**\
    There are two files in the compressed file:\
    - `Tweets.14cat.train` contains 2504 tweets to be used for taining
    the classification model\
    - `Tweets.14cat.test` contains 625 tweets to be used testing\
    The format of the files is as follows (tab separated):\
    `       tweet_ID tweet category   `
-   You need to build a module (using an programming language) to
    **extract the BOW features** from the training files. Simply apply
    the following:\
    - Read the tweets and preprocess it (remove links+tokenise). Do not
    apply stemming or stopping at this stage\
    - Find all the unique terms, and give each of them a unique ID
    (starting from 1 to the number of terms)\
    - Print the terms and the corresponding ID in a file and call it
    `feats.dic`
-   The next step now is to convert both the training file into set of
    features files. You need to build another module to read the tweets
    file and the `feats.dic`, then print the features in the following
    format:\
    `       11 783:1 1068:1 2026:1 4769:1 5961:1 6596:1 6696:1 7682:1 9699:1 10506:1 #doc_ID   `\
    Where the first number is the class ID (Please get the corresponding
    classes IDs from this [file](lab6/classIDs.txt)), followed by the
    list of features (ordered) in the formant
    `feature_ID:feature_value`. Features values at this stage will be
    binary, so it is one of the term exists, zero otherwise (features
    with value zero do not have to be printed, for this SVM classifier).
    At the end of each line, any comment could be added by adding the
    character \"\#\". In this case, we can add the document ID
    (tweet\_ID), which can help in error analysis later.\
    Please save the output to a file called `feats.train`. For
    validation, it should have the same number of lines as the training
    data file.
-   Use the same module in the previuos step to convert the test file of
    tweets into features file as well. You should use the same
    `feats.dic` file generated from the training data. For terms in the
    test file that do not exist in `feats.dic` (does not have a
    corresponding feature ID, since it never appear in the training
    data), please neglect these terms, or define a new feature ID that
    corresponds to OOV terms. Out file should be called `feats.test`,
    and should be in the same format as `feats.train`
-   It worth noting that in practice, when trying to classify text that
    has no label known yet, you can add any randon number instead of the
    class ID. For example, it can be something like this:\
    `       88 83:1 108:1 202:1 769:1 963:1 999:1 #unknown_label   `
-   Once the training and test features file are ready, you can now
    train a classifier and test the performance. In this lab, we will
    use [SVM multiclass
    Classifier](https://www.cs.cornell.edu/people/tj/svm_light/svm_multiclass.html).
    Please download the running binaries directly. There are running
    binaries for
    [Linux](http://download.joachims.org/svm_multiclass/current/svm_multiclass_linux64.tar.gz)
    and
    [Windows](http://download.joachims.org/svm_multiclass/current/svm_multiclass_windows.zip)
    available. You still can combile the [source
    code](http://download.joachims.org/svm_multiclass/current/svm_multiclass.tar.gz)
    on your machine for optimal performance.
-   Train the classification model:\
        `svm_multiclass_learn -c 1000 feats.train model`\
    - The `c` parameter could be optimized for better performance.
    However, for this stage, just set it to 1000.\
    - The output of this process will be a `model` file, saved in the
    same directory.
-   Classify the tweets in the test file:\
        `svm_multiclass_classify feats.test model pred.out`\
    - The output here will be the prediction file `pred.out`. The file
    will have the following format:\
    `         7 -0.546 -0.680 -0.600 -0.411 -0.458 -0.521 4.624 -0.744 -0.610 -0.687 2.436 -0.612 -0.571 -0.615     14 0.011 -0.023 0.044 -0.100 0.047 0.080 -0.014 0.135 -0.172 -0.069 -0.021 -0.003 -0.175 0.261     9 -0.085 -0.055 0.046 0.091 0.080 -0.073 -0.226 -0.206 0.441 -0.114 0.089 -0.134 0.087 0.059     1 1.786 -0.116 -0.232 0.007 -0.161 -0.056 -0.354 -0.181 0.045 -0.228 -0.165 -0.171 -0.037 -0.133`\
    The first number corresponds to the predicted class ID. The
    remaining numbers are the prediction score for each of the classes
    (14 classes in this case). All positive numbers could be considered
    as possible classes. However, the SVM selected one is that with the
    highest score.

Modifying you Classifier
------------------------

Think about what can make a better classification.

You can think about trying the following:

-   Apply stemming and stopping.
-   Duplicate hashtags words (e.g. convert \"`#car`\" to
    \"`#car car`\").
-   Expand tweet text that has link with the page title of that link
-   Try non-textual features: Tweet length, presence of hashtags, links,
    emojis, etc.
-   Can you try another classifier and compare the results?
-   Get more training data! You can check [this
    paper](http://arxiv.org/pdf/1503.04424.pdf) for potential idea on
    the same task

Try at least two possible methods for improving the classification.
Let\'s call the prediction files for the new methods `pred.out2`,
`pred.out3`, . . . etc.

Evaluation
----------

Build a module that has the following inputs: 1) `feats.test`, 2)
`pred.out`, compare the predicted class to the true class, and calcucate
the following measures:

-   Accuracy
-   Precision, recall, and F1 for each of the classes
-   Macro-F1 score of the system

You now need to prepare the following evaluation outputs:

-   Print the measures in a file called `Eval.txt` with the following
    format:
    `         Accuracy = 0.673         Macro-F1 = 0.631         Results per class:          1:   P=0.8   R=0.6   F=0.685          2:   P=0.45  R=0.712 F=0.551         3:   . . .`
-   For each of the methods you created to improve classification,
    please generate the evaluation file: `Eval2.txt`, `Eval3.txt`, . . .
    etc.
-   Find out which methods achieves the best performance (measure by
    Macro-F1), and generate the confusion matrix among all classes for
    it.

### Note

Parts of this lab are part of CW2, so please try to finish it properly.

::: {align="CENTER"}
![](/images/page_bar.gif){width="489" height="1"}\
[Home](/) : [Teaching](/teaching/) : [Courses](/teaching/courses/) : [Tts](/teaching/courses/tts/) 
:::
:::

+-----------------------------------------------------------------------+
| ::: {align="center"}                                                  |
| Informatics Forum, 10 Crichton Street, Edinburgh, EH8 9AB, Scotland,  |
| UK\                                                                   |
| Tel: +44 131 651 5661, Fax: +44 131 651 1426, E-mail:                 |
| school-office\@inf.ed.ac.uk\                                          |
| Please [contact our webadmin](/about/webmaster.html) with any         |
| comments or corrections. [Logging and Cookies](/about/cookies.html)\  |
| Unless explicitly stated otherwise, all material is copyright © The   |
| University of Edinburgh                                               |
| :::                                                                   |
+-----------------------------------------------------------------------+
