#!/usr/bin/env python


import json
import os,sys,random, datetime

import import_utilities

from pprint import pprint
import re
import codecs

import nltk
from nltk.corpus import stopwords

personal_pronouns = ["i","me","we","us","you","she","her","he","him","it","they","them"]

import time
start_time = time.time()

import uuid
poem_id = uuid.uuid1()

from pattern.en import verbs, conjugate, PARTICIPLE
from pattern.en import parse
from pattern.en import article, referenced


######################################################
################## WHEN TESTING CHANGE THIS ##########
######################################################

type_of_run="All"

poem_style ="Creeley-Style"

######################################################
######################################################
######################################################


DATA_DIR  =  "../../data/poetryFoundation/"
GENERATED_DIR  =  "../../generated/poetryFoundation/"

READ_JSON_PATH = "../../json/ALCHEMY_POEMS_JSON_ALL/"

READ_TXT_PATH = "txt_poems_"+type_of_run+"/"

READ_LIST_PATH = DATA_DIR+"NLTK_POS_LISTS_poetryFoundation_POEMs.txt"

the_vowels = ["a","e","i","o","u"]

# adjectives (JJ), adverbs (RB), foreign words (FW), interjection (UH)
JJ = []
RB = []
FW = []
UH = []
VBD = []
VBZ = []

#################################################
#                                                 #
#   READ NLTK LISTS
#                                                 #
#################################################

list_data=open(READ_LIST_PATH).read()
LISTS_ls = list_data.split("=")
#print len(LISTS_ls)
RB=LISTS_ls[1].split(",")
JJ=LISTS_ls[3].split(",")
VBD=LISTS_ls[5].split(",")
VBZ=LISTS_ls[7].split(",")
#FW=LISTS_ls[9].split(",")
#UH=LISTS_ls[11].split(",")
authors=LISTS_ls[13].split(" ~!~ ")


rap_data=open("../../generated/ohhla/ohhla_reservoir.txt").read()
rap_mouth=rap_data.split(" ")
rap_mouth= list(set(rap_mouth))
rap_mouth.sort(key=len)

science_data=open("../../generated/generic/science.txt").read()
science_mouth=science_data.split(" ")
science_mouth=list(set(science_mouth))

poetry_data=open("../../generated/generic/2014-08-03_23_poetryFoundation_RESERVOIR_ALL.txt").read()
poetry_mouth=poetry_data.split(" ")
poetry_mouth=list(set(poetry_mouth))


print "Creeley-Style POEMS\n\nTechnical process: the following poems were produced using a 10,000+ corpus\nsent to Alchemy API to produce entity-recognition, POS, and sentiment reports.\nThat info influences replacement algorithms\nReplacement uses NLTK synsets and Pattern.en\nand a reservoir of words found in the corpus that do not have synonyms.\n\nAverage word-length is constrained so output reads like\nRobert Creeley becoming Samuel Beckett in Gertrude Stein's gut. \n\nLanguage: Python\nBlogged here: http://bdp.glia.ca/smaller-words-shrink-gapped\nModified for ELO performance, Bergen, Aug. 4th 2015\nCode on github: https://github.com/jhave/Big-Data-Poetry"


if type_of_run == "6":
    print "\n###############################\nWARNING used limited test data\n###############################\n\n"


# list of json files returned from Alchemy (without .DS_Store or system files)
json_files=[]
json_files_shuffled = []

# list of file names to be accessed randomly
for item in os.listdir(READ_JSON_PATH):
    if not item.startswith('.') and os.path.isfile(os.path.join(READ_JSON_PATH, item)):
        json_files.append(item)
random.shuffle(json_files)
json_files_shuffled = json_files

# list of other titles as source for making new titles
titles_ls=codecs.open(DATA_DIR+ "ALL_poetryFoundation_BIO_ALL_TITLES.txt",'r',encoding='utf-8').read().split(" !~*~! ")
for t in titles_ls:
    # import_utilities.strip_punctuation(t)
    if t.count(" ") > len(t)/2  or " , " in t:
        titles_ls.remove(t)
        # print "removing '"+t+"'"
    if t in import_utilities.stopwords_ls:
        titles_ls.remove(t)
        #print "removing '"+t+"'"

#print "len(titles_ls):",len(titles_ls)

keywords_dict = {}
concepts_dict = {}
entities_dicti = {}
relation_dict = {}

filenames = []

