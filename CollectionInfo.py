#!/usr/bin/python

import wx, re, sqlite3

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
             'watermark':'regex',
             'quantity':'number'}

COL_TRANSLATE = {'Card Name':'cardname','Mana Cost':'manacost','CMC':'convertedmanacost','Type':'type','Subtype':'subtype','Power':'power','Toughness':'toughness','Expansion':'expansion','Rarity':'rarity','Artist':'artist','Rating':'rating','Votes':'votes','Qty':'quantity'}

class CollectionInfo(wx.Notebook):

    def __init__(self,parent=None,fname=None):
        wx.Notebook.__init__(self,parent,style=wx.TAB_TRAVERSAL)
        self.parent = parent

        if not fname:
            fname = 'my_library.db'
        self.db_conn = sqlite3.connect(fname);
        self.db_conn.row_factory = sqlite3.Row
        self.db_cursor = self.db_conn.cursor();

        self.db_cursor.execute('select * from cards')
        self.my_library = self.db_cursor.fetchall()

        # ***** initialize the my_library tab *****
        self.my_library_tab = wx.ScrolledWindow(self)
        self.my_library_grid = wx.grid.Grid(self.my_library_tab)
        self.my_library_grid.SetMinSize((350,355))
        self.current_row = -1

        my_library_sizer = wx.FlexGridSizer(rows=1,cols=1)
        my_library_sizer.SetMinSize(size=(350,363))
        self.my_library_tab.SetSizer(my_library_sizer)

        self.my_library_grid.CreateGrid(0,0)
        self.my_library_grid.EnableEditing(False)
        self.my_library_grid.SetColLabelSize(wx.grid.GRID_AUTOSIZE)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.change_sort_by)

        self.my_library_fields = ['Card Name','Qty']
        self.my_library_sort_by = ['Card Name','v']

        my_library_sizer.Add(item=self.my_library_grid,flag=wx.EXPAND)
        my_library_sizer.AddGrowableCol(0,1)
        my_library_sizer.AddGrowableRow(0,1)

        self.AddPage(self.my_library_tab,text='My Library')

        self.my_library_grid.Bind(wx.grid.EVT_GRID_SELECT_CELL,self.cell_selected)
        self.update_my_library_grid()

    def change_sort_by(self,event):
        colNum = event.GetCol()
        if colNum < 0:
            self.cell_selected(event)
            return
        colName = re.sub(' [v|\^]$','',self.my_library_grid.GetColLabelValue(colNum))
        if self.my_library_sort_by[0] == colName:
            self.my_library_sort_by[1] = 'v' if self.my_library_sort_by[1]=='^' else '^'
        else:
            self.my_library_sort_by = [colName,'v']

        self.update_my_library_grid()

        self.my_library_grid.AutoSize()
        self.my_library_grid.Show()
        self.my_library_tab.EnableScrolling(x_scrolling=True,y_scrolling=True)
        self.my_library_tab.Fit()

    def key_sort(self,card):
        
        field = COL_TRANSLATE[self.my_library_sort_by[0]]
        if TYPE_DICT[field] == 'number':
            if card[field] == None:
                return -1000000.0
            elif self.my_library_sort_by[0] == 'Rating':
                return float(re.sub('/5$','',card[field]))
            else:
                return float(re.sub('\{1/2\}','.5',unicode(card[field])))
        else:
            return card[field]
    
    def update_my_library_grid(self):

        self.my_library.sort(key=self.key_sort,reverse=(True if self.my_library_sort_by[1]=='^' else False))        

        self.parent.statusbar.SetStatusText('Displaying library...')
        vcenter = wx.grid.GridCellAttr()
        vcenter.SetAlignment(wx.ALIGN_LEFT,wx.ALIGN_CENTER)
        self.my_library_grid.DeleteRows(0,self.my_library_grid.GetNumberRows()) 
        self.my_library_grid.DeleteCols(0,self.my_library_grid.GetNumberCols())

        nCols = 0
        for colName in self.my_library_fields:
            self.my_library_grid.AppendCols()
            colLabel = colName if self.my_library_sort_by[0]!=colName else (colName+' '+self.my_library_sort_by[1])
            self.my_library_grid.SetColLabelValue(nCols,colLabel)
            nCols += 1

        self.my_library_grid.Hide()
        for card in self.my_library:
            r = self.my_library_grid.GetNumberRows()
            self.my_library_grid.AppendRows()
            nCols = 0
            for colName in self.my_library_fields:
                self.my_library_grid.SetCellValue(r,nCols,unicode(card[COL_TRANSLATE[colName]]))
                nCols += 1
            self.my_library_grid.SetRowAttr(r,vcenter)
            self.my_library_grid.EnableDragRowSize(False)
            self.parent.progressbar.SetValue(int(float(r)/float(len(self.my_library))*100))
            self.parent.progressbar.Update()

        for i in range(self.my_library_grid.GetNumberCols()):
            self.my_library_grid.AutoSizeColumn(i)

        self.parent.progressbar.SetValue(0)
        self.my_library_grid.Show()
        self.my_library_grid.SetRowLabelSize(wx.grid.GRID_AUTOSIZE)
        self.my_library_grid.SetColLabelSize(wx.grid.GRID_AUTOSIZE)

        if len(self.my_library) > 0:
            self.parent.card_info.update_card(self.my_library[0])

        self.parent.statusbar.SetStatusText('Ready.')
        self.my_library_tab.EnableScrolling(x_scrolling=True,y_scrolling=True)
        self.my_library_tab.Fit()

    def set_collection_fields(self,key,value):

        self.my_library_grid.Hide()
        if value:
            self.my_library_fields.append(key)
            colNum = self.my_library_grid.GetNumberCols()
            self.my_library_grid.AppendCols()
            self.my_library_grid.SetColLabelValue(colNum,key)
            for i in range(self.my_library_grid.GetNumberRows()):
                self.my_library_grid.SetCellValue(i,colNum,unicode(self.my_library[i][COL_TRANSLATE[key]]))
            self.my_library_grid.AutoSizeColumn(colNum)
        else:
            colNum = -1
            for i in range(self.my_library_grid.GetNumberCols()):
                if re.sub(' [v|/^]$','',self.my_library_grid.GetColLabelValue(i)) == key:
                    self.my_library_fields = self.my_library_fields[0:i]+self.my_library_fields[i+1:]
                    if self.my_library_sort_by[0] == re.sub(' [v|/^]$','',self.my_library_grid.GetColLabelValue(i)):
                        self.my_library_sort_by = ['Card Name','v']
                        self.update_my_library_grid()
                    else:
                        self.my_library_grid.DeleteCols(i)
                    break
            for i in range(len(self.my_library_fields)):
                self.my_library_grid.SetColLabelValue(i,self.my_library_fields[i]+(' '+self.my_library_sort_by[1] if self.my_library_fields[i]==self.my_library_sort_by[0] else ''))
        self.my_library_grid.Show()

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
        self.my_library = self.db_cursor.fetchall()

        self.update_my_library_grid()

    def new_search(self,event):
        
        search_dict = dict(zip(self.search_keys,map(lambda k: self.search_fields[k].GetValue(),self.search_keys)))
        for key in search_dict.keys():
            if search_dict[key] == "":
                del search_dict[key]
        
        # ***** update the current search window *****
        self.set_current_search(search_dict)
        self.update_current_search_tab()

        # ***** update the my_library window *****
        self.do_current_search(event)

    def update_search(self,event):

        search_dict = dict(zip(self.search_keys,map(lambda k: self.search_fields[k].GetValue(),self.search_keys)))
        for key in search_dict.keys():
            if search_dict[key] == "":
                del search_dict[key]

        self.add_to_current_search(search_dict)
        self.update_current_search_tab()
        
    def cell_selected(self,event):
        if event.GetRow() != self.current_row and len(self.my_library) > 0:
            self.parent.card_info.update_card(self.my_library[event.GetRow()])
            self.parent.card_info.update_expansion_combo(self.my_library[event.GetRow()])
        self.current_row = event.GetRow()
        self.my_library_grid.SelectRow(self.current_row)
        #self.my_library_grid.SetGridCursor(self.current_row,0)
        event.Skip()
        
