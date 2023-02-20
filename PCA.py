import numpy as np 
import scipy as sp 
from scipy import linalg as LA 
import sys 
import matplotlib.pyplot as plt
from numpy.random import default_rng 

# This code reads a coma separated value file containing a system of 
# vector data points and runs PCA on them. 
#
# It takes three command-line arguments: 
# 1. The name of the file containing the vectors. Each line in this file 
# is treated as a vector. 
# 2. The dimension to which the data should be reduced 
# 3. The name of the file to which the program should write its output 
# 
# This program outputs its result to a coma separated value file. 
# Each line in this file corresponds to a dimension-reduced version 
# of the data point on that line in the original file. 
#
# Written by Kimball Johnston 
# February 2022 

# This generates a random unit vector with the desired number 
# of dimensions 
def Rand_Unit(rng, dim):
  u = np.array(np.zeros((dim)))

  d = dim 
  if dim % 2 == 1:
    d = d - 1

  for i in range(0, d, 2):
    r1 = rng.uniform()
    r2 = rng.uniform() 
    u[i] = np.sqrt(-2 * np.log(r1)) * np.cos(2 * np.pi * r2)
    u[i + 1] = np.sqrt(-2 * np.log(r1)) * np.sin(2 * np.pi * r2)

  if (dim % 2) == 1:
    r1 = rng.uniform()
    r2 = rng.uniform() 
    u[dim - 1] = np.sqrt(-2 * np.log(r1)) * np.cos(2 * np.pi * r2)

  u = u / LA.norm(u)
  return u

# This gets the top k right singular vectors of X 
def get_right_sing(X, k): 
	vecs = np.zeros((k, len(X[0,:]))) 
	rng = default_rng() 
	A = np.copy(X)

	for i in range(k):
		u = np.zeros((len(X[0,:]), 1)) 
		u[:,0] = Rand_Unit(rng, len(vecs[0,:])) 
		err = 10 

		#for j in range(1000):
		while err > 0.001: 
			u_next = A.T @ (A @ u) 
			e_val = LA.norm(u_next) / LA.norm(u)
			err = LA.norm((e_val * u) - u_next) 
			u = u_next / abs(u_next).max()  

		u = u / LA.norm(u)
		vecs[i,:] = u.T   
		A = A - A @ u @ u.T

	return vecs 

# Load the data to reduce 
X = np.loadtxt(open(sys.argv[1], "rb"), delimiter=",")
n = len(X) 
print(len(X[0,:]))

# Center the data 
C_n = np.identity(n) - np.ones((n, n)) / n 
X_centered = C_n @ X

# Run SVD on the data 
desired_dim = int(sys.argv[2]) 
U, S, Vt = LA.svd(X_centered, full_matrices = False)
#Vt = get_right_sing(X_centered, desired_dim) 

X_reduced = np.zeros((len(X), desired_dim))

# Compute the dot product of each row (data point) in the data set
# and the top k right singular vectors, where k is the desired dimension.
# These dot products are the coordinates of the data point in the 
# subspace defined by these right singular vectors. 
for i in range(desired_dim): 
	X_reduced[:,i] = X_centered @ Vt[i,:].T 

# Save the result 
np.savetxt(sys.argv[3], X_reduced, delimiter = ',')