ALL_poems_intro = "<html xmlns='http://www.w3.org/1999/xhtml'><head>   <title>POEMs on BDP: Big-Data-Poetry</title><style type='text/css'>    body { margin: 40; padding: 20px; width: 85%; font: 14px Helvetica, Arial; }     table { border-collapse: collapse; }     form, td, p { margin: 20; padding: 0; } img { border: none; }  h4  { font: 18px ;}   a { color: #949494; text-decoration: none; } a:hover, .footer a { color: #2c2c2c; text-decoration: underline; }     a:focus { outline: none; }    .white { background: #fff; color: #000; } .black { background: #121212; color: #000; } .black a:hover, .black .footer a { color: #ddd; text-decoration: underline; } .header { padding: 70px 0 117px; position: relative;} .header, .footer { width: 750px; margin: 0 auto; } .body { width: 700px; margin: 20 auto; } .switcher { float: right; margin: 43px 0 0 0; cursor: pointer; } .switcher div { float: left; } .rss { float: right; margin-top: -53px;} </style> </head> <body class='white'> <table  width='70%' height='100%' border=0' align='center'> <tr><h1>$$cnt$$ <i>$$style$$</i> Poems</h1><h2>generated by <a href='http://bdp.glia.ca'/>bdp.glia.ca</a> in $$gentime$$ seconds on $$datetime$$</h2>" 
ALL_poems=ALL_poems_intro
bio=""

num_of_files = 0
cnt=0

# preliminare weird seeds
prelim_weird_seed="uncompacted, selfhood, seeth, rainbow, lexical, haloing, butterflies,terracotta, fountaining, unhoused, stripteasing, cramful, washpan, limekiln, imprisoned, sphered, gingham, incestuous, flax, circulation, teapots, jugular, viperish, bulldog, fingertips, hubcaps, cowlick, waterbed, maxed, chaliced, textual, dreamshovels, splint, highpoints, pulsebeat, foamline, ISP, USB"
RESERVOIR=[w for w in prelim_weird_seed.split(",")]

