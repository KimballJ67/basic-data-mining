import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Scanner;

/*
 * This program reads a collection of text files and creates a vectorized k-gram representation of
 * them. 
 * 
 * Usage: Give the program the following command line arguments. 
 * 1. The directory where the text files are stored 
 * 2. The name of the file where you would like the program's output to be stored 
 * 3. The value of k to use 
 * 4. The number of k-grams to extract from each file. This number is randomly sampled from the
 * total k-grams in the file. 
 * 
 * The program has two outputs. 
 * 1. A comma separated value file. Each row in the file represents one text file. 
 * This text file is represented as a vector of zeroes and ones. Each entry in the vector represents a 
 * specific k-gram, and it is q if that k-gram appears in the text file and 0 otherwise. 
 * 2. A file containing the names of each text file processed. The lines in this file correspond 
 * to the lines in the comma separated value file--i.e., the first line in this file gives the name 
 * of the book represented by the first line of the comma separated value file. 
 * 
 * Notes: 
 * 1. This programs converts all text to lowercase and ignores non-alpha-numeric characters 
 * such as punctuation 
 * 
 * 2. This program expects text files originating from Project Gutenberg. As such, it expects the files
 * to have a header ending with "*** START OF THE PROJECT GUTENBERG EBOOK <Book_name> ***" 
 * and a footer beginning with "*** END OF THE PROJECT GUTENBERG EBOOK <Book_name> ***". 
 * It also accepts files with a header ending in 
 * "*END*THE SMALL PRINT! FOR PUBLIC DOMAIN ETEXTS*Ver.04.29.93*END*" and no footer save 
 * "The end of the Project Gutenberg e-text of <Book_name>". 
 * 
 * Written by Kimball Johnston 
 * February, 2022 
 */

public class kGrams {
	
	/**
	 * Contains all lines that can end the header at the beginning of a book. 
	 * No text before the header ends is included in k-grams. 
	 */
	private static final String[] headers = { "*** START OF THE PROJECT GUTENBERG EBOOK", 
			"*** START OF THIS PROJECT GUTENBERG EBOOK",
			"*END*THE SMALL PRINT!", 
			"***START OF THE PROJECT GUTENBERG EBOOK"};
	
	/**
	 * Contains all lines that can begin the footer at the end of a book. 
	 * No text after the footer begins is included in k-grams. 
	 */
	private static final String[] footers = { "*** END OF THE PROJECT GUTENBERG EBOOK", 
			"The end of the Project Gutenberg e-text of" }; 
	
	public static void main(String[] args) {
		String dir = args[0]; 
		if (dir.charAt(dir.length() - 1) != '/')
			dir += '/'; 
		
		File f = new File(args[0]);
		
		if(!f.isDirectory()) {
			System.out.println("Error: The first argument must be a directory!"); 
			return; 
		}
		
		int k = 0; 
		try {
			k = Integer.parseInt(args[2]);
		} catch(NumberFormatException e) {
			System.out.println("Error: The third argument must be a positive integer");
			return;
		}
		
		ArrayList<HashSet<String>> kGrams = new ArrayList<HashSet<String>>(); 
		ArrayList<String> names = new ArrayList<String>(); 
		
		System.out.println("Parsing files"); 
		
		// Get a set of k-grams for each  file 
		for (String fileName : f.list()) 
			try {
				if(fileName.equals(".DS_Store"))
					continue;
				
				System.out.println(fileName);
				
				kGrams.add(getKGrams(dir + fileName, k));
				names.add(fileName);
			} catch(FileNotFoundException e) {
				System.out.println(e.getMessage());
				return;
			}
		
		int numGrams = 0; 
		try {
			numGrams = Integer.parseInt(args[3]);
		} catch(NumberFormatException e) {
			System.out.println("Error: The fourth argument must be a positive integer");
			return;
		}
		
		// Cut the number of k-grams down to the user-specified input 
		for (int i = 0; i < kGrams.size(); i++) {
			if(kGrams.get(i).size() <= numGrams) 
				continue; 
			
			HashSet<Integer> toRemove = new HashSet<Integer>();
			ArrayList<Integer> allOptions = new ArrayList<Integer>();
			
			for (int j = 0; j < kGrams.get(i).size(); j++)
				allOptions.add(j);
			
			Collections.shuffle(allOptions);
			for (int j = 0; j < kGrams.get(i).size() - numGrams; j++) 
				toRemove.add(allOptions.get(j));
			
			int j = 0;
			Iterator<String> iter = kGrams.get(i).iterator();
			
			while (iter.hasNext()) {
				iter.next();
				
				if (toRemove.contains(j)) 
					iter.remove();
				
				j++;
			}
		}
	
		// Get all k-grams present across all books 
		HashSet<String> allGrams = new HashSet<String>(); 
		for (int i = 0; i < kGrams.size(); i++) 
			for (String gram : kGrams.get(i)) 
				allGrams.add(gram); 
		
		// Map each k-gram to a number (this number will be index representing that k-gram
		// in the vectors representing the text) 
		HashMap<String, Integer> vectorMap = new HashMap<String, Integer>(); 
		int index = 0; 
		for (String gram : allGrams) {
			vectorMap.put(gram, index);
			index++;
		}
		
		// Get a numerical vector representation of each text 
		ArrayList<byte[]> vectors = new ArrayList<byte[]>();
		for (int i = 0; i < kGrams.size(); i++) {
			byte[] vec = new byte[allGrams.size()]; 
			
			for (String gram : kGrams.get(i)) 
				vec[vectorMap.get(gram)] = 1;
			
			vectors.add(vec);
		}
		
		System.out.println();
		System.out.println("Writing to file");
		
		try(PrintWriter w = new PrintWriter(args[1] + ".csv")) {
			for(int i = 0; i < vectors.size(); i++) {
				System.out.println(names.get(i));
				
				for (int j = 0; j < vectors.get(0).length - 1; j++) 
					w.print(vectors.get(i)[j] + ",");
				w.print(vectors.get(i)[vectors.get(0).length - 1] + "");				
				w.println();
			}
			
		} catch (FileNotFoundException e) {
			System.out.println("There was an error saving the output"); 
		}
		
		try(PrintWriter w = new PrintWriter(args[1] + "_Names.txt")) {
			for(int i = 0; i < names.size(); i++) {
				w.println(names.get(i));
			}
			
		} catch (FileNotFoundException e) {
			System.out.println("There was an error saving the output"); 
		}
	}
	
