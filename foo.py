import wx
 
class MyForm(wx.Frame):
 
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, 'My Form')
 
        # Add a panel so it looks the correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)
 
        bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_OTHER, (16, 16))
        font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)
 
        titleIco = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        title = wx.StaticText(self.panel, wx.ID_ANY, 'My Title')
        title.SetFont(font)
 
        # 1st row of widgets
        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        inputOneIco = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        labelOne = wx.StaticText(self.panel, wx.ID_ANY, 'Name')
        inputTxtOne = wx.TextCtrl(self.panel, wx.ID_ANY,'')
 
        sampleList = ['zero', 'one', 'two', 'three', 'four', 'five',
                      'six', 'seven', 'eight']
        rb = wx.RadioBox(
                self.panel, wx.ID_ANY, "wx.RadioBox", wx.DefaultPosition,
                wx.DefaultSize, sampleList, 2, wx.RA_SPECIFY_COLS
                )
 
        # 2nd row of widgets
        multiTxt = wx.TextCtrl(self.panel, wx.ID_ANY, '',
                               size=(200,100),
                               style=wx.TE_MULTILINE)
        sampleList = ['one', 'two', 'three', 'four']
        combo = wx.ComboBox(self.panel, wx.ID_ANY, 'Default', wx.DefaultPosition,
                            (100,-1), sampleList, wx.CB_DROPDOWN)
 
        # Create the sizers
        topSizer    = wx.BoxSizer(wx.VERTICAL)
        titleSizer  = wx.BoxSizer(wx.HORIZONTAL)
        bagSizer    = wx.GridBagSizer(hgap=5, vgap=5)
 
        # Add widgets to sizers
        titleSizer.Add(titleIco, 0, wx.ALL, 5)
        titleSizer.Add(title, 0, wx.ALL, 5)
 
        bagSizer.Add(inputOneIco, pos=(0,0),
                     flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,
                     border=5)
        bagSizer.Add(labelOne, pos=(0,1),
                     flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,
                     border=5)
        bagSizer.Add(inputTxtOne, pos=(0,2),
                     flag=wx.EXPAND|wx.ALL,
                     border=10)
        bagSizer.AddGrowableCol(2, 0)
        bagSizer.Add(rb, pos=(0,3), span=(3,2))
 
        bagSizer.Add(multiTxt, pos=(1,0),
                     flag=wx.ALL,
                     border=5)
        bagSizer.Add(combo, pos=(1,1),
                     flag=wx.ALL,
                     border=5)
 
        # Add sub-sizers to topSizer
        topSizer.Add(titleSizer, 0, wx.CENTER)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(bagSizer, 0, wx.ALL|wx.EXPAND, 5)
 
        self.panel.SetSizer(topSizer)
 
        # SetSizeHints(minW, minH, maxW, maxH)
        self.SetSizeHints(250,200,700,300)
        topSizer.Fit(self)
 
# Run the program
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MyForm().Show()
    app.MainLoop()
