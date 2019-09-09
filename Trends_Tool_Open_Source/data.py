import mailbox
import requests
import pickle
import bs4
import io
import csv
import re
import gensim
import datetime

class Data () :
    def __init__(self, cont):
        self.c = cont
        self.db = load('DATABASE')
    def getAllAttribute(self, attr) :
        return getAllAttribute(self.db, attr)
    def save(self) :
        tagTheData(self.db)
        dump(self.db, 'DATABASE')
    def createNewConcept(self, name, parent) :
        db = self.db
        concepts = db['concepts']
        if name in concepts.keys() :
            raise Exception('Tried to make already excisting concept')
        concepts[name] = {'parent': parent, 'keyWords': []}
    def addKeyword(self, concept, keyword) :
        db = self.db
        if keyword in db['keyWords'] : raise Exception('Tried to add excisting keyWord.')
        concepts = db['concepts']
        if concept not in concepts.keys() : raise Exception('No such concept to add' + \
            'keywords: ' + str(keywords) + ' to.')
        concepts[concept]['keyWords'].append(keyword)
        db['keyWords'].append(keyword)
    def newSearch(self, name) :
        makeCustomSource(self.db, name)
    def addBadKeyWord(self, badKW) :
        db = self.db
        db['keyWords'].append(badKW)
    def getKeywords(self, source) :
        db = self.db
        if source not in db['sources']['kw:count'].keys() and source != 'Bigrams' and source != 'Search':
            raise Exception('Couldnt find source to get key words for source: ' + source)
        if source == 'Bigrams' :
            kwsRaw =  db['sources']['bigramCount']
        elif source == 'Search' :
            keyWords = list(db['sources']['search'].keys())
            keyWordsWithCounts = []
            for keyWord in keyWords :
                if keyWord not in db['keyWords'] :
                    keyWordsWithCounts.append((keyWord, len(db['sources']['search'][keyWord])))
            return keyWordsWithCounts
        else :
            kwsRaw = db['sources']['kw:count'][source]
        res = []
        for kw in kwsRaw :
            if kw[0] not in db['keyWords'] : res.append(kw)
        return res
    def getDataPiece(self, source, kw) :
        db = self.db
        if source == 'Bigrams' :
            allegible = db['sources']['bigramToDataPieces'][kw]
        elif source == 'Search' :
            allegible = db['sources']['search'][kw]
        elif source.split(':')[0] == 'TopicModel':
            print('Source: ' + str(source))
            print('KW: ' + str(kw))
            return db['topicModelling'][source.split(':')[1]]['topics'][kw]
        else :
            allegible = db['sources']['kw:dataIndexes'][source][kw]
        import random
        return makeDataSummary(db, allegible[random.randint(0,len(allegible)-1)])
    def navigate(self, extention) :
        db = self.db
        if extention == '' :
            extention = 'Selective_laser_melting'
        return wikipediaImport(db, extention)
    def removeConcept(self, name):
        db = self.db
        concept = db['concepts'][name]
        for kw in concept['keyWords'] :
            while kw in db['keyWords'] :
                db['keyWords'].remove(kw)
        del db['concepts'][name]
    def removeKW(self, name, parent) :
        self.db['keyWords'].remove(name)
        self.db['concepts'][parent]['keyWords'].remove(name)
    def init(self) :
        db = self.db
        initSave(db)
        self.createNewConcept('Application', None)
        self.createNewConcept('Organisation', 'Application')
        self.createNewConcept('Material', 'Application')
        self.createNewConcept('Technique', 'Application')
        self.createNewConcept('Market', 'Application')
        self.createNewConcept('Industry', 'Market')
        self.createNewConcept('Geographical', 'Market')
        self.save()
    def conceptPlotInfo(self, conc) :
        return plotCount(self.db, conc)
    def topicModel(self, concept, numOfTopics) :
        topicModelling(self.db, concept, (datetime.date(2013, 1, 1),
                        datetime.date(2019, 6, 1)), numOfTopics)


#------------------------------Info handelling------------------------------
def countBigrams():
    #we need a dict that contains the count of each bigram
    db = load('DATABASE')
    bigramData = getAllAttribute(db, 'bigrams')
    bigramToDataPieces = {}
    bigramCount = {}
    #we need a dict with bigrams to the data pieces that contain the bigram
    for piece in bigramData :
        index = piece[0]
        bigrams = piece[1]
        for bigram in bigrams :
            if bigram not in bigramToDataPieces.keys():
                bigramToDataPieces[bigram] = [index]
            else :
                bigramToDataPieces[bigram].append(index)
            if bigram not in bigramCount.keys() :
                bigramCount[bigram] = 1
            else :
                bigramCount[bigram] += 1
    #filter out the 1 counts
    for bigram in list(bigramCount.keys()) :
        if bigramCount[bigram] < 5 :
            del bigramCount[bigram]
    #sorting to a sorted list
    import operator
    bigramCount = sorted(bigramCount.items(),key = operator.itemgetter(1),reverse = True)
    print(bigramCount)
    db['sources']['bigramCount'] = bigramCount
    db['sources']['bigramToDataPieces'] = bigramToDataPieces
    dump(db, 'DATABASE')

def dbWrap(func) :
    def wrapper(*args, **kwargs) :
        db = load('DATABASE')
        func(db, *args, **kwargs)
        dump(db, 'DATABASE')
    return wrapper
 # data = {num: {property: val}}
