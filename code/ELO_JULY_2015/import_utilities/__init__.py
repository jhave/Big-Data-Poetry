#! /usr/bin/env python
from collections import Counter

import re

from nltk_contrib.readability.textanalyzer import syllables_en
from nltk.corpus import cmudict,wordnet as wn
from nltk.corpus import stopwords
import nltk, re, pprint
from nltk import Text
from nltk.corpus import cmudict
import nltk

from json import JSONDecoder
from functools import partial
from string import whitespace
import string

import random
from random import shuffle


from nltk.corpus import stopwords   # stopwords to detect language
from nltk import wordpunct_tokenize # function to split up our words

#
# pattern.en
# module to singularize and do verb tenses
# http://www.clips.ua.ac.be/pattern
#
from pattern.en import wordnet
from pattern.en import pluralize, singularize
from pattern.en import comparative, superlative
from pattern.en import conjugate, lemma, lexeme, PARTICIPLE
# # # print conjugate('googled', tense=PARTICIPLE, parse=True)  
# >>> googling
# NOTE: it also does sentiment, returns a tuple...
# from pattern.en import sentiment
# and can be used with weights using http://sentiwordnet.isti.cnr.it/ 

##############################################################
# stoplist http://www.lextek.com/manuals/onix/stopwords1.html
# more comprehensive than default in nltk

stopwords_ls=["a","about","above","across","after","again","against","all","almost","alone","along","already","also","although","always","among","an","and","another","any","anybody","anyone","anything","anywhere","are","area","areas","around","as","ask","asked","asking","asks","at","away","b","back","backed","backing","backs","be","became","because","become","becomes","been","before","began","behind","being","beings","best","better","between","big","both","but","by","c","came","can","cannot","case","cases","certain","certainly","clear","clearly","come","could","d","did","differ","different","differently","do","does","done","down","downed","downing","downs","during","e","each","early","either","end","ended","ending","ends","enough","even","evenly","ever","every","everybody","everyone","everything","everywhere","f","face","faces","fact","facts","far","felt","few","find","finds","first","for","four","from","full","fully","further","furthered","furthering","furthers","g","gave","general","generally","get","gets","give","given","gives","go","going","good","goods","got","great","greater","greatest","group","grouped","grouping","groups","h","had","has","have","having","he","her","here","herself","high","higher","highest","him","himself","his","how","however","i","if","important","in","interest","interested","interesting","interests","into","is","it","its","itself","j","just","k","keep","keeps","kind","knew","know","known","knows","l","large","largely","last","later","latest","least","less","let","lets","like","likely","long","longer","longest","m","made","make","making","man","many","may","me","member","members","men","might","more","most","mostly","mr","mrs","much","must","my","myself","n","necessary","need","needed","needing","needs","never","new","newer","newest","next","no","nobody","non","noone","not","nothing","now","nowhere","number","numbers","o","of","off","often","old","older","oldest","on","once","one","only","open","opened","opening","opens","or","order","ordered","ordering","orders","other","others","our","out","over","p","part","parted","parting","parts","per","perhaps","place","places","point","pointed","pointing","points","possible","present","presented","presenting","presents","problem","problems","put","puts","q","quite","r","rather","really","right","room","rooms","s","said","same","saw","say","says","second","seconds","see","seem","seemed","seeming","seems","sees","several","shall","she","should","show","showed","showing","shows","side","sides","since","small","smaller","smallest","so","some","somebody","someone","something","somewhere","state","states","still","such","sure","t","take","taken","than","that","the","their","them","then","there","therefore","these","they","thing","things","think","thinks","this","those","though","thought","thoughts","three","through","thus","to","today","together","too","took","toward","turn","turned","turning","turns","two","u","under","until","up","upon","us","use","used","uses","v","very","w","want","wanted","wanting","wants","was","way","ways","we","well","wells","went","were","what","when","where","whether","which","while","who","whole","whose","why","will","with","within","without","work","worked","working","works","would","x","y","year","years","yet","you","young","younger","youngest","your","yours","z"]

