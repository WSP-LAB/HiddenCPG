import pickle
from CPGPath import CPGPath

def read_cpg_path(file_path):
  with open(file_path, 'rb') as f:
    path = pickle.load(f)
  return path

def save_cpg_path(file_path, path):
  with open(file_path, 'wb') as f:
    pickle.dump(path, f, pickle.HIGHEST_PROTOCOL)
