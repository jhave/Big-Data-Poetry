#! /usr/bin/env python

"""

MOodified from
https://github.com/shanbady/NLTK-Boston-Python-Meetup

Tangent#1 : generate a poem use synsets from nltk wordnet to replace all but stopwords
Goal: generate a set of poems from entire corpus.

1. 
Read in a .txt file poem

2.
For each poem: 

    Tokenize
    Find synsets
    Select replacement word

3. 
Write new poem to txt file in "generated/tangent1_synset/"


"""



from __future__ import division

from random import randint
from random import shuffle

from nltk_contrib.readability.textanalyzer import syllables_en
from nltk.corpus import cmudict,wordnet as wn
from nltk.corpus import stopwords
import nltk, re, pprint
from nltk import Text

WhitespaceTokenizer = nltk.WhitespaceTokenizer

import re
import os, datetime
import sys
import random
import string

import time


###############################
# Custom HELPER FUNCTIONs      #
###############################

import import_utilities




#
#  IMPORTANT : while testing change this dir
#

DATA_DIR  =  "../../../../../data/poetryFoundation/txt_ALL/"
# #  NOTE: "txt_6" directory contains only 6 files for testing
GENERATED_DIR  =  "../../../../../data/poetryFoundation/GENERATED/ELO_2015/poetryFoundation"+datetime.datetime.now().strftime('%Y-%m-%d_%H')+"/"

# add meronymns
# introduce a swearing shuffle
# brands array
# spice it up: porn & poetry terms (define a balancing term for that)



#
# RESERVOIR
# take all UNIQUE terms, that return no synset from wordnet
# store in a reservoir
# use to replace other words that are unique
#
# easier way than counting to extract a vocabulary of words specific to each corpus
#
# TODO: save trigram context of each RESERVOIR word, then utilize as lookup

RESERVOIR=["Jha"]

#
# LANGUAGE TEST using import_utilities.get_language(line) so that foreign language does not automatically get put into reservoir
#
l_thresh=2
xl_thresh=0
#only check ohhla for language after title, artist, album stuff
if "ohhla" in DATA_DIR.split("/")[-2] :
    l_thresh=6
else:
    xl_thresh=0

#################################################

labels_to_keep = ['Artist','Album','Song','Typed', 'VERSE','CHORUS']
personal_pronouns = ["i","me","we","us","you","she","her","he","him","it","they","them"]

weird_avoid=["Pine Tree State","sanguine","anapest","sidereal", "Supreme Being", "antediluvian" ]