personal_pronouns = ["i","me","we","us","you","she","her","he","him","it","they","them"]

impera =["could","should","would","couldn't","wouldn't", "shouldn't","did","didn't","will","will not","does","does not","can","cannot"]

conjuncts = ["after","although","as","as if","as long as","as much as","as soon as","as though","because","before","even","even if","even though","if","if only","if when","if then ","inasmuch","in order that","just as","lest","now","now since","now that","now when","once","provided","provided that","rather than","since","so that","supposing","than","that","though","til","unless","until","when","whenever","where","whereas","where if","wherever","whether","which","while","who","whoever","why"]


indef_prono =["anybody","anyone","anything","everybody","everyone","everything","nobody","none","no one","nothing","somebody","someone","something"]

prepo =["aboard","about","above","across","after","against","along","amid","among","anti","around","as","at","before","behind","below","beneath","beside","besides","between","beyond","but","by","concerning","considering","despite","down","during","except","excepting","excluding","following","for","from","in","inside","into","minus","near","of","off","on","onto","opposite","outside","over","past","per","plus","regarding","round","save","since","than","through","to","toward","towards","under","underneath","unlike","until","up","upon","versus","via","with","within","without"]

rel_prono=["that","when","which","whichever","whichsoever","who","whoever","whosoever","whom","whomever","whomsoever whose","whosesoever whatever","whatsoever","whose"]
#
# parseStressOfLine(line) 
# function that takes a line
# parses it for stress
# corrects the cmudict bias toward 1
# and returns two strings 
#
# 'stress' in form '0101*,*110110'
#   -- 'stress' also returns words not in cmudict '0101*,*1*zeon*10110'
# 'stress_no_punct' in form '0101110110'


def parseStressOfLine(line):
    
    prondict = cmudict.dict()
    stress=""
    stress_no_punct=""
    print line

    tokens = [words.lower() for words in nltk.word_tokenize(line)] 
    for word in tokens:        

        word_punct =  strip_punctuation_stressed(word.lower())
        word = word_punct['word']
        punct = word_punct['punct']

        #print word

        if word not in prondict:
            # if word is not in dictionary
            # add it to the string that includes punctuation
            stress= stress+"*"+word+"*"
        else:
            zero_bool=True
            for s in prondict[word]:
                # oppose the cmudict bias toward 1
                # search for a zero in array returned from prondict
                # if it exists use it
                # print strip_letters(s),word
                if strip_letters(s)=="0":
                    stress = stress + "0"
                    stress_no_punct = stress_no_punct + "0"
                    zero_bool=False
                    break

            if zero_bool:
                stress = stress + strip_letters(prondict[word][0])
                stress_no_punct=stress_no_punct + strip_letters(prondict[word][0])

        if len(punct)>0:
            stress= stress+"*"+punct+"*"

    return {'stress':stress,'stress_no_punct':stress_no_punct}





def get_language_likelihood(input_text):
    """Return a dictionary of languages and their likelihood of being the 
    natural language of the input text
    """

    input_text = input_text.lower()
    input_words = wordpunct_tokenize(input_text)

    language_likelihood = {}
    total_matches = 0
    for language in stopwords._fileids:
        language_likelihood[language] = len(set(input_words) &
                set(stopwords.words(language)))

    return language_likelihood

def get_language(input_text):
    """Return the most likely language of the given text
    """

    likelihoods = get_language_likelihood(input_text)
    return sorted(likelihoods, key=likelihoods.get, reverse=True)[0]

exclaims =["oh","ooh","ah","aiiya","eek","ooo"]
state_abbrev= ["IT", "US", "AL","AK","AZ","AR","CA","CO","CT","DE","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","MD","MA","MI","MN","MS","MO","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY", "oh","hi","id"]# REMOVED "DC","FL",


#count words (not tokens, and not punctuation)
nonPunct = re.compile('.*[A-Za-z0-9].*')  # must contain a letter or digit
def countWords(str):
    filtered = [w for w in str if nonPunct.match(w)]
    counts = Counter(filtered)
    return sum(c for w,c in counts.iteritems())

