import os

def directory(file):
    path = os.path.dirname(os.path.realpath(__file__)) + '\\' + file
    print(path)
    return path
