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
#create invers dic for  answord2int  invasces 

answord2word = {w_i:w for w,w_i in answord2int.items()}#key to value and value to key 
#add eos in every clanans string 
for i in range(len(clean_ans)):
    clean_ans[i] +=' <EOS>'
    # clean_ans[i] =' <EOS>'+clean_ans[i]


questions_to_int = []
for question in clean_qu:
    ints = []
    for word in question.split():
        if word not in questionword2int:
            ints.append(questionword2int['<OUT>'])
        else:
             ints.append(questionword2int[word])
    
    questions_to_int.append(ints)

answear_to_int = []
for ans in clean_ans:
    ints = []
    for word in ans.split():
        if word not in answord2int:
            ints.append(answord2int['<OUT>'])
        else:
             ints.append(answord2int[word])
    
    answear_to_int.append(ints)

#shorting questing and answear by the length of questions 
sorted_clean_questions = []
sorted_clean_answears = []
for length in range(1,25+1):
    for i in enumerate(questions_to_int):
        if len(i[1]) == length:
            sorted_clean_questions.append(questions_to_int[i[0]])
            sorted_clean_answears.append(answear_to_int[i[0]])


#Cretating Place Holder for input and the tergets 
def model_inputs():
    inputs = tf.placeholder(tf.int32,[None, None],name='input')
    targets = tf.placeholder(tf.int32,[None, None],name='target')
    learning_rate = tf.placeholder(tf.float32,name='learning_rate')
    keep_prob = tf.placeholder(tf.float32,name='keep_prob')
    return inputs,targets,learning_rate,keep_prob
#preprosessing Target
def preprocess_targets(targets,word2int,batch_size):
    left_side = tf.fill([batch_size,1],word2int['<SOS>'])
    right_side= tf.strided_slice(targets,[0,0],[batch_size,-1],[1,1])
    preprocessed_targets = tf.concat([left_side,right_side],1)
    return preprocessed_targets
