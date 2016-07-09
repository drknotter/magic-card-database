#!/usr/bin/python

import wx, re

class CardInfo(wx.Notebook):
    def __init__(self,parent=None,card=None,cur=None):
        wx.Notebook.__init__(self,parent,style=wx.TAB_TRAVERSAL)
        self.db_cursor = cur

        # initialize the card image tab
        self.card_image_panel = wx.Panel(self)

        self.card_bitmap = wx.StaticBitmap(parent=self.card_image_panel)

        self.db_cursor.execute("select * from cards order by random() limit 1")
        card = self.db_cursor.fetchone()        

        self.db_cursor.execute("select * from cards where cardname='%s'"%re.sub("'","''",card['cardname']))
        cards = self.db_cursor.fetchall()
        expansions = []
        self.multiverseid_list = []
        for c in cards:
            expansions.append(c['expansion'])
            self.multiverseid_list.append(c['multiverseid'])
        self.expansion_combo = wx.ComboBox(self.card_image_panel,value=card['expansion'],choices=expansions,style=wx.CB_READONLY)
        self.expansion_combo.Bind(wx.EVT_COMBOBOX,self.new_expansion)

        random = wx.Button(self.card_image_panel,label='Random')
        random.Bind(wx.EVT_BUTTON,self.random_card)

        cardimagesizer = wx.GridBagSizer()
        self.card_image_panel.SetSizer(cardimagesizer)
        cardimagesizer.Add(self.card_bitmap,pos=(0,0),flag=wx.ALIGN_CENTER_HORIZONTAL)
        cardimagesizer.Add(self.expansion_combo,pos=(1,0),flag=wx.EXPAND)
        cardimagesizer.Add(random,pos=(2,0),flag=wx.EXPAND)
        cardimagesizer.AddGrowableRow(2,0)
        cardimagesizer.AddGrowableCol(0,0)

        # initialize the card info tab
        self.card_info_panel = wx.ScrolledWindow(self)
        italic_bold = wx.Font(pointSize=8,family=wx.FONTFAMILY_SWISS,style=wx.FONTSTYLE_ITALIC,weight=wx.FONTWEIGHT_BOLD)
        small = wx.Font(pointSize=8,family=wx.FONTFAMILY_SWISS,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL)

        self.card_name = wx.StaticText(self.card_info_panel)
        self.card_cost = wx.StaticText(self.card_info_panel)
        self.card_type = wx.StaticText(self.card_info_panel)
        self.card_rules = wx.StaticText(self.card_info_panel)
        self.card_pt = wx.StaticText(self.card_info_panel)
        self.card_flavor = wx.StaticText(self.card_info_panel)
        self.card_rarity = wx.StaticText(self.card_info_panel)
        self.card_artist = wx.StaticText(self.card_info_panel)
        self.card_rating = wx.StaticText(self.card_info_panel)
        self.card_votes = wx.StaticText(self.card_info_panel)
        self.card_name.SetFont(small)
        self.card_cost.SetFont(small)
        self.card_type.SetFont(small)
        self.card_rules.SetFont(small)
        self.card_pt.SetFont(small)
        self.card_flavor.SetFont(wx.Font(pointSize=8,family=wx.FONTFAMILY_SWISS,style=wx.FONTSTYLE_ITALIC,weight=wx.FONTWEIGHT_NORMAL))
        self.card_rarity.SetFont(small)
        self.card_artist.SetFont(small)
        self.card_rating.SetFont(small)
        self.card_votes.SetFont(small)

        labels = []
        for t in ['Name:','Cost:','Type:','Rules:','P/T:','Flavor:','Rarity:','Artist:','Rating:','Votes:']:
            labels.append(wx.StaticText(self.card_info_panel,label=t))
            labels[-1].SetFont(italic_bold)

        grid = wx.GridBagSizer(5,10)
        self.card_info_panel.SetSizer(grid)
        grid.AddGrowableCol(idx=2,proportion=1)

        grid.AddSpacer(item=(3,3),pos=(0,0))
        grid.AddSpacer(item=(3,3),pos=(3,0))
        grid.Add(labels[0],pos=(1,1),flag=wx.ALIGN_RIGHT)
        grid.Add(self.card_name,pos=(1,2))
        grid.Add(labels[1],pos=(2,1),flag=wx.ALIGN_RIGHT)
        grid.Add(self.card_cost,pos=(2,2))
        grid.Add(labels[2],pos=(3,1),flag=wx.ALIGN_RIGHT)
        grid.Add(self.card_type,pos=(3,2))
        grid.Add(labels[3],pos=(4,1),flag=wx.ALIGN_RIGHT)
        grid.Add(self.card_rules,pos=(4,2))
        grid.Add(labels[4],pos=(5,1),flag=wx.ALIGN_RIGHT)
        grid.Add(self.card_pt,pos=(5,2))
        grid.Add(labels[5],pos=(6,1),flag=wx.ALIGN_RIGHT)
        grid.Add(self.card_flavor,pos=(6,2))
        grid.Add(labels[6],pos=(7,1),flag=wx.ALIGN_RIGHT)
        grid.Add(self.card_rarity,pos=(7,2))
        grid.Add(labels[7],pos=(8,1),flag=wx.ALIGN_RIGHT)
        grid.Add(self.card_artist,pos=(8,2))
        grid.Add(labels[8],pos=(9,1),flag=wx.ALIGN_RIGHT)
        grid.Add(self.card_rating,pos=(9,2))
        grid.Add(labels[9],pos=(10,1),flag=wx.ALIGN_RIGHT)
        grid.Add(self.card_votes,pos=(10,2))

        # initialize dbase info tab
        self.dbase_info_panel = wx.ScrolledWindow(self)

        self.dbgrid = wx.GridBagSizer(5,10)
        self.dbase_info_panel.SetSizer(self.dbgrid)

        self.AddPage(self.card_image_panel,text='Card Image')
        self.AddPage(self.card_info_panel,text='Card Info')
        self.AddPage(self.dbase_info_panel,text='D-base Info')

        self.update_card(card)

    def random_card(self,event):
        self.db_cursor.execute("select * from cards order by random() limit 1")
        card = self.db_cursor.fetchone()        
        self.update_card(card)
        self.update_expansion_combo(card)

    def new_expansion(self,event):
        self.db_cursor.execute("select * from cards where cardname='%s' and multiverseid='%s'"%(re.sub("'","''",self.get_name()),self.multiverseid_list[self.expansion_combo.GetSelection()]))
        card = self.db_cursor.fetchone()
        self.update_card(card)
        self.update_expansion_combo(card)

    def update_expansion_combo(self,card):
        self.multiverseid_list = []
        expansions = []
        self.db_cursor.execute("select * from cards where cardname='%s'" % re.sub("'","''",card['cardname']))
        cards = self.db_cursor.fetchall()
        for c in cards:
            expansions.append(c['expansion'])
            self.multiverseid_list.append(c['multiverseid'])
        self.expansion_combo.SetItems(items=expansions)
        self.expansion_combo.SetValue(card['expansion'])

    def update_card(self,card):

        # update the card image tab
        card_image = wx.Image(name='images/%s.jpg'%card['multiverseid'],type=wx.BITMAP_TYPE_JPEG)
        self.card_bitmap.SetBitmap(card_image.ConvertToBitmap())

        self.card_image_panel.Layout()
        self.card_image_panel.FitInside()

        # update the card info tab
        self.card_name.SetLabel(card['cardname'])
        t = ''
        if card['manacost']:
            t = card['manacost']
        self.card_cost.SetLabel(t)
        t = card['type']
        if card['subtype']:
            t += ' - '+card['subtype']
        self.card_type.SetLabel(t)
        t = ''
        if card['cardtext']:
            t = re.sub('(<item>|</item>)','\n',card['cardtext']).strip()
        self.card_rules.SetLabel(t)
        self.card_rules.Wrap(145)
        t = ''
        if card['power']:
            t = card['power']+'/'+card['toughness']
        self.card_pt.SetLabel(t)
        t = ''
        if card['flavortext']:
            t = re.sub('(<item>|</item>)','\n',card['flavortext']).strip()
        self.card_flavor.SetLabel(t)
        self.card_flavor.Wrap(145)
        self.card_rarity.SetLabel(card['rarity'])
        self.card_artist.SetLabel(card['artist'])
        t = ''
        if card['rating']:
            t = card['rating']
        self.card_rating.SetLabel(t)
        t = ''
        if card['votes']:
            t = card['votes']
        self.card_votes.SetLabel(t)

        self.card_info_panel.Layout()
        self.card_info_panel.FitInside()
        self.card_info_panel.SetScrollRate(2,5)

        # update dbase info tab
        small = wx.Font(pointSize=8,family=wx.FONTFAMILY_SWISS,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL)
        children = self.dbgrid.GetChildren()
        for i in range(len(children)):
            self.dbgrid.Remove(0)
        self.dbase_info_panel.DestroyChildren()
        self.dbase_info_panel.Refresh()
        self.dbase_info_panel.Update()
        labels = []
        for key in card.keys():
            if card[key]:
                labels.append(wx.StaticText(self.dbase_info_panel,label=key+":"))
                labels[-1].SetFont(small)
                labels.append(wx.StaticText(self.dbase_info_panel,label=unicode(card[key])))
                labels[-1].SetFont(small)
        
        self.dbgrid.AddSpacer(item=(3,3),pos=(0,0))
        self.dbgrid.AddSpacer(item=(3,3),pos=(3,0))
        for i in range(len(labels)/2):
            self.dbgrid.Add(labels[2*i],pos=(i+1,1),flag=wx.ALIGN_RIGHT)
            self.dbgrid.Add(labels[2*i+1],pos=(i+1,2))

        self.dbase_info_panel.Layout()
        self.dbase_info_panel.FitInside()
        self.dbase_info_panel.SetScrollRate(2,5)

    def get_name(self):
        return self.card_name.GetLabel()
