from __future__ import annotations

import os
import datetime
from copy import deepcopy
from enum import IntEnum
from dbmanager import BaseTable, BaseDB, Attribute, AttrType, ForeignKey, ForeignKeyOption
from filemanager import FileManager

class TableAccountBook(BaseTable):

    class TransactionType(IntEnum):
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
        DEPOSIT = Attribute('deposit', AttrType.DATE, default=None, description='입금일자')
    
    NAME = 'account_book'
    FKS:tuple[ForeignKey,] = ()

class TableSupplementary(BaseTable):

    class SupplementaryType(IntEnum):
        QUOTATION = 0
        TRANSACTION = 1
        INVOICE = 2
    
    class Attributes:
        PK = Attribute('pk', AttrType.INTEGER, True, pk=True)
        AB_PK = Attribute('account_book_pk', AttrType.INTEGER, True, description='장부 PK')
        TYPE = Attribute('type', AttrType.INTEGER, True, checks=('>=0', '<=2'), description='0:견적서|1:거래명세서|2:적격증빙')
        PATH = Attribute('file_path', AttrType.TEXT, default=None, description='파일 경로')

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

class Transaction:

    def __init__(
            self,
            pk: int|None,
            date: datetime.date,
            description: str,
            account: str,
            transaction_type: TableAccountBook.TransactionType,
            supply_value: int,
            vat: int,
            remark: str,
            deposit: datetime.date,
            supplementaries: dict[TableSupplementary.SupplementaryType, Supplementary]
        ):
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        if isinstance(deposit, str):
            deposit = datetime.datetime.strptime(deposit, '%Y-%m-%d').date()
        self.__pk               = pk              
        self.__date             = date            
        self.__description      = description     
        self.__account          = account         
        self.__transaction_type = transaction_type
        self.__supply_value     = supply_value    
        self.__vat              = vat             
        self.__remark           = remark          
        self.__deposit          = deposit         
        self.__supplementaries  = supplementaries.copy()

    @property
    def pk(self): return self.__pk
    @property
    def date(self): return self.__date
    @property
    def description(self): return self.__description
    @property
    def account(self): return self.__account
    @property
    def transaction_type(self): return self.__transaction_type
    @property
    def supply_value(self): return self.__supply_value
    @property
    def vat(self): return self.__vat
    @property
    def remark(self): return self.__remark
    @property
    def deposit(self): return self.__deposit

    @property
    def str_date(self):
        return self.__date.strftime('%Y/%m/%d')[2:]
    
    @property
    def str_transaction_type(self):
        if self.__transaction_type == TableAccountBook.TransactionType.INCOME:
            return '수입'
        elif self.__transaction_type == TableAccountBook.TransactionType.EXPENDITURE:
            return '지출'
        elif self.__transaction_type == TableAccountBook.TransactionType.FIXED_ASSET:
            return '고정자산'
    
    @property
    def str_supply_value(self):
        return f'{self.__supply_value:,}'

    @property
    def str_vat(self):
        return f'{self.__vat:,}'

    @property
    def str_deposit(self):
        if self.__deposit is None:
            return ''
        else:
            return self.__deposit.strftime('%Y/%m/%d')[2:]
        
    @property
    def clean_account(self):
        """파일명에 사용할 수 없는 특수문자들과 공백을 제거한 거래처명"""
        # TODO
        return self.__account.replace(' ', '')

    def set_pk(self, value):
        self.__pk = value

    def set_date(self, value):
        self.__date = value

    def set_description(self, value):
        self.__description = value

    def set_account(self, value):
        self.__account = value

    def set_transaction_type(self, value):
        self.__transaction_type = value

    def set_supply_value(self, value):
        self.__supply_value = value

    def set_vat(self, value):
        self.__vat = value

    def set_remark(self, value):
        self.__remark = value

    def set_deposit(self, value):
        self.__deposit = value

    def get_supplementary(self, supplementary_type:TableSupplementary.SupplementaryType) -> Supplementary:
        return self.__supplementaries[supplementary_type]

    def set_supplementary(self, supplementary:Supplementary):
        self.__supplementaries[supplementary.supplementary_type] = supplementary

    def get_supplementary_file_path(self, supplementary_type:TableSupplementary.SupplementaryType) -> str:
        tran_type = {
            0: '수입',
            1: '지출',
            2: '자산'
        }.get(self.transaction_type, self.transaction_type)
        supp_type = {
            0: '견적서',
            1: '거래명세서',
            2: '적격증빙'
        }.get(supplementary_type, supplementary_type)
        date = self.date
        year = date.year
        month = date.month
        day = date.day
        file_name = f'{str(year)[-2:]}{month:>02}{day:>02}_{tran_type}_{self.clean_account}_{supp_type}'
        file_path = os.path.join(str(year), f'{month:>02}', file_name)
        return file_path

