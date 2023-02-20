# Basic Data Mining

This contains the code for Kimball Johnston and Seth Doubek's data mining final project. 
It only contains code written by Kimball Johnston and does not contain any of the 
code written by Seth Doubek. 

The code for this project can be divided into three stages: vectorization, 
dimensionality reduction, and clustering. 

To maximize flexibility, I've kept these stages separate so far. My vectorization
code resides in a separate file from my dimensionality reduction code. That way, we
can write multiple programs for each stage and can swap out between them with ease. 

Thus far, I've added one method of vectorization and one method of dimensionality 
reduction. However, we should add other techniques, such as matrix sketching, in 
the future. 

## GENERAL PATTERN 

My vectorization code outputs two files: one is a CSV file where each row contains 
a vector representing one book. The other is a a TXT file of book names. Line i in 
the text file contains the name of the book represented by line i in the CSV file. 

My dimensionality reduction code takes as input a CSV file. It outputs another CSV
file. Each row in this CSV file contains a dimension-reduced version of the vector
on the corresponding row in the input file. 

My clustering code takes as input a CSV file of data points and a file of data labels.
Line i in the data label file should contain the label for line i in the CSV file. 
It outputs a file containing cluster information. 

I would suggest we maintain this pattern (vectorization code outputs a CSV file and
dimensionality reduction code takes as input a CSV file and outputs another CSV file)
going forward. That way, we can easily try out different vectorization techniques
paired with different dimensionality reduction techniques. What's more, if we maintain
this modularity, we'll even be able to chain dimensionality reduction if we wish (i.e.
feeding the output of one dimensionality technique into the input of another technique). 

The following sections list and describe the code for each stage of the project. 

## VECTORIZATION CODE 

### 1. k-Grams 

The java file kGrams.java contains my code for using k-grams to vectorize
the books. It takes four command line arguments: the directory where the books' text
files are stored, the name of the file to which output should be written, the value
of k to use, and the number of k-grams to extract from each file. For example, running

java kGrams Books Vectors 2 10000 

on the command line will pull a random selection of 10,000 2-grams from each file in the
"Books" directory. It will write its output to the files Vectors.csv and 
Vectors_Names.txt.

This program can be compiled with the command "javac kGrams.java". 

This program was written expecting TXT files from Project Gutenberg. Project 
Gutenberg books have a specific header and footer, which this program is designed to 
skip. If books from other sources are used, this program will require modification. 

See the documentation in kGrams.java for more details. 

I've left some extraneous prints in the code. Feel free to remove them or
comment them out. 

## DIMENSIONALITY REDUCTION CODE 

### 1. PCA 

The Python file PCA.py contains my code for running PCA on a data file. It takes
four command line arguments: the name of the CSV file containing the data to reduce, the
dimension to which you would like to reduce the data, and the name of the file to which
output should be written. For example, running 

Python3 PCA.py Vectors.csv 3 Reduced.csv 

on the command line will reduce the data contained in Vectors.csv to 3 dimensions and then
write this reduced data to the file Reduced.csv. 

I left a statement in the code that prints out the number of columns in the data
matrix you're reducing. Feel free to comment it out if it annoys you. 

## CLUSTERING CODE 

### 1. Lloyd's 

The Python file Lloyds.py contains my code for running Lloyd's clustering algorithm 
on a data file. It takes five command-line arguments: the name of the CSV file containing the
data points, the name of a text file containing the data points' labels (line i in this file 
should contain the label of the ith data point), the number of clusters to identify, the name
of the file to which cluster information should be written, and (optionally) the method that 
should be used to initialize the clusters (this can be "g" for Gonzalez's algorithm or "p" for
k-means++, which is the default value). For instance, if you would like to run Lloyd's algorithm
initialized with k-means++ to identify five clusters in the data in Reduced.csv, you might run 
the following command. 

Python3 Lloyds.py Reduced.csv Vectors_Names.txt 5 Clusters.txt 

Output will be saved in a text file. For each cluster, this file will contain a number
followed by a colon and a newline. Each subsequent line will contain the name of a book in 
that cluster. Clusters will be separated by empty new lines. 

### 2. Mixture of Gaussians 

The Python file MixGauss.py contains my code for calculating a mixture of Gaussians 
clustering for the data. It uses an expectation maximization algorithm. It takes five command-
line arguments: the name of the CSV file containing the data, the name of the text file contianing
the data points' labels (the ith line in this file should correspond to the ith data point), the 
number of clusters to identify, the name of the file in which to save output, and an optional 
argument specifying the method to use to initialize the clusters ("g" for Gonzalez's algorithm and 
p--the default--for k-means++. For instance, you could run this code with the following command. 

Python3 MixGauss.py Reduced.csv Vectors_Names.txt 5 Gauss_Clusters.txt 

The output file will be a text file that is divided into two parts. The first part will 
contain each a line for each book in the data file. This line will have the book's name followed by 
a colon. After the colon will come a tab-separated list of the book's weight for each cluster. 
Following the weight section of the file will be the cluster section. This will include the files
associated with each cluster (as before). Now, however, each cluster will contain a book if that
book has at least 10 percent weight in that cluster, so books can appear in multiple clusters (unlike 
in Lloyd's algorithm). 

## RESULTS 

Descriptions of the various output files produced by the above code can be found in the files 
"Cluster File Descriptions.docx" and "Dimension Reduced File Descriptions.docx". "Dimension Reduced 
Vector Data" contains the outputs of the PCA code. The folder "Clusters" contains the outputs of the 
Lloyd's and mixture of Gaussians code. The file "Final Project Poster.pdf" contains an overall 
description of our results. 

## CHANGES: 

1. (No longer relevant.) 
I added a new function to the PCA Python code. Running SVD was slow because it required 
computing all singular values. I wrote a function to just compute the top k right singular 
vectors (and not to compute the left singular vectors at all). This routine seems to be 
much faster. I've had success running it on data files with column sizes up to a few hundred 
thousand. This also let me boost the number of k-grams being drawn from each text file to the
thousands instead of the hundreds. I've compared the results of my method to those of the default
SVD method on datasets with a few thousand columns, and they seemed to match up. That being said,
I haven't tested it extensively enough to be certain I didn't make an error. 

2. I realized that the native SVD library had an option that, when set, caused it to forgo 
calculating the complete U and V matrices. Using this option, the library code was fast enough
to work on large problem sizes (several hundred thousand columns). To my relief, it gave the same
results as the code I wrote by hand. Naturally, it's better to use the library code, so I commented
out my code. 
