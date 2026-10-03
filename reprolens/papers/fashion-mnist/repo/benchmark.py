#!/usr/bin/env python3
"""
Simple benchmark runner for ReproLens prototype.
Runs RandomForest and LogisticRegression on Fashion-MNIST and outputs accuracy.
"""
import sys
import time
import numpy as np
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.utils import shuffle
from utils import mnist_reader

def load_data():
    """Load Fashion-MNIST data."""
    X, Y = mnist_reader.load_mnist(path='data/fashion', kind='train')
    Xt, Yt = mnist_reader.load_mnist(path='data/fashion', kind='t10k')
    scaler = preprocessing.StandardScaler().fit(X)
    X = scaler.transform(X)
    Xt = scaler.transform(Xt)
    return X, Y, Xt, Yt

def run_model(clf_name, clf_params, X, Y, Xt, Yt, num_repeat=1):
    """Run a single model and return accuracy scores."""
    accuracies = []
    for i in range(num_repeat):
        Xs, Ys = shuffle(X, Y)
        clf = globals()[clf_name](**clf_params)
        start_time = time.perf_counter()
        clf.fit(Xs, Ys)
        score = clf.score(Xt, Yt)
        duration = time.perf_counter() - start_time
        accuracies.append(score)
        print(f'#test: {i} acc: {score:.3f} time: {duration:.3f}s classifier: "{clf_name}" parameter: {clf_params}')
    return accuracies

def main():
    if len(sys.argv) < 2:
        print("Usage: python benchmark.py --model=rf|logreg")
        sys.exit(1)

    arg = sys.argv[1]
    if not arg.startswith('--model='):
        print("Usage: python benchmark.py --model=rf|logreg")
        sys.exit(1)

    model = arg.split('=')[1]
    if model not in ['rf', 'logreg']:
        print("Error: model must be 'rf' or 'logreg'")
        sys.exit(1)

    print(f"Loading Fashion-MNIST data...")
    X, Y, Xt, Yt = load_data()

    if model == 'rf':
        clf_name = 'RandomForestClassifier'
        clf_params = {'n_estimators': 100, 'criterion': 'gini', 'max_depth': 100}
    elif model == 'logreg':
        clf_name = 'LogisticRegression'
        # Use liblinear solver for faster convergence, increase max_iter
        clf_params = {'C': 1.0, 'penalty': 'l2', 'multi_class': 'ovr', 'max_iter': 1000, 'solver': 'liblinear'}

    print(f"Training {clf_name} ({clf_params})...")
    accuracies = run_model(clf_name, clf_params, X, Y, Xt, Yt, num_repeat=1)

    mean_acc = np.mean(accuracies)
    print(f"Test accuracy: {mean_acc:.3f}")

if __name__ == "__main__":
    main()