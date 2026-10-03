from utils import mnist_reader
X, Y = mnist_reader.load_mnist(path='data/fashion', kind='train')
print('Loaded', len(Y), 'samples')