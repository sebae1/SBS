import os
import traceback
import wx
from ui import FrameMain
from db import DB

def main():
    app = wx.App()
    try:
        if not os.path.isfile(DB.DB_FILE_PATH):
            DB.create_new()
        else:
            DB.validate(False)
    except DB.ValidationError as e:
        wx.MessageBox(f'DB 검사 중 오류가 발생했씁니다.\n\n{e}', '안내')
    except:
        wx.MessageBox(f'DB 검사 중 예기치 않은 오류가 발생했습니다.\n\n{traceback.format_exc()}', '안내')
    else:
        DB.CUR.execute('PRAGMA foreign_keys = ON;')
        FrameMain().Show()
    app.MainLoop()

if __name__ == '__main__':
    main()