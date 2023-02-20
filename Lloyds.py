import numpy as np
from numpy import linalg as LA
import random 
import sys 
import matplotlib.pyplot as plt
from matplotlib import cm 

# This script runs Lloyd's algorithm. It uses several random restarts. 
#
# It takes the following command-line arguments 
# 1. The name of a file containing a set of data points (in CSV format) to cluster 
# 2. The name of a file containing the each data point's label (so the data point on 
# row one of the data file is associated with the label on row one of the names file) 
# 3. k, the number of clusters to identify 
# 4. The name of the file to which cluster information should be written 
# 5. (Optional) The method that should be used to initialize the clusters. This 
# can be "g" for Gonzalez's algorithm or "p" for k-means++. If this argument
# is not provided, it defaults to "p". 

####Function definitions####

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

# Runs Lloyd's algorithm on dataset X using the specified starting centers S1  
def Lloyd(X, S1): 
  unchanged = False 
  S = []
  for i in range(len(S1)):
    S.append(S1[i])

  while not unchanged: 
    unchanged = True 
    newS = []
    clusterCount = np.zeros(len(S))

    for i in range(len(S)):
      newS.append(np.zeros(len(S[0])))
    
    for i in range(len(X)):
      x = X[i,]
      clusterNum = phi(S, x)[1]
      newS[clusterNum] += x
      clusterCount[clusterNum] += 1 
    
    for i in range(len(newS)): 
      newS[i] /= clusterCount[i] 
      if not (newS[i] == S[i]).all(): 
        unchanged = False 
    S = newS
  
  return S

# Calculate the error 
def four_means_cost(S, X): 
  sum = 0 
  
  for i in range(len(X)): 
    x = X[i,]
    s = phi(S, x)[0] 
    sum += LA.norm(x - s)**2 
  
  return np.sqrt(sum / len(X))

####Main routine#### 

# Load the data to cluster 
X = np.loadtxt(open(sys.argv[1], "rb"), delimiter=",")

# Load the data labels 
with open(sys.argv[2]) as f: 
  Names = f.readlines() 

k = int(sys.argv[3])

numRestarts = 5 
bestCost = float('inf') 
bestS = [] 

# Run Lloyd's algorithm with several random restarts 
for i in range(numRestarts): 
	# Initialize clusters 
	if len(sys.argv) >= 6 and sys.argv[5] == 'g': 
		S1 = Gonzalez(X, k) 
	else:  
		S1 = k_means_plus_plus(X, k) 

	S = Lloyd(X, S1) 
	cost = four_means_cost(S, X) 
	if cost < bestCost: 
		bestCost = cost 
		bestS = S 

clusters = dict() 
for i in range(k): 
	clusters[i] = [] 

# Put each data in the list corresponding to its cluster 
for i in range(len(X)): 
  x = X[i,] 
  s, num = phi(S, x) 
  clusters[num].append(Names[i])
 
# Write the results to a file 
outFile = open(sys.argv[4], "w") 
for i in range(k): 
	outFile.write(str(i) + ":\n") 
	outFile.writelines(clusters[i]) 
	outFile.write("\n") 

outFile.close() 

# Generate plot if 2D 
if X.shape[1] == 2: 
	colours = [] 

	for i in range(k): 
		colours.append(cm.hsv(i / k)) 
	
	for i in range(len(X)): 
		x = X[i,] 
		s, num = phi(S, x) 
		plt.plot(x[0], x[1], 'o', color = colours[num])

	for i in range(len(S)): 
		s = S[i]
		plt.plot(s[0], s[1], 's', color = 'black') 

	plt.title("Data Clusters") 
	plt.savefig(sys.argv[4][:-4] + "_Image.png") 
