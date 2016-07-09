#!/usr/bin/python

import wx, re

EXPANSIONS = ['','Alara Reborn','Alliances','Antiquities','Apocalypse','Arabian Nights','Archenemy','Battle Royale Box Set','Beatdown Box Set','Betrayers of Kamigawa','Champions of Kamigawa','Chronicles','Classic Sixth Edition','Coldsnap','Conflux','Darksteel','Dissension','Duel Decks: Ajani vs. Nicol Bolas','Duel Decks: Divine vs. Demonic','Duel Decks: Elspeth vs. Tezzeret','Duel Decks: Elves vs. Goblins','Duel Decks: Garruk vs. Liliana','Duel Decks: Jace vs. Chandra','Duel Decks: Knights vs. Dragons','Duel Decks: Phyrexia vs. the Coalition','Eighth Edition','Eventide','Exodus','Fallen Empires','Fifth Dawn','Fifth Edition','Fourth Edition','From the Vault: Dragons','From the Vault: Exiled','From the Vault: Legends','From the Vault: Relics','Future Sight','Guildpact','Homelands','Ice Age','Innistrad','Invasion','Judgment','Legends','Legions','Limited Edition Alpha','Limited Edition Beta','Lorwyn','Magic 2010','Magic 2011','Magic 2012','Magic: The Gathering-Commander','Masters Edition','Masters Edition II','Masters Edition III','Masters Edition IV','Mercadian Masques','Mirage','Mirrodin','Mirrodin Besieged','Morningtide','Nemesis','New Phyrexia','Ninth Edition','Odyssey','Onslaught','Planar Chaos','Planechase','Planeshift','Portal','Portal Second Age','Portal Three Kingdoms','Premium Deck Series: Fire and Lightning','Premium Deck Series: Graveborn','Premium Deck Series: Slivers','Promo set for Gatherer','Prophecy','Ravnica: City of Guilds','Revised Edition','Rise of the Eldrazi','Saviors of Kamigawa','Scars of Mirrodin','Scourge','Seventh Edition','Shadowmoor','Shards of Alara','Starter 1999','Starter 2000','Stronghold','Tempest','Tenth Edition','The Dark','Time Spiral','Time Spiral "Timeshifted"','Torment','Unglued','Unhinged','Unlimited Edition','Urza\'s Destiny','Urza\'s Legacy','Urza\'s Saga','Vanguard','Visions','Weatherlight','Worldwake','Zendikar']

RARITIES = ['','Common','Uncommon','Rare','Mythic Rare','Special']

TYPE_DICT = {'multiverseid':'number',
             'cardname':'regex',
             'manacost':'mana',
             'convertedmanacost':'number',
             'type':'regex',
             'subtype':'regex',
             'cardtext':'regex',
             'flavortext':'regex',
             'power':'number',
             'toughness':'number',
             'expansion':'exact',
             'rarity':'exact',
             'loyalty':'number',
             'cardnum':'regex',
             'artist':'regex',
             'colorindicator':'regex',
             'rating':'number',
             'votes':'number',
             'watermark':'regex'}

COL_TRANSLATE = {'Card Name':'cardname','Mana Cost':'manacost','CMC':'convertedmanacost','Type':'type','Subtype':'subtype','Power':'power','Toughness':'toughness','Expansion':'expansion','Rarity':'rarity','Artist':'artist','Rating':'rating','Votes':'votes'}