def initSave(db) :
    saveOverwrite(db,
        programmingSymbols = ['|', '{', '}', '[', ']','=', ';', "_", "/", "-", "!", "\'", "\""],
        searchStrings = ['additive manfacturing', 'Service logistics 3D printing',\
         'consolidation 3D printing'],
        categories = ["News", "Web"],
        mboxPaths = ["Google Alerts1.mbox", "Google Alerts2.mbox", "Google Alerts3.mbox"],
        alertAdditionalTags = ["(blog)", "(press", "release)", "(registration)"],
        stopWords = ["additive","http","link","error","printing","technology","printed","3d","printing","additive","manufacturing","a","about","above","after","again","against","ain","all","am","an","and","any","are","aren","aren't","as","at","be","because","been","before","being","below","between","both","but","by","can","couldn","couldn't","d","did","didn","didn't","do","does","doesn","doesn't","doing","don","don't","down","during","each","few","for","from","further","had","hadn","hadn't","has","hasn","hasn't","have","haven","haven't","having","he","her","here","hers","herself","him","himself","his","how","i","if","in","into","is","isn","isn't","it","it's","its","itself","just","ll","m","ma","me","mightn","mightn't","more","most","mustn","mustn't","my","myself","needn","needn't","no","nor","not","now","o","of","off","on","once","only","or","other","our","ours","ourselves","out","over","own","re","s","same","shan","shan't","she","she's","should","should've","shouldn","shouldn't","so","some","such","t","than","that","that'll","the","their","theirs","them","themselves","then","there","these","they","this","those","through","to","too","under","until","up","ve","very","was","wasn","wasn't","we","were","weren","weren't","what","when","where","which","while","who","whom","why","will","with","won","won't","wouldn","wouldn't","y","you","you'd","you'll","you're","you've","your","yours","yourself","yourselves","could","he'd","he'll","he's","here's","how's","i'd","i'll","i'm","i've","let's","ought","she'd","she'll","that's","there's","they'd","they'll","they're","they've","we'd","we'll","we're","we've","what's","when's","where's","who's","why's","would","able","abst","accordance","according","accordingly","across","act","actually","added","adj","affected","affecting","affects","afterwards","ah","almost","alone","along","already","also","although","always","among","amongst","announce","another","anybody","anyhow","anymore","anyone","anything","anyway","anyways","anywhere","apparently","approximately","arent","arise","around","aside","ask","asking","auth","available","away","awfully","b","back","became","become","becomes","becoming","beforehand","begin","beginning","beginnings","begins","behind","believe","beside","besides","beyond","biol","brief","briefly","c","ca","came","cannot","can't","cause","causes","certain","certainly","co","com","come","comes","contain","containing","contains","couldnt","date","different","done","downwards","due","e","ed","edu","effect","eg","eight","eighty","either","else","elsewhere","end","ending","enough","especially","et","etc","even","ever","every","everybody","everyone","everything","everywhere","ex","except","f","far","ff","fifth","first","five","fix","followed","following","follows","former","formerly","forth","found","four","furthermore","g","gave","get","gets","getting","give","given","gives","giving","go","goes","gone","got","gotten","h","happens","hardly","hed","hence","hereafter","hereby","herein","heres","hereupon","hes","hi","hid","hither","home","howbeit","however","hundred","id","ie","im","immediate","immediately","importance","important","inc","indeed","index","information","instead","invention","inward","itd","it'll","j","k","keep","keeps","kept","kg","km","know","known","knows","l","largely","last","lately","later","latter","latterly","least","less","lest","let","lets","like","liked","likely","line","little","'ll","look","looking","looks","ltd","made","mainly","make","makes","many","may","maybe","mean","means","meantime","meanwhile","merely","mg","might","million","miss","ml","moreover","mostly","mr","mrs","much","mug","must","n","na","name","namely","nay","nd","near","nearly","necessarily","necessary","need","needs","neither","never","nevertheless","new","next","nine","ninety","nobody","non","none","nonetheless","noone","normally","nos","noted","nothing","nowhere","obtain","obtained","obviously","often","oh","ok","okay","old","omitted","one","ones","onto","ord","others","otherwise","outside","overall","owing","p","page","pages","part","particular","particularly","past","per","perhaps","placed","please","plus","poorly","possible","possibly","potentially","pp","predominantly","present","previously","primarily","probably","promptly","proud","provides","put","q","que","quickly","quite","qv","r","ran","rather","rd","readily","really","recent","recently","ref","refs","regarding","regardless","regards","related","relatively","research","respectively","resulted","resulting","results","right","run","said","saw","say","saying","says","sec","section","see","seeing","seem","seemed","seeming","seems","seen","self","selves","sent","seven","several","shall","shed","shes","show","showed","shown","showns","shows","significant","significantly","similar","similarly","since","six","slightly","somebody","somehow","someone","somethan","something","sometime","sometimes","somewhat","somewhere","soon","sorry","specifically","specified","specify","specifying","still","stop","strongly","sub","substantially","successfully","sufficiently","suggest","sup","sure","take","taken","taking","tell","tends","th","thank","thanks","thanx","thats","that've","thence","thereafter","thereby","thered","therefore","therein","there'll","thereof","therere","theres","thereto","thereupon","there've","theyd","theyre","think","thou","though","thoughh","thousand","throug","throughout","thru","thus","til","tip","together","took","toward","towards","tried","tries","truly","try","trying","ts","twice","two","u","un","unfortunately","unless","unlike","unlikely","unto","upon","ups","us","use","used","useful","usefully","usefulness","uses","using","usually","v","value","various","'ve","via","viz","vol","vols","vs","w","want","wants","wasnt","way","wed","welcome","went","werent","whatever","what'll","whats","whence","whenever","whereafter","whereas","whereby","wherein","wheres","whereupon","wherever","whether","whim","whither","whod","whoever","whole","who'll","whomever","whos","whose","widely","willing","wish","within","without","wont","words","world","wouldnt","www","x","yes","yet","youd","youre","z","zero","a's","ain't","allow","allows","apart","appear","appreciate","appropriate","associated","best","better","c'mon","c's","cant","changes","clearly","concerning","consequently","consider","considering","corresponding","course","currently","definitely","described","despite","entirely","exactly","example","going","greetings","hello","help","hopefully","ignored","inasmuch","indicate","indicated","indicates","inner","insofar","it'd","keep","keeps","novel","presumably","reasonably","second","secondly","sensible","serious","seriously","sure","t's","third","thorough","thoroughly","three","well","wonder", "&"],
        nerTags = ['ORGANIZATION', 'LOCATION', 'PERSON', 'O'],
        concepts = {},
        keyWords = []
    )

