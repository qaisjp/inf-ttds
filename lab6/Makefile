all: model1

# Train the classification model
model1:
	python3 app.py feats --refresh-dic Tweets.14cat
	../svm/svm_multiclass_learn -c 1000 feats.train model

# Classify the tweets in the test file:
pred.out: model1
	../svm/svm_multiclass_classify feats.test model pred.out
