""" Author :Prathusha JS Naidu 
Homework 1 : CMSC 676 """

import os
import sys
from bs4 import BeautifulSoup
import nltk
import re
from collections import Counter
import time

def word_freq(tokens):
        new_list = []
        tokens = [a.lower() for a in tokens]
        for word in tokens:
                if re.search(r'^\d+\.\d+', word) or not re.search(r'^\W+$', word) or re.search(r'^\w+', word):
                        new_list.append(word)

        new_dict = {}
        for (w,f) in Counter(new_list).iteritems():
                new_dict[w]=f
        return new_dict


def join_dir(full_dir,word_list):
#function to add each tokenized document contents to a global dictionary
        for word in word_list.keys():
                if full_dir.has_key(word):
                        full_dir[word]= full_dir[word] +word_list[word]
                else:
                        full_dir[word] = word_list[word]
        return full_dir

 


if __name__ == "__main__":
        start = time.time()
        start1 = time.clock()
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
        full_dir={}
        for input_file in os.listdir(input_dir):                
                input_path = os.path.join(input_dir,input_file)
                output_path = os.path.join(output_dir,input_file)
                files=open(input_path)
                soup= BeautifulSoup(files,'html.parser') #BeautifulSoup is used for parsing the html documents          
                output_path=output_path[:10]+'.txt' #Create output files to write the tokenized content into
                output_file=open(output_path,"w")

                content=soup.get_text().encode('ascii','replace') #Extracting only text content without html tags
                content = re.sub('[^0-9a-zA-Z]+', ' ', content)#handles special characters

                tokens=nltk.word_tokenize(content) #returns a list with tokenized words from each html document
                tokenized_words='\n'.join(tokens)               
                output_file.write(tokenized_words) #Write tokenized content into respective output files
                
                word_list = word_freq(tokens) #function to calculate frequency of words
                full_dir = join_dir(full_dir,word_list) #function to update a directory with words from all input files
        
        token_output = os.path.join(output_dir,"token_sort.txt") #Creates text file name to wrtie the results sorted by tokens
        t_output=open(token_output, "w")

        for item in sorted(full_dir):
                t_output.write("%s %s \n"%(item,full_dir[item])) #Write contents sorted by tokens

        frequency_output = os.path.join(output_dir,"freq_sort.txt")#Creates text file name to wrtie the results sorted by frequency
        f_output = open(frequency_output, "w")

        for (key,value) in sorted(full_dir.iteritems(), key=lambda(k,v):(-v,k)):
                f_output.write("%s %s \n"%(key,value)) #write contents sorted by frequency of each word

        end= time.time()
        end1 = time.clock()
        print("System time = %s"%(end - start))
        print("Elapsed time = %s"%(end1 - start1))
                

                