def init(name) :
    with open(name, 'wb') as file :
        gt = {}
        pickle.dump(gt, file)

def load(name) :
    print('Loadding: ' + name)
    return pickle.load(open(name, 'rb'))

def database() :
    return load('DATABASE')

def dump(obj, fileName) :
    print('Dumping: ' + fileName)
    with open(fileName, 'wb') as file :
        pickle.dump(obj, file)

def save(db, *args, **kwargs) :
    if 'index' in kwargs.keys() :
        index = kwargs['index']
        if index in db.keys() :
            kwargs.pop('index')
            db[index] = appendDicts(db[index], kwargs)
        else:
            kwargs.pop('index')
            db[index] = kwargs
    else:
        for key, val in kwargs.items() :
            if key in db.keys() :
                raise Exception('Tried to save key: ' + str(key) + ' which was already in db.')
            db[key] = val

def saveOverwrite(db, *args, **kwargs) :
    if 'index' in kwargs.keys() :
        index = kwargs['index']
        kwargs.pop('index')
        for k, v in kwargs.items() :
            db[index][k] = v
    else:
        for key, val in kwargs.items() :
            db[key] = val

def saveSub(sub) :
    def subSaver(db, **kwargs) :
        if not sub in db.keys() :
            db[sub] = {}
        db = db[sub]
        save(db, **kwargs)
    return subSaver

def saveSubOverwrite(sub) :
    def subSaver(db, **kwargs) :
        if not sub in db.keys() :
            db[sub] = {}
        db = db[sub]
        saveOverwrite(db, **kwargs)
    return subSaver

def appendDicts(*dicts) :
    res = dicts[0]
    for d in dicts[1:] :
    #    if type(d[0]) == int :
    #        d = d[1]
        for key, val in d.items() :
            if key in res.keys() :
                raise Exception('Duplicate keys in appendDicts: ' + str(key))
            res[key] = val
    return res

def getAllAttribute(db, attr) :
    res = []
    for num in db['data'].keys():
        try :
            res.append((num, db['data'][num][attr]))
        except :
            continue
    return res

def dbContents(*args) :
    db = database()
    for arg in args :
        db = db[arg]
    res = ""
    for key, val in db.items() :
        res += "%s: len(%s)" %(str(key), str(len(val))) + '\n'
    return res

def remove(db, key) :
    db.pop(key)

def removeSub(db, sub) :
    def subRemover(key) :
        db = db[sub]
        db.pop(key)
    return subRemover
#------------------------------Main Methods------------------------------
#first parse for links
@dbWrap
def parseAlerts(db) :
    linkIndex = 1
    mboxLocations = db['mboxPaths']
    for mboxLocation in mboxLocations :
        mbox = mailbox.mbox(mboxLocation)
        print("Now parsing mbox: "  + mboxLocation)
        for message in mbox:
            if message == None : continue
            linkIndex = mineAlert(db, message, linkIndex)
        mbox.close()
    assighnTimes(db)

def cleanCleanedHtml(alert) :
    text = alert['title'] + '\n' +\
    alert['source'] + '\n' +\
    alert['exampleText']
    if not alert['isBroken'] :
        text += '\n' + alert['cleanedHtml']
    text = text.replace('\\', 'x')
    text = re.sub('(xx(\d|\w)(\d|\w)){2,}', '', text)
    text = re.sub("\'", "", text)
    text = re.sub("\n", "", text)
    text = re.sub("\r", "", text)
    return text

def mineAlert(db, message, index) :
    body = str(getBody(message))
    blocks = makeBlocks(body)
    info = processAlertBlocks(db, blocks)
    for result in info :
        if result == None or index == None : continue
        saveSub('data')(db,
            message = message,
            category = result[0],
            searchString = result[1],
            title = result[2],
            source = result[3],
            additionalTag = result[4],
            exampleText = result[5],
            linkRaw = result[6],
            link = result[6].split("=t&url=", 1)[1].split("&ct=ga", 1)[0],
            index = index,
            dateReceived = message['Date']
            )
        index+=1
    return index
#get info from links
@dbWrap
def crawl(db) :
    data = db['data']
    for index in data.keys() :
        browsed = browse(index, data[index]['link'])
        saveSubOverwrite('data')(db, index = index, crawled = browsed[1], isBroken = browsed[0])

def browse(index, link) :
    isBroken = False
    res = ''
    try :
        res = requests.get(link, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})
        print("link " + str(index) + ": " + str(link) + " recorded.")
    except Exception as err:
        print("link " + str(index) + " has error: " + str(err))
        res = str(err)
        isBroken = True
    return (isBroken, res)
