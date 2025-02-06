import os
import wx
import wx.adv
import wx.lib.newevent
import datetime
from filemanager import FileManager

class DatePicker(wx.Panel):
    
    EvtDateChanged, EVT_DATE_CHANGED = wx.lib.newevent.NewEvent()

    def __init__(self, parent, date:datetime.date|None=None):

        wx.Panel.__init__(self, parent)
        if date is None:
            date = datetime.date.today()
        self.txt_date = wx.TextCtrl(self, size=(80, -1), style=wx.TE_CENTER|wx.TE_READONLY)
        self.txt_date.Bind(wx.EVT_CHAR_HOOK, self._on_char)
        self.btn_date = wx.Button(self, label='선택', style=wx.BU_EXACTFIT)
        self.btn_date.Bind(wx.EVT_BUTTON, self.show_dialog)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany((
            (self.txt_date, 1, wx.ALIGN_CENTER_VERTICAL), ((1, -1), 0),
            (self.btn_date, 0, wx.ALIGN_CENTER_VERTICAL)
        ))
        self.SetSizerAndFit(sizer)

        self.date = date

    def show_dialog(self, event):
        date_dialog = _DateDialog(self)
        with date_dialog:
            if date_dialog.ShowModal() == wx.ID_CANCEL:
                return
        if date_dialog.date:
            self._date = date_dialog.date
            self._set_date_value()
            evt = __class__.EvtDateChanged(attr1=self._date)
            wx.PostEvent(self, evt)

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        if value is None:
            value = datetime.date.today()
        elif isinstance(value, datetime.datetime):
            value = value.date()
        elif not isinstance(value, datetime.date):
            return
        self._date = value
        if self._date:
            self._set_date_value()

    def _set_date_value(self):
        date_str = self._date.strftime('%Y/%m/%d')[2:]
        self.txt_date.SetValue(date_str)

    def _on_char(self, event):
        kc = event.GetKeyCode()
        kc_map = {
            48:"0", 49:"1", 50:"2", 51:"3", 52:"4",
            53:"5", 54:"6", 55:"7", 56:"8", 57:"9",
            wx.WXK_NUMPAD0:"0", wx.WXK_NUMPAD1:"1", wx.WXK_NUMPAD2:"2", wx.WXK_NUMPAD3:"3", wx.WXK_NUMPAD4:"4",
            wx.WXK_NUMPAD5:"5", wx.WXK_NUMPAD6:"6", wx.WXK_NUMPAD7:"7", wx.WXK_NUMPAD8:"8", wx.WXK_NUMPAD9:"9"
        }
        if kc in (314, 316):
            event.Skip()
        elif kc in kc_map:
            ip = self.txt_date.GetInsertionPoint()
            if ip == 10:
                ip -= 1
            if ip in (4, 7):
                self.txt_date.SetInsertionPoint(ip+1)
            else:
                old_value = list(self.txt_date.GetValue())
                old_value[ip] = kc_map[kc]
                old_value = "".join(old_value)
                try   : date = datetime.datetime.strptime(old_value, self._format).date()
                except: return
                else  : self.date = date
                self.txt_date.SetValue(old_value)
                if ip < 9:
                    ip += 1
                if old_value[ip] == "-":
                    ip += 1
                self.txt_date.SetInsertionPoint(ip)
        else:
            return

    def EnableChange(self, flag:bool):
        self.btn_date.Enable(flag)

class _DateDialog(wx.Dialog):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.date = None
        self.calendar = wx.adv.CalendarCtrl(self, date=parent.date)
        self.calendar.Bind(wx.adv.EVT_CALENDAR, self.double_clicked)
        self.calendar.Bind(wx.adv.EVT_CALENDAR_SEL_CHANGED, self.date_change)
        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.calendar, flag= wx.BOTTOM, border=5)
        sizer.Add(button_sizer, flag=wx.EXPAND)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(sizer, flag=wx.ALL, border=5)
        self.SetSizerAndFit(main_sizer)
        self.CenterOnParent()

    def date_change(self, event):
        date_format = '%d/%m/%y %H:%M:%S'
        date_str = self.calendar.GetDate()
        date = date_str.Format(date_format)
        dt = datetime.datetime.strptime(date, date_format)
        self.date = dt.date()

    def double_clicked(self, event):
        self.EndModal(wx.ID_OK)

