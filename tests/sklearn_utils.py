from sklearn.tree import DecisionTreeClassifier
from sklearn import datasets
from sklearn.model_selection import train_test_split

_dataset = datasets.load_iris()
X_train, X_test, _y_train, _y_test = train_test_split(_dataset.data, _dataset.target, test_size=0.3)
feature_names = _dataset.feature_names


def create_sklearn_model(max_depth=5):
    model = DecisionTreeClassifier(max_depth=max_depth)
    model.fit(X_train, _y_train)
    return model
