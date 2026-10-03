from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
from utils import mnist_reader
from sklearn.utils import shuffle
import time

X, Y = mnist_reader.load_mnist(path='data/fashion', kind='train')
Xt, Yt = mnist_reader.load_mnist(path='data/fashion', kind='t10k')

scaler = preprocessing.StandardScaler().fit(X)
X = scaler.transform(X)
Xt = scaler.transform(Xt)

Xs, Ys = shuffle(X, Y)

clf = RandomForestClassifier(n_estimators=10, criterion='gini', max_depth=10)

start = time.perf_counter()
clf.fit(Xs, Ys)
score = clf.score(Xt, Yt)
duration = time.perf_counter() - start

print(f'Score: {score:.3f}, Time: {duration:.1f}s')