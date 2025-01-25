import wx
from ui import FrameMain

def main():
    app = wx.App()
    FrameMain().Show()
    app.MainLoop()

if __name__ == '__main__':
    main()