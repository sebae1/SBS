from __future__ import annotations

import os
import pathlib
import sqlite3
from enum import StrEnum

class AttrType(StrEnum):
    TEXT = 'TEXT'
    INTEGER = 'INTEGER'
    REAL = 'REAL'
    BLOB = 'BLOB'
    DATE = 'DATE'
    TIMESTAMP = 'TIMESTAMP'

class ForeignKeyOption(StrEnum):
    CASCADE = 'CASCADE'
    SET_NULL = 'SET NULL'
    SET_DEFAULT = 'SET DEFAULT'
    NO_ACTION = 'NO ACTION'
    RESTRICT = 'RESTRICT'

class Attribute:

    def __init__(
            self,
            name: str,
            dtype: AttrType,
            not_null: bool = False,
            default: any = None,
            pk: bool = False,
            unique: bool = False,
            checks: tuple[str,] = (),
            description: str = ''
        ):

        self.__name = name
        self.__dtype = dtype
        self.__not_null = self.bool_to_int(not_null)
        self.__default = self.bool_to_int(default)
        self.__pk = self.bool_to_int(pk)
        self.__unique = self.bool_to_int(unique)
        self.__checks = checks
        self.__description = description
    
    def __str__(self):
        return self.__name
    
    @staticmethod
    def bool_to_int(value:bool) -> int:
        if isinstance(value, bool):
            return 1 if value else 0
        return value
    
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
            attr: Attribute,
            parent_table: BaseTable,
            parent_attr: Attribute,
            on_delete: ForeignKeyOption = ForeignKeyOption.NO_ACTION,
            on_update: ForeignKeyOption = ForeignKeyOption.NO_ACTION
        ):
        self.__attr         = attr    
        self.__parent_table = parent_table
        self.__parent_attr  = parent_attr 
        self.__on_delete    = on_delete      
        self.__on_update    = on_update      

    @property
    def attr        (self): return self.__attr 
    @property
    def parent_attr (self): return self.__parent_attr    
    @property
    def parent_table(self): return self.__parent_table
    @property
    def on_delete   (self): return self.__on_delete      
    @property
    def on_update   (self): return self.__on_update      

    def __str__(self):
        """<참조테이블명>-<참조속성>-<FK속성>"""
        return f'{self.__parent_table.NAME}-{self.__parent_attr}-{self.__attr}'

    def get_creation_query(self) -> str:
        query = f'FOREIGN KEY ({self.__attr.name}) ' \
            f'REFERENCES {self.__parent_table.NAME}({self.__parent_attr.name}) ' \
            f'ON DELETE {self.__on_delete} ' \
            f'ON UPDATE {self.__on_update}'
        return query

class _ReadOnlyMeta(type):

    _locked = True

    def __setattr__(cls, name, value):
        if name != '_locked' and cls._locked:
            raise AttributeError('Cannot set attribute of this class')
        super().__setattr__(name, value)

    def lock_set_attr(cls):
        cls._locked = True

    def unlock_set_attr(cls):
        cls._locked = False

class BaseTable(metaclass=_ReadOnlyMeta):
    
    class Attributes:
        pass

    NAME = None
    FKS:tuple[ForeignKey,] = ()

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

