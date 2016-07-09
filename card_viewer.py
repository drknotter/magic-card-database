#!/usr/bin/python

import wx, wx.grid, sqlite3, re, time, string, traceback
import EnhancedStatusBar as ESB
from CardInfo import CardInfo
from SearchInfo import SearchInfo
from CollectionInfo import CollectionInfo

APP_EXIT = 1
RANDOM_BTN = 2
RARITIES_COMBO = 4
DECK_OPEN = 5
SEARCH_FIELDS = 6
COLLECTION_FIELDS = 7
SEARCH_FIELD_SELECT = 100
COLLECTION_FIELD_SELECT = 200

def cardmatch(expr, match_type, item):
    try:
        if item is None:
            return None
        if match_type == 'number':
            if( re.search('\*',item) ):
                return False
            item = re.sub('{1/2}','.5',item)
            if expr[0] == '>':
                return float(expr[1:]) < float(item)
            elif expr[0] == '<':
                return float(expr[1:]) > float(item)
            else:
                return float(expr) == float(item)
        elif match_type == 'regex':
            if expr[0:2] == 'r/':
                reg = re.compile(expr[2:])
            else:
                reg = re.compile(expr,re.I)
            return reg.search(item) is not None

        elif match_type == 'exact':
            return expr == item

        elif match_type == 'mana':

            itemsplit = re.split('\{([^\}]+)\}',item)[1::2]
            if expr[0] == '>' or expr[0] == '<':
                exprsplit = re.split('\{([^\}]+)\}',expr[1:])
            else:
                exprsplit = re.split('\{([^\}]+)\}',expr)

            symbols = []
            for i in exprsplit[0::2]:
                if isinstance(i,unicode):
                    for letter in i:
                        symbols.append(letter)
            symbols.extend(exprsplit[1::2])

            exprfreq = dict([(i, symbols.count(i)) for i in set(symbols)])
            itemfreq = dict([(i, itemsplit.count(i)) for i in set(itemsplit)])

            if expr[0] == '>':
                for symbol in exprfreq:
                    if re.search('^\d+$',symbol):
                        flag = False
                        for s in itemfreq:
                            if re.search('^\d+$',s):
                                flag = True
                                if int(s) < int(symbol):
                                    return None
                        if flag == False:
                            return None
                    elif symbol not in itemfreq.keys() or itemfreq[symbol] < exprfreq[symbol]:
                        return None
                return True
            elif expr[0] == '<':
                for symbol in itemfreq:
                    if re.search('^\d+$',symbol):
                        flag = False
                        for s in exprfreq:
                            if re.search('^\d+$',s):
                                flag = True
                                if int(s) < int(symbol):
                                    return None
                        if flag == False:
                            return None
                    elif symbol not in exprfreq.keys() or exprfreq[symbol] < itemfreq[symbol]:
                        return None
                return True
            else:
                return exprfreq == itemfreq

        return None
    except:
        print 'Exception: badly formatted search term:',expr
        print traceback.print_exc()
        return None

