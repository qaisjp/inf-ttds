all: model pred.out

# Train the classification model
model: feats.train
	../svm/svm_multiclass_learn -c 1000 feats.train model

# Classify the tweets in the test file:
pred.out: model feats.test
	../svm/svm_multiclass_classify feats.test model pred.out