#clean the html and remove duplicates
@dbWrap
def parseHTML(db) :
    markDuplicates(db)
    for p in db['data'].keys() :
        print('Parsing data piece: ' + str(p))
        data = db['data'][p]
        if 'isDuplicate' in data.keys(): continue
        if data['isBroken'] : continue
        saveSub('data')(db, index = p, cleanedHtml = clean(db, p))

def clean(db, index) :
    data = db['data']
    progSymbPercAllowed = 4
    minimumAmmountOfMatches = 1
    minWords = 2
    exampleTextWords = removeStopWords(db, data['exampleText'])
    for word in data['source'].split() :
        exampleTextWords = exampleTextWords.replace(word, "")
    exampleTextWords = exampleTextWords.split()
    parts = specialSplit(data['crawled'].text)
    assesed = []
    for part in parts :
        if part == '' :
            continue
        #determine parameters
        progPerc = (programmingSymbolsCount(db, part)/len(part)) * 100
        words = len(removeStopWords(db, part).split())
        matches = 0
        for word in exampleTextWords :
            if word in part :
                matches+=1
        if matches >= minimumAmmountOfMatches and progPerc < progSymbPercAllowed \
            and words >= minWords:
            decision = "@"
        elif progPerc < progSymbPercAllowed and words >= minWords:
            decision = "/"
        else :
            decision = "_"
        assesed.append((part, decision))
    return coreOf(assesed)

def markDuplicates(db) :
    allLinks = getAllAttribute(db, 'link')
    toDelete = []
    for first in allLinks :
        link1 = first[1]
        index1 = first[0]
        searchString1 = db['data'][index1]['searchString']
        for second in allLinks :
            link2 = second[1]
            index2 = second[0]
            searchString2 = db['data'][index2]['searchString']
            if index1 != index2 and link1 == link2 and \
            first not in toDelete and second not in toDelete :
                print("Found duplicate: " + str(index1) + " and " + \
                str(index2) + " have the same link.")
                if searchString1 != searchString2 :
                    found = False
                    while not found :
                        for searchString in db['searchStrings'] : #to replace for dynamicnes
                            if searchString1 == searchString :
                                toDelete.append(first)
                                found = True
                            elif searchString2 == searchString :
                                toDelete.append(second)
                                found = True
                else :
                    toDelete.append(first)
    for p in toDelete :
        print('Marking data piece: ' + str(p[0]) + ' as duplicate')
        saveSubOverwrite('data')(db, index = p[0], isDuplicate = True)
#moddeling
@dbWrap
def NERTagAll(db):
    import modelling as m
    for p in db['data'].keys() :
        data = db['data'][p]
        print('Parsing data piece: ' + str(p))
        if 'isDuplicate' in data.keys(): continue
        if data['isBroken'] : continue
        saveSub('data')(db, index = p, NERTags = m.tag(data['cleanedHtml']))

def makeSourcesFromNer() :
    db = load('DATABASE')
    nerTags = db['nerTags']
    taggedData = getAllAttribute(db, 'NERTags')
    db['sources'] = {}
    res = {}
    #the unique key words per data piece per ner tag
    for tag in nerTags :
        res[tag] = {}
    for piece in taggedData :
        index = piece[0]
        tagList = piece[1]
        for tag in tagList :
            word = tag[0]
            nerTag = tag[1]
            if index in res[nerTag].keys() :
                if word not in res[nerTag][index] :
                    res[nerTag][index].append(word)
            else :
                res[nerTag][index] = [word]
    # the data pieces that contain a keyword per ner tag
    res3 = {}
    for nerTag, dataDict in res.items() :
        res3[nerTag] = {}
        for index, keyWordList in dataDict.items() :
            for word in keyWordList :
                if word in res3[nerTag].keys():
                    res3[nerTag][word].append(index)
                else :
                    res3[nerTag][word] = [index]
    db['sources']['kw:dataIndexes'] = res3
    # the ammount of data pieces that contain a key word per ner tag
    res2 = {}
    for tag in res.keys() :
        res2[tag] = {}
        for index, wordList in res[tag].items() :
            for word in wordList :
                if word in res2[tag].keys() :
                    res2[tag][word] += 1
                else:
                    res2[tag][word] = 1
    #filter out the 1 counts
    for tag in list(res2.keys()) :
        wordDict = res2[tag]
        for word in list(wordDict.keys()) :
            count = wordDict[word]
            if count == 1 :
                del wordDict[word]
    #sorting to a sorted list
    for tag, wordDict in res2.items() :
        import operator
        res2[tag] = sorted(wordDict.items(),key = operator.itemgetter(1),reverse = True)
    db['sources']['kw:count'] = res2
    #print(res2)
    dump(db, 'DATABASE')

def wikipediaImport(db, extention) :
    link = 'https://en.wikipedia.org/wiki/' + extention
    bannedWikiWords = ['error', 'file', 'clarify', 'Citation_needed', 'Words_to_watch', 'tal_object_identifier']
    import re
    try :
        res = requests.get(link, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}).text
    except Exception as err:
        print('Error: ' + err)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(res, 'html.parser')
    temp = soup.find(id='mw-content-text').div.find_all([re.compile("^h"), 'p' ])
    linksSoup = soup.find(id='mw-content-text').div.find_all(href=True)
    links = []
    for linkTag in linksSoup :
        href = linkTag['href']
        use = True
        for string in bannedWikiWords :
            if string in href : use = False
        if '/wiki/' in href and use:
            new = href.split('/')
            links.append(new[len(new)-1])
        links = list(dict.fromkeys(links))
    res = {}
    res['links'] = links
    wiki = {}
    head = 'General info'
    curr = ''
    for tag in temp :
        if 'h' in tag.name :
            if curr != '' :
                wiki[head] = curr + '\n\n'
            head = tag.get_text()
            head = head.replace('[edit]', '')
            curr = ''
        else :
            curr += tag.get_text()
    res['text'] = wiki
    stopWords = db['stopWords']
    keyWords = {}
    for key, value in res['text'].items() :
        if key != 'links' :
            textWords = value.split()
            for word in textWords :
                if word in stopWords :
                    textWords = remove_values_from_list(textWords, word)
            keyWords[key] = textWords
    res['keyWords'] = keyWords
    name = link.split('/')
    name = name[len(name)-1]
    #db['sources']['wikipedia'][name] =
    return res

