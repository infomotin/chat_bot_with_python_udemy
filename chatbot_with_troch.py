
import torch
import torch.nn as nn
from torch import optim as optim
import torch.nn.functional as F
import csv
import random
import re
import os
import unicodedata
import codecs
import itertools
#chacking CUDA GPU is avalabe

CUDA = torch.cuda.is_available()
device = torch.device("cuda" if CUDA else "cpu")

#importing Training Data from text file 
lines_filepath = os.path.join("New folder","movie_lines.txt") #using folder for join os functions 
movie_conversations_filepath = os.path.join("New folder","movie_conversations.txt")
with open(lines_filepath,'r') as file:
    lines = file.readlines()#read text file in every line 
for line in lines[:8]:#just Show 8 line data 
    
    print(line.strip())
#Now describe eatch line data set 
#L1045 +++$+++ u0 +++$+++ m0 +++$+++ BIANCA +++$+++ They do not!
#lineId        characterId  movieId  character text
line_fields = ["lineId","characterId","moviID","chractor","text"]
#now splite with file 
lines = {}

with open(lines_filepath,'r',encoding='iso-8859-1') as f: 
    #now f is object of text that are encodeing 
    #for loop to acces every line 
    for line in f:
        #this type of data enhance and adding key value on another dic file and enhance with line_fields  
        # single_row data # ['L666256', 'u9034', 'm616', 'VEREKER', "Colonel Durnford... William Vereker. I hear you 've been seeking Officers?\n"]
        values = line.split(" +++$+++ ")
        # print(value)
        #single row data object soting with lineobj = {}
        lineObj = {}
        for i,field in enumerate(line_fields):
            #lines 
            # i=0
            # lineId
            # 1
            # characterId
            # 2
            # moviID
            # 3
            # chractor
            # 4
            #now value of values[0] = L1045
            
            # print(i)
            # print(field)
            lineObj[field] = values[i]
            # print(lineObj)
            # lineObj = {'lineId': 'L167399', 'characterId': 'u4866', 'moviID': 'm324', 'chractor': 'SONNY'}
            lines[lineObj["lineId"]] = lineObj
            #print(lines)
            #one single line woth dic file that is 'L167399': {'lineId': 'L167399', 'characterId': 'u4866', 'moviID': 'm324', 'chractor': 'SONNY'}
        
        
#Now Working with this data type
# u0 +++$+++ u2 +++$+++ m0 +++$+++ ['L194', 'L195', 'L196', 'L197'] 
#charector 1id    charetor 2id  movie id  setof conversions ultacneId 

# so that as like movi 
conv_fields = ['charector1id','charector2id','moviID','conversID']
conversations =[]
with open(movie_conversations_filepath,'r',encoding='iso-8859-1') as f:
    for line in f:
        values = line.split(" +++$+++ ")
        convObj={}
        for i,field in enumerate(conv_fields):
            convObj[field]=values[i]
            
        lineIds = eval(convObj["conversID"])
        convObj["lines"] =[]
        for lineId in lineIds:
            convObj["lines"].append(lines[lineId])
        conversations.append(convObj)
        #{'charector1id': 'u0', 'charector2id': 'u2', 'moviID': 'm0', 'conversID': "['L194', 'L195', 'L196', 'L197']\n", 'lines': [{'lineId': 'L194', 'characterId': 'u0', 'moviID': 'm0', 'chractor': 'BIANCA', 'text': 'Can we make this quick?  Roxanne Korrine and Andrew Barrett are having an incredibly horrendous public break- up on the quad.  Again.\n'}, {'lineId': 'L195', 'characterId': 'u2', 'moviID': 'm0', 'chractor': 'CAMERON', 'text': "Well, I thought we'd start with pronunciation, if that's okay with you.\n"}, {'lineId': 'L196', 'characterId': 'u0', 'moviID': 'm0', 'chractor': 'BIANCA', 'text': 'Not the hacking and gagging and spitting part.  Please.\n'}, {'lineId': 'L197', 'characterId': 'u2', 'moviID': 'm0', 'chractor': 'CAMERON', 'text': "Okay... then how 'bout we try out some French cuisine.  Saturday?  Night?\n"}]}
#Excutind pair of secetence 
qu_pair = []
for conversation in conversations:
    for i in range(len(conversation["lines"])-1):
        inputline = conversation["lines"][i]["text"].strip()
        targetline = conversation["lines"][i+1]["text"].strip()
        if inputline and targetline:
            qu_pair.append([inputline,targetline])
# save this file
datafile = os.path.join("New folder","formated_movie_lines.txt")
demiliter = '\t'
#cleaing the ans and qu 
demiliter = str(codecs.decode(demiliter, "unicode_escape"))
# str(codecs.decode(
#     {P:f "))


# write a new csv file 
print("Written A New CSV ans And Quations File ")
with open(datafile,'w',encoding="utf-8") as outfile:
    write = csv.writer(outfile, delimiter=demiliter)
    for pait in qu_pair:
        write.writerow(pait)
print("Writer Sunsscd!!!")
