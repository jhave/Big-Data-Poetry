#!/usr/bin/python
# -*- coding: utf-8 -*-


'''Example script to generate text from 18mb Poetry Foundation corpus.

NOTE: testing on smaller corpus recommended

BASED on Keras examples: https://github.com/fchollet/keras/blob/master/examples/lstm_text_generation.py

BACKGROUND INFO: for a clear detailed simple description of how and why this method works, see http://ml4a.github.io/guides/recurrent_neural_networks/

At least 20 epochs are required before the generated text
starts sounding coherent.

'''

from __future__ import print_function
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file

import numpy as np
import random
import sys

import datetime

#
#  Source TEXT
#
path = '../TXTS/MITPressDRAFT.txt'
path_id=path.split("/")[-1].split('.')[0]
print ('Path id: ',path_id)
text = open(path).read()#.lower()

chars = sorted(list(set(text)))
print("SOURCE text: ",path)
print('Total chars:', len(chars))
print('Corpus length:', len(text))

#
# CLEANUP : TO BE IMPROVED: preserve lineation within network ... ?
# 
junk= ['\u2003','\x97', '\xa0', '{', '|', '}', '~', '\x97', '\xa0', '¡', '¢', '£', '¤', '\xad', '°', '´', '·', '¿', 'À', 'Á', 'Æ', 'Ç', 'È', 'É', 'Ë', 'Í', 'Î', 'Ó', 'Ú', 'ß', 'à', 'á', 'â', 'ã', 'ä', 'å', 'æ', 'ç', 'è', 'é', 'ê', 'ë', 'ì', 'í', 'î', 'ï', 'ð', 'ñ', 'ò', 'ó', 'ô', 'ö', 'ø', 'ù', 'ú', 'û', 'ü', 'ý', 'þ', 'ÿ', 'ā', 'ć', 'č', 'ē', 'ę', 'Ł', 'ł', 'ō', 'ő', 'œ', 'ř', 'Ş', 'ş', 'Š', 'š', 'ū', 'ź', 'Ż', 'ż', 'Ž', 'ž', 'ʻ', '˚', '̀', '́', '̃', '̈', '̧', 'Γ', 'Λ', 'Ο', 'Χ', 'ά', 'έ', 'ί', 'α', 'β', 'γ', 'δ', 'ε', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'ς', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω', 'ό', 'ύ', 'Ϯ', '\u2009', '\u200a', '–', '—', '‘', '’', '‚', '“', '”', '•', '…', '\u2028', '™', '⅔', '↔', '≈', '≠', '⌒', '●', '♂', '♥', '未', '艾', '言', 'ﬁ', 'ﬂ', '\ufeff', '�','****!****', '~~~~!~~~','̊', '_', 'ϯ', 'Ü'] 
for char in junk:     
	text = text.replace(char,"")

text = "\n".join([txt_i 
	for txt_i in text.replace('\t', '  ').split('\n')
	if len(txt_i)])

# print("After cleanup:",len(text), "first 200 characters:")
# print(text[:300])

chars = sorted(list(set(text)))
print(" ".join([ch[0] for ch in chars]))
print('After cleanup total chars:', len(chars))
print('Corpus length:', len(text))


words = list(text.split(' '))
counts = {word_i: 0 for word_i in words}
for word_i in text.split(' '):
	counts[word_i] += 1

#counts
#print([(word_i, counts[word_i]) for word_i in sorted(counts, key=counts.get, reverse=True)])
#print(" ".join([word_i for word_i in sorted(counts, key=counts.get, reverse=True)]))



	#
	# MODEL 
	#

	char_indices = dict((c, i) for i, c in enumerate(chars))
	indices_char = dict((i, c) for i, c in enumerate(chars))


	# how much text to make
	num_nodes=256
	generated_SIZE=800
	batch_size = 60
	learning_rate = 0.001

	# cut the text in semi-redundant sequences of maxlen characters
	maxlen = 60
	step = 3

	sentences = []
	next_chars = []

	for i in range(0, len(text) - maxlen, step):
		sentences.append(text[i: i + maxlen])
		next_chars.append(text[i + maxlen])
	print('nb sequences:', len(sentences))

	print('Vectorization...')
	X = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
	y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
	for i, sentence in enumerate(
		sentences):
		for t, char in enumerate(sentence):
			X[i, t, char_indices[char]] = 1
		y[i, char_indices[next_chars[i]]] = 1


	# build the model: a single LSTM
	print('Build model...')
	model = Sequential()
	model.add(LSTM(num_nodes, input_shape=(maxlen, len(chars)), return_sequences=True))
	#model.add(Dropout(0.8))
	model.add(LSTM(num_nodes))
	#model.add(Dropout(0.8))
	model.add(Dense(len(chars)))
	model.add(Activation('softmax'))

	optimizer = RMSprop(learning_rate)
	model.compile(loss='categorical_crossentropy', optimizer=optimizer)

	#
	# SAVE STATE of model
	#

	# serialize model to JSON
	model_json = model.to_json()
	model_js_fn = "../MODELS/"+datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')+"_keras_lstm_MODEL_"+path_id+".json"
	with open(model_js_fn, "w") as json_file:
		json_file.write(model_json)
	print("Saved model JSON to disk:"+model_js_fn) 


	# TEMPERATURE
	def sample(preds, temperature=0.1):
		# helper function to sample an index from a probability array
		preds = np.asarray(preds).astype('float64')
		preds = np.log(preds) / temperature
		exp_preds = np.exp(preds)
		preds = exp_preds / np.sum(exp_preds)
		probas = np.random.multinomial(1, preds, 1)
		return np.argmax(probas)

	# train the model, output generated text after each iteration
	for iteration in range(1, 1000):
		
		start_index = random.randint(0, len(text) - maxlen - 1)
		sentence = text[start_index: start_index + maxlen]

		print() 
		output_TXT=''
		output_TXT = 'Source: '+path_id+'\n\nDate: '+datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')+'\n\nBatch_size: '+str(batch_size)+'\n\nnum_nodes: '+str(num_nodes)+'\ngenerated_SIZE: '+str(generated_SIZE)+'\nmaxlen: '+str(maxlen)+'\nstep: '+str(step)+'\n\nlearning_rate: '+str(learning_rate)+'\n\n---------- Generating with seed: \"' + sentence + '\"'
		print(output_TXT)

		print()
		print('-' * 50)
		print('Iteration', iteration)

		model.fit(X, y, batch_size=batch_size, nb_epoch=1)

		for diversity in [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2]:

			print('\n----- diversity:', diversity)

			generated = ''
			
			for i in range(generated_SIZE):
				x = np.zeros((1, maxlen, len(chars)))
				for t, char in enumerate(sentence):
					x[0, t, char_indices[char]] = 1.

				preds = model.predict(x, verbose=0)[0]
				next_index = sample(preds, diversity)
				next_char = indices_char[next_index]

				generated += next_char
				sentence = sentence[1:] + next_char

				sys.stdout.write(next_char)
				sys.stdout.flush()
			print()

			output_TXT += '----- diversity:'+str(diversity)+'\n\n'
			output_TXT += generated+'\n\n'

		# 
		# SAVE TXT output
		#
		txt_fn = "../GENERATED/"+datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')+"_keras_lstm_"+path_id+"_"+str(iteration)+".txt"
		f_txt=open(txt_fn,'w')
		f_txt.write(output_TXT)       
		f_txt.close(); 

		print ('\n\nSaving ', txt_fn) 

		# serialize weights to HDF5
		model_fn = "../MODELS/"+datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')+"_keras_lstm_WEIGHTS_"+path_id+"_"+str(iteration)+".h5"
		model.save_weights(model_fn)
		print("Saved model WEIGHTS to disk:"+model_fn) 



