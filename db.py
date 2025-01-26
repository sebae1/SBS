from __future__ import annotations

from enum import Enum
from dbmanager import BaseTable, BaseDB, Attribute, AttrType, ForeignKey, ForeignKeyOption

class TableAccountBook(BaseTable):

    class TransactionType(Enum):
        INCOME = 0
        EXPENDITURE = 1
        FIXED_ASSET = 2

    class Attributes:
        PK = Attribute('pk', AttrType.INTEGER, True, pk=True)
        DATE = Attribute('date', AttrType.DATE, True, description='거래일자')
        DESC = Attribute('description', AttrType.TEXT, True, description='거래내역')
        ACC = Attribute('account', AttrType.TEXT, True, description='거래처')
        TYPE = Attribute('type', AttrType.INTEGER, True, checks=('>=0', '<=2'), description='0:수입|1:지출|2:고정자산')
        SV = Attribute('supply_value', AttrType.INTEGER, True, checks=('>=0',), description='공급가액')
        VAT = Attribute('value_added_tax', AttrType.INTEGER, True, checks=('>=0',), description='부가세')
        REMARK = Attribute('remark', AttrType.TEXT, description='비고')
        DEPOSIT = Attribute('deposit', AttrType.INTEGER, True, default=0, checks=('>=0', '<=1'), description='입금여부')
    
    NAME = 'account_book'
    FKS:tuple[ForeignKey,] = ()

class TableSupplementary(BaseTable):

    class SupplementaryType(Enum):
        QUOTATION = 0
        TRANSACTION = 1
        INVOICE = 2
    
    class Attributes:
        PK = Attribute('pk', AttrType.INTEGER, True, pk=True)
        AB_PK = Attribute('account_book_pk', AttrType.INTEGER, True, description='장부 PK')
        TYPE = Attribute('type', AttrType.INTEGER, True, checks=('>=0', '<=2'), description='0:견적서|1:거래명세서|2:적격증빙')
        PATH = Attribute('file_path', AttrType.TEXT, True, description='파일 경로')

    NAME = 'supplementary'
    FKS:tuple[ForeignKey,] = (
        ForeignKey(
            Attributes.AB_PK, 
            TableAccountBook, 
            TableAccountBook.Attributes.PK, 
            ForeignKeyOption.CASCADE, 
            ForeignKeyOption.CASCADE
        ),
    )

class DB(BaseDB):

    TABLES:tuple[BaseTable,] = (
        TableAccountBook, 
        TableSupplementary
    )