# single word poem list
# as they are put into RESERVOIR 
# they are also made into a poem
SMALL_POEM_ALL=ALL_poems_intro
SMALL_POEM=""
#################################################
#                                                 #
#   READ DIRECTORY    #
#                                                 #
#################################################
def extractFeaturesAndWritePoem(READ_PATH,file_type):
    
    

    global ALL_poems,bio,cnt,SMALL_POEM,SMALL_POEM_ALL

    inp=0
    sub_cnt=0
    words_total=0
    lines_total=0

    pause_every = 0

    for subdir, dirs, files in os.walk(READ_PATH):
        for file in files:

            if type_of_run == "ALL":
                random.shuffle(files)
            
            num_of_files = len(files)-1 # deduct the DS_store
            #print (num_of_files,'readDirectory',READ_PATH)
            
            if file_type in file  and 'readme' not in file:

                JSON_alchemy_loaded = False

                # ID
                id=file.split(".")[0]
                #print "\nID:",id.split("_")[1]

                filenames.append(id)
                cnt+=1

                # print('')
                # print('')
                # print('OPENED:',id)
                # print('')
                # print('')

                ##############
                #  HOW MANY? #
                ##############
                sub_cnt+=1
                if sub_cnt>=int(inp):
                    if int(inp) != 0:
                        end_time = time.time()
                        es = end_time-start_time
                        print sub_cnt, "poems,\n",lines_total,"lines,\n",words_total,"words \ngenerated in\n",("%.2f" % es),"seconds"
                        
                    words_total=0
                    lines_total=0

                    # RESTART

                    sub_cnt=0
                    inp = raw_input("\n\n^^^^^^^^^^^^^^\n\nHow many poems do u want? ")

                    if not inp:
                        print "You entered nothing! 10 poems will be generated."
                        inp=10
                        
                    pause_every = raw_input("\nPause every 1 or 2 or ... poems?")
                    if not pause_every:
                        print "You entered nothing! Pause will occur every 10 poems."
                        pause_every=10

                    sleep_time = raw_input("\nPause for how many seconds?")
                    if not sleep_time:
                        print "You entered no time! 10 second wait assigned."
                        sleep_time=10

                    print "\n\n^^^^^^^^^^^^^^^"
                    start_time = time.time()

                print 'Poem #',sub_cnt

                poem_replaced = ""
                replacement_word = ""
                previous_replacement_word = ""
                
                author=""
                titles=""
                title=""
                new_title=""

                replaced_ls =[]
                new_titles_ls = []
                quit_language=0
                oscillator=0

                word_cnt=0

                # if EXCEPTION is raised... do not add to html
                SKIP_bool=False

                ##########################
                # Load  POEM TEXT FILE   #
                ##########################

                ##
                # PAUSE
                ##
                #time.sleep(5)

                txt_fn_path = DATA_DIR + READ_TXT_PATH + id.split("_")[1]+".txt"
                #print "txt_fn_path:",txt_fn_path

                if os.path.isfile(txt_fn_path) and cnt>0:
                    txt_data=open(txt_fn_path).read()

                    # http://blog.webforefront.com/archives/2011/02/python_ascii_co.html
                    # txt_data.decode('ISO-8859-2') .decode('utf-8')
                    # unicode(txt_data)

                    author=txt_data.split("****!****")[0].strip(' \t\n\r')
                    
                    title=txt_data.split("****!****")[1].strip(' \t\n\r')
                    
                    bio=txt_data.split("****!****")[2]#.strip(' \t\n\r')

                    ######  CLEAN BIO
                    bio.replace("\t","&#9;")
                    bio.replace("\n"," <br>")
                    bio.replace("\r"," <br>")
                    poem_replaced=bio
                    #print poem_replaced

                    ###############################
                    # REPLACE AUTHOR NAME in poem #
                    ###############################
                    author_ln=author.split(" ")[-1].lstrip()
                    author_fn=author.split(" ")[:-1]
                    author = " ".join(n for n in author_fn)+author_ln
                    #
                    #poem_replaced = poem_replaced.replace(author_ln,"Jhave")

                    #######################
                    # replace BOOK TITLES #
                    #######################
                    #print "TITLES"]
                    new_title = getNewTitle("title").encode('utf-8')

                    #######################
                    # fake AUTHOR         #
                    #######################
                    
                    new_author= " ".join(random.choice(authors).split(" ")[1:-2])+" "+random.choice(authors).split(" ")[-2]
                    #print "new AUTHOR",new_author                           

                    ############################
                    # replace years with another
                    ############################
                    for w1 in poem_replaced.split("("):
                        for w2 in w1.split(")"):
                            if w2 is not None and w2.isdigit():
                                new_num = random.randint(int(w2)-5,int(w2)+5)
                                #print "REPLACING #:",w2,new_num
                                poem_replaced = poem_replaced.replace(w2,str(new_num))
                                replaced_ls.append(new_num)                            
                                               

                    #################
                    # Load JSON     #
                    #################
                    response = loadJSONfile(READ_JSON_PATH+"poetryFoundation_"+id.split("_")[1]+"_Alchemy_JSON.txt")

                    if response != "failed":

                        JSON_alchemy_loaded = True

                        if response.get('entities') is not None:
                            for idx,entity in enumerate(response['entities']):

                                #DATA clean the original words (redundant duplicate but for some reason it works... and is necessary... a kludge of crowbars and bleach)
                                ce = entity['text'].replace("0xc2"," ")
                                ce = ce.replace("0xe2","'")
                                ce = re.sub('(' + '|'.join(import_utilities.chars.keys()) + ')', import_utilities.replace_chars, ce)
                                ce = ce.encode('utf-8')

                                try:
                                    content = ce.decode('utf-8').encode('ascii', 'xmlcharrefreplace')
                                except UnicodeDecodeError:
                                    "AAAARGGGGHHH!!!!"

                                if content in poem_replaced:
                                                       
                                    #################################################
                                    #                                               #
                                    # Replace similar entities from other JSON      #
                                    # Using data from ALCHEMY API                   #
                                    #                                               #
                                    #################################################
                                    replacement_entity = findSimilarEntityinRandomJSON(content,entity['type'])

                                    cr = re.sub('(' + '|'.join(import_utilities.chars.keys()) + ')', import_utilities.replace_chars, replacement_entity)

                                    poem_replaced = poem_replaced.replace(content,replacement_entity)

                                    replaced_ls.append(replacement_entity)
                    

                    ##########################
                    #   POS REPLACMENT       #
                    ##########################

                    token_tuples = nltk.word_tokenize(poem_replaced)
                    tt = nltk.pos_tag(token_tuples)

                    #################
                    #  ADJECTIVES   #
                    #################
                    for i in tt:
                        if "/i" not in i[0] and len(i[0])>3 and i[0] != "died":
                            origw =  re.sub('(' + '|'.join(import_utilities.chars.keys()) + ')', import_utilities.replace_chars, i[0])
                            origw =import_utilities.strip_punctuation(origw) 
                            if i[1]=='JJ' :
                                JJr = random.choice(JJ)
                                # # JJr =  re.sub('(' + '|'.join(import_utilities.chars.keys()) + ')', import_utilities.replace_chars, JJr)
                                # JJr = import_utilities.strip_punctuation(JJr)
                                JJr = import_utilities.moveBeginAndEndPunctuationFromStrToString(i[0],JJr.lstrip().lstrip())
                                
                                if i[0].istitle():
                                    JJr = JJr.title()

                                poem_replaced = re.sub(r'\b' + import_utilities.strip_punctuation(i[0]) + r'\b', JJr, poem_replaced,1)#poem_replaced.replace(i[0],JJr,1)
                                replaced_ls.append(JJr)
                            if i[1]=='RB':
                                RBr = random.choice(RB)
                                RBr = import_utilities.moveBeginAndEndPunctuationFromStrToString(i[0],RBr.lstrip().lstrip())

                                if i[0].istitle():
                                    RBr = RBr.title()
                                poem_replaced = re.sub(r'\b' + import_utilities.strip_punctuation(i[0])  + r'\b', RBr, poem_replaced,1)
                                replaced_ls.append(RBr)


                    ########################
                    # IS IT ENGLISH?       #
                    ########################
                    for line  in poem_replaced.split('\n\r'):
                        if len(line)>0 :
                            if "english" not in import_utilities.get_language(line):
                                quit_language+=1
                                #print "NOT english:",quit_language,line
                            else:
                                quit_language-=1

                    
                    #########################
                    #   SYNSET REPLACE      #
                    #########################
                    for idx,word in enumerate(poem_replaced.split(' ')):

                        similarterm=""

                        if "<br>" not in word and "&#9;" not in word and len(word)>0:


                            words_total+=1


                            #########################
                            #   PRONOUN ' VERB      #
                            #########################
                            if len(word.split("'"))>1:
                                if word.split("'")[0] in personal_pronouns:
                                    replacement_word = random.choice(personal_pronouns)+"'"+word.split("'")[1]+' '
                                poem_replaced.replace(word,replacement_word)             
                                #print "word,",word,"replacement_word:",replacement_word
                           
                            ####################################################
                            # Replacement of OTHERs                            #
                            ####################################################

                            elif not word.lower().strip(" \n\t\r") in stopwords.words('english'):

                                # take off leading brackets, commas etc...
                                word_punct_nopunct = import_utilities.strip_punctuation_bool(word)
                                word_nopunct = word_punct_nopunct['word'].strip(" \n\t\r")
                                word_punct = word_punct_nopunct['punct']
                                punct_bool = word_punct_nopunct['punct_bool']

                             

                                #######################################################
                                # MAIN EXCHANGE PROCESS CALL >>>>>>>   GET THE SYNSET #
                                #######################################################    
                                if word_nopunct[-4:].lower()=="here":
                                    similarterm=random.choice(import_utilities.heres)
                                else:
                                    #print "WORD:",word_nopunct
                                    if len(word_nopunct)>3:

                                        oscillator  = oscillator+1
                                        
                                        ############################################
                                        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                        # STYLE SWITCH..... should in future use POS
                                        # ... i.e. if noun & oscillator%3, do...
                                        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                        ############################################
                                        # synset
                                        similarterm = import_utilities.synset_creeley(word_nopunct)
                                        #print "synset", similarterm

                                        if similarterm is not None and similarterm == word_nopunct and len(word_nopunct)>4:
                                            #RESERVOIR.sort(key=len)
                                            poetry_mouth.sort(key=len)
                                            similarterm= poetry_mouth[idx%len(poetry_mouth)]#RESERVOIR[idx%len(RESERVOIR)]
                                            #print "NEW",idx,len(RESERVOIR),similarterm,word_nopunct,"PRE>>>>>>>>LAST CHANGE STOP: ", word, "~",similarterm

                                            

                                #######################################                      
                                # abbreviations for fucking states!   #
                                #######################################
                                if word_nopunct.upper() in import_utilities.state_abbrev and word_nopunct.lower() not in stopwords.words('english') and "me," not in word:
                                    tmp = similarterm
                                    if word_nopunct == "oh": 
                                        similarterm = random.choice(import_utilities.exclaims)
                                    else:

                                        similarterm = random.choice(poetry_mouth)#RESERVOIR)
                                    #print word_nopunct," replaced by", tmp, "replaced with:",similarterm, "in:",line

                                ##############
                                # hyphenated #
                                ##############
                                hyp =word.split("-")
                                #print word,len(hyp)
                                if len(hyp) >1:
                                    similarterm=""
                                    for w in hyp:
                                        if len(w) > 2:
                                            if import_utilities.synset_creeley(w) is not None:
                                                similarterm +=  import_utilities.synset_creeley(w)+"-"
                                            else:
                                                similarterm += w+"-"
                                    similarterm = import_utilities.strip_underscore(similarterm[:-1])
                                    #print "hyphenated:",word,"replaced by: "+similarterm

                                
                                #########################################################    
                                # is it a TRUNCATED VERB slang as in singin or wishin   #
                                #########################################################
                                # if similarterm == word_nopunct and len(word)>2 and 'in' in word_nopunct[-2:]:
                                #     similarterm = import_utilities.synset_creeley(word_nopunct+'g')
                                #     ## #print "TRUNCATED SLANG word: '"+word+"'",similarterm
                                #     interim = import_utilities.lemma(similarterm)
                                #     ## #print interim
                                #     similarterm = import_utilities.conjugate(interim, tense=import_utilities.PARTICIPLE, parse=True)[:-1] 
                                #     # # # #print word,"widx:",widx," line_pos_tags[widx][0]:",line_pos_tags[widx][0]," line_pos_tags[widx][1]:",line_pos_tags[widx][1]
                                   

                                #################      
                                # SWEAR WORD    #
                                #################
                                ##print "at the garden of if:", word
                                if word_nopunct in import_utilities.curses:
                                    similarterm = random.choice(import_utilities.curses)
                                    ##print "SWEAR WORD word: '"+word+"'",similarterm

                                                          
                                ############################################
                                # manually get rid of some terrible choices
                                ############################################
                                naw_terms=["mind","lonely"]
                                if similarterm == "ilk":
                                    similarterm = "like"

                                if similarterm == "Nox":
                                    similarterm = "oil"

                                if similarterm == "ope":
                                    similarterm = "does"

                                if similarterm == "information technology":
                                    similarterm = "it"

                                if similarterm == "velleity":
                                    similarterm = "want"

                                if similarterm == "Crataegus laevigata":
                                    similarterm = "may"

                                if similarterm == "eff":
                                    similarterm = "know"

                                if similarterm == "naw":
                                    similarterm = "mind"

                                if similarterm == "lento":
                                    similarterm = "slow"

                                #print "SIMILAR:",similarterm

                                if similarterm is not None:
                                    if len(hyp) >1:
                                        replacement_word = similarterm
                                    else:
                                        replacement_word = word.replace(word_nopunct, similarterm)
                                        replacement_word = import_utilities.strip_underscore(replacement_word)
                                        replacement_word = import_utilities.replaceNumbers(replacement_word)
                                else:
                                    replacement_word = random.choice(poetry_mouth)#RESERVOIR)

                                ################################
                                # RESERVOIR_OF_WEIRDNESS       #
                                # create a large pool of words #
                                ################################  

                                if word_nopunct.lower() in import_utilities.impera:
                                    replacement_word=random.choice(import_utilities.impera)
                                    #print word,"IMPERA:",replacement_word
                                elif word_nopunct.lower() in import_utilities.conjuncts:
                                    replacement_word=random.choice(import_utilities.conjuncts)
                                    #print word," CONJUNCTION replaced with",replacement_word
                                elif word_nopunct.lower() in import_utilities.indef_prono:
                                    replacement_word=random.choice(import_utilities.indef_prono)
                                    #print word," INDEF_prono replaced with",replacement_word
                                elif word_nopunct.lower() in import_utilities.prepo:
                                    replacement_word=random.choice(import_utilities.prepo)
                                    #print word," prepo replaced with",replacement_word
                                elif word_nopunct.lower() in import_utilities.rel_prono:
                                    replacement_word=word
                                    #print word," rel_prono LEAVE alone: ",replacement_word
                                elif word_nopunct.lower()[-2:] =="ly":
                                    if import_utilities.synset_creeley(word) is not None:
                                        replacement_word=import_utilities.strip_underscore(import_utilities.synset_creeley(word))#(word[:-2])
                                    #print word," ADVERB: ",replacement_word
                                    # if replacement_word[-2:] !="ly":
                                    #     replacement_word +="ly"
                                                                            
                                else:
                                    if len(hyp) <2 and "like" not in word_nopunct and import_utilities.singularize(word_nopunct) ==  import_utilities.singularize(replacement_word) and word_nopunct.lower() not in import_utilities.stopwords_ls:

                                        if word not in RESERVOIR and quit_language<0 and import_utilities.countPunctuation(word)<1 and len(word_nopunct)>3 and not word_nopunct.istitle(): 
                                            
                                            #print "ADDING",word,"to reservoir"
                                            #################################################
                                            # ADDING ONLY SMALL WORDS 
                                            # & MAKING A POEM OUT OF THEM
                                            #################################################
                                            if len(word)<7 and len(word)>0:
                                                small_word = word
                                                if random.randint(0,4)==3:
                                                    small_word +="\n"
                                                #print small_word
                                                small_word +=" "
                                                SMALL_POEM+=small_word

                                                RESERVOIR.append(word)
                                                #SMALL_POEM_ALL.append(small_word)
                                            
                                            replacement_word = random.choice(poetry_mouth)#RESERVOIR)#rap_mouth)# RESERVOIR)
                                            #print word_nopunct,"replaced from reservoir with", replacement_word
                                       # print "'"+word_nopunct+"'  vs RESERVOIR  replacement_word:",replacement_word #,"    new_line:",new_line
                                if quit_language>1 and not word_nopunct.istitle():
                                    #print quit_language, "Probably foreign language: make a word salad in english"
                                    replacement_word = random.choice(poetry_mouth)#RESERVOIR)#science_mouth)#RESERVOIR)
                                    #print word_nopunct,"OTHER replaced from reservoir with", replacement_word
                                
                                ###################################################
                                # MOST REPLACEMENT occurs here...                 #
                                ###################################################
                                poem_ls = poem_replaced.split(' ')
                                idx =  poem_ls.index(word)

                                # print idx,",", poem_ls[idx],",", word ,",",replacement_word
                                #print word ," --- ",previous_replacement_word,replacement_word

                                idx_2 =  poem_ls.index(word)

                                if poem_ls[idx_2]==word and poem_ls[idx_2]==replacement_word:
                                    print "SAME idx-2 replacement_word=",replacement_word
                                    replacement_word=random.choice(poetry_mouth)
                                    print "NEW ",replacement_word

                                # BUG test: is potential replacement a comma or period or empty?
                                if replacement_word.lstrip().rstrip() =="," or replacement_word.lstrip().rstrip() =="" or replacement_word.lstrip().rstrip() ==".":
                                    print "found a comma/empty why?",replacement_word.lstrip().rstrip()
                                    replacement_word=random.choice(poetry_mouth)
                                    print "line633 REPLACING with ",replacement_word


                                #print idx,idx_2,"  poem_ls[idx_2]=", poem_ls[idx_2],"  poem_ls[idx]=", poem_ls[idx]," word=", word ,"    replacement=",replacement_word

                                if poem_ls[idx]==word:
                                    poem_ls[idx]=replacement_word
                                if poem_ls[idx_2]==word:
                                    poem_ls[idx_2]=replacement_word
                                poem_replaced = " ".join(poem_ls)


                                
                                if len(word)>5 and replacement_word.lstrip().rstrip() == word_nopunct.lstrip().rstrip():

                                    #####################################################
                                    #  since word is same as replacement, try alchemy?  #
                                    #####################################################
                                    
                                    #replacement_entity = findSimilarEntityinRandomJSON(content,entity['type'])

                                    # a last ditch pseudo random select 
                                    # TODO USE THE NLTK LISTS TO SELECT POS WORD
                                    # RESERVOIR.sort(key=len)
                                    # replacement_word = RESERVOIR[idx%len(RESERVOIR)]
                                    poetry_mouth.sort(key=len)


                                    #INSERTION
                                    replacement_word = random.choice(poetry_mouth)#[idx%len(poetry_mouth)]
                                    print "NEWEST ran",idx,len(poetry_mouth),"LAST CHANGE STOP: ", word, "~",replacement_word

                                # check again
                                if poem_ls[idx]==word and poem_ls[idx]==replacement_word:
                                    print "AGAIN SAME idx replacement_word=",replacement_word
                                    replacement_word=random.choice(poetry_mouth)
                                    print "line663 AGAIN NEW rand pf=",replacement_word

                        
                                # REPLACE (but catch for weird chars)
                                try:

                                    if poem_ls[idx]==word and "****" not in word and "." != word and "\n" not in word:

                                        # INSERTION
                                        poem_ls[idx]=replacement_word
                                        print "line673 REPLACING",poem_ls[idx]," with ",replacement_word


                                    # REASSEMBLE the poem    
                                    poem_replaced = " ".join(poem_ls)

                                    # store this word so that conjugation can be checked 
                                    previous_replacement_word=replacement_word

                                except Exception, e:
                                    #print "PENULTIMATE SKIP_bool replace FAIL",e
                                    SKIP_bool=True
                                    continue

                    ###########################################################################
                    # testing Pattern.en as parser for conjugation and article replacement    #
                    # much more robust than my hand-coded hacks                               #        
                    ###########################################################################
                    
                    # correct CONJUGATion of paticiple verbs with pattern.en
                    parsed = parse(poem_replaced,tags = True) 
                    pre_verbal = ["'m","'s","'re"]
                    for idx,p in enumerate(parsed.split(" ")):
                        tok =p.split("/")[0]
                        typ=p.split("/")[1]
                        #print idx,tok,typ
                        if tok in pre_verbal:
                            #print "pre_verbal:",tok
                            next_word= parsed.split(" ")[idx+1].split("/")

                            # try try try
                            for ix,n in enumerate(next_word): 
                                next_word[ix] = re.sub('(' + '|'.join(import_utilities.chars.keys()) + ')', import_utilities.replace_chars, n).encode('utf-8')
                            try:
                                #print  next_word,next_word[0],next_word[1][:2]
                                # if it's a verb that follows
                                if next_word[1][:2] =="VB":
                                    before_verb = " ".join(w for w in poem_replaced.split(" ")[:idx])#.encode('utf-8')
                                    after_verb = " ".join(w for w in poem_replaced.split(" ")[idx+1:])#.encode('utf-8') 
                                    new_verb = conjugate(next_word[0], tense=PARTICIPLE, parse=True).encode('utf-8')
                                    # insert new
                                    #print "CONJUGATION needed, changing:",poem_replaced.split(" ")[idx],"to",parsed.split(" ")[idx],poem_replaced.split(" ")[idx-1]+" "+new_verb
                                    poem_replaced = before_verb+" "+new_verb+" "+after_verb
                            except Exception, e:
                                # print "INside parsed COnjugation loop",e
                                continue


                    # correct ARTICLES
                    for idx,word in enumerate(poem_replaced.split(" ")):
                        if len(word)>0 and idx != 0 and " " not in word:
                            # A or AN
                            if poem_replaced.split(" ")[idx-1].lower() =="a" or poem_replaced.split(" ")[idx-1].lower() =="an":
                                #print word,"---",article(word)+" "+word
                                before_article = " ".join(w for w in poem_replaced.split(" ")[:idx-1])
                                after_article = " ".join(w for w in poem_replaced.split(" ")[idx+1:])
                                new_conj = referenced(word)
                                # capitalize
                                if poem_replaced.split(" ")[idx-1].istitle():
                                    new_conj = new_conj.split(" ")[0].title()+" "+new_conj.split(" ")[1]
                                poem_replaced = before_article+" "+new_conj+" "+after_article


                    #########################
                    #   WRITE SINGLE POEM   #
                    #########################
                    if not SKIP_bool:

                        tmp_poem=""   

                        # poem_replaced.replace("\t","&#9;")
                        # poem_replaced.replace("\n"," <br>")
                        # poem_replaced.replace("\r"," <br>")

                        HTML_poem=""
                        for line in poem_replaced.split("\n"):
                            #print "LINE", line
                            lines_total+=1
                            HTML_poem += line+"<br>"

                        if len(response) >0 and len(id.split("_"))>1:

                            ALL_poems = "<br>[ A  generated-poem based upon: <i>"+ title +"</i> by <b>"+ author+"</b>]<br><br><i>"+new_title+"</i><br> by <b>"+ new_author   +"</b><br>"+HTML_poem+ALL_poems.split("</h2>")[1].replace("  ","&nbsp")

                            tmp_poem= "[A generated-poem based upon: '"+ title+"' by "+ author +"]\n\n"+new_title+ "\nby "+new_author+"\n"+poem_replaced
  
                            #####################
                            #                   #
                            #                   #
                            #     PAUSE IT      #
                            #                   #
                            #                   #
                            #####################

                            if (int(sub_cnt)%int(pause_every) == 0 and int(sub_cnt) !=0):
                                time.sleep(int(sleep_time))

                            #####################
                            #                   #
                            #                   #
                            #       PRINT       #
                            #                   #
                            #                   #
                            #####################

                            print "\n~~~\n"  +tmp_poem

                            # SLOW TYPEWRITER PRESENTATION
                            # for line in tmp_poem:
                            #    for c in line:
                            #         time.sleep(0.04)
                            #         sys.stdout.write(c)#(c.encode("utf8"))
                            #         sys.stdout.flush()
