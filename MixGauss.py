import numpy as np
from numpy import linalg as LA
import random 
import sys 
import math 
import matplotlib.pyplot as plt
from matplotlib import cm

# This code runs the expectation maximization algorithm from section 8.4.1 
# in the textbook to calculate a mixture of Gaussians soft clustering of 
# the data. 
# 
# Input 
# 1. The name of the data file in which to identify soft clusters 
# 2. The name of the text file containing the data points' names 
# 3. The number of clusters to identify 
# 4. The name of the file in which to save output 
# 5. (Optional) The method used to initialize the centers. g for Gonzalez's 
# algorithm and p for k-means++. Defaults to p. 

####Function Definitions####

# Identifies which center in S is closest to query point x 
def phi(S, x):
	center = None 
	min = float('inf')
	centerNum = -1

	for i in range(len(S)): 
		s = S[i]
		dist = LA.norm(x - s)
		if dist < min: 
			center = s
			centerNum = i
			min = dist 
  
	return center, centerNum

# Performs Gonzalz's algorithm on dataset X 
def Gonzalez(X, k):
	s1 = X[random.randint(0, len(X) - 1),]
	S = [ s1 ]

	for i in range(k - 1):
		max = -1 * float('inf')
		si = X[0,]
		for j in range(len(X)):
			x = X[j,] 
			dist = LA.norm(x - phi(S, x)[0])
			if dist > max:
				max = dist
				si = x 
		S.append(si)
  
	return S

# Runs the k-means++ algorithm on dataset X  
def k_means_plus_plus(X, k): 
	s1 = X[random.randint(0, len(X) - 1),] 
	S = [ s1 ]

	for i in range(k - 1): 
		distances = np.zeros(len(X))
    #total = 0
		for j in range(len(distances)): 
			x = X[j,]
			dist = LA.norm(x - phi(S, x)[0])**2
			distances[j] = dist
      #total += dist 
    #distances /= total 

		centerIndex = random.choices(range(len(X)), distances)[0]
		S.append(X[centerIndex,])
  
	return S 

# Evaluates the Gaussian with the given mean and covariance matrix at 
# point x 
def Gauss(mu, Sigma, x): 
	return math.exp(-(x - mu) @ LA.inv(Sigma) @ (x - mu).T/2) / math.sqrt((2 * math.pi)**len(x) * abs(LA.det(Sigma))) 

# Runs mixture of Gaussians with starting set S on X 
def MixGauss(X, S): 
	# Initialize weights as hard clusters 
	w = np.zeros((len(X), len(S))) 
	for i in range(len(X)): 
		w[i, phi(S, X[i,:])[1]] = 1 
	 
	change = 1
	firstIter = True 

	while change > 0.1: 
	#for l in range(20): 
		W = np.zeros((len(S))) 
		mu = np.zeros((len(S), X.shape[1])) 
		Sigma = np.zeros((len(S), X.shape[1], X.shape[1])) 

		# Calculate Gaussians 
		for i in range(len(S)): 
			# Calculate the total weight in each cluster 
			for j in range(len(X)): 
				W[i] += w[j, i] 

			# Calculate the mean of each cluster's Gaussian 
			for j in range(len(X)): 
				mu[i,:] += w[j, i] * X[j,:] 
			mu[i,:] /= W[i] 

			# Calculate each cluster's Gaussian's covariance matrix 
			for j in range(len(X)): 
				Sigma[i,:,:] += w[j, i] * np.outer((X[j,:] - mu[i,:]), (X[j,:] - mu[i,:]))
			Sigma[i,:,:] /= W[i] 
		
		# Update weights 
		for i in range(len(X)): 
			for j in range(len(S)): 
				if abs(LA.det(Sigma[j,:,:])) <= 1e-5: 
					continue 
				w[i, j] = Gauss(mu[j,:], Sigma[j,:,:], X[i,:]) 

		# Normalize the weights 
		for i in range(len(X)): 
			w[i,:] /= sum(w[i,:]) 

		# Calculate the score, which will determine whether we have converged 
		score = 0 
		for i in range(len(X)): 
			for j in range(len(S)): 
				if abs(LA.det(Sigma[j,:,:])) <= 1e-5: 
					continue 
				if w[i,j] * Gauss(mu[j,:],Sigma[j,:,:],X[i,:]) <= 0: 
					continue 

				score -= math.log(w[i, j] * Gauss(mu[j,:], Sigma[j,:,:], X[i,:]))

		if firstIter: 
			oldscore = score
			firstIter = False  
			continue 
		
		change = abs(score - oldscore) 
		oldscore = score 	
	return w, mu, Sigma 

####Main routine#### 
# Load the data to cluster 
X = np.loadtxt(open(sys.argv[1], "rb"), delimiter=",")
 
# Load the data labels 
with open(sys.argv[2]) as f:
	Names = f.readlines()
 
k = int(sys.argv[3])

# Initialize clusters 
if len(sys.argv) >= 6 and sys.argv[5] == 'g':
	S1 = Gonzalez(X, k)
else:
	S1 = k_means_plus_plus(X, k)

w, mu, Sigma = MixGauss(X, S1) 

# Write the results to a file 

# Write each book's weight in each cluster 
outFile = open(sys.argv[4], "w")
for i in range(len(X)):
	outFile.write(Names[i][:-1] + ": ") 
	for j in range(w.shape[1]): 
		outFile.write("\t" + str(w[i, j]))
	outFile.write("\n")

outFile.write("\n") 

# Write clusters, where a book is in a cluster if it has more than 10% weight 
# in that cluster 
for i in range(k): 
	outFile.write(str(i) + ":\n") 
	for j in range(len(X)): 
		if w[j, i] >= 0.1: 
			outFile.write(Names[j]) 
	outFile.write("\n") 

outFile.close() 

# Generate plot if 2D 
if X.shape[1] == 2:  
	colours = []  

	for i in range(k): 
		colours.append(i / k) 
  
	for i in range(len(X)): 
		x = X[i,] 
		col = 0 
		for j in range(k): 
			col += w[i,j] * colours[j] 

		plt.plot(x[0], x[1], 'o', color = cm.hsv(col)) 

	for i in range(k): 
		plt.plot(mu[i, 0], mu[i,1], 's', color = 'black') 

	plt.title("Gaussian Clusters") 
	plt.savefig(sys.argv[4][:-4] + "_Image.png") 