def countChars(str):
    filtered = [w for w in str if nonPunct.match(w)]
    counts = Counter(filtered)
    if len(filtered)>0:
        return float(sum(len(w)*c for w,c in counts.iteritems())) / len(filtered)
    else:
        return 0.0
#count punctuation
def countPunctuation(str):
    filtered = [w for w in str if not nonPunct.search(w)]
    for w in str:
        
        np=nonPunct.match(w)
        # print w,np
        # if np:
        #     print np
        # else:
        #     print 'no match'
    counts = Counter(filtered)
    return len(counts)

# STRIP PUNCTUATION BUT KEEP IT TO BE ADDED LATER
def strip_punctuation_stressed(word):
    # define punctuations
    punctuations = '!()-[]{};:"\,<>./?@#$%^&*_~'
    my_str = word

    # remove punctuations from the string
    no_punct = ""
    punct=""
    for char in my_str:
        if char not in punctuations:
            ####print "CHAR:", char
            no_punct = no_punct + char
        else:
            punct = punct+char

    ####print "word:",no_punct,"punct:", punct
    return {'word':no_punct,'punct':punct}


# STRIP PUNCTUATION & discard
def strip_punctuation(word):
    # define punctuations
    punctuations = '!()-[]{};:"\,<>./?@#$%^&*_~'
    my_str = word

    # remove punctuations from the string
    no_punct = ""
    punct=""
    for char in my_str:
        if char not in punctuations:
            ####print "CHAR:", char
            no_punct = no_punct + char
        
    return no_punct

