#importing Basic laibray for chatbot 

import numpy as np 
import tensorflow as tf
import time 
import re

#data reding 
lines = open('movie_lines.txt',encoding="utf-8", errors="ignore").read().split('\n')
conversations = open('movie_conversations.txt',encoding="utf-8", errors="ignore").read().split('\n')
#create a data set

id2line = {}

for line in lines:
    _line = line.split(' +++$+++ ')
    if len(_line) == 5:
        id2line[_line[0]]= _line[4]
conversations_ids = []

for conversation in conversations[:-1]:
    _conversation = conversation.split(' +++$+++ ')[-1][1:-1].replace("'","").replace(" ","")
    conversations_ids.append(_conversation.split(','))

#splace qu and ans 
qu = []
ans = []

for conversation in conversations_ids:
    for i in range(len(conversation)-1):
        qu.append(id2line[conversation[i]])
        ans.append(id2line[conversation[i+1]])
#cleaing qu and ans func

def clean_text(text):
    text = text.lower()
    text = re.sub(r"i'm","i am",text)
    text = re.sub(r"he's","he is",text)
    text = re.sub(r"she's","she is",text)
    text = re.sub(r"that's","that is",text)
    text = re.sub(r"what's","what is",text)
    text = re.sub(r"where's","where is",text)
    text = re.sub(r"\'ll"," will",text)
    text = re.sub(r"\'ve"," have",text)
    text = re.sub(r"\'re"," are",text)
    text = re.sub(r"\'d"," would",text)
    text = re.sub(r"won't","will not",text)
    text = re.sub(r"can't","can not",text)
    text = re.sub(r"won't","will not",text)
    text = re.sub(r"[-()\"$#/:;<>{}_+=|~^*&.?,]","",text)
    return text

#cleaning qu and ans

clean_qu = []
clean_ans = []
for qu1 in qu:
    clean_qu.append(clean_text(qu1))
for ans1 in ans:
    clean_ans.append(clean_text(ans1))
#create a dic for eatch sentences in word
word2count = {}
for an in clean_ans:
    for word in an.split():
        if word not in word2count:
            word2count[word]=1
        else:
            word2count[word] +=1
for qu in clean_qu:
    #print(type(qu))
    for word in qu.split():
        if word not in word2count:
            word2count[word]=1
        else:
            word2count[word] +=1

#crete a dic for questions word 
threshold = 20
questionword2int = {}
word_num = 0
for word,count in word2count.items():
    if count >= threshold:
        questionword2int[word] = word_num
        word_num +=1
answord2int = {}
word_num = 0
for word,count in word2count.items():
    if count >= threshold:
        answord2int[word] = word_num
        word_num +=1
#adding Token 
tokens = ['<PAD>','<EOS>','<OUT>','<SOS>']
for token in tokens:
    questionword2int[token] = len(questionword2int)+1
    #questionword2int[token] = len()
for token in tokens:
    answord2int[token] = len(answord2int)+1
    #questionword2int[token] = len()