# 
                            #sys.stdout.write("\n")

                            txt_fn = id.split("_")[1]+"_POEMs.txt"

                            WRITE__PATH = "../../generated/poetryFoundation/"+poem_style+datetime.datetime.now().strftime('%Y-%m-%d_%H')+"/"
                            if not os.path.exists(WRITE__PATH):
                                    os.makedirs(WRITE__PATH)

                            txt_fn_path = WRITE__PATH+txt_fn
                            f_txt=open(txt_fn_path,'w')
                            f_txt.write(tmp_poem)#.encode('utf-8'))       
                            f_txt.close();   
                            #print "\nTXT file created at:",txt_fn_path

                            WRITE__PATH = "../../generated/poetryFoundation/"+poem_style+"_SMALL_POEMS"+datetime.datetime.now().strftime('%Y-%m-%d_%H')+"/"
                            if not os.path.exists(WRITE__PATH):
                                    os.makedirs(WRITE__PATH)
                            txt_fn_path = WRITE__PATH+txt_fn
                            f_txt=open(txt_fn_path,'w')
                            f_txt.write("[A generated-poem based upon: '"+ title+"' by "+ author +"]\n\n"+SMALL_POEM)#.encode('utf-8'))       
                            f_txt.close(); 
                            SMALL_POEM=""  
                            
                            #######
                            #   write them all.... wasteful... but useful if run is interrupted....
                            ###########  

                            # if cnt==1:
                            #     ALL_poems = ALL_poems_intro+ALL_poems
                            # else:
                            ALL_poems = ALL_poems_intro+ALL_poems.replace("  ","&nbsp")
                            ALL_poems = ALL_poems.replace("$$datetime$$",datetime.datetime.now().strftime('%Y-%m-%d at %H:%M'))
                            ALL_poems = ALL_poems.replace("$$cnt$$",str(cnt))
                            ALL_poems = ALL_poems.replace("$$style$$",poem_style)
                            ALL_poems = ALL_poems.replace("$$gentime$$",str(time.time() - start_time))

                            # ALL POEMS
                            txt_fn = datetime.datetime.now().strftime('%Y-%m-%d')+"_BDP_generated_"+poem_style+"_POEMS_"+str(poem_id)+".html"
                            

                            GEN_PATH = GENERATED_DIR+type_of_run+"_html/"
                            if not os.path.exists(GEN_PATH):
                                    os.makedirs(GEN_PATH)

                            txt_fn_path = GEN_PATH+txt_fn

                            f_txt=open(txt_fn_path,'w')
                            f_txt.write(ALL_poems+"</hmtl>")       
                            f_txt.close();   
                            #print "\nTXT file created at:",txt_fn_path
                        # except Exception, e:
                        #         print "At the final LOOP",e
                        #         #continue
                        #         pass


                        else:
                            pass
                            #print "~! EMPTY response:", author

                    else:
                        cnt = cnt-1







