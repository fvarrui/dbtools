import pyodbc

from .table import Table
from .view import View
from .column import Column
from .foreign_key import ForeignKey

class Database:

    conn : object = None

    def __init__(self, driver : str, server : str, db_name : str):
        self.driver = driver
        self.server = server
        self.db_name = db_name

    def connect(self):
        self.conn = pyodbc.connect(f"Driver={self.driver};Server={self.server};Database={self.db_name};Trusted_Connection=yes;")

    def disconnect(self):
        self.conn.close()

    def __fetchall(self, query: str) -> list:
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)        
            rows = cursor.fetchall()
        finally:
            cursor.close()
        return rows
    
    def __fetchone(self, query: str) -> object:
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)        
            row = cursor.fetchone()
        finally:
            cursor.close()
        return row

    def list_tables(self, prefix: str = "") -> list[str]:
        table_names = []
        for row in self.__fetchall(f"SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE table_name like '{prefix}%' and table_type = 'BASE TABLE' ORDER BY TABLE_NAME"):
            table_names.append(row.TABLE_NAME)
        return table_names

    def list_views(self, prefix: str = "") -> list[str]:
        view_names = []
        for row in self.__fetchall(f"SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE table_name like '{prefix}%' and table_type = 'VIEW' ORDER BY TABLE_NAME"):
            view_names.append(row.TABLE_NAME)
        return view_names
    
    def list_stored_procedures(self, prefix: str = "") -> list[str]:
        sp_names = []
        for row in self.__fetchall(f"SELECT * FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_NAME like '{prefix}%' and ROUTINE_TYPE = 'PROCEDURE' ORDER BY ROUTINE_NAME"):
            sp_names.append(row.ROUTINE_NAME)
        return sp_names
    
    def is_table(self, table_name: str) -> bool:
        row = self.__fetchone(
            f"""
            SELECT 
                CASE 
                    WHEN COUNT(*) > 0 THEN 'true'
                    ELSE 'false'
                END AS IS_TABLE
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE table_name = '{table_name}' and table_type = 'BASE TABLE'
            """
        )
        return row.IS_TABLE == 'true'
    
    def is_view(self, view_name: str) -> bool:
        row = self.__fetchone(
            f"""
            SELECT 
                CASE 
                    WHEN COUNT(*) > 0 THEN 'true'
                    ELSE 'false'
                END AS IS_VIEW
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE table_name = '{view_name}' and table_type = 'VIEW'
            """
        )
        return row.IS_VIEW == 'true'

    def exists_table_or_view(self, table_name: str) -> bool:
        row = self.__fetchone(
            f"""
            SELECT 
                CASE 
                    WHEN COUNT(*) > 0 THEN 'true'
                    ELSE 'false'
                END AS IT_EXISTS
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE table_name = '{table_name}';            
            """
        )
        return row.IT_EXISTS == 'true'
    
    def __get_table_comment(self, table_name: str) -> str:
        """
        Obtiene el comentario de una tabla
        - table_name: nombre de la tabla
        """
        row = self.__fetchone(
            f"""
            SELECT 
                ep.value as TABLE_COMMENT
            FROM sys.extended_properties ep
            JOIN sys.objects o ON ep.major_id = o.object_id
            WHERE ep.name = 'MS_Description' and o.type_desc = 'USER_TABLE' and o.name = '{table_name}'
            """
        )
        return row.TABLE_COMMENT if row else ''
    
    def __get_column_description(self, table_name: str, column_name: str) -> str:
        """
        Obtiene la descripción de una columna
        - table_name: nombre de la tabla o vista
        - column_name: nombre de la columna
        """
        row = self.__fetchone(
            f"""
            SELECT 
                t.name as TABLE_NAME, 
                c.name as COLUMN_NAME, 
                ep.value as COLUMN_DESCRIPTION
            FROM 
                sys.tables as t
                INNER JOIN sys.columns as c ON t.object_id = c.object_id
                LEFT JOIN sys.extended_properties as ep ON ep.major_id = c.object_id AND ep.minor_id = c.column_id AND ep.name = 'MS_Description' AND ep.class = 1
			WHERE t.name = '{table_name}' AND c.name = '{column_name}'
			UNION
            SELECT 
                t.name as TABLE_NAME, 
                c.name as COLUMN_NAME, 
                ep.value as COLUMN_DESCRIPTION
            FROM 
                sys.views as t
                INNER JOIN sys.columns as c ON t.object_id = c.object_id
                LEFT JOIN sys.extended_properties as ep ON ep.major_id = c.object_id AND ep.minor_id = c.column_id AND ep.name = 'MS_Description' AND ep.class = 1
            WHERE t.name = '{table_name}' AND c.name = '{column_name}'
            """
        )
        return row.COLUMN_DESCRIPTION
    
    def __get_primary_keys(self, table_name: str) -> list[str]:
        """
        Obtiene las claves primarias de una tabla
        - table_name: nombre de la tabla
        """
        rows = self.__fetchall(
            f"""
            SELECT 
                COLUMN_NAME
            FROM 
                INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE OBJECTPROPERTY(OBJECT_ID(CONSTRAINT_SCHEMA + '.' + QUOTENAME(CONSTRAINT_NAME)), 'IsPrimaryKey') = 1 AND TABLE_NAME = '{table_name}'
            """
        )
        return [ row.COLUMN_NAME for row in rows ]
    
    def __get_foreign_keys(self, table_name: str) -> list[ForeignKey]:
        """
        Obtiene las claves foráneas de una tabla
        - table_name: nombre de la tabla        
        """
        rows = self.__fetchall(
            f"""
            SELECT 
                fk.name AS FOREIGN_KEY_NAME,
                cf.name AS REFERENCING_COLUMN,
                tp.name AS REFERENCED_TABLE,
                cp.name AS REFERENCED_COLUMN
            FROM 
                sys.foreign_keys fk
                INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
                INNER JOIN sys.tables tp ON fk.referenced_object_id = tp.object_id
                INNER JOIN sys.columns cp ON tp.object_id = cp.object_id AND fkc.referenced_column_id = cp.column_id
                INNER JOIN sys.tables tf ON fk.parent_object_id = tf.object_id
                INNER JOIN sys.columns cf ON tf.object_id = cf.object_id AND fkc.parent_column_id = cf.column_id
            WHERE tf.name = '{table_name}'; 
            """        
        )
        return [ ForeignKey(row.FOREIGN_KEY_NAME, row.REFERENCING_COLUMN, row.REFERENCED_TABLE, row.REFERENCED_COLUMN) for row in rows ]
    
    def __get_columns(self, table_name: str) -> list[Column]:
        """
        Obtiene las columnas de una tabla o vista
        - table_name: nombre de la tabla o vista
        """
        rows = self.__fetchall(
            f"""
            SELECT 
                *
            FROM 
                INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION         
            """
        )
        columns = []
        for row in rows:
            is_nullable = row.IS_NULLABLE == "YES"
            column = Column(row.COLUMN_NAME, row.DATA_TYPE, row.CHARACTER_MAXIMUM_LENGTH, is_nullable)
            column.description = self.__get_column_description(table_name, column.name)
            columns.append(column)
        return columns
    
    def get_view(self, view_name: str) -> View:

        if not self.exists_table_or_view(view_name):
            raise Exception(f"La vista '{view_name}' no existe en la base de datos")

        # Crear la vista
        view = View()
        view.name = view_name

        # Obtiene las columnas de la vista
        view.columns = self.__get_columns(view_name)

        return view        

    def get_table(self, table_name: str) -> Table:

        if not self.exists_table_or_view(table_name):
            raise Exception(f"La tabla '{table_name}' no existe en la base de datos")

        # Crear la tabla
        table = Table()
        table.name = table_name
        table.description = self.__get_table_comment(table_name)

        # Obtiene las columnas de la tabla
        table.columns = self.__get_columns(table_name)

        # Obtiene las claves primarias y las asigna a las columnas correspondientes
        table.primary_keys = self.__get_primary_keys(table_name)
        for column in table.columns:
            if column.name in table.primary_keys:
                column.is_primary_key = True

        # Obtiene las claves foráneas y las asigna a las columnas correspondientes
        table.foreign_keys = self.__get_foreign_keys(table_name)
        for foreign_key in table.foreign_keys:
            for column in table.columns:
                if column.name == foreign_key.referencing_column:
                    column.relation = foreign_key

        return table
    
    def get_views(self, view_name: str) -> list[Table]:
        views = []
        for view_name in self.list_views():
            views.append(self.get_view(view_name))
        return views

    def get_tables(self, table_name: str) -> list[Table]:
        tables = []
        for table_name in self.list_tables():
            tables.append(self.get_table(table_name))
        return tables