class BaseDB(metaclass=_ReadOnlyMeta):

    DB_FILE_PATH = os.path.join(
        pathlib.Path(__file__).absolute().parent,
        'database.db'
    )
    CON = None
    CUR = None
    TABLES:tuple[BaseTable,] = ()

    class ValidationError(Exception):

        def __init__(self, error_message:str):
            Exception.__init__(self)
            self.__error_message = error_message
        
        def __str__(self):
            return self.__error_message

    @classmethod
    def validate(cls, strict:bool):
        """DB 스키마 검사
        문제가 있으면 raise 함

        strict:                      |   True    |      False     
        -----------------------------+-----------+----------------
        0. 파일 존재하지 않음        |   raise   | create new file
        1. 테이블 존재하지 않음      |   raise   | create and pass
        2. 속성 존재하지 않음        |   raise   | create and pass
        3. 속성의 조건 일치하지 않음 |   raise   |     raise
        4. 불필요한 테이블 존재함    |   raise   | delete and pass
        5. 불필요한 속성 존재함      |   raise   |     raise
        6. 외래키 설정 일치하지 않음 |   raise   |     raise
        """
        if strict \
            and not os.path.isfile(cls.DB_FILE_PATH): # 0
            raise cls.ValidationError('DB 파일이 존재하지 않음.')

        con = sqlite3.connect(cls.DB_FILE_PATH)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables_exist = set([r[0] for r in cur.fetchall()])

        def _validate_strict():
            tables_defined = set([table.NAME for table in cls.TABLES])
            if tables_defined-tables_exist: # 1
                con.close()
                raise cls.ValidationError(f'테이블 존재하지 않음: {", ".join(tables_defined-tables_exist)}')
            if tables_exist-tables_defined: # 4
                con.close()
                raise cls.ValidationError(f'불필요한 테이블 존재함: {", ".join(tables_exist-tables_defined)}')
            for table in cls.TABLES:
                name_vs_attr = {
                    attr.name: attr 
                    for attr in table.get_attributes()
                }
                cur.execute(f'PRAGMA table_info({table.NAME});')
                table_info = cur.fetchall()
                for column in table_info:
                    idx, name, dtype, nn, default, pk = column
                    if name not in name_vs_attr: # 5
                        con.close()
                        raise cls.ValidationError(f'불필요한 속성 존재함: {table.NAME}-{name}')
                    attr = name_vs_attr[name]
                    if attr.dtype != dtype \
                        or str(attr.nn) != str(nn) \
                        or str(attr.default) != str(default) \
                        or str(attr.pk) != str(pk): # 3
                        con.close()
                        raise cls.ValidationError(f'속성의 조건 일치하지 않음: {table.NAME}-{name}')
                    del name_vs_attr[name]
                if name_vs_attr: # 2
                    con.close()
                    raise cls.ValidationError(f'속성 존재하지 않음: {", ".join(list(name_vs_attr.keys()))}')

                label_vs_fk = {
                    str(fk): fk
                    for fk in table.FKS
                }
                cur.execute(f'PRAGMA foreign_key_list({table.NAME});')
                fk_info = cur.fetchall()
                for values in fk_info: # 6
                    idx, seq, parent_table_name, attr_name, \
                        parent_attr_name, on_update, on_delete, _ = values
                    label = f'{parent_table_name}-{parent_attr_name}-{attr_name}'
                    if label not in label_vs_fk:
                        con.close()
                        raise cls.ValidationError(f'외래키 일치하지 않음: {table.NAME}')
                    fk = label_vs_fk[label]
                    if fk.on_delete != on_delete \
                        or fk.on_update != on_update:
                        con.close()
                        raise cls.ValidationError(f'외래키 일치하지 않음: {table.NAME}')
                    del label_vs_fk[label]
                if label_vs_fk:
                    con.close()
                    raise cls.ValidationError(f'외래키 일치하지 않음: {table.NAME}')

        def _validate_not_strict():
            tables_defined = set([table.NAME for table in cls.TABLES])
            for table in tables_exist-tables_defined: # 4
                cur.execute(f'DROP TABLE {table};')
            for table in cls.TABLES:
                if table.NAME not in tables_exist: # 1
                    cur.execute(table.get_creation_query())
                    continue
                name_vs_attr = {
                    attr.name: attr 
                    for attr in table.get_attributes()
                }

                cur.execute(f'PRAGMA table_info({table.NAME});')
                table_info = cur.fetchall()
                for column in table_info:
                    idx, name, dtype, nn, default, pk = column
                    if name not in name_vs_attr: # 5
                        con.close()
                        raise cls.ValidationError(f'불필요한 속성 존재함: {table.NAME}-{name}')
                    attr = name_vs_attr[name]
                    if attr.dtype != dtype \
                        or str(attr.nn) != str(nn) \
                        or str(attr.default) != str(default) \
                        or str(attr.pk) != str(pk): # 3
                        con.close()
                        raise cls.ValidationError(f'속성의 조건 일치하지 않음: {table.NAME}-{name}')
                    del name_vs_attr[name]
                for name, attr in name_vs_attr.items(): # 2
                    item = f'{attr.name} {attr.dtype}'
                    if attr.default is not None:
                        item = f'{item} DEFAULT {attr.default}'
                    if attr.not_null:
                        item = f'{item} NOT NULL'
                    if attr.pk:
                        item = f'{item} PRIMARY KEY'
                    if attr.unique:
                        item = f'{item} UNIQUE'
                    cur.execute(f'ALTER TABLE {table.NAME} ADD COLUMN {item};')
                
                label_vs_fk = {
                    str(fk): fk
                    for fk in table.FKS
                }
                cur.execute(f'PRAGMA foreign_key_list({table.NAME});')
                fk_info = cur.fetchall()
                for values in fk_info: # 6
                    idx, seq, parent_table_name, attr_name, \
                        parent_attr_name, on_update, on_delete, _ = values
                    label = f'{parent_table_name}-{parent_attr_name}-{attr_name}'
                    if label not in label_vs_fk:
                        con.close()
                        raise cls.ValidationError(f'외래키 일치하지 않음: {table.NAME}')
                    fk = label_vs_fk[label]
                    if fk.on_delete != on_delete \
                        or fk.on_update != on_update:
                        con.close()
                        raise cls.ValidationError(f'외래키 일치하지 않음: {table.NAME}')
                    del label_vs_fk[label]
                if label_vs_fk:
                    con.close()
                    raise cls.ValidationError(f'외래키 일치하지 않음: {table.NAME}')

        if strict:
            _validate_strict()
        else:
            _validate_not_strict()

        cls.unlock_set_attr()
        cls.CON = con
        cls.CUR = cur
        cls.lock_set_attr()
    
    @classmethod
    def create_new(cls):
        if os.path.isfile(cls.DB_FILE_PATH):
            raise cls.ValidationError('DB 파일이 이미 존재함.')
        con = sqlite3.connect(cls.DB_FILE_PATH)
        cur = con.cursor()
        for table in cls.TABLES:
            query = table.get_creation_query()
            cur.execute(query)
        con.commit()
        con.close()