#################
# get NEW title    #
#################

def getNewTitle(old_title):
    new_title=""
    total_str = random.choice(titles_ls)+ " "+random.choice(titles_ls)+ " "+import_utilities.strip_punctuation(random.choice(titles_ls))
    total = total_str.split(' ')
    random.shuffle(total)
    for w in total:
        if total.index(w)%4:
            new_title += w +" " 

    new_title = " ".join(w for w in new_title.split(" ") if " , " not in w and len(w)<7)

    new_title = new_title.replace("Review","")

    new_title = ' '.join(unique_list(new_title.split()))
    # check last word
    if new_title.lower().split(" ")[-1] in import_utilities.stopwords_ls:
        new_title = new_title.rsplit(' ', 1)[0]
    
    # 
    new_title = new_title.rsplit(' ', 1)[0] +" "+ new_title.split(" ")[-1].rstrip(",:;").title()
    return new_title

##################
# remove repeat words
def unique_list(l):
    ulist = []
    [ulist.append(x) for x in l if x not in ulist and x not in import_utilities.stopwords_ls]
    return ulist

#################
# Load JSON     #
#################

def loadJSONfile(fn):

    id=fn.split(".")[0]
    #print "Inside loadJSONfile id=",id

    try:
        json_data=open(fn)
        response = json.load(json_data)
        json_data.close()   

        return response

    except ValueError:
        #print "############# decoding JSON failed",fn
        pass

    return "failed"
    

