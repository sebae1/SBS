from __future__ import annotations

import os
import pathlib
import sqlite3
from enum import Enum

# 속성 기본 타입
TEXT = 'TEXT'
INTEGER = 'INTEGER'
REAL = 'REAL'
BLOB = 'BLOB'
DATE = 'DATE'
TIMESTAMP = 'TIMESTAMP'

# FK 옵션
CASCADE = 'CASCADE'
SET_NULL = 'SET NULL'
SET_DEFAULT = 'SET DEFAULT'
NO_ACTION = 'NO ACTION'
RESTRICT = 'RESTRICT'

class Attribute:

    def __init__(
            self,
            name: str,
            dtype: str,
            not_null: bool = False,
            default: any = None,
            pk: bool = False,
            unique: bool = False,
            checks: tuple[str,] = (),
            description: str = ''
        ):
        self.__name = name
        self.__dtype = dtype
        self.__not_null = not_null
        self.__default = default
        self.__pk = pk
        self.__unique = unique
        self.__checks = checks
        self.__description = description
    
    def __str__(self):
        return self.__name
    
    @property
    def name(self): return self.__name
    @property
    def dtype(self): return self.__dtype
    @property
    def not_null(self): return self.__not_null
    @property
    def nn(self): return self.__not_null
    @property
    def default(self): return self.__default
    @property
    def pk(self): return self.__pk
    @property
    def unique(self): return self.__unique
    @property
    def checks(self): return self.__checks
    @property
    def description(self): return self.__description
    @property
    def desc(self): return self.__description

class ForeignKey:

    def __init__(
            self,
            parent_attr: Attribute,
            reference_table: BaseTable,
            reference_attr: Attribute,
            on_delete: str = NO_ACTION,
            on_update: str = NO_ACTION
        ):
        self.__parent_attr     = parent_attr    
        self.__reference_table = reference_table
        self.__reference_attr  = reference_attr 
        self.__on_delete       = on_delete      
        self.__on_update       = on_update      
    
    @property
    def parent_attr    (self): return self.__parent_attr    
    @property
    def reference_table(self): return self.__reference_table
    @property
    def reference_attr (self): return self.__reference_attr 
    @property
    def on_delete      (self): return self.__on_delete      
    @property
    def on_update      (self): return self.__on_update      

    def get_creation_query(self) -> str:
        query = f'FOREIGN KEY ({self.__parent_attr.name}) ' \
            f'REFERENCES {self.__reference_table.NAME}({self.__reference_attr.name}) ' \
            f'ON DELETE {self.__on_delete} ' \
            f'ON UPDATE {self.__on_update}'
        return query

class _ReadOnlyMeta(type):

    def __setattr__(cls, name, value):
        raise AttributeError('Cannot set attribute of this class')

class BaseTable(metaclass=_ReadOnlyMeta):

    NAME = None
    FKS:tuple[ForeignKey,] = ()

    class Attributes:
        pass

    @classmethod
    def get_attributes(cls) -> list[Attribute,]:
        attributes = []
        for key in dir(cls.Attributes):
            attr = getattr(cls.Attributes, key)
            if isinstance(attr, Attribute):
                attributes.append(attr)
        return attributes

    @classmethod
    def get_pk(cls) -> Attribute|None:
        for key in dir(cls.Attributes):
            attr = getattr(cls.Attributes, key)
            if not isinstance(attr, Attribute):
                continue
            if attr.pk:
                return attr

    @classmethod
    def get_creation_query(cls) -> str:
        attrs = []
        for attr in cls.get_attributes():
            item = f'{attr.name} {attr.dtype}'
            if attr.default is not None:
                item = f'{item} DEFAULT {attr.default}'
            if attr.not_null:
                item = f'{item} NOT NULL'
            if attr.pk:
                item = f'{item} PRIMARY KEY'
            if attr.unique:
                item = f'{item} UNIQUE'
            if attr.checks:
                check = [
                    c if c.startswith(attr.name) else f'{attr.name}{c}'
                    for c in attr.checks
                ]
                check = ' AND '.join(check)
                item = f'{item} CHECK ({check})'
            attrs.append(item)
        attrs = ', '.join(attrs)
        query = f'CREATE TABLE {cls.NAME} ({attrs}'
        if cls.FKS:
            fks = [fk.get_creation_query() for fk in cls.FKS]
            fks = ', '.join(fks)
            query = f'{query}, {fks}'
        query = f'{query});'
        return query

# ///////////////////////////////////////////////////////////////////////////////

class TableAccountBook(BaseTable):

    NAME = 'account_book'

    class TransactionType(Enum):
        INCOME = 0
        EXPENDITURE = 1
        FIXED_ASSET = 2

    class Attributes:
        PK = Attribute('pk', INTEGER, True, pk=True)
        DATE = Attribute('date', DATE, True, description='거래일자')
        DESC = Attribute('description', TEXT, True, description='거래내역')
        ACC = Attribute('account', TEXT, True, description='거래처')
        TYPE = Attribute('type', INTEGER, True, checks=('>=0', '<=2'), description='0:수입|1:지출|2:고정자산')
        SV = Attribute('supply_value', INTEGER, True, checks=('>=0',), description='공급가액')
        VAT = Attribute('value_added_tax', INTEGER, True, checks=('>=0',), description='부가세')
        REMARK = Attribute('remark', TEXT, description='비고')
        DEPOSIT = Attribute('deposit', INTEGER, True, default=0, checks=('>=0', '<=1'), description='입금여부')
        QUO = Attribute('quotation', TEXT, description='견적서 파일 경로')
        TRANSACTION = Attribute('transac', TEXT, description='거래명세서 파일 경로')
        INVOICE = Attribute('invoice', TEXT, description='적격증빙 파일 경로')

class DB(metaclass=_ReadOnlyMeta):

    DB_FILE_PATH = os.path.join(
        pathlib.Path(__file__).absolute().parent,
        'database.db'
    )

    TABLES:tuple[BaseTable,] = (TableAccountBook,)

    @classmethod
    def validate(cls):
        # TODO raise or pass
        return
    
    @classmethod
    def create_new(cls):
        # //////////////////////////////////////////
        # TODO 파일 존재 검사
        if os.path.isfile(cls.DB_FILE_PATH):
            os.remove(cls.DB_FILE_PATH)
        # //////////////////////////////////////////

        con = sqlite3.connect(cls.DB_FILE_PATH)
        cur = con.cursor()
        for table in cls.TABLES:
            query = table.get_creation_query()
            print(query)
            cur.execute(query)
        con.commit()

# /////////////////////////////////////////////////////////////////////////

if __name__ == '__main__':
    DB.create_new()