# sample different segments of archive
break_cnt=0
break_cnt_min=9000
break_cnt_max=12000
#################################################
#                                               #
#    READ FILES                                 #
#                                               #
#################################################
for subdir, dirs, files in os.walk(DATA_DIR):
    for file in files:
        #print break_cnt,subdir+file

        break_cnt+=1
        if break_cnt<break_cnt_min:#and break_cnt>break_cnt_max:
            continue

        if ".txt" in file  and 'readme' not in file:
            html_file_number=file.split(".")[0]
            #print "\n******\nWORKING ON file",file#,"\nhtml_file_number",html_file_number
            # 
            # & PARSE POEM
            #
            cnt=0
            new_poem = ""
            quit_language=0
            url=""
            prev_word=""
           
            pf = open(subdir+file, 'rU')
            for line in pf:

                #print "\n"
                
                wordmap = []
                new_line=""
                replacement_word=""
                
                
                if cnt>=l_thresh and len(line) > 12 and "[" not in line and "english" not in import_utilities.get_language(line):
                    quit_language+=1
                    #print import_utilities.get_language(line), quit_language, "line:",line
                else:
                    if cnt>=6:
                        quit_language-=1
                    ##print "quit_language:",quit_language,"line:", line

                '''

KEEP

<pre>
Artist: Spice 1
Album:  1990-Sick
Song:   1-800 (Str8 from the Pen)
Typed by : Timo.Scheffler@allgaeu.org

                '''
                if "<a href='http:" in line:
                    url = line
                    # #print "url:",url

                elif '<pre>' not in line and '</pre >' not in line and '< /pre >' not in line:

                    # POS part-of-speech
                    line_pos_tags = nltk.pos_tag(line.strip(' \t\n\r').split(' '))
                    # # # #print "\n",line
                    # # # #print line_pos_tags



                    if len(line)>0:
                        new_line="\n"

                    cnt=cnt+1
                    #capitalize artist,album,song
                    label_idx=99
                    skip_line=False

                    # if line is not empty, push each word of line into array with syllable cnt
                    if len(line) > 1:

                        widx=0
                        # get each WORD
                        for word in line.strip(' \t\n\r').split(' '):

                            # scramble emails
                            if '@' in word:
                                word = ''.join(random.sample(word,len(word)))

                            # deal with end case
                            if '</pre>' in word:
                                word = word.split('</pre>')[0]

                            #####################################
                            # non-empty word, start replacement #
                            #####################################
                            if len(word)>0:

                                # # # #print word,"widx:",widx," line_pos_tags[widx][0]:",line_pos_tags[widx][0]," line_pos_tags[widx][1]:",line_pos_tags[widx][1]

                                # booleans that allow us to leave the VERSE CHORUS format
                                labelling=False
                                VC = False
                                
                                # if it's ALL punctuation, don't change it
                                if import_utilities.isAllPunct(word):
                                    new_line += word+' '
                                    # #print "import_utilities.isAllPunct new_line",new_line
                                # if it's numeric, shuffle it
                                elif import_utilities.hasNumbers(word):
                                    new_line += import_utilities.replaceNumbers(word)+' '
                                    # #print "import_utilities.replaceNumbers new_line",new_line
                                else:
                                    # is it Artist, Album, Song
                                    for ltk in labels_to_keep:
                                        if ltk in word:
                                            ## # #print 'found an ',ltk
                                            labelling = True
                                            label_idx=0

                                            if 'VERSE' in ltk or 'CHORUS' in ltk:
                                                ## # #print "skip this line"
                                                new_line += ltk+" "
                                                # #print "VERSE new_line",new_line
                                          
                                                skip_line=True
                                            else:
                                                replacement_word=ltk
                                                if 'Typed' not in ltk:
                                                    new_line += replacement_word+": "
                                                    # #print "Typed new_line",new_line
                                                else:
                                                    new_line += replacement_word+" "
                                                    # #print "else Typed new_line",new_line



                                    ###########################################################
                                    # REPLACEMENT of pronouns with compressed verb (as in I'd)#
                                    ###########################################################                
                                    if len(word.split("'"))>1:

                                        if word.split("'")[0] in personal_pronouns:
                                            replacement_word = random.choice(personal_pronouns)+"'"+word.split("'")[1]+' '
                                            # #print "COMPOSITE pronoun'verb word:'"+word+"'    replacement:",replacement_word

                                            new_line += replacement_word
                                            # #print "PRONOUNS new_line:",new_line

                                    ####################################################
                                    # Replacement of OTHERs                            #
                                    ####################################################

                                    elif not word.lower() in stopwords.words('english') and not labelling and not skip_line:

                                        # take off leading brackets, commas etc...
                                        word_punct_nopunct = import_utilities.strip_punctuation_bool(word)
                                        word_nopunct = word_punct_nopunct['word']
                                        word_punct = word_punct_nopunct['punct']
                                        punct_bool = word_punct_nopunct['punct_bool']

                                        #######################################################
                                        # MAIN EXCHANGE PROCESS CALL >>>>>>>   GET THE SYNSET #
                                        #######################################################    
                                        if word_nopunct[-4:].lower()=="here":
                                            similarterm=random.choice(import_utilities.heres)
                                        else:
                                            #print "WORD:",word_nopunct
                                            similarterm = import_utilities.find_synset_word(word_nopunct)#(word.lstrip().rstrip())

                                        
                                        ############################################
                                        # manually get rid of some terrible choices
                                        ############################################
                                        if similarterm == "ilk":
                                            ##print "like"
                                            similarterm = "like"
                                        if similarterm == "ope":
                                            ##print "doth"
                                            similarterm = "does"
                                        if similarterm =="Strategic Arms Limitation Talks":
                                            similarterm = random.choice(RESERVOIR) 

                                        for wa in weird_avoid:
                                            if similarterm == wa:
                                                similarterm = random.choice(RESERVOIR)             

                                        #######################################                      
                                        # abbreviations for fucking states!   #
                                        #######################################
                                        if word_nopunct.upper() in import_utilities.state_abbrev and word_nopunct.lower() not in stopwords.words('english') or word_nopunct.lower() is "me":
                                            tmp = similarterm
                                            if word_nopunct == "oh": 
                                                similarterm = random.choice(import_utilities.exclaims)
                                            else:
                                                similarterm = random.choice(RESERVOIR)
                                            #print word_nopunct," STATE replaced by", tmp, "replaced with:",similarterm, "in:",line

                                        ##############
                                        # hyphenated #
                                        ##############
                                        hyp =word.split("-")
                                        #print word,len(hyp)
                                        if len(hyp) >1:
                                            similarterm=""
                                            for w in hyp:
                                                if len(w) > 2:
                                                    similarterm +=  import_utilities.find_synset_word(w)+"-"
                                            similarterm = import_utilities.strip_underscore(similarterm[:-1])
                                            #print "hyphenated:",word,"replaced by: "+similarterm
                                                


                                        
                                        #########################################################    
                                        # is it a TRUNCATED VERB slang as in singin or wishin   #
                                        #########################################################
                                        if similarterm == word_nopunct and len(word)>2 and 'in' in word_nopunct[-2:]:
                                            similarterm = import_utilities.find_synset_word(word_nopunct+'g')
                                            ## #print "TRUNCATED SLANG word: '"+word+"'",similarterm
                                            interim = import_utilities.lemma(similarterm)
                                            ## #print interim
                                            similarterm = import_utilities.conjugate(interim, tense=import_utilities.PARTICIPLE, parse=True)[:-1] 
                                            # # # #print word,"widx:",widx," line_pos_tags[widx][0]:",line_pos_tags[widx][0]," line_pos_tags[widx][1]:",line_pos_tags[widx][1]
                                           

                                        #################      
                                        # SWEAR WORD    #
                                        #################
                                        ##print "at the garden of if:", word
                                        if word_nopunct in import_utilities.curses:
                                            similarterm = random.choice(import_utilities.curses)
                                            ##print "SWEAR WORD word: '"+word+"'",similarterm


                                        if len(hyp) >1:
                                            replacement_word = similarterm
                                        else:
                                            replacement_word = word.replace(word_nopunct, similarterm)
                                            replacement_word = import_utilities.strip_underscore(replacement_word)
                                            replacement_word = import_utilities.replaceNumbers(replacement_word)

                                        if label_idx<2:
                                            replacement_word = ' '.join(word[0].upper() + word[1:] for word in replacement_word.split())
                                            ## # #print "CAPITALIZE",replacement_word

                                        #########################
                                        # RESERVOIR_OF_WEIRDNESS  #
                                        #########################   
                                        # #print "SINGULARS",import_utilities.singularize(word_nopunct)," repalced by",import_utilities.singularize(replacement_word)
                                        if word_nopunct.lower() in import_utilities.impera:
                                            replacement_word=random.choice(import_utilities.impera)
                                        elif word_nopunct.lower() in import_utilities.conjuncts:
                                            replacement_word=random.choice(import_utilities.conjuncts)
                                            #print word," CONJUNCTION replaced with",replacement_word
                                        elif word_nopunct.lower() in import_utilities.indef_prono:
                                            replacement_word=random.choice(import_utilities.indef_prono)
                                            #print word," INDEF_prono replaced with",replacement_word
                                        elif word_nopunct.lower() in import_utilities.prepo:
                                            replacement_word=random.choice(import_utilities.prepo)
                                            # print word," prepo replaced with",replacement_word
                                        elif word_nopunct.lower() in import_utilities.rel_prono:
                                            replacement_word=word
                                            # print word," rel_prono LEAVE alone: ",replacement_word
                                        elif word_nopunct.lower()[-2:] =="ly":
                                            replacement_word=import_utilities.strip_underscore(import_utilities.find_synset_word(word))#(word[:-2])
                                            #print word," ADVERB: ",replacement_word
                                            # if replacement_word[-2:] !="ly":
                                            #     replacement_word +="ly"
                                                                                    
                                        else:
                                            if len(hyp) <2 and "like" not in word_nopunct and import_utilities.singularize(word_nopunct) ==  import_utilities.singularize(replacement_word) and "english" in import_utilities.get_language(line):
                                                if word not in RESERVOIR and quit_language<0 and import_utilities.countPunctuation(word)<1 and word not in weird_avoid: 
                                                    
                                                    #print "add to RESERVOIR: ",import_utilities.countPunctuation(word),word
                                                    
                                                    #if word not in RESERVOIR:
                                                        #print word

                                                    RESERVOIR.append(word)

                                                replacement_word = random.choice(RESERVOIR)
                                            #print word,"  vs RESERVOIR  replacement_word:",replacement_word #,"    new_line:",new_line
                                        if quit_language>1:
                                            #print quit_language, "Probably foreign language: make a word salad in english"
                                            replacement_word = random.choice(RESERVOIR)
                                        

                                        # correct the plural or singular but first strip off punct again...replace after
                                        # word_punct_nopunct = import_utilities.strip_punctuation_bool(replacement_word )
                                        # word_nopunct = word_punct_nopunct['word']
                                        # word_punct = word_punct_nopunct['punct']
                                        # punct_bool = word_punct_nopunct['punct_bool']

                                        # replacement_word= import_utilities.pluralize_singularize(import_utilities.strip_punctuation( import_utilities.singularize(word_nopunct)),import_utilities.strip_punctuation( prev_word))
                                        new_line += replacement_word+" "
                                        # #print "BIG BLOCK new_line",new_line
                                        #print "MAIN word: '"+word+"' replacement: '"+replacement_word#+"' new_line:",new_line



                                    elif not labelling and not skip_line:
                                        if word.isalpha():
                                            #print "SAME?:",word
                                            #new_line += word+" "
                                            if not word.lower() in personal_pronouns :
                                                new_line += word+" "
                                                replacement_word=word
                                                # #print "skip STOP word: *"+word+"*","new_line:",new_line
                                            else:
                                                replacement_word = random.choice(personal_pronouns)
                                                # #print word+" random personal_pronouns: *"+replacement_word+"*"
                                                new_line += import_utilities.pluralize_singularize(replacement_word,prev_word)+" "
                                                # #print "else STOP new_line",new_line
                                        else:
                                              # # #print "verse GAP"
                                              new_line += "\n"
                                              # #print "GAP new_line",new_line

                                    prev_word = replacement_word
                            #else:
                                ## # #print len(line),"line break"
                                #new_line += "\n"

                                widx+=1


                                    



                    

                    #
                    #  POEM line + line ...
                    #  
                    # # #print new_line  +"\n\n*******"
                    new_poem += new_line

                    ## #print "\nLINE:",line,"NEW LINE:",new_line,"\n"
                    #print new_line#,"\n"



            # 
            # WRITE new POEM TO FILE
            #
            txt_fn = html_file_number+".txt"
            print "\n\n>>>>>>>>>\nTXT Filename: ", txt_fn.encode('utf-8')

            txt_fn_path = GENERATED_DIR+txt_fn
            # # #print "txt_fn_path: ",txt_fn_path.encode('utf-8')


            if not os.path.exists(GENERATED_DIR):
                os.makedirs(GENERATED_DIR)

            f=open(txt_fn_path,'w+')

            if url is not None:
                dp = url+new_poem
            else: 
                dp = new_poem

            f.write(dp)

            f.close();

            print new_poem
            time.sleep(5)
            

            #
            # SAVE THE RESERVOIR
            #

            txt_fn_path = GENERATED_DIR+"poetryFoundation_RESERVOIR.txt"
            if not os.path.exists(GENERATED_DIR):
                os.makedirs(GENERATED_DIR)

            f=open(txt_fn_path,'w+')

            dp = ' '.join(RESERVOIR)
            f.write(dp)

            f.close();


print "RESERVOIR:", ' '.join(RESERVOIR)

#print "\n\n****\n",new_poem







    

