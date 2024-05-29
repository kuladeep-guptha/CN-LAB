import pandas as pd
import numpy as np


data={'x':[-1.41,-0.70,0,0.70,1.41],
      'y':[-1.41,-0.70,0,0.70,1.41],
      'z':[-1.41,-0.70,0,0.70,1.41]}
data_matrix = np.array([data['x'], data['y'], data['z']])


covariance_matrix = np.cov(data_matrix)

print(covariance_matrix)