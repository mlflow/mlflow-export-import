import sklearn
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics 
from sklearn import datasets
from sklearn.model_selection import train_test_split

def create_sklearn_model(max_depth=5):
    dataset = datasets.load_iris()
    X_train, X_test, y_train, y_test = train_test_split(dataset.data, dataset.target, test_size=0.3)
    clf = DecisionTreeClassifier(max_depth=max_depth)
    clf.fit(X_train, y_train)
    predictions = clf.predict(X_test)
    accuracy_score = metrics.accuracy_score(y_test,predictions)
    print("accuracy_score:",accuracy_score)
    return clf
    

