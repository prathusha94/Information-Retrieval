""" Author :Prathusha JS Naidu 
Homework 1 : CMSC 676 """

import os
import sys
from bs4 import BeautifulSoup
import nltk
import re
import codecs
from collections import Counter
from collections import OrderedDict
import time
import math


def tokenize_data(input_path):
        files=codecs.open(input_path,encoding='utf-8',errors='ignore')
        file_data = BeautifulSoup(files.read(),'html.parser').get_text()#BeautifulSoup is used for parsing the html documents
                                
        data = re.sub('[^0-9a-zA-Z]+',' ', file_data)#handles special characters
        tokens=nltk.word_tokenize(data) #returns a list with tokenized words from each html document
        
        tokens=[item.lower() for item in tokens]
        tokens=[item for item in tokens if len(item)>1] ###### PREPROCESSING : Remove all words with length 1
        tokenized_words=[word for word in tokens if word not in stop_words] #####PREPROCESSING : Remove stop words
        return tokenized_words
        

def word_freq(tokens):
        new_dict = {}
        for (w,f) in Counter(tokens).items():
                new_dict[w]=f
        return new_dict


def join_dir(full_dir,word_list):
        for word in word_list.keys():
                if word in full_dir:
                        full_dir[word]= full_dir[word] +word_list[word]
                else:
                        full_dir[word] = word_list[word]
        return full_dir

def remove_words(temp_path):
#####PREPROCESING :  Remove words that occur only once in the entire corpus , i.e words with value =1
        temp_dict={}
        with open(temp_path) as file:
                for line in file:
                        (key,value)=line.split()
                        temp_dict[key]=value
        #print("Lenght before removing words appearing just once: %s"%len(temp_dict))
        check_dir=temp_dict.copy()
        new_dir=full_dir.copy()
        for a, b in new_dir.items():
                if check_dir.get(a) == 1:
                        del temp_dict[a]

        #print("Length after removing words appearing just once: %s \n"%len(temp_dict))
        return temp_dict


def calc_dnum(full_dir,temp_dict):
#Function to calculate the total number of documents each word appears in       
        dnum_list={}
        for a,b in temp_dict.items():
                if a in full_dir:
                        dnum_list[a]=v
                                
        return dnum_list

def BM25(temp_dict, length, dnum_list, doc_count,avg_dl):
        wt_dict={}     
        for k,v in temp_dict.items():
                term_freq=temp_dict[k]
                n=dnum_list[k]
                idf=math.log(doc_count/n)
                num=(int(term_freq)*(k1+1))
                denom=k1*(1-b+(b*(length/avg_dl)))
                bm25=idf*(num/(float(term_freq) + float(denom)))
                wt_dict[k]=round(bm25,2)
        
        return wt_dict



if __name__ == "__main__":
        start = time.time()
        start1 = time.clock()
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
        temp_dir = "temp"
        full_dir={}
        avg_dl=0
        doc_count=0
        k1=2
        b=0.75
        file=open("stoplist.txt","r") #Open the file with given list of stopwords
        stop_words=file.read() 
        stop_words=stop_words.split() #Convert the words from the file into a list 
        
        #os.listdir returns a list containing the names of all files in the  input directory/path mentioned
        for input_file in os.listdir(input_dir):
                input_path = os.path.join(input_dir,input_file)     
                temp_path = os.path.join(temp_dir,input_file)

                temp_path=temp_path[:8]+'.txt' #Create temperary files with the extension .txt
                temp_file=open(temp_path,"w") 

                tokens=tokenize_data(input_path) #Function to load data and tokenize each input file
                avg_dl+=avg_dl+len(tokens)
                doc_count+=1

                word_list = word_freq(tokens) #Function to calculate frequency of words

                #Write the tokenized words and their respective frequencies into a temperary file
                for (k,v) in word_list.items():
                        temp_file.write("%s  %s\n"%(k,v))
                       
                full_dir = join_dir(full_dir,word_list) #function to update a directory with words from all input files
                
        if(doc_count!=0):
                avg_dl=avg_dl/doc_count
        #Read each file from the temperary folder
        for temp_file in os.listdir(temp_dir):
                temp_path = os.path.join(temp_dir,temp_file)     
                output_path = os.path.join(output_dir,temp_file)

                temp_dict=remove_words(temp_path) #Function to remove words that appear only once in the entire corpus.
                
                dnum_list=calc_dnum(full_dir,temp_dict)
               
                term_wt=BM25(temp_dict,len(temp_dict),dnum_list,doc_count, avg_dl)

                #print(term_wt)
                output_file=open(output_path,"w")
                for (k,v) in term_wt.items():
                        output_file.write("%s %s\n"%(k,v))
                
        
        end= time.time()
        end1 = time.clock()
        print("System time = %s"%(end - start))
        print("Elapsed time = %s"%(end1 - start1))
        
