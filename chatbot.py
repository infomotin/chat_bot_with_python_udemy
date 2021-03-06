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
#create Encoder rnn layer
def encoder_rnn(rnn_input,rnn_size,num_layers,keep_prob,sequence_length):
    lstm = tf.contrib.rnn.BasicLSTMCell(rnn_size)
    lstm_dropout = tf.contrib.rnn.DropoutWrapper(lstm,input_keep_prob=keep_prob)
    encoder_cell = tf.contrib.rnn.MultiRNNCell([lstm_dropout]*num_layers)
    encoder_output, encoder_state = tf.nn.bidirectional_dynamic_rnn(cell_fw=encoder_cell,
                                                                    cell_bw=encoder_cell,
                                                                    sequence_length=sequence_length,
                                                                    inputs=rnn_input,
                                                                    dtype=tf.float32)
    return encoder_state 
#decoder tranning Set 
def decode_training_set(encoder_state,decoder_cell,decoder_embedded_input,sequence_length,decoder_scope,output_fun,keep_prob,batch_size):
    attention_states = tf.zeros([batch_size,1,decoder_cell.output_size])
    attention_keys,attention_values,attention_score_fun,attention_construct_function=tf.contrib.seq2seq.prepare_attention(attention_states,
                                                                                                                            attention_options = 'bahdanau',
                                                                                                                            num_units=decoder_cell.output_size)

    training_decoder_function = tf.contrib.seq2seq.attention_decoder_fn_train(encoder_state[0],
                                                                                attention_keys,
                                                                                attention_values,
                                                                                attention_score_fun,
                                                                                attention_construct_function,
                                                                                name = "attn_dec_train"        
                                                                                        )
    decoder_output,decoder_final_state,decoder_fianl_context_state = tf.contrib.seq2seq.dynamic_rnn_decoder(decoder_cell,
                                                                                                    training_decoder_function,
                                                                                                    decoder_embedded_input,
                                                                                                    sequence_length,
                                                                                                    scope = decoder_scope)  
    decoder_output_dropout = tf.nn.dropout(decoder_output,keep_prob)  
    return output_fun(decoder_output_dropout)  
#decode test validations Set
def decode_test_set(encoder_state,decoder_cell,decoder_embedding_matrix,sos_id,eos_id,maximum_length,num_words,sequence_length,decoder_scope,output_fun,keep_prob,batch_size):
    attention_states = tf.zeros([batch_size,1,decoder_cell.output_size])
    attention_keys,attention_values,attention_score_fun,attention_construct_function=tf.contrib.seq2seq.prepare_attention(attention_states,
                                                                                                                            attention_options = 'bahdanau',
                                                                                                                            num_units=decoder_cell.output_size)

    test_decoder_function = tf.contrib.seq2seq.attention_decoder_fn_inference(  output_fun,
                                                                                encoder_state[0],
                                                                                attention_keys,
                                                                                attention_values,
                                                                                attention_score_fun,
                                                                                attention_construct_function,
                                                                                decoder_embedding_matrix,
                                                                                sos_id,
                                                                                eos_id,
                                                                                maximum_length,
                                                                                num_words,
                                                                                name = "attn_dec_inf"        
                                                                                        )
    test_predictions,decoder_final_state,decoder_fianl_context_state = tf.contrib.seq2seq.dynamic_rnn_decoder(decoder_cell,
                                                                                                    test_decoder_function,
                                                                                                    
                                                                                                    scope = decoder_scope)  
    #decoder_output_dropout = tf.nn.dropout(decoder_output,keep_prob)  
    #return output_fun(decoder_output_dropout)
    return test_predictions

#decoder RNN Create 
def decder_rnn(decoder_embedded_input,decoder_embedding_matrix,encoder_state,num_words,sequence_length,rnn_size,num_layers,word2int,keep_prob,batch_size):
    with tf.variable_scope("decoding") as decoding_scope:
        lstm = tf.contrib.rnn.BasicLSTMCell(rnn_size)
        lstm_dropout = tf.contrib.rnn.DropoutWrapper(lstm,input_keep_prob=keep_prob)
        decoder_cell = tf.contrib.rnn.MultiRNNCell([lstm_dropout]*num_layers)
        weights = tf.truncated_normal_initializer(stddev=0.1)
        biases = tf.zeros_initializer()
        output_fun = lambda x: tf.contrib.layers.fully_connected(x,
                                                                num_words,
                                                                None,
                                                                scope = decoding_scope,
                                                                weights_initializer=weights,
                                                                biases_initializer=biases)
        training_predictions = decode_training_set(encoder_state,
                                                    decoder_cell,
                                                    decoder_embedded_input,
                                                    sequence_length,
                                                    decoding_scope,
                                                    output_fun,
                                                    keep_prob,
                                                    batch_size
                                                    )
        decoding_scope.reuse_variables()
        test_predictions = decode_test_set(encoder_state,
                                            decoder_cell,
                                            decoder_embedding_matrix,
                                            word2int['<SOS>'],
                                            word2int['<EOS>'],
                                            sequence_length-1,
                                            num_words,
                                            decoding_scope,
                                            output_fun,
                                            keep_prob,
                                            batch_size
                                            )

                                            # sos_id,eos_id,maximum_length,,sequence_length,decoder_scope,)
    return training_predictions,test_predictions
def seq2seq_model(inputs,targets,keep_prob,batch_size,sequence_length,answers_num_words,questions_num_words,encoder_embedding_size,decoder_embedding_size,rnn_size,num_layers,questionswords2int):
    encoder_embedding_input = tf.contrib.layers.embed_sequence(inputs,
                                                                answers_num_words+1,
                                                                encoder_embedding_size,
                                                                initializer = tf.random_uniform_initializer(0,1)
                                                                        )
    encoder_state = encoder_rnn(encoder_embedding_input,rnn_size,num_layers,keep_prob,sequence_length)
    preprocess_targets = preprocess_targets(targets,questionswords2int,batch_size)  
    decoder_embedding_matrix = tf.Variable(tf.random_uniform([questions_num_words+1,decoder_embedding_size],0,1))                                                                      
    decoder_embedded_input = tf.nn.embedding_lookup(decoder_embedding_matrix,preprocess_targets)
    training_predictions,test_predictions = decoder_rnn(decoder_embedded_input,
                                                        decoder_embedding_matrix,
                                                        encoder_state,
                                                        questions_num_words,
                                                        sequence_length,
                                                        rnn_size,
                                                        num_layers,
                                                        questionswords2int,
                                                        keep_prob,
                                                        batch_size
                                                        )
    return training_predictions,test_predictions
# training seq2seq_model

#setup hyperrameting 

epochs = 100
batch_size =64
rnn_size = 512
num_layers =3
encoding_embedding_size = 512
decoding_embedding_size = 512
learning_rate = 0.01
learning_rate_decay = 0.9
min_learning_rate = 0.0001
keep_probability = 0.5

#tf session 
ops.reset_default_graph()
import tensorflow.compat.v1 as tfc
session = tfc.InteractiveSession()
#loding Model inputs 
inputs, targets, learning_rate ,keep_prob =  model_inputs()
#setting The sequence length 
sequence_length = tf.placeholder_with_default(25, None, name='sequence_length')
