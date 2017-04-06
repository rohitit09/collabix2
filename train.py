import nltk
train = [(dict(a=1,b=1,c=1), 'y'),(dict(a=1,b=1,c=1), 'x'),(dict(a=1,b=1,c=0), 'y'),(dict(a=0,b=1,c=1), 'fund'),(dict(a=0,b=1,c=1), 'fund'),(dict(a=0,b=0,c=1), 'y'),(dict(a=0,b=1,c=0), 'x'),(dict(a=0,b=0,c=0), 'x'),(dict(a=0,b=1,c=1), 'fund')]
test = [(dict(a=1,b=0,c=1)),(dict(a=1,b=0,c=0)),(dict(a=0,b=1,c=1))]
classifier = nltk.classify.NaiveBayesClassifier.train(train)
print sorted(classifier.labels())
print classifier.classify_many(test)
for pdist in classifier.prob_classify_many(test):
	print('%.4f %.4f' % (pdist.prob('x'), pdist.prob('y')))