# STRIP PUNCTUATION & notify if found
def strip_punctuation_bool(word):
    # define punctuations
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~_'''
    my_str = word

    # remove punctuations from the string
    no_punct = ""
    punct=""
    position=""
    punct_bool=False
    for char in my_str:
        if char not in punctuations:
            ### # ##print "CHAR:", char
            no_punct = no_punct + char
            
        else:
            punct_bool=True
            punct += char
            #no_punct = no_punct+' '

    ### # ##print "word:",no_punct,"punct:", punct
    return {'word':no_punct,'punct':punct, 'punct_bool':punct_bool}

# convert the cmudict prondict into just numbers
def strip_letters(ls):
    ###print "strip_letters"
    nm = ''
    for ws in ls:
        ###print "ws",ws
        for ch in list(ws):
            ###print "ch",ch
            if ch.isdigit():
                nm=nm+ch
                ###print "ad to nm",nm, type(nm)
    return nm



# clean up date of birth diverse formatting
def process_dob(poet_dob):

    birth = '0000'
    death = '0000'

    # empty
    if poet_dob == '':
        birth = '0000'
        death = '0000'

    # form "b. 1964"
    if poet_dob.split(".")[0]=='b' or poet_dob.split(".")[0]=='b.':
        birth=poet_dob.split(".")[1]
        death ='0000'

    # form "1964-2022"
    elif len(poet_dob.split("-"))>1:
        birth=poet_dob.split("-")[0]
        death =poet_dob.split("-")[1]

    return birth,death


# correct errors in reading json
def json_parse(fileobj, decoder=JSONDecoder(), buffersize=2048):
    buffer = ''
    for chunk in iter(partial(fileobj.read, buffersize), ''):
         chunk.strip()
         buffer += chunk
         while buffer:
             try:
                 result, index = decoder.raw_decode(buffer)
                 yield result
                 buffer = buffer[index:]
             except ValueError:
                 # Not enough data to decode, read more
                 break


# remove annoying characters
chars = {
    '\xc2\x82' : ',',        # High code comma
    '\xc2\x84' : ',,',       # High code double comma
    '\xc2\x85' : '...',      # Tripple dot
    '\xc2\x88' : '^',        # High carat
    '\xc2\x91' : '\x27',     # Forward single quote
    '\xc2\x92' : '\x27',     # Reverse single quote
    '\xc2\x93' : '\x22',     # Forward double quote
    '\xc2\x94' : '\x22',     # Reverse double quote
    '\xc2\x95' : ' ',
    '\xc2\x96' : '-',        # High hyphen
    '\xc2\x97' : '--',       # Double hyphen
    '\xc2\x99' : ' ',
    '\xc2\xa0' : ' ',
    '\xc2\xa6' : '|',        # Split vertical bar
    '\xc2\xab' : '<<',       # Double less than
    '\xc2\xbb' : '>>',       # Double greater than
    '\xc2\xbc' : '1/4',      # one quarter
    '\xc2\xbd' : '1/2',      # one half
    '\xc2\xbe' : '3/4',      # three quarters
    '\xca\xbf' : '\x27',     # c-single quote
    '\xcc\xa8' : '',         # modifier - under curve
    '\xcc\xb1' : '' ,        # modifier - under line
    '\xe2\x80\x99': '\'',   # apostrophe
    '\xe2\x80\x94': '--'    # em dash \xe2\x80\x99
    #'\xe2':"\'"

}


# USAGE new_str = re.sub('(' + '|'.join(chars.keys()) + ')', replace_chars, text)
def replace_chars(match):
    char = match.group(0)
    return chars[char]


heres=["nowhere","somewhere","there","anywhere","not here","here"]

#####################
# ALERT  @$!
#####################

# HOW_TO put all utilities into subdirectory and call them in: sys.path.insert(0,'/utilities')
#import profanityFilter_ARR.py
curses = [
'2g1c',
'2 girls 1 cup',
'acrotomophilia',
'anal',
'anilingus',
'anus',
'arsehole',
'ass',
'asshole',
'assmunch',
'auto erotic',
'autoerotic',
'babeland',
'baby batter',
'ball gag',
'ball gravy',
'ball kicking',
'ball licking',
'ball sack',
'ball sucking',
'bangbros',
'bareback',
'barely legal',
'barenaked',
'bastardo',
'bastinado',
'bbw',
'bdsm',
'beaver cleaver',
'beaver lips',
'bestiality',
'bi curious',
'big black',
'big breasts',
'big knockers',
'big tits',
'bimbos',
'birdlock',
'bitch',
'black cock',
'blonde action',
'blonde on blonde action',
'blow j',
'blow your l',
'blue waffle',
'blumpkin',
'bollocks',
'bondage',
'boner',
'boob',
'boobs',
'booty call',
'brown showers',
'brunette action',
'bukkake',
'bulldyke',
'bullet vibe',
'bung hole',
'bunghole',
'busty',
'butt',
'buttcheeks',
'butthole',
'camel toe',
'camgirl',
'camslut',
'camwhore',
'carpet muncher',
'carpetmuncher',
'chocolate rosebuds',
'circlejerk',
'cleveland steamer',
'clit',
'clitoris',
'clover clamps',
'clusterfuck',
'cock',
'cocks',
'coprolagnia',
'coprophilia',
'cornhole',
'cum',
'cumming',
'cunnilingus',
'cunt',
'darkie',
'date rape',
'daterape',
'deep throat',
'deepthroat',
'dick',
'dildo',
'dirty pillows',
'dirty sanchez',
'dog style',
'doggie style',
'doggiestyle',
'doggy style',
'doggystyle',
'dolcett',
'domination',
'dominatrix',
'dommes',
'donkey punch',
'double dong',
'double penetration',
'dp action',
'eat my ass',
'ecchi',
'ejaculation',
'erotic',
'erotism',
'escort',
'ethical slut',
'eunuch',
'faggot',
'fecal',
'felch',
'fellatio',
'feltch',
'female squirting',
'femdom',
'figging',
'fingering',
'fisting',
'foot fetish',
'footjob',
'frotting',
'fuck',
'fucking',
'fuck buttons',
'fudge packer',
'fudgepacker',
'futanari',
'g-spot',
'gang bang',
'gay sex',
'genitals',
'giant cock',
'girl on',
'girl on top',
'girls gone wild',
'goatcx',
'goatse',
'gokkun',
'golden shower',
'goo girl',
'goodpoop',
'goregasm',
'grope',
'group sex',
'guro',
'hand job',
'handjob',
'hard core',
'hardcore',
'hentai',
'homoerotic',
'honkey',
'hooker',
'hot chick',
'how to kill',
'how to murder',
'huge fat',
'humping',
'incest',
'intercourse',
'jack off',
'jail bait',
'jailbait',
'jerk off',
'jigaboo',
'jiggaboo',
'jiggerboo',
'jizz',
'juggs',
'kike',
'kinbaku',
'kinkster',
'kinky',
'knobbing',
'leather restraint',
'leather straight jacket',
'lemon party',
'lolita',
'lovemaking',
'make me come',
'male squirting',
'masturbate',
'menage a trois',
'milf',
'missionary position',
'motherfucker',
'mound of venus',
'mr hands',
'muff diver',
'muffdiving',
'muthafucka',
'nambla',
'nawashi',
'negro',
'neonazi',
'nig nog',
'nigga',
'nigger',
'nimphomania',
'nipple',
'nipples',
'nsfw images',
'nude',
'nudity',
'nympho',
'nymphomania',
'octopussy',
'omorashi',
'one cup two girls',
'one guy one jar',
'orgasm',
'orgy',
'paedophile',
'panties',
'panty',
'pedobear',
'pedophile',
'pegging',
'penis',
'phone sex',
'piece of shit',
'piss pig',
'pissing',
'pisspig',
'playboy',
'pleasure chest',
'pole smoker',
'ponyplay',
'poof',
'poop chute',
'poopchute',
'porn',
'porno',
'pornography',
'prince albert piercing',
'pthc',
'pubes',
'pussy',
'queaf',
'raghead',
'raging boner',
'rape',
'raping',
'rapist',
'rectum',
'reverse cowgirl',
'rimjob',
'rimming',
'rosy palm',
'rosy palm and her 5 sisters',
'rusty trombone',
's&m',
'sadism',
'scat',
'schlong',
'scissoring',
'semen',
'sex',
'sexo',
'sexy',
'shaved beaver',
'shaved pussy',
'shemale',
'shibari',
'shit',
'shota',
'shrimping',
'slanteye',
'slut',
'smut',
'snatch',
'snowballing',
'sodomize',
'sodomy',
'spic',
'spooge',
'spread legs',
'strap on',
'strapon',
'strappado',
'strip club',
'style doggy',
'suck',
'sucks',
'suicide girls',
'sultry women',
'swastika',
'swinger',
'tainted love',
'taste my',
'tea bagging',
'threesome',
'throating',
'tied up',
'tight white',
'tit',
'tits',
'titties',
'titty',
'tongue in a',
'topless',
'tosser',
'towelhead',
'tranny',
'tribadism',
'tub girl',
'tubgirl',
'tushy',
'twat',
'twink',
'twinkie',
'two girls one cup',
'undressing',
'upskirt',
'urethra play',
'urophilia',
'vagina',
'venus mound',
'vibrator',
'violet blue',
'violet wand',
'vorarephilia',
'voyeur',
'vulva',
'wank',
'wet dream',
'wetback',
'white power',
'women rapping',
'wrapping men',
'wrinkled starfish',
'xx',
'xxx',
'yaoi',
'yellow showers',
'yiffy',
'zoophilia']




#
# HELPR FUNCTION: FIND A SIMILAR WORD OF SIMILAR SIZE
#

#
# HELPR FUNCTION: FIND A SIMILAR WORD OF SIMILAR SIZE
#

def find_synset_word(word):
    

    wordstring=word

    # get rid of punctuation
    #wordstring.translate(None, string.punctuation)
    word_punct = strip_punctuation_bool(word)
    word = word_punct['word']
    punct = word_punct['punct']

    syllableSize=syllables_en.count(word)

    synsets = wn.synsets(word)
    shuffle(synsets)
    #print word,"synset:",synsets


    replacement_candidates = []

    for syns in synsets:

        lemmas =  syns.lemma_names
        ## # ##print "LEMMAS:",lemmas
        ## # ##print "hypernyms:",syns.hypernyms()
        ## # ##print "hyponyms:",syns.hyponyms()
        ## # ##print "holonyms:",syns.member_holonyms()
        ## # print syns,"antonyms:",syns.lemmas[0].antonyms()
        
        for w in lemmas:
            replacement_candidates.append(w)

        for w in syns.hyponyms():
            replacement_candidates.append(w.name.split(".")[0])

        # for w in syns.hypernyms():
        #     replacement_candidates.append(w.name.split(".")[0])

        # for w in syns.member_holonyms():
        #     replacement_candidates.append(w.name.split(".")[0])

        # for w in syns.member_meronyms():
        #     replacement_candidates.append(w.name.split(".")[0])

        # for w in syns.member_synonyms():
        #     replacement_candidates.append(w.name.split(".")[0])

        for w in syns.lemmas[0].antonyms():
            replacement_candidates.append(w.name.split(".")[0])

        ## # ##print "replacement_candidates:",replacement_candidates
        shuffle(replacement_candidates)

        for wordstring in replacement_candidates:
            #find an approximate matchb
            #print "wordstring in name:",wordstring
            if (approx_equal(wordstring,word) and wordstring.lower() != word.lower() and len(wordstring)>len(word)):
                #print "SYNSET approx_equal:",word,wordstring
                return wordstring+punct
            #len same, word not
            elif(len(wordstring) == len(word) and wordstring.lower() != word.lower()):
                #print "SYNSET len same, word not:",word,wordstring
                return wordstring+punct
            elif word.lower() not in wordstring.lower() and wordstring.lower() not in word.lower():
                #print word, "SYNSET not in:",wordstring+punct
                return wordstring+punct

            # elif(syllables_en.count(wordstring) == syllableSize and wordstring.lower() != word.lower() and len(word)):
            #     ##print "SYNSET syllable same, word not:",word,wordstring
            #     return wordstring+punct


        # nothing found yet, look inside ...
        #s = wordnet.synsets(word)             
        replacement_candidates = []
        for w in syns.attributes():
            ##print "attributes :",w.name.split(".")[0]
            replacement_candidates.append(w.name.split(".")[0])
        for w in syns.similar_tos():
            ##print "similar_tos:",w.name.split(".")[0]
            replacement_candidates.append(w.name.split(".")[0])
        for w in syns.substance_meronyms():
            ##print "substance_meronyms :",w.name.split(".")[0]
            replacement_candidates.append(w.name.split(".")[0])
        for w in syns.entailments():
            ##print "entailments :",w.name.split(".")[0]
            replacement_candidates.append(w.name.split(".")[0])
        # print word,"nothing found yet, look inside ...",replacement_candidates

        replacement_candidates.sort(key = len)
        for wordstring in replacement_candidates:
            #print "trying :",wordstring
            if wordstring not in stopwords.words('english') and wordstring not in personal_pronouns and wordstring not in word:
                ##print "SYNSET final choice:",word,wordstring
                return wordstring+punct


    ##print "SYNSET escape case, return original:",word
    return    wordstring






#########################
# HELPER FUNCTIONs      #
#########################

def pluralize_singularize(word,prev_word):
    if "thing" in word:
        print word,prev_word
    if "these" in prev_word:
        return pluralize(word)
    elif "this" in prev_word:
        return singularize(word)
    else:
        return word

# TEST FOR APPROX. EQUIVALENCE
def approx_equal(self, other, delta=4):
    count = abs(len(self) - len(other))
    for c,k in zip(self, other):
        count += c != k
    return count <= delta


#Check whether 'str' contains ANY punctuation
def containsAnyPunct(str):
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~_'''
    return 1 in [c in str for c in punctuations]