@dbWrap
def topicModellingPrepAll(db) :
    import spacy
    import pandas as pd
    data = db['data']
    nlp = spacy.load('en', disable=['parser', 'ner'])
    for index, attrs in data.items() :
        if 'isDuplicate' in data.keys(): continue
        if data['isBroken'] : continue
        res = attrs['cleanedHtml']
        res = res.lower()
        res = lowered.replace(',', '')
        res = res.replace('.', '')
        res = res.replace(':', '')
        res = res.replace('\"', '')
        res = res.replace('\'', '')
        res = res.replace('(', '')
        res = res.replace(')', '')
        res = res.replace('!', '')
        res = res.replace('/', '')
        res = res.split()
        res = [re.sub('\S*@\S*\s?', '', sent) for sent in res]
        #how to lemmatize
        doc = nlp(string)
        return " ".join([token.lemma_ for token in doc])

#['message', 'category', 'searchString', 'title', 'source', 'additionalTag',
#'exampleText', 'linkRaw', 'link', 'dateReceived', 'crawled', 'isBroken']

def writeDataCsv(db):
    data = db['data']
    rowsToWrite = [['message', 'category', 'searchString', 'title', 'dateReceived', \
    'link', 'exampleText', 'additionalTag', 'source', 'isBroken']]
    for index, content in data.items() :
        this = []
        this.append(content['message'])
        this.append(content['category'])
        this.append(content['searchString'])
        this.append(content['title'])
        this.append(str(content['dateReceived'].strftime("%m/%d/%Y, %H:%M:%S")))
        this.append(content['link'])
        this.append(content['exampleText'])
        this.append(content['additionalTag'])
        this.append(content['source'])
        broken = content['isBroken']
        this.append(str(broken))
        rowsToWrite.append(this)
    saveAsExcel('data', rowsToWrite)

def writeErrorReportCsv(db):
    data = db['data']
    working = 0
    broken = 0
    uncleanable = 0
    duplicates = 0
    errors = {}
    yearMonth = {}
    for index, contents in data.items():
        month = contents['dateReceived'].strftime('%m-%Y')
        if contents['isBroken']:
            broken += 1
            if month not in yearMonth.keys() :
                yearMonth[month] = [1,0,0,0]
            else :
                yearMonth[month][0] += 1
            if contents['crawled'] not in errors.keys() :
                errors[contents['crawled']] = 1
            else :
                errors[contents['crawled']] += 1
        else :
            if 'isDuplicate' in contents.keys() :
                duplicates += 1
                if month not in yearMonth.keys() :
                    yearMonth[month] = [0,1,0,0]
                else :
                    yearMonth[month][1] += 1
            elif contents['cleanedHtml'] == '' :
                uncleanable += 1
                if month not in yearMonth.keys() :
                    yearMonth[month] = [0,0,1,0]
                else :
                    yearMonth[month][2] += 1
            else :
                if month not in yearMonth.keys() :
                    yearMonth[month] = [0,0,0,1]
                else :
                    yearMonth[month][3] += 1
                working += 1
    del yearMonth['05-2019']
    rowsToWrite = []
    rowsToWrite.append(['Working', 'Broken', 'uncleanable', 'duplicates'])
    rowsToWrite.append([str(working), str(broken), str(uncleanable), str(duplicates)])
    rowsToWrite.append([])
    rowsToWrite.append(['error', 'count'])
    for error, count in errors.items():
        rowsToWrite.append([error, str(count)])
    rowsToWrite.append([])
    rowsToWrite.append(['month-year', 'broken', 'duplicates', 'uncleanable', 'working'])
    for time, quad in yearMonth.items():
        rowsToWrite.append([time, str(quad[0]), str(quad[1]), str(quad[2]), str(quad[3])])
    saveAsExcel('error report', rowsToWrite)

def writeAllTheCsv(db) :
    writeDataCsv(db)
    writeErrorReportCsv(db)

def makeCustomSource(db, string) :
    data = getAllAttribute(db, 'preparedData')
    if 'search' not in db['sources'].keys():
        db['sources']['search'] = {}
    matches = []
    for p in data :
        index = p[0]
        preppedData = p[1]
        if string in preppedData :
            matches.append(index)
    db['sources']['search'][string] = matches