class Supplementary:

    def __init__(self, pk:int, supplementary_type:TableSupplementary.SupplementaryType, filepath:str):
        self.__pk = pk
        self.__supplementary_type = supplementary_type
        self.__filepath = filepath
    
    def __str__(self):
        if self.__filepath is None:
            return ''
        else:
            return 'O'

    @property
    def pk(self): return self.__pk
    @property
    def supplementary_type(self): return self.__supplementary_type
    @property
    def filepath(self): return self.__filepath
    
    def set_pk(self, pk:int):
        self.__pk = pk

    def set_filepath(self, filepath:str|None):
        self.__filepath = filepath

class DB(BaseDB):

    TABLES:tuple[BaseTable,] = (
        TableAccountBook, 
        TableSupplementary
    )

    @classmethod
    def get_transaction(cls, pk:int) -> Transaction:
        table = TableAccountBook
        attrs = table.Attributes
        cls.CUR.execute(
            f'SELECT {attrs.DATE}, {attrs.DESC}, {attrs.ACC}, {attrs.TYPE}, ' \
            f'{attrs.SV}, {attrs.VAT}, {attrs.REMARK}, {attrs.DEPOSIT} '
            f'FROM {table} WHERE {attrs.PK}=?;',
            (pk,)
        )
        date, desc, acc, tr_type, \
            sv, vat, remark, deposit = cls.CUR.fetchone()
        tr = Transaction(pk, date, desc, acc, tr_type, sv, vat, remark, deposit, cls.get_supplementaries(pk))
        return tr

    @classmethod
    def insert_transaction(cls, transaction:Transaction) -> Transaction:
        """pk=None인 Transaction으로 레코드 생성하고 pk 업데이트된 Transaction 반환
        supplementary의 pk는 무시하고 새 pk로 업데이트함
        """
        tr = transaction
        new_tr = deepcopy(tr)
        table = TableAccountBook
        attrs = table.Attributes
        cls.CUR.execute(
            f'INSERT INTO {table} (' \
            f'{attrs.DATE}, {attrs.DESC}, {attrs.ACC}, {attrs.TYPE}, ' \
            f'{attrs.SV}, {attrs.VAT}, {attrs.REMARK}, {attrs.DEPOSIT}' \
            ') VALUES (?, ?, ?, ?, ?, ?, ?, ?);',
            (
                tr.date, tr.description, tr.account, tr.transaction_type,
                tr.supply_value, tr.vat, tr.remark, tr.deposit
            )
        )
        cls.CON.commit()
        pk = cls.CUR.lastrowid
        new_tr.set_pk(pk)
        table = TableSupplementary
        attrs = table.Attributes
        for supp_type in table.SupplementaryType:
            filepath = new_tr.get_supplementary(supp_type).filepath
            if filepath is None:
                new_filepath = None
            else:
                ext = os.path.splitext(filepath)[-1]
                new_filepath = f'{new_tr.get_supplementary_file_path(supp_type)}{ext}'
                FileManager.move_file(filepath, new_filepath)
            cls.CUR.execute(
                f'INSERT INTO {table} (' \
                f'{attrs.AB_PK}, {attrs.TYPE}, {attrs.PATH}' \
                ') VALUES (?, ?, ?)',
                (pk, supp_type, new_filepath)
            )
            supp = Supplementary(cls.CUR.lastrowid, supp_type, new_filepath)
            new_tr.set_supplementary(supp)
        cls.CON.commit()
        return new_tr
    
    @classmethod
    def update_transaction(cls, transaction:Transaction):
        """pk, supplementaries를 제외한 나머지 속성 업데이트"""
        tr = transaction
        table = TableAccountBook
        attrs = table.Attributes
        cls.CUR.execute(
            f'UPDATE {table} SET ' \
            f'{attrs.DATE}=?, {attrs.DESC}=?, {attrs.ACC}=?, {attrs.TYPE}=?, ' \
            f'{attrs.SV}=?, {attrs.VAT}=?, {attrs.REMARK}=?, {attrs.DEPOSIT}=?' \
            f' WHERE {attrs.PK}=?;',
            (
                tr.date, tr.description, tr.account, tr.transaction_type,
                tr.supply_value, tr.vat, tr.remark, tr.deposit,
                tr.pk
            )
        )
        cls.CON.commit()

    @classmethod
    def delete_transactions(cls, pks:list|int):
        if isinstance(pks, int):
            pks = [pks,]
        pks = tuple(pks)
        placeholders = ', '.join(['?' for _ in range(len(pks))])
        table = TableSupplementary
        attrs = table.Attributes
        cls.CUR.execute(
            f'SELECT {attrs.PATH} FROM {table} WHERE {attrs.AB_PK} IN ({placeholders}) AND {attrs.PATH} IS NOT NULL;',
            pks
        )
        for record in cls.CUR.fetchall():
            filepath = record[0]
            FileManager.remove_file(filepath)

        table = TableAccountBook
        attrs = table.Attributes
        cls.CUR.execute(
            f'DELETE FROM {table} WHERE {attrs.PK} IN ({placeholders});',
            pks
        )
        cls.CON.commit()
    
    @classmethod
    def search_transaction(
            cls, 
            date_start: datetime.date, 
            date_end: datetime.date,
            transaction_types: list[TableAccountBook.TransactionType,]
        ) -> list[Transaction,]:
        table = TableAccountBook
        attrs = table.Attributes
        placeholders = ', '.join(['?' for _ in range(len(transaction_types))])
        cls.CUR.execute(
            f'SELECT {attrs.PK}, {attrs.DATE}, {attrs.DESC}, {attrs.ACC}, {attrs.TYPE}, ' \
            f'{attrs.SV}, {attrs.VAT}, {attrs.REMARK}, {attrs.DEPOSIT} '
            f'FROM {table} WHERE {attrs.DATE}>=? AND {attrs.DATE}<=? AND {attrs.TYPE} IN ({placeholders}) ' \
            f'ORDER BY {attrs.DATE} DESC;',
            (date_start, date_end, *transaction_types)
        )
        trs = []
        for record in cls.CUR.fetchall():
            pk, date, desc, acc, tr_type, \
                sv, vat, remark, deposit = record
            tr = Transaction(pk, date, desc, acc, tr_type, sv, vat, remark, deposit, cls.get_supplementaries(pk))
            trs.append(tr)
        return trs

    @classmethod
    def get_supplementaries(
            cls, 
            account_book_pk: int
        ) -> dict[TableSupplementary.SupplementaryType, Supplementary]:
        table = TableSupplementary
        attrs = table.Attributes
        cls.CUR.execute(
            f'SELECT {attrs.PK}, {attrs.TYPE}, {attrs.PATH} FROM {table} WHERE {attrs.AB_PK}=?;',
            (account_book_pk,)
        )
        supplementaries = {}
        for supp in cls.CUR.fetchall():
            pk, supp_type, filepath = supp
            supplementaries[supp_type] = Supplementary(pk, supp_type, filepath)
        for supp_type in TableSupplementary.SupplementaryType:
            if supp_type in supplementaries:
                continue
            cls.CUR.execute(
                f'INSERT INTO {table} ({attrs.AB_PK}, {attrs.TYPE}) VALUES (?, ?);',
                (account_book_pk, supp_type)
            )
            pk = cls.CUR.lastrowid
            supplementaries[supp_type] = Supplementary(pk, supp_type, None)
        cls.CON.commit()
        return supplementaries

    @classmethod
    def update_supplementary(cls, pk:int, filepath:str|None):
        table = TableSupplementary
        attrs = table.Attributes
        if filepath is None:
            cls.CUR.execute(f'SELECT {attrs.PATH} FROM {table} WHERE {attrs.PK}=?;', (pk,))
            old_file_path = cls.CUR.fetchone()[0]
            if old_file_path is not None:
                FileManager.remove_file(old_file_path)
            new_filepath = None
        else:
            cls.CUR.execute(f'SELECT {attrs.AB_PK}, {attrs.TYPE} FROM {table} WHERE {attrs.PK}=?;', (pk,))
            ab_pk, supp_type = cls.CUR.fetchone()
            tr = cls.get_transaction(ab_pk)
            ext = os.path.splitext(filepath)[-1]
            new_filepath = f'{tr.get_supplementary_file_path(supp_type)}{ext}'
            if filepath == new_filepath:
                return
            FileManager.move_file(filepath, new_filepath)
        cls.CUR.execute(
            f'UPDATE {table} SET {attrs.PATH}=? WHERE {attrs.PK}=?;',
            (new_filepath, pk)
        )
        cls.CON.commit()

