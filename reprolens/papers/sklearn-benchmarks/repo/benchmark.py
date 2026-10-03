#!/usr/bin/env python3
"""
Simple benchmark runner for scikit-learn internal benchmarks.
Runs classifiers on standard sklearn datasets and outputs accuracy.
"""
import sys
import time
import numpy as np
from sklearn import preprocessing, datasets
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split

def load_data(dataset: str):
    """Load a scikit-learn built-in dataset."""
    if dataset == 'iris':
        data = datasets.load_iris()
    elif dataset == 'digits':
        data = datasets.load_digits()
    elif dataset == 'wine':
        data = datasets.load_wine()
    elif dataset == 'breast_cancer':
        data = datasets.load_breast_cancer()
    else:
        raise ValueError(f"Unknown dataset: {dataset}")
    
    X, y = data.data, data.target
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    scaler = preprocessing.StandardScaler().fit(X_train)
    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)
    
    return X_train, y_train, X_test, y_test

def run_model(clf_name, clf_params, X, Y, Xt, Yt, num_repeat=1):
    """Run a single model and return accuracy scores."""
    accuracies = []
    for i in range(num_repeat):
        Xs, Ys = shuffle(X, Y)
        clf = globals()[clf_name](**clf_params)
        start_time = time.perf_counter()
        clf.fit(Xs, Ys)
        score = clf.score(X_test, Y_test)
        duration = time.perf_counter() - start_time
        accuracies.append(score)
        print(f'#test: {i} acc: {score:.3f} time: {duration:.3f}s classifier: "{clf_name}" parameter: {clf_params}')
    return accuracies

def main():
    if len(sys.argv) < 2:
        print("Usage: python benchmark.py --model=rf|logreg --dataset=iris|digits|wine|breast_cancer")
        sys.exit(1)

    args = {}
    for arg in sys.argv[1:]:
        if arg.startswith('--model='):
            args['model'] = arg.split('=')[1]
        elif arg.startswith('--dataset='):
            args['dataset'] = arg.split('=')[1]
    
    if 'model' not in args or 'dataset' not in args:
        print("Usage: python benchmark.py --model=rf|logreg --dataset=iris|digits|wine|breast_cancer")
        sys.exit(1)

    model = args['model']
    dataset = args['dataset']
    
    print(f"Loading {dataset} data...")
    X, Y, Xt, Yt = load_data(dataset)

    if model == 'rf':
        clf_name = 'RandomForestClassifier'
        clf_params = {'n_estimators': 100, 'criterion': 'gini', 'max_depth': 10, 'random_state': 42}
    elif model == 'logreg':
        clf_name = 'LogisticRegression'
        clf_params = {'C': 1.0, 'penalty': 'l2', 'multi_class': 'ovr', 'max_iter': 1000, 'solver': 'liblinear', 'random_state': 42}
    else:
        print("Error: model must be 'rf' or 'logreg'")
        sys.exit(1)

    print(f"Training {clf_name} ({clf_params}) on {dataset}...")
    accuracies = run_model(clf_name, clf_params, X, Y, Xt, Yt, num_repeat=1)

    mean_acc = np.mean(accuracies)
    print(f"Test accuracy: {mean_acc:.3f}")

if __name__ == "__main__":
    main()