def tagTheData(db) :
    data = db['data']
    concepts = db['concepts']
    organisation = getChildren(concepts, 'Organisation') + ['Organisation']
    geographical = getChildren(concepts, 'Geographical') + ['Geographical']
    rest = [x for x in concepts.keys() if x not in organisation + geographical]
    print(rest)
    for concept in organisation :
        concepts[concept]['matches'] = []
        keyWords = concepts[concept]['keyWords']
        for keyWord in keyWords :
            for index, content in data.items():
                if 'NERTags' not in content.keys()  or 'bigrams' not in content.keys() : continue
                if '_' in keyWord :
                    for tag in content['bigrams'] :
                        if tag == keyWord :
                            concepts[concept]['matches'].append(index)
                else :
                    for tag in content['NERTags'] :
                        if tag[0] == keyWord and tag[1] == 'ORGANIZATION' :
                            concepts[concept]['matches'].append(index)
        concepts[concept]['matches'] = list(set(concepts[concept]['matches']))
        print('Parsed: ' + concept)
    for concept in geographical :
        concepts[concept]['matches'] = []
        keyWords = concepts[concept]['keyWords']
        for keyWord in keyWords :
            for index, content in data.items():
                if 'NERTags' not in content.keys()  or 'bigrams' not in content.keys() : continue
                if '_' in keyWord :
                    for tag in content['bigrams'] :
                        if tag == keyWord :
                            concepts[concept]['matches'].append(index)
                else :
                    for tag in content['NERTags'] :
                        if tag[0] == keyWord and tag[1] == 'LOCATION' :
                            concepts[concept]['matches'].append(index)
        concepts[concept]['matches'] = list(set(concepts[concept]['matches']))
        print('Parsed: ' + concept)
    for concept in rest :
        concepts[concept]['matches'] = []
        keyWords = concepts[concept]['keyWords']
        for keyWord in keyWords :
            keyWord = keyWord.lower()
            for index, content in data.items():
                if 'preparedData' not in content.keys() or 'bigrams' not in content.keys(): continue
                if '_' in keyWord :
                    for tag in content['bigrams'] :
                        if tag == keyWord :
                            concepts[concept]['matches'].append(index)
                else :
                    if keyWord in content['preparedData'] :
                        concepts[concept]['matches'].append(index)
        concepts[concept]['matches'] = list(set(concepts[concept]['matches']))
        print('Parsed: ' + concept)

def getChildren(concepts, parentConceptName):
    filter = parentConceptName
    conceptDict = concepts
    filterList = [filter]
    while True :
        subjects = []
        for key, cont in conceptDict.items():
            if cont['parent'] in filterList and key not in filterList:
                subjects.append(key)
        filterList.extend(subjects)
        if len(subjects) == 0 : break
    return filterList

def printConceptMatchCount(db):
    for conceptName, contents in db['concepts'].items() :
        count =  str(len(contents['matches']))
        print(conceptName + ': ' + count)
        print(contents['keyWords'])

def topicModelling(db, parent, timeFrame, topics) :
    concepts = db['concepts']
    conceptsToUse = []
    conceptsToUse = conceptsToUse + getChildren(db['concepts'], parent)
    res = []
    for concept in conceptsToUse :
        matches = concepts[concept]['matches']
        for match in matches :
            rec = db['data'][match]['dateReceived']
            if rec >= timeFrame[0] and timeFrame[1] >= rec :
                res.append(match)
    import modelling
    ins = modelling.dataPrep()
    if 'topicModelling' not in db.keys():
        db['topicModelling'] = {}
    db['topicModelling'][parent] = ins.topicModel(db, res, topics)


def plotCount(db, concept) :
    concs = getChildren(db['concepts'], concept)
    matches = []
    for conc in concs :
        matches.extend(db['concepts'][conc]['matches'])
    matches = list(set(matches))
    res = {}
    for match in matches :
        date = db['data'][match]['dateReceived']#.strftime("%m/%d/%Y, %H:%M:%S")
        if date not in res.keys():
            res[date] = 1
        else :
            res[date] += 1
    glob = {}
    matches = []
    for m in db['data'].keys() :
        if db['data'][m]['isBroken'] == False and 'isDuplicate' not in db['data'][m].keys():
            matches.append(m)
    for match in matches :
        date = db['data'][match]['dateReceived']#.strftime("%m/%d/%Y, %H:%M:%S")
        if date not in glob.keys():
            glob[date] = 1
        else :
            glob[date] += 1
    return (glob, res)

#------------------------------Methods------------------------------
def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]

def makeDataSummary(db, index) :
    dataPiece = db['data'][index]
    res = "*************************************" + "\n" + \
    "Link#: " + str(index) + \
    "  Date received: " + dataPiece['dateReceived'].strftime("%m/%d/%Y, %H:%M:%S") + "\n" + \
    "Title: " + dataPiece['title'] + "\n" + \
    "Source: " + dataPiece['source'] + "    AdditionalTag(s): " + dataPiece['additionalTag'] + "\n" + \
     "ExampleText: " + shortenLines(dataPiece['exampleText'], 48) + "\n" + \
     "Link: " + shortenLines(str(dataPiece['link']), 50) + "\n" + "Cleaned HTML: " + "\n" + \
     shortenLines(dataPiece['cleanedHtml'], 70) + "\n"
    return res
#TODO
def assighnTimes(db) :
    data = db['data']
    import calendar
    import datetime
    monAbbrToNumDict = dict((v,k) for k,v in enumerate(calendar.month_abbr))
    for key, val in data.items() :
        dateReceived = val['dateReceived']
        day = int(dateReceived[5:7])
        month = int(monAbbrToNumDict[ dateReceived[8:11]])
        year = int(dateReceived[12:16])
        realDate = datetime.date(year, month, day)
        val['dateReceived'] = realDate

#Counts the porgramming symbols in a string
def programmingSymbolsCount(db, string) :
    programmingSymbols = db['programmingSymbols']
    count = 0
    for char in string :
        if char in programmingSymbols :
            count+=1
    return count

def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))