def create_sqlite_stmt(current_search):

    stmt = "select * from cards"
    if len(current_search) > 0:
        stmt += " where "

    # clean up misplaced |'s and &'s
    for i in range(len(current_search)):
        if i%2 == 0:
            if current_search[i][2][0:2] != 'r/':
                current_search[i][2] = re.sub('(\&|\|)[\s\&\|]*','\g<1>',current_search[i][2])
                current_search[i][2] = re.sub('^[\s\&\|]*','',current_search[i][2])
                current_search[i][2] = re.sub('[\s\&\|]*$','',current_search[i][2])
                if TYPE_DICT[current_search[i][1]] == 'number':
                    current_search[i][2] = re.sub('[^\|\&\<\>\d\.]','',current_search[i][2])
                current_search[i][2] = re.sub("'","''",current_search[i][2])

    for i in range(len(current_search)):
        if i%2 == 0:
            if current_search[i][0] == 'not':
                stmt += 'not '
            if current_search[i][2][0:2] != 'r/':
                substrs = re.split('\s*([\&\|])\s*',current_search[i][2])
                substmt = '('
                for item in substrs:
                    if item == '&':
                        substmt += ' and '
                    elif item == '|':
                        substmt += ' or '
                    else:
                        substmt += "cardmatch('%s','%s',%s)" % (item,TYPE_DICT[current_search[i][1]],current_search[i][1])
                substmt += ')'
                stmt += substmt
            else:
                stmt += "cardmatch('%s','%s',%s)" % (current_search[i][2],TYPE_DICT[current_search[i][1]],current_search[i][1])
        else:
            stmt += " "+current_search[i]+" "
            
    #stmt += " group by cardname"
    return stmt