#############################
# find Similare entities    #
#############################
def findSimilarEntityinRandomJSON(orig,typ):

    not_found=True
    cnt =-1
    
    random.shuffle(json_files)
    #print "\nENTERING findSimilarEntityinRandomJSON",orig,typ

    while (not_found):

        cnt+=1
        if cnt>len(json_files)-1:
            cnt=0
            
            #print "EXITING find Similar Without FINDING"
            break

        fn = READ_JSON_PATH+json_files[cnt]
        
        try:
            json_data=open(fn)
            response = json.load(json_data)
            json_data.close() 

        except ValueError:
            #print "############# decoding JSON failed",fn
            response = "failure"
            pass



        #print "findSimilarEntityinRandomJSON in fn=",fn,len(response)
        
        if response != "failure" and response.get('entities') is not None:
            # NOTED SORTED SO SMALLEST FIRST FOR CREELEY STYLE
            response['entities'].sort(key=len)
            # OR Shuffled....
            #random.shuffle(response['entities'])
            for idx,entity in enumerate(response['entities']):
                if orig.encode('utf-8') not in entity['text'].encode('utf-8')  and entity['type']==typ:
                    #print orig.encode('utf-8') ,"::",entity['text'].encode('utf-8')

                    ce = re.sub('(' + '|'.join(import_utilities.chars.keys()) + ')', import_utilities.replace_chars, entity['text'])
                    return ce.encode('utf-8')
        else:
            pass
            #print "entities response empty?",random.shuffle(json_files)

    return orig#"**** DID NOT FIND ****"