class FileSelector(wx.Window):

    def __init__(self, parent, filetype:str, filepath:str|None):
        wx.Window.__init__(self, parent)
        self.__filetype = filetype
        self.__filepath = filepath
        self.__set_layout()
        self.__bind_events()
        self.__set_filename()

    def __set_layout(self):
        tc = wx.TextCtrl(self, size=(150, -1), style=wx.TE_READONLY)
        bt_open = wx.Button(self, label='열기', style=wx.BU_EXACTFIT)
        bt_edit = wx.Button(self, label='선택', style=wx.BU_EXACTFIT)
        bt_del  = wx.Button(self, label='삭제', style=wx.BU_EXACTFIT)
        sz = wx.BoxSizer(wx.HORIZONTAL)
        sz.AddMany((
            (tc, 0, wx.ALIGN_CENTER_VERTICAL), ((3, -1), 0),
            (bt_open, 0, wx.ALIGN_CENTER_VERTICAL), ((3, -1), 0),
            (bt_edit, 0, wx.ALIGN_CENTER_VERTICAL), ((3, -1), 0),
            (bt_del , 0, wx.ALIGN_CENTER_VERTICAL)
        ))
        self.SetSizerAndFit(sz)

        self.__tc      = tc     
        self.__bt_open = bt_open
        self.__bt_edit = bt_edit
        self.__bt_del  = bt_del 

    def __bind_events(self):
        self.__bt_open.Bind(wx.EVT_BUTTON, self.__on_open)
        self.__bt_edit.Bind(wx.EVT_BUTTON, self.__on_edit)
        self.__bt_del .Bind(wx.EVT_BUTTON, self.__on_del )
    
    def __on_open(self, event):
        if self.__filepath is None:
            wx.MessageBox('선택된 파일이 없습니다.', '안내', parent=self)
        else:
            if self.__filepath[1] == ':':
                os.startfile(self.__filepath)
            else:
                os.startfile(os.path.join(FileManager.ROOT_DIR, self.__filepath))

    def __on_edit(self, event):
        dlg = wx.FileDialog(None, f'{self.__filetype} 파일을 선택하세요.', wildcard=f'{self.__filetype} 파일 (*.pdf;*.xlsx)|*.pdf;*.xlsx', style=wx.FD_FILE_MUST_EXIST|wx.FD_OPEN)
        res = dlg.ShowModal()
        filepath = dlg.GetPath()
        dlg.Destroy()
        if res != wx.ID_OK:
            return
        self.__filepath = filepath
        self.__set_filename()

    def __on_del(self, event):
        if self.__filepath is None:
            wx.MessageBox('선택된 파일이 없습니다.', '안내', parent=self)
            return
        dlg = wx.MessageDialog(None, '파일을 삭제할까요?', '안내', style=wx.YES_NO|wx.NO_DEFAULT)
        res = dlg.ShowModal()
        dlg.Destroy()
        if res == wx.ID_YES:
            self.__filepath = None
            self.__set_filename()

    def __set_filename(self):
        if self.__filepath is None:
            self.__tc.Clear()
        else:
            filename = os.path.split(self.__filepath)[-1]
            self.__tc.SetValue(filename)

    def SetFilepath(self, filepath:str|None):
        self.__filepath = filepath
        self.__set_filename()

    def GetFilepath(self) -> str|None:
        return self.__filepath

    def GetFilepathStr(self) -> str|None:
        return '' if self.__filepath is None else self.__filepath

class Deposit(wx.Window):

    def __init__(self, parent, date:datetime.date|None):
        wx.Window.__init__(self, parent)
        if date is None:
            date = datetime.date.today()
        self.__date = date
        self.__set_layout()
        self.__bind_events()
        self.__ck.SetValue(False)
        self.__on_check(None)
    
    def __set_layout(self):
        dp = DatePicker(self, self.__date)
        ck = wx.CheckBox(self, label='입금완료')
        sz = wx.BoxSizer(wx.HORIZONTAL)
        sz.AddMany((
            (dp, 0, wx.ALIGN_CENTER_VERTICAL), ((5, -1), 0),
            (ck, 0, wx.ALIGN_CENTER_VERTICAL)
        ))
        self.SetSizerAndFit(sz)

        self.__dp = dp
        self.__ck = ck

    def __bind_events(self):
        self.__ck.Bind(wx.EVT_CHECKBOX, self.__on_check)
    
    def __on_check(self, event):
        flag = self.__ck.IsChecked()
        self.__dp.EnableChange(flag)
        if flag:
            self.__dp.date = self.__dp.date
        else:
            self.__dp.txt_date.Clear()

    def IsChecked(self) -> bool:
        return self.__ck.IsChecked()

    def GetDate(self) -> datetime.date|None:
        return self.__dp.date

    def SetDate(self, date:datetime.date|None):
        if date is None:
            self.__ck.SetValue(False)
        else:
            self.__ck.SetValue(True)
            self.__dp.date = date
        self.__on_check(None)