class SearchInfo(wx.Notebook):

    def __init__(self,parent=None,cur=None):
        wx.Notebook.__init__(self,parent,style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.db_cursor = cur

        # ***** initialize the search tab *****
        self.search_tab = wx.Panel(parent=self,style=wx.TAB_TRAVERSAL)
        self.search_tab.SetMinSize(minSize=(350,355))

        self.search_keys = ['cardname','cardtext','manacost','convertedmanacost','type','subtype','power','toughness','rarity','expansion','artist','flavortext']
        self.search_fields = {'cardname': wx.TextCtrl(self.search_tab,style=wx.TE_PROCESS_ENTER), 
                              'cardtext': wx.TextCtrl(self.search_tab,style=wx.TE_PROCESS_ENTER),
                              'manacost': wx.TextCtrl(self.search_tab,style=wx.TE_PROCESS_ENTER),
                              'convertedmanacost': wx.TextCtrl(self.search_tab,style=wx.TE_PROCESS_ENTER),
                              'type': wx.TextCtrl(self.search_tab,style=wx.TE_PROCESS_ENTER),
                              'subtype': wx.TextCtrl(self.search_tab,style=wx.TE_PROCESS_ENTER),
                              'power': wx.TextCtrl(self.search_tab,style=wx.TE_PROCESS_ENTER),
                              'toughness': wx.TextCtrl(self.search_tab,style=wx.TE_PROCESS_ENTER),
                              'rarity' : wx.ComboBox(self.search_tab,value='',choices=RARITIES,style=wx.CB_READONLY),
                              'expansion' : wx.ComboBox(self.search_tab,value='',choices=EXPANSIONS,style=wx.CB_READONLY),
                              'artist': wx.TextCtrl(self.search_tab,style=wx.TE_PROCESS_ENTER),
                              'flavortext': wx.TextCtrl(self.search_tab,style=wx.TE_PROCESS_ENTER)}

        self.current_search = [];

        self.search_button = wx.Button(self.search_tab,label='Search All')
        self.collection_button = wx.Button(self.search_tab,label='  Search\nCollection')
        self.add_button = wx.Button(self.search_tab,label=' Add to\nCurrent')
        self.clear_button = wx.Button(self.search_tab,label='Clear')

        search_sizer = wx.GridBagSizer()
        search_sizer.SetMinSize(size=(350,363))
        self.search_tab.SetSizer(search_sizer)

        search_sizer.Add(wx.StaticText(parent=self.search_tab,label='Rules Text:'),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,border=2,pos=(1,0))
        search_sizer.Add(self.search_fields['cardtext'],flag=wx.EXPAND|wx.ALL,border=2,pos=(1,1))
        search_sizer.Add(wx.StaticText(parent=self.search_tab,label="Card Name:"),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,border=2,pos=(0,0))
        search_sizer.Add(self.search_fields['cardname'],flag=wx.EXPAND|wx.ALL,border=2,pos=(0,1))
        search_sizer.Add(wx.StaticText(parent=self.search_tab,label='Mana Cost:'),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,border=2,pos=(2,0))
        search_sizer.Add(self.search_fields['manacost'],flag=wx.EXPAND|wx.ALL,border=2,pos=(2,1))
        search_sizer.Add(wx.StaticText(parent=self.search_tab,label='CMC:'),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,border=2,pos=(3,0))
        search_sizer.Add(self.search_fields['convertedmanacost'],flag=wx.EXPAND|wx.ALL,border=2,pos=(3,1))
        search_sizer.Add(wx.StaticText(parent=self.search_tab,label='Type:'),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,border=2,pos=(4,0))
        search_sizer.Add(self.search_fields['type'],flag=wx.EXPAND|wx.ALL,border=2,pos=(4,1))
        search_sizer.Add(wx.StaticText(parent=self.search_tab,label='Subtype:'),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,border=2,pos=(5,0))
        search_sizer.Add(self.search_fields['subtype'],flag=wx.EXPAND|wx.ALL,border=2,pos=(5,1))
        search_sizer.Add(wx.StaticText(parent=self.search_tab,label='Power:'),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,border=2,pos=(6,0))
        search_sizer.Add(self.search_fields['power'],flag=wx.EXPAND|wx.ALL,border=2,pos=(6,1))
        search_sizer.Add(wx.StaticText(parent=self.search_tab,label='Toughness:'),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,border=2,pos=(7,0))
        search_sizer.Add(self.search_fields['toughness'],flag=wx.EXPAND|wx.ALL,border=2,pos=(7,1))
        search_sizer.Add(wx.StaticText(parent=self.search_tab,label='Rarity:'),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,border=2,pos=(8,0))
        search_sizer.Add(self.search_fields['rarity'],flag=wx.EXPAND|wx.ALL,border=2,pos=(8,1))
        search_sizer.Add(wx.StaticText(parent=self.search_tab,label='Expansion:'),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,border=2,pos=(9,0))
        search_sizer.Add(self.search_fields['expansion'],flag=wx.EXPAND|wx.ALL,border=2,pos=(9,1))
        search_sizer.Add(wx.StaticText(parent=self.search_tab,label='Artist:'),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,border=2,pos=(10,0))
        search_sizer.Add(self.search_fields['artist'],flag=wx.EXPAND|wx.ALL,border=2,pos=(10,1))
        search_sizer.Add(wx.StaticText(parent=self.search_tab,label='Flavor Text:'),flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,border=2,pos=(11,0))
        search_sizer.Add(self.search_fields['flavortext'],flag=wx.EXPAND|wx.ALL,border=2,pos=(11,1))

        subsizer = wx.FlexGridSizer(1,4)
        subsizer.Add(self.search_button,flag=wx.EXPAND)
        subsizer.Add(self.collection_button,flag=wx.EXPAND)
        subsizer.Add(self.add_button,flag=wx.EXPAND)
        subsizer.Add(self.clear_button,flag=wx.EXPAND)
        subsizer.AddGrowableCol(0,1)
        subsizer.AddGrowableCol(1,1)
        subsizer.AddGrowableCol(2,1)
        subsizer.AddGrowableCol(3,1)
        subsizer.AddGrowableRow(0,0)

        search_sizer.AddSizer(subsizer,flag=wx.EXPAND|wx.ALL,pos=(12,0),span=(1,2))

        search_sizer.AddGrowableCol(1,1)
        search_sizer.AddGrowableCol(2,1)
        search_sizer.AddGrowableCol(3,1)
        #search_sizer.AddGrowableRow(12,1)

        for key in self.search_fields:
            self.search_fields[key].Bind(wx.EVT_TEXT_ENTER,self.new_search)
        self.search_button.Bind(wx.EVT_BUTTON,self.new_search)
        self.add_button.Bind(wx.EVT_BUTTON,self.update_search)
        self.clear_button.Bind(wx.EVT_BUTTON,self.clear_search)

        # ***** initialize the current search tab *****
        self.current_tab = wx.ScrolledWindow(self,style=wx.TAB_TRAVERSAL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.current_sizer = wx.GridBagSizer()
        self.current_sizer.SetMinSize(size=(350,337))
        sizer.Add(self.current_sizer,0,wx.EXPAND)
        current_button = wx.Button(self.current_tab,label='Search')
        current_button.Bind(wx.EVT_BUTTON,self.do_current_search)
        sizer.Add(current_button,flag=wx.ALIGN_CENTER_HORIZONTAL)

        self.current_tab.SetSizer(sizer)
        self.update_current_search_tab()

        # ***** initialize the search results tab *****
        self.results_tab = wx.ScrolledWindow(self)
        self.results = []
        self.results_grid = wx.grid.Grid(self.results_tab)
        self.results_grid.SetMinSize((350,355))
        self.current_row = -1

        results_sizer = wx.FlexGridSizer(rows=1,cols=1)
        results_sizer.SetMinSize(size=(350,363))
        self.results_tab.SetSizer(results_sizer)

        self.results_grid.CreateGrid(0,0)
        self.results_grid.EnableEditing(False)
        self.results_grid.SetColLabelSize(wx.grid.GRID_AUTOSIZE)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.change_sort_by)

        self.result_fields = ['Card Name']
        self.result_sort_by = ['Card Name','v']

        results_sizer.Add(item=self.results_grid,flag=wx.EXPAND)
        results_sizer.AddGrowableCol(0,1)
        results_sizer.AddGrowableRow(0,1)

        self.AddPage(self.search_tab,text='Search')
        self.AddPage(self.current_tab,text='Current Search')
        self.AddPage(self.results_tab,text='Search Results')

        self.results_grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.cell_selected)

    def clear_search(self,event):
        for key in self.search_fields:
            self.search_fields[key].SetValue('')

    def change_sort_by(self,event):
        colNum = event.GetCol()
        if colNum < 0:
            self.cell_selected(event)
            return
        colName = re.sub(' [v|\^]$','',self.results_grid.GetColLabelValue(colNum))
        if self.result_sort_by[0] == colName:
            self.result_sort_by[1] = 'v' if self.result_sort_by[1]=='^' else '^'
        else:
            self.result_sort_by = [colName,'v']

        self.update_results_grid()

        self.results_grid.AutoSize()
        self.results_grid.Show()
        self.results_tab.EnableScrolling(x_scrolling=True,y_scrolling=True)
        self.results_tab.Fit()

    def key_sort(self,card):
        
        field = COL_TRANSLATE[self.result_sort_by[0]]
        if TYPE_DICT[field] == 'number':
            if card[field] == None:
                return -1000000.0
            elif self.result_sort_by[0] == 'Rating':
                return float(re.sub('/5$','',card[field]))
            else:
                return float(re.sub('{1/2}','.5',card[field]))
        else:
            return card[field]
    
    def update_results_grid(self):

        self.results.sort(key=self.key_sort,reverse=(True if self.result_sort_by[1]=='^' else False))        

        self.parent.statusbar.SetStatusText('Displaying results...')
        vcenter = wx.grid.GridCellAttr()
        vcenter.SetAlignment(wx.ALIGN_LEFT,wx.ALIGN_CENTER)
        self.results_grid.DeleteRows(0,self.results_grid.GetNumberRows()) 
        self.results_grid.DeleteCols(0,self.results_grid.GetNumberCols())

        nCols = 0
        for colName in self.result_fields:
            self.results_grid.AppendCols()
            colLabel = colName if self.result_sort_by[0]!=colName else (colName+' '+self.result_sort_by[1])
            self.results_grid.SetColLabelValue(nCols,colLabel)
            nCols += 1

        self.results_grid.Hide()
        for card in self.results:
            r = self.results_grid.GetNumberRows()
            self.results_grid.AppendRows()
            nCols = 0
            for colName in self.result_fields:
                self.results_grid.SetCellValue(r,nCols,unicode(card[COL_TRANSLATE[colName]]))
                nCols += 1
            self.results_grid.SetRowAttr(r,vcenter)
            self.results_grid.EnableDragRowSize(False)
            self.parent.progressbar.SetValue(int(float(r)/float(len(self.results))*100))
            self.parent.progressbar.Update()

        self.results_grid.AutoSize()

        self.parent.progressbar.SetValue(0)
        self.results_grid.Show()
        self.results_grid.SetRowLabelSize(wx.grid.GRID_AUTOSIZE)
        self.results_grid.SetColLabelSize(wx.grid.GRID_AUTOSIZE)

        if len(self.results) > 0:
            self.parent.card_info.update_card(self.results[0])

        self.parent.statusbar.SetStatusText('Found %d matches.' % len(self.results))
        self.results_tab.EnableScrolling(x_scrolling=True,y_scrolling=True)
        self.results_tab.Fit()

    def set_result_fields(self,key,value):

        self.results_grid.Hide()
        if value:
            self.result_fields.append(key)
            colNum = self.results_grid.GetNumberCols()
            self.results_grid.AppendCols()
            self.results_grid.SetColLabelValue(colNum,key)
            for i in range(self.results_grid.GetNumberRows()):
                self.results_grid.SetCellValue(i,colNum,unicode(self.results[i][COL_TRANSLATE[key]]))
            self.results_grid.AutoSizeColumn(colNum)
        else:
            colNum = -1
            for i in range(self.results_grid.GetNumberCols()):
                if re.sub(' [v|/^]$','',self.results_grid.GetColLabelValue(i)) == key:
                    self.result_fields = self.result_fields[0:i]+self.result_fields[i+1:]
                    if self.result_sort_by[0] == re.sub(' [v|/^]$','',self.results_grid.GetColLabelValue(i)):
                        self.result_sort_by = ['Card Name','v']
                        self.update_results_grid()
                    else:
                        self.results_grid.DeleteCols(i)
                    break
            for i in range(len(self.result_fields)):
                self.results_grid.SetColLabelValue(i,self.result_fields[i]+(' '+self.result_sort_by[1] if self.result_fields[i]==self.result_sort_by[0] else ''))
        self.results_grid.Show()

    def update_current_search_tab(self):

        sizer = self.current_sizer
        sizer.Clear(True)
        sizer.RemoveGrowableRow(0)
        sizer.RemoveGrowableRow(1)
        sizer.RemoveGrowableCol(0)
        sizer.RemoveGrowableCol(2)

        if( len(self.current_search) == 0 ):

            sizer.AddGrowableRow(0)
            sizer.AddGrowableCol(0)
            sizer.Add(wx.StaticText(parent=self.current_tab,label="There are no search items."),flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,pos=(0,0))

        else:

            sizer.AddGrowableCol(2)

            for i in range(len(self.current_search)):
                if i%2 == 0:
                    not_box = wx.ComboBox(parent=self.current_tab,value=self.current_search[i][0],choices=['','not'],style=wx.CB_READONLY,size=(60,-1),id=i/2)
                    not_box.Bind(wx.EVT_COMBOBOX,self.not_search_item)
                    sizer.Add(not_box,pos=(i,0),flag=wx.ALIGN_LEFT|wx.TOP,border=5)

                    key = self.current_search[i][1]
                    value = self.current_search[i][2]
                    sizer.Add(wx.StaticText(parent=self.current_tab,label=key+" = '"+value+"'"),pos=(i,1),flag=wx.TOP|wx.LEFT|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,border=5)

                    removeButton = wx.Button(self.current_tab,label='Remove',id=i/2)
                    removeButton.Bind(wx.EVT_BUTTON,self.remove_search_item)
                    sizer.Add(removeButton,pos=(i,2),flag=wx.ALIGN_RIGHT|wx.TOP,border=5)
                else:
                    and_or_box = wx.ComboBox(parent=self.current_tab,value=self.current_search[i],choices=['and','or'],style=wx.CB_READONLY,size=(60,-1),id=(i-1)/2)
                    and_or_box.Bind(wx.EVT_COMBOBOX,self.and_or_search_item)
                    sizer.Add(and_or_box,pos=(i,0),flag=wx.ALIGN_LEFT|wx.TOP,border=5)

            self.current_tab.EnableScrolling(x_scrolling=True,y_scrolling=True)
            self.current_tab.SetScrollbars(20,20,10,10)

        self.current_tab.Fit()

    def remove_search_item(self,event):

        event_id=event.GetId()

        if event_id == 0:
            self.current_search = self.current_search[2:]
        else:
            tmp = self.current_search[0:(event_id*2-1)]
            tmp.extend(self.current_search[(event_id*2+1):])
            self.current_search = tmp

        self.update_current_search_tab()

    def not_search_item(self,event):
        
        event_id=event.GetId()
        selection = event.GetSelection()

        if selection == 0:
            self.current_search[event_id*2][0] = ''
        else:
            self.current_search[event_id*2][0] = 'not'

    def and_or_search_item(self,event):

        event_id=event.GetId()
        selection = event.GetSelection()

        if selection == 0:
            self.current_search[event_id*2+1] = 'and'
        else:
            self.current_search[event_id*2+1] = 'or'

    def set_current_search(self,search_dict):

        self.current_search = [['',key,search_dict[key]] for key in search_dict]
        for i in range(len(self.current_search)-1,0,-1):
            self.current_search.insert(i,'and')

    def add_to_current_search(self,search_dict):
        
        tmp_list = [['',key,search_dict[key]] for key in search_dict]
        for i in range(len(tmp_list)-1,0,-1):
            tmp_list.insert(i,'and')
        if( len(self.current_search) > 0 ):
            self.current_search.append('and')
        self.current_search.extend(tmp_list)

    def do_current_search(self,event):
        self.ChangeSelection(2)

        children = self.current_sizer.GetChildren()

        stmt = create_sqlite_stmt(self.current_search)
        print "stmt = ",stmt
        self.parent.statusbar.SetStatusText('Searching database...')
        self.db_cursor.execute(stmt)
        self.results = self.db_cursor.fetchall()

        self.update_results_grid()

    def new_search(self,event):
        
        search_dict = dict(zip(self.search_keys,map(lambda k: self.search_fields[k].GetValue(),self.search_keys)))
        for key in search_dict.keys():
            if search_dict[key] == "":
                del search_dict[key]
        
        # ***** update the current search window *****
        self.set_current_search(search_dict)
        self.update_current_search_tab()

        # ***** update the results window *****
        self.do_current_search(event)

    def update_search(self,event):

        search_dict = dict(zip(self.search_keys,map(lambda k: self.search_fields[k].GetValue(),self.search_keys)))
        for key in search_dict.keys():
            if search_dict[key] == "":
                del search_dict[key]

        self.add_to_current_search(search_dict)
        self.update_current_search_tab()
        
    def cell_selected(self,event):
        if event.GetRow() != self.current_row and len(self.results) > 0:
            self.parent.card_info.update_card(self.results[event.GetRow()])
            self.parent.card_info.update_expansion_combo(self.results[event.GetRow()])
        self.current_row = event.GetRow()
        self.results_grid.SelectRow(self.current_row)
        #self.results_grid.SetGridCursor(self.current_row,0)
        event.Skip()
        
