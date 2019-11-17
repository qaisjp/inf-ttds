.PHONY: pred.out pred.out2 Eval.txt Eval2.txt

# Train the classification model, and classify the tweets in the test file:
pred.out:
	python3 app.py feats --refresh-dic Tweets.14cat
	../svm/svm_multiclass_learn -c 1000 feats.train model
	../svm/svm_multiclass_classify feats.test model pred.out

pred.out2:
	python3 app.py feats --refresh-dic Tweets.14cat # TODO
	../svm/svm_multiclass_learn -c 1000 feats.train model
	../svm/svm_multiclass_classify feats.test model pred.out2

Eval.txt: pred.out app.py
	python3 app.py eval feats.test pred.out Eval.txt

Eval2.txt: pred.out2 app.py
	python3 app.py eval feats.test pred.out2 Eval2.txt
