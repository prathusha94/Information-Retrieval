""" Author :Prathusha JS Naidu 
Homework 5 : CMSC 676 """

import os
import sys
from bs4 import BeautifulSoup
import nltk
import re
import codecs
import argparse
from operator import itemgetter
from collections import Counter
from collections import OrderedDict
from collections import defaultdict
import time
import math
from copy import deepcopy
import pandas as pd
from itertools import islice

nested_dict={}
global_dir={} ##Total number of times a word appears in the entire corpus (including the number of times a word appears within each document)
global_wordlist={} ## Total number of documents containing a particular word
k1=2
b=0.75
term_dict={}
cluster_list={}
sim_flag=[] #Indicates if a cluster is active or not
similarity_matrix=defaultdict(dict)


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
########Calculates term weights using the BM25 formula #########
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

def calculate_similarity(doc1,doc2):
########## Constructs Similarity score matrix ###################
        norm_doc1=math.sqrt(sum(v*v for v in doc1.values()))
        norm_doc2=math.sqrt(sum(v*v for v in doc2.values()))
        common_keys = doc1.keys() & doc2.keys()
        cos_similarity = sum(doc1[k] * doc2[k] for k in common_keys)/(norm_doc1 * norm_doc2)
        return cos_similarity

def num_active_cluster(flag):
###### returns the number of active clusters ######
        active_clusters = [c for c in flag.keys() if flag[c]==1]
        return len(active_clusters)

def calculate_highest_sim():
##### Returns documents with highest similarity score #####
        high=0
        result=(high,0,0)
        for d1 in similarity_matrix.keys():
                for d2 in similarity_matrix[d1].keys():
                        if(d1!=d2):
                                if(sim_flag[d1]==1 and sim_flag[d2]==1):
                                        if(similarity_matrix[d1][d2]>high):
                                                high=similarity_matrix[d1][d2]
                                                result=(high,d1,d2)
        return result

def calculate_lowest_sim():
##### Returns documents with lowest similarity score #####
        low=1
        result=(low,0,0)
        for d1 in similarity_matrix.keys():
                for d2 in similarity_matrix[d1].keys():
                        if(d1!=d2):
                                if(sim_flag[d1]==1 and sim_flag[d2]==1):
                                        if(similarity_matrix[d1][d2]<low):
                                                low=similarity_matrix[d1][d2]
                                                result=(low,d1,d2)
        return result


def group_average_link(new_cluster,c):
        
        avg=0
        if isinstance(c, str):
                current_cluster=[(c)]
        else:
                current_cluster = cluster_list[c]
        n1=len(current_cluster)
        n2=len(cluster_list[new_cluster])
        for doc1 in range(1,n1+1):
                for doc2 in range(1,n2+1):
                        if doc2 in similarity_matrix[doc1].keys():
                                avg=avg+similarity_matrix[doc1][doc2]
                                
                        else:
                                avg=avg+similarity_matrix[doc2][doc1]

        avg=avg/(n1+n2)
        return avg



if __name__ == "__main__":
        parser=argparse.ArgumentParser()
        parser.add_argument("Input", help="Input file")
        parser.add_argument("Output",help="Output file")
        args=parser.parse_args()

        file=open("stoplist.txt","r") #Open the file with given list of stopwords
        stop_words=file.read() 
        stop_words=stop_words.split() #Convert the words from the file into a list
      
        input_dir = args.Input #Stores input directory passed as first argument
        #os.listdir returns a list containing the names of all files in the  input directory/path mentioned
        for input_file in os.listdir(input_dir):
                input_path = os.path.join(input_dir,input_file)
                tokens=tokenize_data(input_path) #Function to load data and tokenize each input file
        

        removed_dict={} #Stores result of removal of all words that appearonly once in the entire dictionary.
        avg_dl=0
        doc_count=0        
        sim_flag={}
        
                
        removed_dict=remove_words() 
        
        doc_count=len(nested_dict)
        for ID,word in removed_dict.items():
                avg_dl+=len(removed_dict[ID])
        avg_dl=avg_dl/doc_count

        for ID,word in removed_dict.items(): ## Constructs term dictionary matrix
                term_wt=BM25(word,doc_count, avg_dl)
                term_dict[ID]=term_wt

        doc_list=[]
        for ID in term_dict.keys():
                doc_list.append(ID)
        sorted(doc_list)

        
        ##Construct similarity matrix from term document matrix
        ##Sim_flag denotes which documents/clusters are active
        for i in range(0,doc_count):
                for j in range(i,doc_count):                        
                        similarity_matrix[j+1][i+1]=calculate_similarity(term_dict[doc_list[i]],term_dict[doc_list[j]])
                sim_flag[i+1]=1
                cluster_list[int(doc_list[i])]=doc_list[i] ##Initialise singleton clusters
            
        
        ## Creation and merging of new clusters
        new_cluster=doc_count+1
        output="Clustering documents : \n"
        least_similar,low_c1,low_c2=calculate_lowest_sim()
        print(least_similar,low_c1,low_c2)
        while(num_active_cluster(sim_flag)>1):
                highest_sim, cluster1, cluster2 = calculate_highest_sim()
                print(highest_sim)
                sim_flag[cluster1]=-1
                sim_flag[cluster2]=-1
                output+="%s  %s ------>%s \n"%(cluster1,cluster2,new_cluster)
                cluster_list[new_cluster]=(cluster1,cluster2)
                sim_flag[new_cluster]=1
                for c,flag in sim_flag.items():
                        if(flag==1):
                                similarity_matrix[new_cluster][c]=group_average_link(new_cluster,c)
                new_cluster+=1


        output_dir=args.Output
        output_path=os.path.join(output_dir,"Output")+'.txt'
        output_file=open(output_path,"w")
        output_file.write(output)

        
        
        
        
