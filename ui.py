import datetime
import wx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from app import APP_NAME
from db import DB, Transaction, Supplementary, TableSupplementary, TableAccountBook
from widget import DatePicker, FileSelector, Deposit
from filemanager import FileManager
from ossl import DialogOSSL
from info import DialogHelp

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

    COLOR_INCOME = '#00B050'
    COLOR_EXPENDITURE = '#C00000'
    COLOR_FIXED_ASSET = '#E97132'
    
    def __init__(self, parent: wx.Window):
        wx.Panel.__init__(self, parent)
        self.__set_layout()
        self.__bind_events()
        self.__on_something_changed(None)

    def __set_layout(self):
        # ///////////////////////////////////////////////////////////
        # 좌측의 컨트롤 패널
        pn_control = wx.Panel(self, style=wx.BORDER_SIMPLE)
        
        today = datetime.date.today()
        sb_year = wx.StaticBox(pn_control, label='연도')
        rb_recent_year = wx.RadioButton(sb_year, label='최근 1 년', style=wx.RB_GROUP)
        rb_every_year = wx.RadioButton(sb_year, label='연도별')
        sc_every_year = wx.SpinCtrl(sb_year, value=str(today.year), initial=today.year, min=2020, max=2100)
        sz_year = wx.GridBagSizer(5, 5)
        sz_year.AddMany((
            (rb_recent_year, (0, 0), (1, 2), wx.ALIGN_CENTER_VERTICAL),
            (rb_every_year, (1, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL),
            (sc_every_year, (1, 1), (1, 1), wx.ALIGN_CENTER_VERTICAL)
        ))
        sz_sb_year = wx.StaticBoxSizer(sb_year)
        sz_sb_year.Add(sz_year, 1, wx.EXPAND|wx.ALL, 10)

        sb_income = wx.StaticBox(pn_control, label='수입')
        rb_tran_date = wx.RadioButton(sb_income, label='장부일자기준', style=wx.RB_GROUP)
        rb_deposit_date = wx.RadioButton(sb_income, label='입금일자기준')
        rb_deposit_date.SetToolTip('미입금건은 표시되지 않음.')
        sz_income = wx.BoxSizer(wx.VERTICAL)
        sz_income.AddMany((
            (rb_tran_date, 0), ((-1, 5), 0),
            (rb_deposit_date, 0)
        ))
        sz_sb_income = wx.StaticBoxSizer(sb_income)
        sz_sb_income.Add(sz_income, 1, wx.EXPAND|wx.ALL, 10)

        sz_control_vert = wx.BoxSizer(wx.VERTICAL)
        sz_control_vert.AddMany((
            (sz_sb_year, 0, wx.EXPAND), ((-1, 10), 0),
            (sz_sb_income, 0, wx.EXPAND), ((-1, 10), 1)
        ))
        sz_control = wx.BoxSizer(wx.HORIZONTAL)
        sz_control.Add(sz_control_vert, 1, wx.EXPAND|wx.ALL, 10)
        pn_control.SetSizerAndFit(sz_control)

        # ///////////////////////////////////////////////////////////
        # 우측의 표시 패널
        pn_board = wx.Panel(self)

        font = self.GetFont()
        font.SetPointSize(20)
        bold = font.Bold()
        st_income_label      = wx.StaticText(pn_board, size=(250, -1), style=wx.ALIGN_CENTRE_HORIZONTAL, label='수입')
        st_expenditure_label = wx.StaticText(pn_board, size=(250, -1), style=wx.ALIGN_CENTRE_HORIZONTAL, label='지출')
        st_fixed_asset_label = wx.StaticText(pn_board, size=(250, -1), style=wx.ALIGN_CENTRE_HORIZONTAL, label='고정자산')
        st_income_sv         = wx.StaticText(pn_board, size=(250, -1), style=wx.ALIGN_CENTRE_HORIZONTAL, label='0')
        st_expenditure_sv    = wx.StaticText(pn_board, size=(250, -1), style=wx.ALIGN_CENTRE_HORIZONTAL, label='0')
        st_fixed_asset_sv    = wx.StaticText(pn_board, size=(250, -1), style=wx.ALIGN_CENTRE_HORIZONTAL, label='0')
        st_income_vat        = wx.StaticText(pn_board, size=(250, -1), style=wx.ALIGN_CENTRE_HORIZONTAL, label='0')
        st_expenditure_vat   = wx.StaticText(pn_board, size=(250, -1), style=wx.ALIGN_CENTRE_HORIZONTAL, label='0')
        st_fixed_asset_vat   = wx.StaticText(pn_board, size=(250, -1), style=wx.ALIGN_CENTRE_HORIZONTAL, label='0')
        st_supply_value      = wx.StaticText(pn_board, style=wx.ALIGN_CENTRE_HORIZONTAL, label='금액')
        st_vat               = wx.StaticText(pn_board, style=wx.ALIGN_CENTRE_HORIZONTAL, label='부가세')
        st_income_label     .SetFont(bold)
        st_expenditure_label.SetFont(bold)
        st_fixed_asset_label.SetFont(bold)
        st_income_sv        .SetFont(bold)
        st_expenditure_sv   .SetFont(bold)
        st_fixed_asset_sv   .SetFont(bold)
        st_income_vat       .SetFont(bold)
        st_expenditure_vat  .SetFont(bold)
        st_fixed_asset_vat  .SetFont(bold)
        st_supply_value     .SetFont(bold)
        st_vat              .SetFont(bold)
        st_income_sv        .SetForegroundColour(wx.Colour(__class__.COLOR_INCOME     ))
        st_expenditure_sv   .SetForegroundColour(wx.Colour(__class__.COLOR_EXPENDITURE))
        st_fixed_asset_sv   .SetForegroundColour(wx.Colour(__class__.COLOR_FIXED_ASSET))
        st_income_vat       .SetForegroundColour(wx.Colour(__class__.COLOR_INCOME     ))
        st_expenditure_vat  .SetForegroundColour(wx.Colour(__class__.COLOR_EXPENDITURE))
        st_fixed_asset_vat  .SetForegroundColour(wx.Colour(__class__.COLOR_FIXED_ASSET))

        sz_grid_value = wx.FlexGridSizer(3, 4, 10, 10)
        sz_grid_value.AddGrowableCol(0)
        sz_grid_value.AddMany((
            ((-1, -1), 0), (st_income_label, 0, wx.ALIGN_CENTER), (st_expenditure_label, 0, wx.ALIGN_CENTER), (st_fixed_asset_label, 0, wx.ALIGN_CENTER),
            (st_supply_value, 0, wx.ALIGN_CENTER), (st_income_sv, 0, wx.ALIGN_CENTER), (st_expenditure_sv, 0, wx.ALIGN_CENTER), (st_fixed_asset_sv, 0, wx.ALIGN_CENTER),
            (st_vat, 0, wx.ALIGN_CENTER), (st_income_vat, 0, wx.ALIGN_CENTER), (st_expenditure_vat, 0, wx.ALIGN_CENTER), (st_fixed_asset_vat, 0, wx.ALIGN_CENTER)
        ))

        fig = plt.figure()
        ax = fig.add_subplot(111)
        cv = FigureCanvas(pn_board, -1, fig)

        sz_vert = wx.BoxSizer(wx.VERTICAL)
        sz_vert.AddMany((
            (sz_grid_value, 0, wx.ALIGN_CENTER_HORIZONTAL), ((-1, 10), 0),
            (cv, 1, wx.EXPAND)
        ))
        pn_board.SetSizer(sz_vert)

        # ///////////////////////////////////////////////////////////
        # 전체 레이아웃
        sz_horz = wx.BoxSizer(wx.HORIZONTAL)
        sz_horz.AddMany((
            (pn_control, 0, wx.EXPAND), ((10, -1), 0),
            (pn_board, 1, wx.EXPAND)
        ))
        sz = wx.BoxSizer(wx.HORIZONTAL)
        sz.Add(sz_horz, 1, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(sz)

        self.__rb_recent_year  = rb_recent_year 
        self.__rb_every_year   = rb_every_year  
        self.__sc_every_year   = sc_every_year  
        self.__rb_tran_date    = rb_tran_date   
        self.__rb_deposit_date = rb_deposit_date
        self.__st_income_sv       = st_income_sv      
        self.__st_expenditure_sv  = st_expenditure_sv 
        self.__st_fixed_asset_sv  = st_fixed_asset_sv 
        self.__st_income_vat      = st_income_vat     
        self.__st_expenditure_vat = st_expenditure_vat
        self.__st_fixed_asset_vat = st_fixed_asset_vat
        self.__fig = fig
        self.__ax  = ax 
        self.__cv  = cv 
        self.__annotation = None
        self.__bars = []
    
    def __bind_events(self):
        self.__rb_recent_year .Bind(wx.EVT_RADIOBUTTON, self.__on_something_changed)
        self.__rb_every_year  .Bind(wx.EVT_RADIOBUTTON, self.__on_something_changed)
        self.__sc_every_year  .Bind(wx.EVT_SPINCTRL   , self.__on_something_changed)
        self.__rb_tran_date   .Bind(wx.EVT_RADIOBUTTON, self.__on_something_changed)
        self.__rb_deposit_date.Bind(wx.EVT_RADIOBUTTON, self.__on_something_changed)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.__on_destroy)
        self.__cv.mpl_connect('motion_notify_event', self.__on_hover_canvas)

    def __on_destroy(self, event):
        plt.close(self.__fig)
        event.Skip()

    def __on_something_changed(self, event):
        dlgp = wx.ProgressDialog('안내', '데이터를 수집 중입니다.')
        dlgp.Pulse()
        self.__sc_every_year.Enable(self.__rb_every_year.GetValue())
        if self.__rb_recent_year.GetValue():
            today = datetime.date.today()
            year = today.year
            month = today.month+1
            if month == 13:
                year += 1
                month = 1
            date2 = datetime.date(year, month, 1)
            date1 = date2.replace(year=year-1)
            date2 -= datetime.timedelta(days=1)
        else:
            year = self.__sc_every_year.GetValue()
            date1 = datetime.date(year, 1, 1)
            date2 = datetime.date(year, 12, 31)
        months = [(date1.month+i-1)%12+1 for i in range(12)]
        bar_graph_data = {
            '수입': [0 for _ in range(12)],
            '지출': [0 for _ in range(12)],
            '고정자산': [0 for _ in range(12)]
        }
        bar_colors = {
            '수입'    : __class__.COLOR_INCOME     ,
            '지출'    : __class__.COLOR_EXPENDITURE,
            '고정자산': __class__.COLOR_FIXED_ASSET
        }
        tran_types = [tt for tt in TableAccountBook.TransactionType]
        trs = DB.search_transaction(date1, date2, tran_types)
        svs = {tt:0 for tt in TableAccountBook.TransactionType}
        vats = {tt:0 for tt in TableAccountBook.TransactionType}
        flag_deposit = self.__rb_deposit_date.GetValue()
        for tr in trs:
            if tr.transaction_type == TableAccountBook.TransactionType.INCOME \
                and flag_deposit \
                and tr.deposit is None:
                    continue
            month_index = months.index(tr.date.month)
            if tr.transaction_type == TableAccountBook.TransactionType.INCOME:
                bar_graph_data['수입'][month_index] += tr.supply_value
            elif tr.transaction_type == TableAccountBook.TransactionType.EXPENDITURE:
                bar_graph_data['지출'][month_index] += tr.supply_value
            elif tr.transaction_type == TableAccountBook.TransactionType.FIXED_ASSET:
                bar_graph_data['고정자산'][month_index] += tr.supply_value
            svs[tr.transaction_type] += tr.supply_value
            vats[tr.transaction_type] += tr.vat
        self.__st_income_sv      .SetLabel(f'{svs[TableAccountBook.TransactionType.INCOME]:,}'     )
        self.__st_expenditure_sv .SetLabel(f'{svs[TableAccountBook.TransactionType.EXPENDITURE]:,}')
        self.__st_fixed_asset_sv .SetLabel(f'{svs[TableAccountBook.TransactionType.FIXED_ASSET]:,}')
        self.__st_income_vat     .SetLabel(f'{vats[TableAccountBook.TransactionType.INCOME]:,}'     )
        self.__st_expenditure_vat.SetLabel(f'{vats[TableAccountBook.TransactionType.EXPENDITURE]:,}')
        self.__st_fixed_asset_vat.SetLabel(f'{vats[TableAccountBook.TransactionType.FIXED_ASSET]:,}')
        self.__ax.clear()
        self.__ax.set_title('금액')
        x = np.arange(12) 
        width = 0.25
        multiplier = 0
        self.__bars.clear()
        for label, values in bar_graph_data.items():
            offset = width * multiplier
            self.__bars.extend(
                self.__ax.bar(
                    x+offset, 
                    values, 
                    width, 
                    label=label, 
                    color=bar_colors[label]
                )
            )
            multiplier += 1
        self.__annotation = self.__ax.annotate(
            '', 
            xy = (0, 0), 
            xytext = (0, 10), 
            textcoords ='offset points',
            ha = 'center',  
            va = 'bottom',
            bbox = dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.8),
            arrowprops = dict(arrowstyle='->', color='black')
        )
        self.__annotation.set_visible(False)
        self.__ax.tick_params(axis='both', which='both', labelleft=False, bottom=False, left=False)
        self.__ax.set_xticks(x+width, [f'{m}월' for m in months])
        self.__ax.legend(loc='lower left', ncols=3, bbox_to_anchor=(0, 1))
        self.__fig.tight_layout()
        self.__cv.draw()
        dlgp.Destroy()

    def __on_hover_canvas(self, event):
        if self.__annotation is None:
            return
        vis = self.__annotation.get_visible()
        if event.inaxes == self.__ax:
            for bar in self.__bars:
                contains, _ = bar.contains(event)
                if contains:
                    value = bar.get_height()
                    self.__annotation.xy = (bar.get_x() + bar.get_width()/2, value)
                    self.__annotation.set_text(f'{value:,} 원')
                    self.__annotation.set_visible(True)
                    self.__cv.draw_idle()
                    return
        if vis:
            self.__annotation.set_visible(False)
            self.__cv.draw_idle()

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
        wx.Frame.__init__(self, None, title=APP_NAME)
        self.__set_layout()
        self.__set_menubar()

        self.SetSize((1200, 800))
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

    def __set_menubar(self):
        menubar = wx.MenuBar()
        menu = wx.Menu()
        menubar.Append(menu, '메뉴')
        self._mi_license = menu.Append(-1, 'OSS 라이센스')
        self.Bind(wx.EVT_MENU, self.__on_license, self._mi_license)
        self._mi_print = menu.Append(-1, '도움말')
        self.Bind(wx.EVT_MENU, self.__on_help, self._mi_print)
        menu.AppendSeparator()
        self._mi_quit = menu.Append(-1, '종료')
        self.Bind(wx.EVT_MENU, self.__on_quit, self._mi_quit)
        self.SetMenuBar(menubar)
    
    def __on_license(self, event):
        dlg = DialogOSSL(self)
        dlg.ShowModal()
        dlg.Destroy()

    def __on_help(self, event):
        dlg = DialogHelp(self)
        dlg.ShowModal()
        dlg.Destroy()

    def __on_quit(self, event):
        self.Destroy()