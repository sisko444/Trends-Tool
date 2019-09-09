import wx
from wx.lib.plot import PolyLine, PlotCanvas, PlotGraphics

def drawBarGraph(title, data):
    import datetime
    #make a list with (month, year, count)

    monMin = 8
    yearMin =  2015
    mon = monMin
    year = yearMin
    maxMon = 5
    maxYear = 2019
    graph = []
    ord = 1
    while year < maxYear or mon <= maxMon :
        count = 0
        i = 1
        while i <= 31 :
            try :
                if datetime.date(year, mon, i) in data.keys() :
                    count += data[datetime.date(year, mon, i)]
                i += 1
            except :
                i += 1
        ord += 1
        graph.append((year, mon, ord, count))
        if mon < 12 :
            mon += 1
        else :
            mon = 1
            year += 1
    lines = []
    for info in graph :
        points = [(info[2], 0), (info[2],info[3])]
        mon = info[1]
        color = 'black'
        lines.append(PolyLine(points, colour = color,
            legend = str(info[1]) + '/' + str(info[0]), width = 10))
    return PlotGraphics(lines, title, "Months",
        "Number of data pieces")

########################################################################
class concPlot(wx.Frame):

    #----------------------------------------------------------------------
    def __init__(self, data, conc):
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          'Data piece matches for \'' + conc + '\' over time', size = wx.Size( 800,520 ))

        # Add a panel so it looks the correct on all platforms
        panel = wx.Panel(self, wx.ID_ANY)

        # create some sizers
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # create the widgets
        self.globPlot = PlotCanvas(panel)
        self.globPlot.Draw(drawBarGraph('Total ammount of data pieces over time', data[0]))

        self.concPlot = PlotCanvas(panel)
        self.concPlot.Draw(drawBarGraph('Ammount of data pieces within \'' + conc + '\' over time', data[1]))

        # layout the widgets
        mainSizer.Add(self.globPlot, 1, wx.EXPAND)
        mainSizer.Add(self.concPlot, 1, wx.EXPAND)
        panel.SetSizer(mainSizer)