##############################
#    READ DIRECTORY          #
##############################
extractFeaturesAndWritePoem(READ_JSON_PATH,"txt")



# #############################
# # STASH THE DATA           #
# #############################

ALL_poems = ALL_poems.replace("$$datetime$$",datetime.datetime.now().strftime('%Y-%m-%d at %H:%M'))
ALL_poems = ALL_poems.replace("$$cnt$$",str(cnt))
ALL_poems = ALL_poems.replace("$$gentime$$",str(time.time() - start_time))

ALL_poems = ALL_poems.split("</h2>")[0]+"</h2>"+ALL_poems.split("</h2>")[1].replace("  ","&nbsp")

# ALL POEMS
txt_fn = datetime.datetime.now().strftime('%Y-%m-%d')+"_BDP_generated_"+poem_style+"_POEMS_"+str(poem_id)+".html"

txt_fn_path = DATA_DIR+"generated/POEMS/"+txt_fn
f_txt=open(txt_fn_path,'w')
f_txt.write(ALL_poems+"</hmtl>")   
#f_txt.write(codecs.BOM_UTF16_BE)    
f_txt.close();   
print "\nTXT file created at:",txt_fn_path
#print "ALL_poems:\n",ALL_poems


# RESERVOIR
txt_fn = datetime.datetime.now().strftime('%Y-%m-%d_%H')+"_poetryFoundation_RESERVOIR_"+type_of_run+".txt"
txt_fn_path = DATA_DIR+"generated/"+txt_fn
f_txt=open(txt_fn_path,'w')
f_txt.write(", ".join(RESERVOIR))       
f_txt.close();   
print "\nRESERVOIR TXT file created at:",txt_fn_path


print "RESERVOIR:",RESERVOIR


