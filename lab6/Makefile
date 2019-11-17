all: model pred.out

feats.test feats.train feats.dic: Tweets.14cat.train Tweets.14cat.test
	python3 app.py feats --refresh-dic Tweets.14cat

# Train the classification model
model: feats.train
	../svm/svm_multiclass_learn -c 1000 feats.train model

# Classify the tweets in the test file:
pred.out: model feats.test
	../svm/svm_multiclass_classify feats.test model pred.out
