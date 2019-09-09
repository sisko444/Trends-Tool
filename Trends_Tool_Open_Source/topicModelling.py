#import gensim
import GADM1
from GADM1 import Gatherer, Alert, AlertLink
from gensim import corpora
from gensim.models import LdaModel, LdaMulticore
import gensim.downloader as api
from gensim.utils import simple_preprocess, lemmatize
from nltk.corpus import stopwords
import re
import logging
#from pprint import pprint
def getData() :
    db = GADM1.database()
    relevantAlerts = db.relevant
    data = []
    for alert in relevantAlerts :
        words = alert.clean.split()
        data.append(words)
    return data
def getDataSegregated() :
    db = GADM1.database()
    relevantAlerts = db.relevant
    data = []
    years = [2015, 2016, 2017, 2018, 2019]
    months = [1, 2 , 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    for year in years :
        yearList = [alert for alert in relevantAlerts if alert.dateReceived.year == year]
        yearRes = [year]
        for month in months :
            monthYearlist = [alert for alert in yearList if alert.dateReceived.month == month]
            monthRes = [month]
            for alert in monthYearlist :
                words = alert.clean.split()
                monthRes.append(words)
            yearRes.append(monthRes)
        data.append(yearRes)
    return data
#mydict = corpora.Dictionary()
#mycorpus = [mydict.doc2bow(doc, allow_update=True) for doc in docs]
#word_counts = [[(mydict[id], count) for id, count in line] for line in mycorpus]
#pprint(word_counts)
def prep(data) :
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
    logging.root.setLevel(level=logging.INFO)
    stop_words = stopwords.words('english')
    stop_wordsBefore = stop_words + ['com', 'edu', 'subject', 'lines', \
        'would', 'article', 'could', "additive","http","link","error",\
        "printing","technology","printed","3d","printing","additive",\
        "manufacturing", "able", 'additive']
    stop_wordsAfterWebError = ["error", "link", "http", "unavailable", "http"\
    , "winerror", "host", "attempt", "connection", "site", "remote", "range", \
    "timeout", "request", "not", "googletag", "website", "policy", "security"]
    stop_wordsAfterTooGeneral = ["able", 'additive', "printing", "manufacturing"\
    , "technology", "new", "also", "print"]

    data_processed = []

    for i, doc in enumerate(data):
        doc_out = []
        for wd in doc:
            if wd not in stop_wordsBefore :
                try :
                    lemmatized_word = lemmatize(wd, allowed_tags=re.compile('(NN|JJ|RB)'))  # lemmatize
                except RuntimeError :
                    continue
                wordBytes = str(lemmatized_word)
                word = wordBytes[3:len(wordBytes)-5]
                if lemmatized_word and (word not in stop_wordsAfterWebError)\
                    and (word not in stop_wordsAfterTooGeneral):
                    doc_out = doc_out + [lemmatized_word[0].split(b'/')[0].decode('utf-8')]
                else:
                    continue
        data_processed.append(doc_out)

    # Print a small sample
    #print(data_processed[0][:5])
    #> ['anarchism', 'originated', 'term', 'abuse', 'first']
    return data_processed

def run(data_processed) :
    # Step 3: Create the Inputs of LDA model: Dictionary and Corpus
    dct = corpora.Dictionary(data_processed)
    corpus = [dct.doc2bow(line) for line in data_processed]


    # Step 4: Train the LDA model
    lda_model = LdaMulticore(corpus=corpus,
                             id2word=dct,
                             random_state=100,
                             num_topics=7,
                             passes=10,
                             chunksize=1000,
                             batch=False,
                             alpha='asymmetric',
                             decay=0.5,
                             offset=64,
                             eta=None,
                             eval_every=0,
                             iterations=100,
                             gamma_threshold=0.001,
                             per_word_topics=True)

    # save the model
    lda_model.save('lda_model.model')

    # See the topics
    lda_model.print_topics(-1)
# [(0, '0.001*"also" + 0.000*"first" + 0.000*"state" + 0.000*"american" + 0.000*"time" + 0.000*"book" + 0.000*"year" + 0.000*"many" + 0.000*"person" + 0.000*"new"'),
#  (1, '0.001*"also" + 0.001*"state" + 0.001*"ammonia" + 0.000*"first" + 0.000*"many" + 0.000*"american" + 0.000*"war" + 0.000*"time" + 0.000*"year" + 0.000*"name"'),
#  (2, '0.005*"also" + 0.004*"american" + 0.004*"state" + 0.004*"first" + 0.003*"year" + 0.003*"many" + 0.003*"time" + 0.003*"new" + 0.003*"war" + 0.003*"person"'),
#  (3, '0.001*"atheism" + 0.001*"also" + 0.001*"first" + 0.001*"atheist" + 0.001*"american" + 0.000*"god" + 0.000*"state" + 0.000*"many" + 0.000*"new" + 0.000*"year"'),
#  (4, '0.001*"state" + 0.001*"also" + 0.001*"many" + 0.000*"world" + 0.000*"agave" + 0.000*"time" + 0.000*"new" + 0.000*"war" + 0.000*"god" + 0.000*"person"'),
#  (5, '0.001*"also" + 0.001*"abortion" + 0.001*"first" + 0.001*"american" + 0.000*"state" + 0.000*"many" + 0.000*"year" + 0.000*"time" + 0.000*"war" + 0.000*"person"'),
#  (6, '0.005*"also" + 0.004*"first" + 0.003*"time" + 0.003*"many" + 0.003*"state" + 0.003*"world" + 0.003*"american" + 0.003*"person" + 0.003*"apollo" + 0.003*"language"')]

if __name__ == "__main__" :
    data = getDataSegregated()
    for year in data :
        print("***\n***\n***\nNew Year: "+ str(year[0]) +"\n***\n***\n***\n")
        dataRun = []
        for month in year[1:] :
            dataRun.extend(month[1:])
        dataRun = prep(dataRun)
        run(dataRun)

    #print(dct)
    #print(corpus)
"""Hi,

I've read in many posts that the text pre-processing step has a big impact on the results you can get with NLP methods. I'm using topic models myself (LDA and DTM/LdaSequence) and cleaned the texts beforehand extensively, but I still have some doubts about the order of the steps I used. I'm hoping someone here can give me some advice on that. The current order is:

1. Lower case all words and clear texts from punctuation
2. Remove stopwords
3. Remove words with a length below 3 characters
4. Lemmatize words
5. Remove words with a length below 3 characters (again, as for example 'doing' will now be 'do' after step 4)
6. Create bigrams via Phrases method (first train it on the texts after step 5 and then apply it to those texts)
7. Prune the dictionary from high frequency words (words that occur in over 95% of the documents) and then prune the texts by excluding those words from the text
8. Create the corpus

I know I do not have to create new texts in step 7 necessarily as I can just create a corpus object with the pruned dictionary, but I would like to inspect the texts after all pruning conditions (and with a corpus object that's not possible), so hence this step.

What I'm not sure of is mostly the timing of the bigram selection. I can imagine I could create 'fake bigrams' because the stopwords and small words are removed beforehand. That being said, if there's always just one stopword in between, I was thinking the result could still be informative. For example, 'price to earnings' would become 'price earning' with the current order of the steps, and that is more informative for me than either 'price to' or 'to earnings' for example. I know I can create trigrams as well, but I'm not keen on doing that as it will only increase the number of words in the dictionary even more. Moreover, I thought about creating bigrams first (i.e., after step 1) but I don't want things like 'this_is' appearing in my vocabulary, as that's just noise. Are these valid enough reasons for this order? Or is this not what is recommended?

Finally, would it be ok to remove words with a length below 4 characters instead of 3? Or is that considered to be too much?

I hope someone can tell me what the best practices are. I'm doing the analysis for a scientific paper and if you have any literature that can help with this, feel free to add that as well.

Many thanks in advance for your help!

Myrthe

Hi Myrthe,

Your plan looks good, also you can look at this thread and find some additional technics.
About plan:
- remove step (3) (because after lemmatization typically your words will be shorter and in (5) you do all that needed)
- In (7) you can "relax" border for high-freq words (from 95% to 10% for example or more (1% if you have very large dataset)), besides prune very rare words.

For bigrams, you can try two variants: make bigrams before (2), and next you work with already "bigramed" corpus (bigrams like "this_is" you can prune later) OR your current variant.
Remove words with length below 4 can be very strict, look to words with length 3 in your corpus and think about "this words is informative?", but I think 3 is enough here.

Hi Ivan,

Thanks so much for the swift reply! Just as additional info: My corpus consists of 1173 texts and they are speeches (in total over 3 million tokens and approximately 24000 types after removing punctuation and lower casing).

I don't quite understand what you mean with relaxing the border for high-frequency words, do you mean 90% instead of 95%?

Is pruning very rare words considered 'normal'? I was thinking of perhaps omitting words that occur in just 1 document, is that ok? With all the extra unique words created in the bigram detection I'll be deleting many words by doing that, so I want to be sure it's appropriate.

To summarize what you propose in terms of the order. Option 1:

1. Lower case all words and clear texts from punctuation
2. Lemmatize words
3. Remove stopwords
4. Remove words with a length below 3 characters
5. Create bigrams via Phrases method (first train it on the texts after step 4 and then apply it to those texts)
6. Prune the dictionary from high frequency words (>95 or >90%?) and low frequency (docfreq=1?) and then prune the texts by excluding those words from the texts
7. Create the corpus

Option 2:

1. Lower case all words and clear texts from punctuation
2. Create bigrams via Phrases method (first train it on the texts after step 1 and then apply it to those texts)
3. Lemmatize words
4. Remove stopwords

5. Remove words with a length below 3 characters
6. Prune the dictionary from high frequency words (>95 or >90%?) and low frequency (docfreq=1?) and then prune the texts by excluding those words from the texts
7. Create the corpus

Which option is best in your expert opinion? I'm sort of leaning towards option 2 as I'm slightly afraid of creating 'fake bigrams' with option 1, but I don't know whether that's considered a big problem in general. The downside of creating bigrams sooner is not only that things like 'this_is' will be created (I could probably be pruned later on if I use 90% for example), but that sometimes bigrams are created with a word in plural form and other times singular form (apple_tree and apple_trees), whereas I just want the singular form, but lemmatization doesn't lemmatize bigrams.. So basically I'm wondering which of the two is better (given these downsides)?

And is it really ok to remove small words (of length 1 or 2)? Or should those words be in the stopwords list? I now have 3 steps where I delete words: stopwords, small words and high (and/or low) frequency words. I just want to be sure it's not too much.

Again, thanks so much for your advice!
 """
