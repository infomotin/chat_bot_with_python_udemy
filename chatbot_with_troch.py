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
CUDA = torch.cuda.is_available()
device = torch.device("cuda" if CUDA else "cpu")
lines_filepath = os.path.join("New folder","movie_lines.txt") 
movie_conversations_filepath = os.path.join("New folder","movie_conversations.txt")
with open(lines_filepath,'r') as file:
    lines = file.readlines()
for line in lines[:8]:    
    print(line.strip())
line_fields = ["lineId","characterId","moviID","chractor","text"]
lines = {}
with open(lines_filepath,'r',encoding='iso-8859-1') as f:    
    for line in f:        
        values = line.split(" +++$+++ ")        
        lineObj = {}
        for i,field in enumerate(line_fields):            
            lineObj[field] = values[i]
            lines[lineObj["lineId"]] = lineObj            
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
qu_pair = []
for conversation in conversations:
    for i in range(len(conversation["lines"])-1):
        inputline = conversation["lines"][i]["text"].strip()
        targetline = conversation["lines"][i+1]["text"].strip()
        if inputline and targetline:
            qu_pair.append([inputline,targetline])
datafile = os.path.join("New folder","formated_movie_lines.txt")
delimiter = '\t'
delimiter = str(codecs.decode(delimiter,"unicode_escape"))
print("Written A New CSV ans And Quations File ")
with open(datafile,'w',encoding="utf-8") as outfile:
    write = csv.writer(outfile,delimiter=delimiter)
    for pait in qu_pair:
        write.writerow(pait)
print("Writer Sunsscd!!!")
datafile = os.path.join("New folder","formated_movie_lines.txt")
with open(datafile,'rb') as file:
    lines = file.readlines()
for line in lines[:10]:
    print(line)
PAD_token = 0 
SOS_token = 1 
EOS_token = 2
class Vocabulary:
    def __init__(self,name):
        self.name = name
        self.word2index = {}
        self.word2count = {}
        self.index2word = {PAD_token:"PAD", SOS_token:"PAD",EOS_token:"EOS"}
        self.num_words = 3
    def addSentence(self,sentence):
        for word in sentence.split(' '):
            self.addWord(word)
    def addWord(self,word):
        if word not in self.word2index:
            self.word2index[word] = self.num_words
            self.word2count[word] = 1 
            self.index2word[self.num_words] = word
        else:
            self.word2count[word] += 1
    def trim(self,min_count):
        keep_words =[]
        for k,v in self.word2count.items():
            if v >= min_count:
                keep_words.append(k)
        print('keep words {}/{} = {:.4f}'.format(len(keep_words),len(self.word2index),len(keep_words)/len(self.word2index)))
        self.name = name
        self.word2index = {}
        self.word2count = {}
        self.index2word = {PAD_token:"PAD", SOS_token:"PAD",EOS_token:"EOS"}
        self.num_words = 3
        for word in keep_words:
            self.addWord(word)
def uniCode2ASCII(s):
    return ''.join(c for c in unicodedata.normalize('NFD', str(s)) if unicodedata.category(c) !='Mn')

def normalizeString(s):
    s = uniCode2ASCII(s.lower().strip())
    s = re.sub(r"([.!?])",r" \1",s)
    s = re.sub("r[^a-zA-Z.!?]+",r" ",s)
    s = re.sub(r"\s+",r" ",s).strip()
    return s

datafile = os.path.join("New folder","formated_movie_lines.txt")
print("Reading Data and Processing -----------")   
lines = open(datafiel,encoding='utf-8').read().strip().split('\n')
pairs = [[normalizeString(s) for s in pair.split('\t') for pair in lines]]
print("OK")


voc = Vocabulary("New folder")
