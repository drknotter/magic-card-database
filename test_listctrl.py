#!/usr/bin/python

import wx
import wx.lib.mixins.listctrl as LCM

class MyApp(wx.App, LCM.ColumnSorterMixin):
    def OnInit(self):
        frame = wx.Frame(None, -1, "Hello from wxPython")

        id=wx.NewId()
        self.list=wx.ListCtrl(frame,id,style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.list.Show(True)

        self.list.InsertColumn(0,"Data #1")
        self.list.InsertColumn(1,"Data #2")
        self.list.InsertColumn(2,"Data #3")

        # 0 will insert at the start of the list
        pos = self.list.InsertStringItem(0,"hello")
        # add values in the other columns on the same row
        self.list.SetStringItem(pos,1,"world")
        self.list.SetStringItem(pos,2,"!")

        pos = self.list.InsertStringItem(0,"wat")
        self.list.SetStringItem(pos,1,"um")
        self.list.SetStringItem(pos,2,"wha")

        self.itemDataMap = {
            0: ("hello","world","!"),
            1: ("wat","um","wha")
            }

        LCM.ColumnSorterMixin.__init__(self,3)

        frame.Show(True)
        self.SetTopWindow(frame)
        return True

    def GetListCtrl(self):
        return self.list

app = MyApp(0)
app.MainLoop()