def isAllPunct(s):
    return all(c in string.punctuation for c in s)

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

# replace digits with other digits...
def replaceNumbers(inputString):
    outputString =''
    for char in inputString:
        if char.isdigit():
            char = random.randrange(9)
            ## # ##print "DIGIT",char
        outputString +=str(char)
    return outputString

# STRIP _
def strip_underscore(word):
    # define punctuations
    punctuations = '''_'''
    my_str = word

    # remove _ from the string
    no_punct = ""
    for char in my_str:
        if char not in punctuations:
            ### # ##print "CHAR:", char
            no_punct = no_punct + char
        else:
            no_punct = no_punct+' '

    ### # ##print "word:",no_punct,"punct:", punct
    return no_punct


# 
def isGarbageInWord_bool(word):
    for l in word.split():
        for ch in chars:
            if l==ch:
                return True
    return False


def moveBeginAndEndPunctuationFromStrToString(source,destination):

    my_str = source
    replacement=destination

    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~_'''

    # remove punctuations from the string
    no_punct = ""
    punct=""
    position=""
    punct_bool=False
    cnt=0
    for char in my_str:
        if char not in punctuations:
            ### # ##print "CHAR:", char
            no_punct = no_punct + char
        else:
            punct_bool=True
            punct += char
            position += str(cnt)+"~"
        cnt+=1


    if len(punct)>0:
        #print position
        posi=position.split("~")
        punc=list(punct)
        for p in posi:
            if len(p)>0:
                if int(p)==0:
                    replacement = punc[posi.index(p)] + replacement
                # get period before quotation marks
                if int(p)==(len(my_str)-2) and punc[posi.index(p)] ==".":
                    replacement = replacement + punc[posi.index(p)] 
                if int(p)==(len(my_str)-1):
                    if "'" not in punc[posi.index(p)]:
                        replacement = replacement + punc[posi.index(p)] 
    
    #print source,replacement              
    return replacement 






############################
############################


#
# HELPR FUNCTION: FIND A SIMILAR WORD OF SIMILAR SIZE
#

#
# HELPR FUNCTION: FIND A SIMILAR WORD OF SIMILAR SIZE
#

def synset_creeley(word):
    

    wordstring=word

    # get rid of punctuation
    #wordstring.translate(None, string.punctuation)
    word_punct = strip_punctuation_bool(word)
    word = word_punct['word']
    punct = word_punct['punct']

    syllableSize=syllables_en.count(word)

    synsets = wn.synsets(word)
    shuffle(synsets)
    #print word,"synset:",synsets


    replacement_candidates = []

    for syns in synsets:

        lemmas =  syns.lemma_names
        # print "word:",word
        # print "LEMMAS:",lemmas
        # print "hypernyms:",syns.hypernyms()
        # print "hyponyms:",syns.hyponyms()
        # print "holonyms:",syns.member_holonyms()
        # print syns,"antonyms:",syns.lemmas[0].antonyms()
        
        for w in lemmas:
            replacement_candidates.append(w)

        for w in syns.hyponyms():
            replacement_candidates.append(w.name.split(".")[0])

        for w in syns.hypernyms():
            replacement_candidates.append(w.name.split(".")[0])

        for w in syns.member_holonyms():
            replacement_candidates.append(w.name.split(".")[0])

        for w in syns.member_meronyms():
            replacement_candidates.append(w.name.split(".")[0])

        # for w in syns.member_synonyms():
        #     replacement_candidates.append(w.name.split(".")[0])

        for w in syns.lemmas[0].antonyms():
            replacement_candidates.append(w.name.split(".")[0])

        for w in syns.attributes():
            replacement_candidates.append(w.name.split(".")[0])

        for w in syns.similar_tos():
            replacement_candidates.append(w.name.split(".")[0])

        for w in syns.substance_meronyms():
            replacement_candidates.append(w.name.split(".")[0])

        for w in syns.entailments():
            replacement_candidates.append(w.name.split(".")[0])

        replacement_candidates.sort(key=len)

        #print word,replacement_candidates
        if replacement_candidates[0] is not None:
            return replacement_candidates[0]
        else:
            return word