	/**
	 * Gets the k-grams contained in a file 
	 * @param filename The file to parse 
	 * @param k The size of the k-grams to generate 
	 * @return A set of all k-grams included in the file 
	 * @throws FileNotFoundException If there is an error reading the file 
	 */
	private static HashSet<String> getKGrams(String filename, int k) throws FileNotFoundException {
		HashSet<String> grams = new HashSet<String>();
		
		try(Scanner scn = new Scanner(new File(filename))) {
			boolean doneWithHeader = false;
			
			// Do not include the header text in the k-gram 
			while(!doneWithHeader) {
				String line = scn.nextLine(); 
				
				for (int i = 0; i < headers.length; i++) 
					if (line.length() >= headers[i].length() 
					&& line.substring(0, headers[i].length()).equals(headers[i])) 
						doneWithHeader = true;
			}
			
			// Initialize the k-gram 
			String[] kgram = new String[k];
			for (int i = 0; i < k; i++) 
				kgram[i] = getStrippedString(scn.next()); 
			
			addKGram(grams, kgram, 0);
			
			boolean hitFooter = false; 
			String line = "";
			int index = 0;
			
			// Include everything up to the footer in the k-gram 
			while (!hitFooter) {
				
				Scanner lineScn = new Scanner(line); 
				
				// Read in words one at a time 
				while (lineScn.hasNext()) {
					kgram[index] = getStrippedString(lineScn.next()); 
					index = (index + 1) % k;
					addKGram(grams, kgram, index); 
				}
			
				// Check that we haven't hit the footer yet 
				if(!scn.hasNextLine())
					break;
				
				line = scn.nextLine(); 
			
				for (int i = 0; i < footers.length; i++) 
					if (line.length() >= footers[i].length() 
							&&line.substring(0, footers[i].length()).equals(footers[i])) 
						hitFooter = true;
				
			}
		} 
		
		return grams; 
	}
	
	/**
	 * Adds the k-gram to the set of k-grams. 
	 * The k-gram is defined as the sequence of words starting at kgram[index] and going to
	 * kgram[(index + k - 1) % k]. 
	 * For instance, the k-gram might be kgram[0], kgram[1], and kgram[2]. It might also be 
	 * kgram[1], kgram[2], and then kgram[0]. 
	 * @param kgrams The set of all k-grams 
	 * @param kgram The words in the k-gram 
	 * @param index The first word in the k-gram 
	 */
	private static void addKGram(HashSet<String> kgrams, String[] kgram, int index) {
		StringBuilder s = new StringBuilder();
		
		for (int i = 0; i < kgram.length; i++) {
			s.append(kgram[(index + i) % kgram.length]); 
			s.append(" ");
		}
		
		kgrams.add(s.toString());
	}
	
	/**
	 * Returns a lower case version of the string stripped of non-alphanumeric characters. 
	 * @param s The string to strip 
	 * @return  A lower case, alphanumeric version of the string 
	 */
	private static String getStrippedString(String s) {
		return s.replaceAll("[^a-zA-Z0-9 ]", "").toLowerCase();
	}

}