class CardViewer(wx.Frame):
    
    def __init__(self, parent=None):
        wx.Frame.__init__(self,parent,style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER) 
            
        self.init_db()
        self.init_ui()

        self.SetTitle('Card Viewer')
        #self.SetClientSize((-1,311))
        self.Fit()
        self.Centre()
        self.Show(True)

    def init_db(self):
        self.db_conn = sqlite3.connect('mtg.db');
        self.db_conn.create_function("CARDMATCH", 3, cardmatch)
        self.db_conn.row_factory = sqlite3.Row
        self.db_cursor = self.db_conn.cursor();        
        
    def init_ui(self):
        
        # ***** initialize menu bar *****
        menubar = wx.MenuBar()

        filemenu = wx.Menu()
        filemenu.AppendItem(wx.MenuItem(filemenu,id=APP_EXIT,text='&Quit\tCtrl+Q',help='Quits the program.'))
        filemenu.AppendItem(wx.MenuItem(filemenu,id=DECK_OPEN,text='&Open\tCtrl+O',help='Opens a deck.'))

        viewmenu = wx.Menu()
        search_fields_menu = wx.Menu()
        collection_fields_menu = wx.Menu()
        self.field_names = ['Mana Cost','CMC','Type','Subtype','Power','Toughness','Rarity','Expansion','Artist','Rating','Votes']
        search_field_items = []
        for i in range(SEARCH_FIELD_SELECT,SEARCH_FIELD_SELECT+len(self.field_names)):
            search_field_items.append(wx.MenuItem(search_fields_menu,id=i,text=self.field_names[i-SEARCH_FIELD_SELECT]))
            search_field_items[-1].SetCheckable(True)
            search_fields_menu.AppendItem(search_field_items[-1])
        collection_field_items = []
        for i in range(COLLECTION_FIELD_SELECT,COLLECTION_FIELD_SELECT+len(self.field_names)):
            collection_field_items.append(wx.MenuItem(collection_fields_menu,id=i,text=self.field_names[i-COLLECTION_FIELD_SELECT]))
            collection_field_items[-1].SetCheckable(True)
            collection_fields_menu.AppendItem(collection_field_items[-1])            
        viewmenu.AppendMenu(id=SEARCH_FIELDS,submenu=search_fields_menu,text='&Search Fields')
        viewmenu.AppendMenu(id=COLLECTION_FIELDS,submenu=collection_fields_menu,text='&Collection Fields')

        menubar.Append(filemenu, '&File')
        menubar.Append(viewmenu, '&View')
        self.SetMenuBar(menubar)

        # ***** initialize  the status bar and progress bar *****
        self.statusbar = ESB.EnhancedStatusBar(self, -1)
        self.progressbar = wx.Gauge(self.statusbar)
        self.statusbar.AddWidget(self.progressbar,ESB.ESB_ALIGN_RIGHT)

        self.statusbar.SetStatusText('Ready.')
        self.SetStatusBar(self.statusbar)        

        # ***** initialize the card info frame *****
        self.card_info = CardInfo(self,cur=self.db_cursor)

        # ***** initialize the search frame *****
        self.search_info = SearchInfo(parent=self,cur=self.db_cursor)

        # ***** initialize the collection info frame *****
        self.collection_info = CollectionInfo(parent=self)

        # ***** initialize the add/remove buttons *****
        self.add_button = wx.Button(parent=self,label='>',size=(30,-1))
        self.remove_button = wx.Button(parent=self,label='<',size=(30,-1))

        add_remove_sizer = wx.FlexGridSizer(2,1)
        add_remove_sizer.Add(self.add_button,flag=wx.EXPAND)
        add_remove_sizer.Add(self.remove_button,flag=wx.EXPAND)
        add_remove_sizer.AddGrowableRow(0,0)
        add_remove_sizer.AddGrowableRow(1,0)

        # bind events
        self.Bind(wx.EVT_MENU,self.on_quit,id=APP_EXIT)
        self.Bind(wx.EVT_MENU,self.on_open,id=DECK_OPEN)
        for i in range(SEARCH_FIELD_SELECT,SEARCH_FIELD_SELECT+len(self.field_names)):
            self.Bind(wx.EVT_MENU,self.search_field_select,id=i)
        for i in range(COLLECTION_FIELD_SELECT,COLLECTION_FIELD_SELECT+len(self.field_names)):
            self.Bind(wx.EVT_MENU,self.collection_field_select,id=i)
        self.add_button.Bind(wx.EVT_BUTTON,self.add_to_collection)
        self.remove_button.Bind(wx.EVT_BUTTON,self.remove_from_collection)

        # layout the entire frame
        sizer = wx.GridBagSizer()
        sizer.Add(self.search_info,pos=(0,0),flag=wx.EXPAND|wx.ALIGN_CENTER)
        sizer.AddSizer(add_remove_sizer,pos=(0,1),flag=wx.EXPAND)
        sizer.Add(self.collection_info,pos=(0,2),flag=wx.EXPAND|wx.ALIGN_CENTER)
        sizer.Add(self.card_info,pos=(0,3),flag=wx.ALIGN_RIGHT)
        sizer.AddGrowableCol(0,0)
        sizer.AddGrowableCol(2,0)
        sizer.AddGrowableRow(0,0)
        self.SetSizer(sizer)
        (w,h) = sizer.GetMinSize()
        self.SetMinSize((w,h+menubar.GetSize()[1]+self.statusbar.GetSize()[1]+8))

    def add_to_collection(self,event):
        
        return 1

    def remove_from_collection(self,event):
        return 1

    def search_field_select(self,event):
        self.search_info.set_result_fields(self.field_names[event.GetId()-SEARCH_FIELD_SELECT],event.IsChecked())

    def collection_field_select(self,event):
        self.collection_info.set_collection_fields(self.field_names[event.GetId()-COLLECTION_FIELD_SELECT],event.IsChecked())

    def on_quit(self,e):
        self.Close()

    def on_open(self,e):
        """ Open a file"""
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a deck", self.dirname, "", "*.db", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            print self.dirname, self.filename
#            f = open(os.path.join(self.dirname, self.filename), 'r')
#            self.control.SetValue(f.read())
#            f.close()
        dlg.Destroy()
        
if __name__ == '__main__':
    cv = wx.App(0)
    CardViewer(None)
    cv.MainLoop()    
