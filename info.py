import wx
from app import APP_NAME, VERSION

HELP_TEXT = f"""{APP_NAME} ({VERSION})

"""

class DialogHelp(wx.Dialog):

    def __init__(self, parent:wx.Frame):
        wx.Dialog.__init__(self, parent, title='도움말', style=wx.DEFAULT_DIALOG_STYLE)
        self._set_layout()
    
    def _set_layout(self):
        st1 = wx.StaticText(self, label=HELP_TEXT)
        st1.SetFont(self.GetFont().Bold())

        st2 = wx.StaticText(self, label='2025 하이프웨어(Hypeware)\ncontact@hypeware.co.kr', style=wx.ALIGN_CENTER)
        font = st2.GetFont().Italic()
        st2.SetFont(font)

        sz_vert = wx.BoxSizer(wx.VERTICAL)
        sz_vert.AddMany((
            (st1, 0, wx.ALIGN_CENTER_HORIZONTAL),
            ((-1, 10), 0),
            (st2, 0, wx.ALIGN_CENTER_HORIZONTAL)
        ))
        sz = wx.BoxSizer(wx.HORIZONTAL)
        sz.Add(sz_vert, 1, wx.EXPAND|wx.ALL, 30)
        self.SetSizerAndFit(sz)
        self.SetSize(self.GetBestSize())
        self.CenterOnScreen()