class keyWordFinder ( wx.Frame ):

    def __init__( self, parent, cont):
        self.c = cont
        self.concFilter = ''
        self.maxCount = -1
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Trends Tool", pos = wx.DefaultPosition, size = wx.Size( 1200,680 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        bSizer6 = wx.BoxSizer( wx.HORIZONTAL )
        bSizer7 = wx.BoxSizer( wx.VERTICAL )
        bSizer8 = wx.BoxSizer( wx.HORIZONTAL )
        bSizer9 = wx.BoxSizer( wx.VERTICAL )

        #---------------LISTBOXES--------------
        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Concepts", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        bSizer9.Add( self.m_staticText1, 0, wx.ALL, 5 )

        m_listBox4Choices = []
        self.concListBox = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox4Choices, 0 )
        self.concListBox.SetMinSize( wx.Size( -1,260 ) )
        bSizer9.Add( self.concListBox, 0, wx.ALL, 5 )
        bSizer8.Add( bSizer9, 1, wx.EXPAND, 5 )
        bSizer10 = wx.BoxSizer( wx.VERTICAL )


        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"Algorithms", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        bSizer10.Add( self.m_staticText2, 0, wx.ALL, 5 )

        m_listBox5Choices = []
        self.sourceListBox = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox5Choices, 0 )
        self.sourceListBox.SetMinSize( wx.Size( -1,260 ) )
        bSizer10.Add( self.sourceListBox, 0, wx.ALL, 5 )
        bSizer8.Add( bSizer10, 1, wx.EXPAND, 5 )
        bSizer7.Add( bSizer8, 3, wx.EXPAND, 5 )
        gSizer2 = wx.GridSizer( 4, 3, 0, 0 )
        #---------------BUTTONS------------------
        self.AddConceptButton = wx.Button( self, wx.ID_ANY, u"AddConc", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.AddConceptButton, 0, wx.ALL, 5 )

        self.AddKeyWordButton = wx.Button( self, wx.ID_ANY, u"AddKW", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.AddKeyWordButton, 0, wx.ALL, 5 )

        self.AddCurrentKeywordAsConceptButton = wx.Button( self, wx.ID_ANY, u"KWasConc", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.AddCurrentKeywordAsConceptButton, 0, wx.ALL, 5 )

        self.setMaxCountButton = wx.Button( self, wx.ID_ANY, u"maxCount", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.setMaxCountButton, 0, wx.ALL, 5 )

        self.newSearchButton = wx.Button( self, wx.ID_ANY, u"newSearch", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.newSearchButton, 0, wx.ALL, 5 )

        self.removeConceptButton = wx.Button( self, wx.ID_ANY, u"removeConc", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.removeConceptButton, 0, wx.ALL, 5 )

        self.concFilterButton = wx.Button( self, wx.ID_ANY, u"filterConc", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.concFilterButton, 0, wx.ALL, 5 )

        self.removeKWButton = wx.Button( self, wx.ID_ANY, u"removeKW", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.removeKWButton, 0, wx.ALL, 5 )

        self.saveButton = wx.Button( self, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.saveButton, 0, wx.ALL, 5 )

        self.plotButton = wx.Button( self, wx.ID_ANY, u"plotConc", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.plotButton, 0, wx.ALL, 5 )

        self.topicModelButton = wx.Button( self, wx.ID_ANY, u"topicModel", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.topicModelButton, 0, wx.ALL, 5 )

        self.buttonx = wx.Button( self, wx.ID_ANY, u"noPurpose", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.buttonx, 0, wx.ALL, 5 )

        bSizer7.Add( gSizer2, 1, wx.EXPAND, 5 )


        #-----------------TEXTCTRL--------------

        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"Arguments", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )
        self.m_staticText5.SetMinSize( wx.Size( -1,20 ) )

        bSizer7.Add( self.m_staticText5, 0, wx.ALL, 5 )

        self.argIn = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.argIn.SetMinSize( wx.Size( 300,-1 ) )
        bSizer7.Add( self.argIn, 0, wx.ALL, 5 )
        bSizer7.AddSpacer(160)
        bSizer6.Add( bSizer7, 7, wx.EXPAND, 5 )

        bSizer12 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Conditions", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        bSizer12.Add( self.m_staticText3, 0, wx.ALL, 5 )

        m_listBox3Choices = []
        self.keyWordBox = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox3Choices, 0 )
        self.keyWordBox.SetMinSize( wx.Size( -1,600 ) )
        bSizer12.Add( self.keyWordBox, 0, wx.ALL, 5 )
        bSizer6.Add( bSizer12, 3, wx.EXPAND, 5 )
        bSizer11 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Data piece", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        bSizer11.Add( self.m_staticText4, 0, wx.ALL, 5 )
        self.cmdOut = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, style = wx.TE_MULTILINE|wx.TE_READONLY)
        self.cmdOut.SetMinSize( wx.Size( 800,600 ) )

        bSizer11.Add( self.cmdOut, 0, wx.ALL, 5 )
        bSizer6.Add( bSizer11, 14, wx.EXPAND, 5 )
        self.SetSizer( bSizer6 )
        self.Layout()
        self.Centre( wx.BOTH )

        ##Bindings
        #buttons
        self.AddConceptButton.Bind(wx.EVT_BUTTON, self.AddConc)
        self.AddKeyWordButton.Bind(wx.EVT_BUTTON, self.AddKW)
        self.newSearchButton.Bind(wx.EVT_BUTTON, self.newSearch)
        self.removeConceptButton.Bind(wx.EVT_BUTTON, self.removeConcept)
        self.AddCurrentKeywordAsConceptButton.Bind(wx.EVT_BUTTON, self.KWasConc)
        self.concFilterButton.Bind(wx.EVT_BUTTON, self.filterConc)
        self.setMaxCountButton.Bind(wx.EVT_BUTTON, self.setMaxCount)
        self.removeKWButton.Bind(wx.EVT_BUTTON, self.removeKW)
        self.saveButton.Bind(wx.EVT_BUTTON, self.save)
        self.topicModelButton.Bind(wx.EVT_BUTTON, self.topicModel)
        self.plotButton.Bind(wx.EVT_BUTTON, self.plot)
        #listboxes
        self.sourceListBox.Bind(wx.EVT_LISTBOX, self.updateKW)
        self.concListBox.Bind(wx.EVT_LISTBOX, self.printConcKWs)
        self.keyWordBox.Bind(wx.EVT_LISTBOX, self.updateDataPiece)


        #init params
        self.Show(True)


    #Button Functions
    def topicModel(self, what) :
        conc = self.concListBox.GetString(self.concListBox.GetSelection()).split(':')[0]
        input = self.argIn.GetValue()
        try :
            num = int(input)
        except :
            num = -1
        info = self.c.get('topic model', name = conc, topics = num)
        self.updateSources()
    def plot(self, what):
        conc = self.concListBox.GetString(self.concListBox.GetSelection()).split(':')[0]
        data = self.c.get('plot data', name = conc)
        frame = concPlot(data, conc)
        frame.Show()
    def newSearch(self, what):
        name = self.argIn.GetValue()
        self.c.put('new search', name = name)
        self.updateKW(None)
    def setMaxCount(self, what):
        inp = self.argIn.GetValue()
        if inp == '' :
            self. maxCount = -1
        else :
            self.maxCount = int(inp)
        self.updateKW(None)
    def removeKW(self, what):
        conc = self.concListBox.GetString(self.concListBox.GetSelection()).split(':')[0]
        self.c.put('remove key word', name = self.argIn.GetValue(), parent = conc)
    def printConcKWs(self, what) :
        conc = self.concListBox.GetString(self.concListBox.GetSelection()).split(':')[0]
        self.c.get('print key words', concept = conc)
    def filterConc(self, what) :
        self.concFilter = self.argIn.GetValue()
        self.updateConc()
    def removeConcept(self, what) :
        selectedConc = self.concListBox.GetString(self.concListBox.GetSelection()).split(':')[0]
        self.c.put('remove concept', name = selectedConc)
        self.updateConc()
    def AddConc(self, what) :
        selected = self.concListBox.GetString(self.concListBox.GetSelection()).split(':')[0]
        newConc = self.argIn.GetValue()
        self.c.put('concept', parent = selected, name = newConc)
        self.updateConc()
    def AddKW(self, what) :
        try :
            selectedConc = self.concListBox.GetString(self.concListBox.GetSelection()).split(':')[0]
        except :
            selectedConc = self.concFilter
        selectedKW = self.keyWordBox.GetString(self.keyWordBox.GetSelection()).split(':')[0]
        self.c.put('key word', parent = selectedConc, keyWord = selectedKW)
        self.updateConc()
        self.updateKW(None)
    def KWasConc(self, what) :
        selectedConc = self.concListBox.GetString(self.concListBox.GetSelection()).split(':')[0]
        selectedKW = self.keyWordBox.GetString(self.keyWordBox.GetSelection()).split(':')[0]
        self.c.put('concept', parent = selectedConc, name = selectedKW)
        self.c.put('key word', parent = selectedKW, keyWord = selectedKW)
        self.updateConc()
        self.updateKW(None)
    def markAsBadKWfunc(self, what) :
        badKW = self.keyWordBox.GetString(self.keyWordBox.GetSelection()).split(':')[0]
        self.c.put('bad key word', keyWord = badKW)
    def printExampleDataPieceFunc(self, what) :
        return
    def save(self, what) :
        self.c.put('save')
    #Update Params
    def updateSources(self) :
        sources = self.c.get('sources')
        if 'O' in sources: sources.remove('O')
        self.sourceListBox.Set(sources)
    def updateConc(self) :
        concepts = self.c.get('concepts', filter = self.concFilter)
        self.concListBox.Set(concepts)
    def updateKW(self, what) :
        source = self.sourceListBox.GetString(self.sourceListBox.GetSelection())
        if self.sourceListBox.GetString(self.sourceListBox.GetSelection()).split(':')[0] == 'TopicModel':
            self.updateCmdOut(self.c.get('topic modelling describtion',
                                        self.sourceListBox.GetString(self.sourceListBox.GetSelection()).split(':')[1]))
            keyWords = self.c.get('keyWords', source)
            self.keyWordBox.Set(keyWords)
            return
        keyWords = self.c.get('keyWords', source)
        res = []
        for i in keyWords :
            split = i.split(':')
            if int(split[len(split)-1]) < self.maxCount or self.maxCount == -1:
                res.append(i)
        self.keyWordBox.Set(res)
    def updateCmdOut(self, input) :
        self.cmdOut.Clear()
        self.cmdOut.AppendText(input)
    def p(self, input) :
        self.cmdOut.AppendText(input)
    def updateDataPiece(self, what) :
        source = self.sourceListBox.GetString(self.sourceListBox.GetSelection()).split(':')[0]
        if source == 'TopicModel' :
            source = self.sourceListBox.GetString(self.sourceListBox.GetSelection())
            kw = self.keyWordBox.GetString(self.keyWordBox.GetSelection())
            self.updateCmdOut(self.c.get('dataPiece', source, kw))
        else :
            kw = self.keyWordBox.GetString(self.keyWordBox.GetSelection()).split(':', 1)[0]
            self.updateCmdOut(self.c.get('dataPiece', source, kw))
class Gui ():
    def __init__(self, cont):
        self.wxApp = wx.App()
        self.gui = keyWordFinder(None, cont)
        self.gui.updateSources()
        self.gui.updateConc()
