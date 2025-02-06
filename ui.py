import datetime
import wx
from app import APP_NAME, VERSION
from db import DB, Transaction, Supplementary, TableSupplementary, TableAccountBook
from widget import DatePicker, FileSelector, Deposit
from filemanager import FileManager

class DialogTransaction(wx.Dialog):

    def __init__(self, parent, pk:int|None):
        """pk=None이면 '추가' 화면, 그렇지 않으면 '조회/수정'"""
        wx.Dialog.__init__(self, parent, title='거래 추가' if pk is None else '거래 조회/수정')
        self.__set_layout()
        self.__bind_events()

        self.__pk = pk
        if pk is None:
            self.__bt_confirm.SetLabel('추가')
            self.__tr = None
        else:
            self.__bt_confirm.SetLabel('수정')
            tr = DB.get_transaction(pk)
            self.__tr = tr
            self.__dp_date.date   = tr.date
            self.__tc_desc        .SetValue(tr.description)
            self.__tc_account     .SetValue(tr.account)
            self.__cb_type        .SetValue(tr.str_transaction_type)
            self.__sc_sv          .SetValue(tr.supply_value)
            self.__sc_vat         .SetValue(tr.vat)
            self.__tc_remark      .SetValue(tr.remark)
            self.__dp_deposit     .SetDate(tr.deposit)
            self.__fs_quotation   .SetFilepath(tr.get_supplementary(TableSupplementary.SupplementaryType.QUOTATION).filepath)
            self.__fs_transaction .SetFilepath(tr.get_supplementary(TableSupplementary.SupplementaryType.TRANSACTION).filepath) 
            self.__fs_invoice     .SetFilepath(tr.get_supplementary(TableSupplementary.SupplementaryType.INVOICE).filepath) 
    
    def __set_layout(self):
        st_date        = wx.StaticText(self, label='일자')
        st_desc        = wx.StaticText(self, label='내용')
        st_account     = wx.StaticText(self, label='거래처')
        st_type        = wx.StaticText(self, label='유형')
        st_sv          = wx.StaticText(self, label='금액')
        st_vat         = wx.StaticText(self, label='부가세')
        st_remark      = wx.StaticText(self, label='비고')
        st_deposit     = wx.StaticText(self, label='입금일')
        st_quotation   = wx.StaticText(self, label='견적서')
        st_transaction = wx.StaticText(self, label='명세서')
        st_invoice     = wx.StaticText(self, label='적격증빙')

        dp_date        = DatePicker(self)
        tc_desc        = wx.TextCtrl(self, size=(200, -1))
        tc_account     = wx.TextCtrl(self, size=(200, -1))
        cb_type        = wx.ComboBox(self, value='수입', choices=['수입', '지출', '고정자산'], style=wx.CB_READONLY)
        sc_sv          = wx.SpinCtrl(self, value='0', initial=0, min=0, max=9999999999)
        sc_vat         = wx.SpinCtrl(self, value='0', initial=0, min=0, max=9999999999)
        tc_remark      = wx.TextCtrl(self, size=(200, 50), style=wx.TE_MULTILINE)
        dp_deposit     = Deposit(self, None)
        fs_quotation   = FileSelector(self, '견적서', None)
        fs_transaction = FileSelector(self, '거래명세서', None)
        fs_invoice     = FileSelector(self, '적격증빙', None)

        sz_grid = wx.FlexGridSizer(11, 2, 5, 5)
        sz_grid.AddGrowableCol(0)
        sz_grid.AddGrowableRow(6)
        sz_grid.AddMany((
            (st_date       , 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (dp_date       , 0, wx.ALIGN_CENTER_VERTICAL),
            (st_desc       , 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (tc_desc       , 0, wx.ALIGN_CENTER_VERTICAL),
            (st_account    , 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (tc_account    , 0, wx.ALIGN_CENTER_VERTICAL),
            (st_type       , 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (cb_type       , 0, wx.ALIGN_CENTER_VERTICAL),
            (st_sv         , 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (sc_sv         , 0, wx.ALIGN_CENTER_VERTICAL),
            (st_vat        , 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (sc_vat        , 0, wx.ALIGN_CENTER_VERTICAL),
            (st_remark     , 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (tc_remark     , 0, wx.ALIGN_CENTER_VERTICAL),
            (st_deposit    , 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (dp_deposit    , 0, wx.ALIGN_CENTER_VERTICAL),
            (st_quotation  , 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (fs_quotation  , 0, wx.ALIGN_CENTER_VERTICAL),
            (st_transaction, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (fs_transaction, 0, wx.ALIGN_CENTER_VERTICAL),
            (st_invoice    , 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (fs_invoice    , 0, wx.ALIGN_CENTER_VERTICAL)
        ))

        bt_confirm = wx.Button(self, label='확인')
        bt_close   = wx.Button(self, label='닫기')
        sz_bt = wx.BoxSizer(wx.HORIZONTAL)
        sz_bt.AddMany((
            (bt_confirm, 0, wx.ALIGN_CENTER_VERTICAL), ((3, -1), 0),
            (bt_close  , 0, wx.ALIGN_CENTER_VERTICAL)
        ))

        sz_vert = wx.BoxSizer(wx.VERTICAL)
        sz_vert.AddMany((
            (sz_grid, 0), ((-1, 10), 0),
            (wx.StaticLine(self), 0, wx.EXPAND), ((-1, 10), 0),
            (sz_bt, 0, wx.ALIGN_RIGHT)
        ))
        sz = wx.BoxSizer(wx.HORIZONTAL)
        sz.Add(sz_vert, 1, wx.EXPAND|wx.ALL, 20)
        self.SetSizerAndFit(sz)

        self.__dp_date        = dp_date       
        self.__tc_desc        = tc_desc       
        self.__tc_account     = tc_account    
        self.__cb_type        = cb_type       
        self.__sc_sv          = sc_sv         
        self.__sc_vat         = sc_vat        
        self.__tc_remark      = tc_remark     
        self.__dp_deposit     = dp_deposit    
        self.__fs_quotation   = fs_quotation  
        self.__fs_transaction = fs_transaction
        self.__fs_invoice     = fs_invoice    
        self.__bt_confirm = bt_confirm
        self.__bt_close   = bt_close  
    
    def __bind_events(self):
        self.__bt_confirm.Bind(wx.EVT_BUTTON, self.__on_confirm)
        self.__bt_close  .Bind(wx.EVT_BUTTON, self.__on_close  )

    def __on_confirm(self, event):
        date = self.__dp_date.date
        desc = self.__tc_desc.GetValue().strip()
        acc = self.__tc_account.GetValue().strip()
        tran_type = self.__cb_type.GetSelection()
        sv = self.__sc_sv.GetValue()
        vat = self.__sc_vat.GetValue()
        remark = self.__tc_remark.GetValue()
        deposit = self.__dp_deposit.GetDate() if self.__dp_deposit.IsChecked() else None
        if not desc:
            wx.MessageBox('내용을 입력하세요.', '안내')
            return
        elif not acc:
            wx.MessageBox('거래처를 입력하세요.', '안내')
            return
        if self.__pk is None:
            suppls = {
                TableSupplementary.SupplementaryType.QUOTATION  : Supplementary(None, TableSupplementary.SupplementaryType.QUOTATION  , self.__fs_quotation  .GetFilepath()),
                TableSupplementary.SupplementaryType.TRANSACTION: Supplementary(None, TableSupplementary.SupplementaryType.TRANSACTION, self.__fs_transaction.GetFilepath()),
                TableSupplementary.SupplementaryType.INVOICE    : Supplementary(None, TableSupplementary.SupplementaryType.INVOICE    , self.__fs_invoice    .GetFilepath())
            }
        else:
            suppls = {
                TableSupplementary.SupplementaryType.QUOTATION  : self.__tr.get_supplementary(TableSupplementary.SupplementaryType.QUOTATION  ),
                TableSupplementary.SupplementaryType.TRANSACTION: self.__tr.get_supplementary(TableSupplementary.SupplementaryType.TRANSACTION),
                TableSupplementary.SupplementaryType.INVOICE    : self.__tr.get_supplementary(TableSupplementary.SupplementaryType.INVOICE    )
            }
            suppls[TableSupplementary.SupplementaryType.QUOTATION  ].set_filepath(self.__fs_quotation  .GetFilepath())
            suppls[TableSupplementary.SupplementaryType.TRANSACTION].set_filepath(self.__fs_transaction.GetFilepath())
            suppls[TableSupplementary.SupplementaryType.INVOICE    ].set_filepath(self.__fs_invoice    .GetFilepath())
        self.__tr = Transaction(self.__pk, date, desc, acc, tran_type, sv, vat, remark, deposit, suppls)
        self.EndModal(wx.ID_OK)
    
    def __on_close(self, event):
        self.EndModal(wx.ID_CLOSE)

    def GetTransaction(self) -> Transaction:
        return self.__tr

class PanelDashboard(wx.Panel):
    
    def __init__(self, parent: wx.Window):
        wx.Panel.__init__(self, parent)
        self.__set_layout()
        self.__bind_events()

    def __set_layout(self):
        return
    
    def __bind_events(self):
        return

class PanelAccountBook(wx.Panel):
    
    def __init__(self, parent: wx.Window):
        wx.Panel.__init__(self, parent)
        self.__set_layout()
        self.__bind_events()
        self.__on_search(None)

    def __set_layout(self):
        today = datetime.date.today()

        bt_week   = wx.Button(self, label='일주일', style=wx.BU_EXACTFIT)
        bt_month  = wx.Button(self, label='한 달', style=wx.BU_EXACTFIT)
        bt_year   = wx.Button(self, label='일 년', style=wx.BU_EXACTFIT)
        dp_start  = DatePicker(self, today-datetime.timedelta(days=7))
        dp_end    = DatePicker(self, today)
        ck_income = wx.CheckBox(self, label='수입')
        ck_exp    = wx.CheckBox(self, label='지출')
        ck_fixed  = wx.CheckBox(self, label='고정자산')
        bt_search = wx.Button(self, label='검색')

        ck_income.SetValue(True)
        ck_exp   .SetValue(True)
        ck_fixed .SetValue(True)

        sz_date_bt = wx.BoxSizer(wx.HORIZONTAL)
        sz_date_bt.AddMany((
            (bt_week , 1, wx.ALIGN_CENTER_VERTICAL), ((3, -1), 0),
            (bt_month, 1, wx.ALIGN_CENTER_VERTICAL), ((3, -1), 0),
            (bt_year , 1, wx.ALIGN_CENTER_VERTICAL)
        ))
        sz_date = wx.BoxSizer(wx.HORIZONTAL)
        sz_date.AddMany((
            (dp_start, 0, wx.ALIGN_CENTER_VERTICAL), ((5, -1), 0),
            (wx.StaticText(self, label='-'), 0, wx.ALIGN_CENTER_VERTICAL), ((5, -1), 0),
            (dp_end, 0, wx.ALIGN_CENTER_VERTICAL)
        ))
        sz_ck = wx.BoxSizer(wx.HORIZONTAL)
        sz_ck.AddMany((
            (ck_income, 0, wx.ALIGN_CENTER_VERTICAL), ((5, -1), 0),
            (ck_exp   , 0, wx.ALIGN_CENTER_VERTICAL), ((5, -1), 0),
            (ck_fixed , 0, wx.ALIGN_CENTER_VERTICAL)
        ))
        sz_search = wx.GridBagSizer(3, 10)
        sz_search.AddMany((
            (sz_date_bt, (0, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL|wx.EXPAND),
            (sz_date, (1, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL),
            (sz_ck, (2, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL),
            (bt_search, (0, 1), (3, 1), wx.EXPAND)
        ))

        bt_add  = wx.Button(self, label='작성')
        bt_del  = wx.Button(self, label='삭제')
        sz_bt = wx.BoxSizer(wx.HORIZONTAL)
        sz_bt.AddMany((
            (bt_add , 0, wx.ALIGN_CENTER_VERTICAL), ((5, -1), 0),
            (bt_del , 0, wx.ALIGN_CENTER_VERTICAL)
        ))

        lc = wx.ListCtrl(self, style=wx.LC_REPORT)
        lc.AppendColumn(''        , wx.LIST_FORMAT_CENTER, 0)
        lc.AppendColumn('일자'    , wx.LIST_FORMAT_CENTER, 100)
        lc.AppendColumn('내용'    , wx.LIST_FORMAT_CENTER, 200)
        lc.AppendColumn('거래처'  , wx.LIST_FORMAT_CENTER, 100)
        lc.AppendColumn('유형'    , wx.LIST_FORMAT_CENTER, 100)
        lc.AppendColumn('금액'    , wx.LIST_FORMAT_CENTER, 100)
        lc.AppendColumn('부가세'  , wx.LIST_FORMAT_CENTER, 100)
        lc.AppendColumn('비고'    , wx.LIST_FORMAT_CENTER, 200)
        lc.AppendColumn('입금일'  , wx.LIST_FORMAT_CENTER, 100)
        lc.AppendColumn('견적서'  , wx.LIST_FORMAT_CENTER, 80)
        lc.AppendColumn('명세서'  , wx.LIST_FORMAT_CENTER, 80)
        lc.AppendColumn('적격증빙', wx.LIST_FORMAT_CENTER, 80)

        sz_top = wx.BoxSizer(wx.HORIZONTAL)
        sz_top.AddMany((
            (sz_search, 0, wx.ALIGN_CENTER_VERTICAL), ((10, -1), 1),
            (sz_bt, 0, wx.ALIGN_BOTTOM)
        ))
        sz_vert = wx.BoxSizer(wx.VERTICAL)
        sz_vert.AddMany((
            (sz_top, 0, wx.EXPAND), ((-1, 5), 0),
            (lc, 1, wx.EXPAND)
        ))
        sz = wx.BoxSizer(wx.HORIZONTAL)
        sz.Add(sz_vert, 1, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(sz)

        self.__bt_add  = bt_add 
        self.__bt_del  = bt_del 
        self.__lc = lc
        self.__bt_week   = bt_week  
        self.__bt_month  = bt_month 
        self.__bt_year   = bt_year  
        self.__dp_start  = dp_start 
        self.__dp_end    = dp_end   
        self.__ck_income = ck_income
        self.__ck_exp    = ck_exp   
        self.__ck_fixed  = ck_fixed 
        self.__bt_search = bt_search
    
    def __bind_events(self):
        self.__bt_add.Bind(wx.EVT_BUTTON, self.__on_add)
        self.__bt_del.Bind(wx.EVT_BUTTON, self.__on_del)
        self.__lc.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.__on_activate_item)
        self.__bt_week .Bind(wx.EVT_BUTTON, self.__on_week )
        self.__bt_month.Bind(wx.EVT_BUTTON, self.__on_month)
        self.__bt_year .Bind(wx.EVT_BUTTON, self.__on_year )
        self.__bt_search.Bind(wx.EVT_BUTTON, self.__on_search)
    
    def __on_add(self, event):
        dlg = DialogTransaction(self, None)
        res = dlg.ShowModal()
        tr = dlg.GetTransaction()
        dlg.Destroy()
        if res != wx.ID_OK:
            return
        DB.insert_transaction(tr)

        files_to_remove = []
        for supp_type in TableSupplementary.SupplementaryType:
            supp = tr.get_supplementary(supp_type)
            if supp.filepath is not None:
                files_to_remove.append(supp.filepath)
        if files_to_remove:
            dlg = wx.MessageDialog(self, '견적서/거래명세서/적격증빙 원본 파일을 삭제할까요?', '안내', style=wx.YES_NO|wx.NO_DEFAULT)
            res = dlg.ShowModal()
            dlg.Destroy()
            if res == wx.ID_YES:
                for filepath in files_to_remove:
                    FileManager.remove_file(filepath)

        self.__on_search(None)
        wx.MessageBox('장부를 작성했습니다.', '안내', parent=self)

    def __on_del(self, event):
        lc = self.__lc
        indice = []
        pks = []
        for i in range(lc.GetItemCount()):
            if lc.IsSelected(i):
                indice.append(i)
                pks.append(lc.GetItemData(i))
        if not indice:
            return
        dlg = wx.MessageDialog(self, f'{len(indice):,} 개의 장부 기록을 삭제할까요?', '안내', style=wx.YES_NO|wx.NO_DEFAULT)
        res = dlg.ShowModal()
        dlg.Destroy()
        if res != wx.ID_YES:
            return
        DB.delete_transactions(pks)
        lc.Freeze()
        for i in indice[::-1]:
            lc.DeleteItem(i)
        lc.Thaw()
        wx.MessageBox('장부 기록을 삭제했습니다.', '안내', parent=self)
    
    def __on_activate_item(self, event):
        pk = event.Data
        idx = event.Index
        dlg = DialogTransaction(self, pk)
        res = dlg.ShowModal()
        tr = dlg.GetTransaction()
        dlg.Destroy()
        if res != wx.ID_OK:
            return
        files_to_remove = []
        for supp_type in TableSupplementary.SupplementaryType:
            supp = tr.get_supplementary(supp_type)
            if supp.filepath is not None \
                and supp.filepath[1] == ':':
                files_to_remove.append(supp.filepath)
            DB.update_supplementary(supp.pk, supp.filepath)
        DB.update_transaction(tr)
        self.set_transaction(idx, tr)
        if files_to_remove:
            dlg = wx.MessageDialog(self, '견적서/거래명세서/적격증빙 원본 파일을 삭제할까요?', '안내', style=wx.YES_NO|wx.NO_DEFAULT)
            res = dlg.ShowModal()
            dlg.Destroy()
            if res == wx.ID_YES:
                for filepath in files_to_remove:
                    FileManager.remove_file(filepath)
        wx.MessageBox('장부를 수정했습니다.', '안내', parent=self)

    def __on_week (self, event):
        today = datetime.date.today()
        start = today-datetime.timedelta(7)
        self.__dp_start.date = start
        self.__dp_end.date = today

    def __on_month(self, event):
        today = datetime.date.today()
        start = today-datetime.timedelta(30)
        self.__dp_start.date = start
        self.__dp_end.date = today

    def __on_year (self, event):
        today = datetime.date.today()
        start = today-datetime.timedelta(365)
        self.__dp_start.date = start
        self.__dp_end.date = today

    def __on_search(self, event):
        date1 = self.__dp_start.date
        date2 = self.__dp_end.date
        if date1 > date2:
            wx.MessageBox('검색 기간의 시작일자가 종료일자보다 늦습니다.', '안내', parent=self)
            return
        tran_types = []
        if self.__ck_income.GetValue():
            tran_types.append(TableAccountBook.TransactionType.INCOME)
        if self.__ck_exp.GetValue():
            tran_types.append(TableAccountBook.TransactionType.EXPENDITURE)
        if self.__ck_fixed.GetValue():
            tran_types.append(TableAccountBook.TransactionType.FIXED_ASSET)
        if not tran_types:
            wx.MessageBox('거래유형을 적어도 한 개 이상 선택하세요.', '안내', parent=self)
            return
        dlgp = wx.ProgressDialog('안내', '장부 기록을 검색 중입니다.')
        dlgp.Pulse()
        lc = self.__lc
        lc.Freeze()
        lc.DeleteAllItems()
        trs = DB.search_transaction(date1, date2, tran_types)
        for i, tr in enumerate(trs):
            self.insert_transaction(i, tr)
        lc.Thaw()
        dlgp.Destroy()
        wx.GetTopLevelParent(self).Raise()

    def insert_transaction(self, index:int, transaction:Transaction):
        lc = self.__lc
        lc.InsertItem(index, '')
        self.set_transaction(index, transaction)

    def set_transaction(self, index:int, transaction:Transaction):
        tr = transaction
        lc = self.__lc
        lc.Freeze()
        lc.SetItemData(index, tr.pk)
        lc.SetItem(index,  1, tr.str_date)
        lc.SetItem(index,  2, tr.description)
        lc.SetItem(index,  3, tr.account)
        lc.SetItem(index,  4, tr.str_transaction_type)
        lc.SetItem(index,  5, tr.str_supply_value)
        lc.SetItem(index,  6, tr.str_vat)
        lc.SetItem(index,  7, tr.remark)
        lc.SetItem(index,  8, tr.str_deposit)
        lc.SetItem(index,  9, str(tr.get_supplementary(TableSupplementary.SupplementaryType.QUOTATION)))
        lc.SetItem(index, 10, str(tr.get_supplementary(TableSupplementary.SupplementaryType.TRANSACTION)))
        lc.SetItem(index, 11, str(tr.get_supplementary(TableSupplementary.SupplementaryType.INVOICE)))
        lc.Thaw()

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

    
