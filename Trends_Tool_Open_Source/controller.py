import gui2 as gui
import data
import pickle

#Output
def p (text) :
    try :
        global app
        app.p(text)
    except :
        print(text)

def updateCmdOut(input) :
    global app
    app.updateCmdOut(input)

def printExampleDataPiece():
    return


# Getters


def getConcepts():
    concepts = db['concepts']
    res = []
    for k in concepts.keys() :
        res.append(k)
    return res

def getRndData() :
    return data.getRndData()

# Putters
def AddConc(selected, newConc) :
    data.createNewConcept(newConc, selected)
    global instance
    instance.app.gui.updateConc()

def AddKW(selectedConc, selectedKW) :
    data.addKeywords(selectedConc, selectedKW)
    global instance
    instance.app.gui.updateKW()

def markAsBadKW() :
    return

def KWasConc(selectedConc, selectedKW) :
    AddConc(selectedConc, selectedKW)
    AddKW(selectedKW, selectedKW)

###Exe
#@data.dbWrap
class Run() :
    def __init__(self):
        self.glob = self.loadGlob()
        project = self.startup(self.glob)
        self.data = data.Data(project)
        self.app = gui.Gui(self)
        self.gui = self.app.gui
        self.app.wxApp.MainLoop()

    def loadGlob(self):
        import os
        if not os.path.isfile('.\\global'):
            with open('global', 'wb') as f :
                pickle.dump({'projects': []}, f)
        return pickle.load(open('global', 'rb'))

    def startup(self, glob):
        print('Projects: ' + str(glob['projects']))
        print('Choose project with index in list or \'N\' for a new project')
        inp = input('Input: ')
        while not isinstance(inp, int) and inp.lower() != 'n' or \
            isinstance(inp, int) and int(inp) >= len(glob['projects']):
            print('Invalid input.')
            inp = input('Input: ')
        if inp.lower() == 'n':
            print('Please enter new project name, only letters are allowed.')
            inp = input('Input: ')
            while not inp.isalpha():
                print('Invalid input.')
                inp = input('Input: ')
            self.newProject(inp)
            return inp
        return glob['projects'][int(inp)]

    def newProject(self, name):
        self.glob['projects'].append(name)

    def get(self, *args, **kwargs) :
        if len(args) > 0 :
            first = args[0]
            if first == 'sources':
                res = self.data.db['nerTags']
                if 'Bigrams'not in res :
                    res.append('Bigrams')
                if 'Search'not in res :
                    res.append('Search')
                if 'topicModelling' in self.data.db.keys() :
                    for key in self.data.db['topicModelling'] :
                        res.append('TopicModel:' + str(key))
                res = list(set(res))
                return res
            elif first == 'topic modelling describtion' :
                return self.data.db['topicModelling'][args[1]]['source']
            elif first == 'plot data' :
                return self.data.conceptPlotInfo(kwargs['name'])
            elif first == 'topic model' :
                conc = kwargs['name']
                topics = kwargs['topics']
                print('topics to model: ' + str(topics))
                return self.data.topicModel(conc, topics)
            elif first == 'keyWords' :
                source = args[1]
                if source.split(':')[0] == 'TopicModel':
                    res = []
                    for item in self.data.db['topicModelling'][source.split(':')[1]]['topics'].keys():
                        res.append(str(item))
                    return res
                wordsWithCountList = self.data.getKeywords(source)
                res = []
                for kw in wordsWithCountList :
                    res.append(kw[0]+ ':' + str(kw[1]))
                return res
            elif first == 'concepts' :
                filter = kwargs['filter']
                conceptDict = self.data.db['concepts']
                filterList = [filter]
                while True :
                    subjects = []
                    for key, cont in conceptDict.items():
                        if cont['parent'] in filterList and key not in filterList:
                            subjects.append(key)
                    filterList.extend(subjects)
                    if len(subjects) == 0 : break
                res = []
                for key in conceptDict.keys() :
                    if key in filterList or filter == '':
                        res.append(key + ': ' +  str(conceptDict[key]['parent']))
                return res
            elif first == 'dataPiece' :
                text = self.data.getDataPiece(args[1], args[2])
                if args[1].split(':')[0] == 'TopicModel':
                    return text
                text = text.replace(args[2], '\n###' + args[2] + '###\n')
                res = 'Randomly selected data piece for source: ' + args[1]+ '\n' +\
                ' and key word: ' + args[2] + ', key word marked with ###X###:\n'
                res += text
                return res
            elif first == 'navigate' :
                return self.data.navigate(args[1])
            elif first == 'print key words' :
                print(self.data.db['concepts'][kwargs['concept']]['keyWords'])
            else :
                raise Exception('Uninterpretable arg.')
        else :
            pass
    def put(self, *args, **kwargs) :
        if len(args) > 0 :
            first = args[0]
            print("Putting: " + first)
            if first == 'key word':
                parent = kwargs['parent']
                keyWord = kwargs['keyWord']
                self.data.addKeyword(parent, keyWord)
            elif first == 'new search':
                self.data.newSearch(kwargs['name'])
            elif first == 'bad key word':
                keyWord = kwargs['keyWord']
                self.data.addBadKeyWord(keyWord)
                kws = self.gui.keyWordBox.GetStrings()
                kws.remove(keyWord)
                self.gui.keyWordBox.Set(kws)
            elif first == 'concept':
                parent = kwargs['parent']
                name = kwargs['name']
                self.data.createNewConcept(name, parent)
            elif first == 'save':
                self.data.save()
            elif first == 'remove concept' :
                self.data.removeConcept(kwargs['name'])
            elif first == 'remove key word' :
                self.data.removeKW(kwargs['name'], kwargs['parent'])
            else :
                raise Exception('Uninterpretable arg')
        else :
            pass
    def output(self, **kwargs) :
        for k, v in kwargs.items() :
            if k == 'cmdOutAppend' :
                self.app.gui.p(v)
            elif k == 'setCmdOut' :
                self.app.gui.updateCmdOut(v)
            else :
                raise Exception('Uninterpretable arg.')

if __name__ == '__main__' :
    Run()
