import wx
from app import APP_NAME, VERSION

class PanelDashboard(wx.Panel):
    
    def __init__(self, parent: wx.Window):
        wx.Panel.__init__(self, parent)

class PanelAccountBook(wx.Panel):
    
    def __init__(self, parent: wx.Window):
        wx.Panel.__init__(self, parent)

class FrameMain(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title=f'{APP_NAME} ({VERSION})')
        self.__set_layout()

        self.SetSize((700, 500))
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def __set_layout(self):
        pn_main = wx.Panel(self)
        nb = wx.Notebook(pn_main)
        pn_db = PanelDashboard(nb)
        pn_ab = PanelAccountBook(nb)
        nb.AddPage(pn_db, '대시보드')
        nb.AddPage(pn_ab, '장부')

        sz = wx.BoxSizer(wx.HORIZONTAL)
        sz.Add(nb, 1, wx.EXPAND|wx.ALL, 15)
        pn_main.SetSizer(sz)

    