#specific make blocks for HTML so that many blank spaces are replaced with a newline
def specialSplit(html) :
    soup = bs4.BeautifulSoup(html, 'html.parser')
    body = soup.get_text()
    body = body.replace("\\n", "\n")
    body = body.replace("\\r", "\r")
    body = body.replace("	", "\r")
    body = body.replace("|", "\r")
    res = []
    for line in body.splitlines() :
        if line != "" : res.append(line)
    return res

#Removes all the stopwords from a string
def removeStopWords(db, string) :
    stopWords = db['stopWords']
    string = string.lower()
    words = string.split()
    result = [x for x in words if x not in stopWords]
    result = wordListToStr(result)
    return result

#Determines the core of the messages
def coreOf(assesedList) :
    res = []
    temp = []
    relevant = False
    for part in assesedList :
        if part[1] != "_" :
            temp.append(part)
            if part[1] == "@" :
                relevant = True
        else :
            if relevant :
                res.append(temp)
            temp = []
            relevant = False
    first = ""
    for part in res :
        for each in part :
            first += each[0] + " "
    return first

#counts the ammount of characters that are also in the programmingSymbols list
#Prepares the message into a list of strings with one link and its information
# per string
def makeBlocks(body) :
    body = body.replace("\\n", "\n")
    body = body.replace("\\r", "\r")
    lines = body.splitlines()
    block = ''
    blocks = []
    for line in lines :
        if line == '' :
            blocks.append(block)
            block = ''
        else :
            block = block + (line + '\n')
    blocks = blocks[:len(blocks)-3]
    return blocks

#processes the blocks of text in an alert to useful information
def processAlertBlocks(db, blocks) :
    #initialize variables
    result = []
    category = ''
    searchString = ''
    title = ''
    source = ''
    additionalTag = ''
    exampleText = ''
    link = ''
    #start process working per block
    for block in blocks :
        blockLines = block.splitlines()
        lines = len(blockLines)
        #if the string is an empty block nothing needs to be done
        if block == '' :
            continue
        #if the block only has one line it must be a line that tells us about\
        # new results.
        if  lines == 1:
            #determine the catogory of the next alerts and search string \
            # selecting by splitting the line into words, category is always \
            #the second word and the search string is always the words from the\
            # seventh word on until the but one last word
            words = blockLines[0].split()
            category = words[1]
            unCut = wordListToStr(words[7:len(words)-1])
            #remove the quotes around the search string
            searchString = unCut[1:len(unCut)-1]
        #if it is not a new result block it can only be a block that contains \
        #one alert
        else :
            #The link is always the last line
            link = str(blockLines[lines - 1])
            link = link[1:len(link)-1]
            #initialize the iterater that looks for the line of the source \
            #backwards in the block from the third to last line becouse the \
            #last line is always the link and the last line of the example text\
            #might be as short or shorter than the source. The shortness of the\
            #line determines whether a line is recognised as the source.
            sourceLine = lines - 3
            while sourceLine > 0:
                #initialise parameters for this line
                lineWords = blockLines[sourceLine].split()
                parWords = extractParentheseText(blockLines[sourceLine]).split()
                #if there is additional tags in the line it must be the source
                alertAdditionalTags = db['alertAdditionalTags']
                if any(tag in parWords for tag in alertAdditionalTags) :
                    #assighn addequate attribute balues and append the result\
                    # of this block
                    additionalTag = wordListToStr(parWords)
                    title = lineListToStr(blockLines[:sourceLine])
                    source = str(blockLines[sourceLine]).replace(wordListToStr(parWords), '')
                    exampleText = lineListToStr(blockLines[sourceLine+1:lines-1])
                    result.append([category, searchString, title, source, additionalTag, exampleText, link])
                    break
                #if there is less than five words in the line it is very likely \
                #this is the source
                if len(lineWords) < 5:
                    #assighn addequate attribute balues and append the result\
                    # of this block
                    title = lineListToStr(blockLines[:sourceLine])
                    source = blockLines[sourceLine]
                    exampleText = lineListToStr(blockLines[sourceLine+1:lines-1])
                    result.append([category, searchString, title, source, additionalTag, exampleText, link])
                    break
                sourceLine = sourceLine - 1
    return result

#python "message" class reader, to get the body of the message
def getBody(message): #getting plain text 'email body'
    body = None
    if message.is_multipart():
        for part in message.walk():
            if part.is_multipart():
                for subpart in part.walk():
                    if subpart.get_content_type() == 'text/plain':
                        body = subpart.get_payload(decode=True)
            elif part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True)
    elif message.get_content_type() == 'text/plain':
        body = message.get_payload(decode=True)
    return body

#converts a list with words back to a string, reverses split()
def wordListToStr(list) :
    result = ''
    for word in list :
        result += (word + ' ')
    result = result[:len(result)-1]
    return result

#takes out all the pieces of a string that are in between "()"
def extractParentheseText(string) :
    openCount = 0
    result = ""
    useChar = False
    for char in str(string) :
        if char == '(' :
            openCount += 1
        useChar = (openCount != 0)
        if char == ')' :
            openCount -= 1
        if useChar :
            result += char
    result = result.replace(")(", ") (")
    return result

#converts a list of lines back to a block of text, reverse of plitlines()
def lineListToStr(list) :
    result = ''
    for line in list :
        result += line + '\n'
    result = result[:len(result)-2]
    return result
#shortens a string by word after it exceeds a character limit
def shortenLines(string, maxLen) :
    lines = string.splitlines()
    res = ''
    lineSize = 0
    for line in lines :
        words = line.split()
        for word in words :
            res += word + ' '
            lineSize += len(word)
            if lineSize > maxLen :
                lineSize = 0
                res = res[:len(res) - 1]
                res += '\n'
    return res
