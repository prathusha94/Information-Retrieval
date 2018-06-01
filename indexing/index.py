""" Author :Prathusha JS Naidu 
Homework 3 : CMSC 676 """

import os
import sys
from bs4 import BeautifulSoup
import nltk
import re
import codecs
from collections import Counter
from collections import OrderedDict
from collections import defaultdict
import time
import math
from copy import deepcopy
import pandas as pd

nested_dict={}
global_dir={} ##Total number of times a word appears in the entire corpus (including the number of times a word appears within each document)
global_wordlist={} ## Total number of documents containing a particular word
k1=2
b=0.75
term_dict={}
def tokenize_data(input_path):
        name=input_path.split('.')[0]
        doc_id=name[6:]
        nested_dict[doc_id]={}
        files=codecs.open(input_path,encoding='utf-8',errors='ignore')
        file_data = BeautifulSoup(files.read(),'html.parser').get_text()#BeautifulSoup is used for parsing the html documents
                                
        data = re.sub('[^0-9a-zA-Z]+',' ', file_data)#handles special characters
        tokens=nltk.word_tokenize(data) #returns a list with tokenized words from each html document
        
        tokens=[item.lower() for item in tokens]
        tokenized_words=[word for word in tokens if word not in stop_words] #####PREPROCESSING : Remove stop words

        for (word,freq) in Counter(tokenized_words).items(): #Calculate word frequency of each word in a document
                        nested_dict[doc_id][word]=freq
        global global_dir                
        global_dir=join_dir(global_dir,nested_dict[doc_id]) 
        
        
        return tokenized_words
        

def join_dir(global_dict,word_list):
        for word in word_list.keys():
                if word in global_dict:
                        global_dict[word]= global_dict[word] +word_list[word]  
                        global_wordlist[word]+=1 
                else:
                        global_dict[word] = word_list[word]
                        global_wordlist[word]=1
        return global_dict

def remove_words():
#######PREPROCESING :  Remove words that occur only once in the entire corpus , i.e words with value =1
        temp_dict=deepcopy(nested_dict)       
        for ID,word in nested_dict.items():
                for k,v in word.items():
                        if global_dir.get(k)==1:
                                del temp_dict[ID][k]
        return temp_dict
                        
        

def BM25(local_dict,doc_count,avg_dl):
        wt_dict={}
        length=len(local_dict)
        for k,v in local_dict.items():
                term_freq=local_dict[k]
                n=global_wordlist[k]
                idf=math.log(doc_count/n)
                num=(int(term_freq)*(k1+1))
                denom=k1*(1-b+(b*(length/avg_dl)))
                bm25=idf*(num/(float(term_freq) + float(denom)))
                wt_dict[k]=round(bm25,2)
        
        return wt_dict

##def file_size(files):
##        mb=1024*1024
##        size=0
##        if type(files) is list:
##                for filename in file:
##                        size+=os.path.getsize(filename)       
##        else: 
##                size=os.path.getsize(files)
##
##        print(size)
##        return size/mb


if __name__ == "__main__":
        start = time.time()
        start1 = time.clock()
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
        removed_dict={}
        avg_dl=0
        doc_count=0
        
        file=open("stoplist.txt","r") #Open the file with given list of stopwords
        stop_words=file.read() 
        stop_words=stop_words.split() #Convert the words from the file into a list
        nested_dict={}
        
        #os.listdir returns a list containing the names of all files in the  input directory/path mentioned
        for input_file in os.listdir(input_dir):
                input_path = os.path.join(input_dir,input_file)
                tokens=tokenize_data(input_path) #Function to load data and tokenize each input file
                
##        input_size=file_size(os.listdir(input_dir))
        
##        print(len(nested_dict['001'])) ##Length of 1st document BEFORE removal of words occuring only once in the entire corpus
                
        removed_dict=remove_words() 
        
##        print(len(removed_dict['001']))##Length of 1st document AFTER removal of words occuring only once in the entire corpus
        
        doc_count=len(nested_dict)
        for ID,word in removed_dict.items():
                avg_dl+=len(removed_dict[ID])
        avg_dl=avg_dl/doc_count


        for ID,word in removed_dict.items():
                term_wt=BM25(word,doc_count, avg_dl)
                term_dict[ID]=term_wt
##        
##        matrix=pd.DataFrame(term_dict)
##        i=matrix.to_string(na_rep='0')
##        print(i)
        
        inverse=defaultdict(dict)
        for key1,value1 in term_dict.items():
                for key2,value2 in value1.items():
                        inverse[key2].update({key1: value2})

        posting_id=0
        postings="Doc Id \t Term weights \n"
        dictionary_file=" "
        dictionary=[]

        for word in inverse.keys():
                counter=0
                for ID in inverse[word].keys():
                        if(inverse[word][ID]!=0):
                                postings+="%s \t %0.03f \n"%(ID,inverse[word][ID])
                                counter+=1
                dictionary.append((word,counter,(posting_id+1)))
                posting_id+=counter
        
        output_path1=os.path.join(output_dir,"postings.txt")
        output_path2=os.path.join(output_dir,"dictionary.txt")
        output_file1=open(output_path1,"w")
        output_file2=open(output_path2,"w")

        output_file1.write(postings)
        dictionary.sort()
        dictionary_file +=''.join("\n%s" % '\n'.join(map(str, x)) for x in dictionary)
        output_file2.write(dictionary_file)
##        p_size=file_size(output_path1)
##        d_size=file_size(output_path2)
##        print("Input size = %d \n"%input_size)
##        print("Postings file size = %d \n"%p_size)
##        print("Dictionary file size = %d \n" %d_size)

        


        end= time.time()
        end1 = time.clock()
        print("System time = %s"%(end - start))
        print("Elapsed time = %s"%(end1 - start1))
        