#saves a csv with dialect = excel
def saveAsExcel(fileName, rowsToWrite) :
    csvName = fileName + ".csv"
    with io.open("Excel\\" + csvName, mode = 'w', newline = '', encoding="utf-8") as f :
        csv.writer(f, dialect='excel').writerows(rowsToWrite)
    print('Wrote excel CSV: ' + fileName)

#------------------------------Analysis-----------------------------

def overlap(db, conc1, conc2) :
    concepts = db['concepts']
    count = 0
    overlap = []
    matches1 = concepts[conc1]['matches']
    matches2 = concepts[conc2]['matches']
    for index in matches1 :
        if index in matches2 :
            count += 1
            overlap.append(index)
    perc = (round(count / len(matches1) * 100, 2), round(count / len(matches2) * 100, 2))
    return (count, overlap, perc)

def printAttr(db, indexList, attr) :
    for index in indexList:
        print(db['data'][index][attr])

def newOverlapConcept(conc1, conc2, newName):
    dataObj = Data(None)
    db = dataObj.db
    indexes = overlap(db, conc1, conc2)[1]
    dataObj.createNewConcept(newName, None)
    db['concepts'][newName]['matches'] = indexes
    dump(db, 'DATABASE')

#------------------------------Execute------------------------------
if __name__ == '__main__' :
    #import datetime
    #db = load('DATABASE')
    db = load('DATABASE')
    categories = {}
    for conc, cont in db['concepts'].items():
        if cont['parent'] == 'Geographical' :
            categories[conc] = getChildren(db['concepts'], conc)
    catToMatches = {}
    for cat, cont in categories.items() :
        catToMatches[cat] = []
        for child in cont :
            catToMatches[cat].extend(db['concepts'][child]['matches'])
        catToMatches[cat] = list(set(catToMatches[cat]))
    toDel = {}
    for cat, matches in catToMatches.items() :
        toDel[cat] = []
        for cat2, matches2 in catToMatches.items() :
            if cat2 == cat : continue
            for match in matches:
                if match in matches2: toDel[cat].append(match)
    for cat, dels in toDel.items() :
        for item in dels:
            if item in catToMatches[cat]:
                catToMatches[cat].remove(item)
    rowsToWrite = [['Category', 'uniqueMatches', 'totalMatches']]
    for cat, cont in catToMatches.items():
        newRow = []
        newRow.append(cat)
        newRow.append(len(cont))
        newRow.append(len(cont) + len(toDel[cat]))
        rowsToWrite.append(newRow)
    saveAsExcel('LocationsAnalysis', rowsToWrite)
    #rowsToWrite = [['Concept', 'Number of data pieces']]
    #for name, cont in db['concepts'].items() :
    #    rowsToWrite.append([name, len(cont['matches'])])
    #conceptNames = ['#']
    #conceptNames.extend(db['concepts'].keys())
    #rowsToWrite.append([])
    #rowsToWrite.append(conceptNames)
    #for name in conceptNames :
    #    if name == '#' : continue
    #    first = name
    #    newRow = [first]
    #    firstData = db['concepts'][first]['matches']
    #    for nameTwo in conceptNames :
    #        if nameTwo == '#' : continue
    #        count = 0
    #        second = nameTwo
    #        secondData = db['concepts'][second]['matches']
    #        for p in secondData :
    #            if p in firstData:
    #                count += 1
    #        newRow.append(count)
    #    rowsToWrite.append(newRow)
    #saveAsExcel("conceptsToDataCount", rowsToWrite)


    #overlap = overlap(db, "North America", "Europe")
    #newOverlapConcept("USA", "Powder Bed Fusion", 'PowderBedFusionUSAOverlap')
    #print(("Overlap Europe and North America: ") + str(overlap[0]))
    #printAttr(db, overlap[1], 'dateReceived')
    #print(overlap[2])
    #init('DATABASE')
    #initSave()
    #parseAlerts()
    #crawl()
    #parseHTML()
    #NERTagAll()
    #topicModellingPrepAll()
    #db['nerTags'].remove('O')
    #dump(db, 'DATABASE')

    #for s in db['sources']['bigramCount'] :
    #    bigram = s[0]
    #    count = s[1]
    #    if 'consum' in bigram :
    #        print(bigram + ': ' + str(count))

    #ins = Data(None)
#    keyWords = []
#    for name, cont in db['concepts'].items() :
#        for keyWord in cont['keyWords']:
#            keyWords.append(keyWord)
#    db['keyWords'] = keyWords

#    i = 0
#    while i < 10 :
#        try :
#            print(ins.getBigrams(20))
#        except Exception as err :
#             print(err)
#        i += 1
    #countBigrams()
#


    #db = load('DATABASE')
    #db['concepts'][]
    #print(getAllAttribute(db, 'preparedData'))
    #markDuplicates(db)
    #db['nerTags'][2] = 'PERSON'
    #db['nerTags'].append('O')
    #Data(None).init()
    #dump(db, 'DATABASE')
    #writeErrorReportCsv(db)
    #helpLists = {'searchStrings': db['searchStrings'], 'programmingSymbols': db['programmingSymbols'], \
#        'categories': db['categories'], 'mboxPaths': db['mboxPaths'], 'alertAdditionalTags': db['alertAdditionalTags']}
    #dump(helpLists, "savedLists")
    #print(db['data'][1].keys())
    #print(db.keys())
    #makeSourcesFromNer()
