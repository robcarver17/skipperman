from app.backend.reporting.arrangement.arrange_options import ArrangementOptionsAndGroupOrder
from app.backend.reporting.options_and_parameters.print_options import PrintOptions
from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *

PRINT_OPTIONS_TABLE = "print_options_table"
INDEX_PRINT_OPTIONS_TABLE = "index_print_options_table"


class sqlDataListOfPrintOptions(GenericSqlData):
    def read(self, report_name: str) -> PrintOptions:
        try:
            if self.table_does_not_exist(PRINT_OPTIONS_TABLE):
                return PrintOptions()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s WHERE %s='%s' ''' % (
                REPORT_OPTION_KEY, REPORT_OPTION_VALUE, PRINT_OPTIONS_TABLE, REPORT_NAME, report_name
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading print options" % str(e1))
        finally:
            self.close()

        as_dict = dict([(raw_item[0], str(raw_item[1])) for raw_item in raw_list ])

        return   PrintOptions.from_dict_of_str(as_dict)


    def write(self, print_options: PrintOptions, report_name: str):
            try:
                if self.table_does_not_exist(PRINT_OPTIONS_TABLE):
                    self.create_table()

                ## NEEDS TO DELETE OLD
                ## TEMPORARY UNTIL CAN DO PROPERLY
                self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (PRINT_OPTIONS_TABLE,
                                                                      REPORT_NAME, report_name))

                as_dict = print_options.as_str_dict()

                for key,value in as_dict.items():
                    insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?, ?,?)" % (
                        PRINT_OPTIONS_TABLE,
                        REPORT_NAME,
                        REPORT_OPTION_KEY,
                        REPORT_OPTION_VALUE)
                    self.cursor.execute(insertion,
                                        (report_name, key, str(value)))

                self.conn.commit()
            except Exception as e1:
                raise Exception("Error %s when writing to print options for report name %s" % (str(e1), report_name))
            finally:
                self.close()

    def create_table(self):


        table_creation_query = """
                    CREATE TABLE %s (
                    %s STR, %s STR, %s STR
                    );
                """ % (PRINT_OPTIONS_TABLE,
                       REPORT_NAME,
                       REPORT_OPTION_KEY,
                       REPORT_OPTION_VALUE
                       )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s,  %s)" % (
            INDEX_PRINT_OPTIONS_TABLE,
            PRINT_OPTIONS_TABLE,
            REPORT_NAME,
            REPORT_OPTION_KEY)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating print options table" % str(e1))
        finally:
            self.close()

LIST_OF_ARRANGEMENTS_TABLE = "report_arrangements_table"
INDEX_LIST_OF_ARRANGEMENTS_TABLE = "index_report_arrangements_table"


class SqlDataListOfArrangementOptions(
     GenericSqlData
):
    def read(self, report_name: str) -> ArrangementOptionsAndGroupOrder:
        try:
            print(".............")
            if self.table_does_not_exist(LIST_OF_ARRANGEMENTS_TABLE):
                print("EMPTY")
                return ArrangementOptionsAndGroupOrder.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s WHERE %s='%s' ''' % (
                REPORT_ARRANGEMENT_COLUMNS,
                REPORT_ARRANGEMENT_METHOD,
                REPORT_GROUP_ORDER,
                LIST_OF_ARRANGEMENTS_TABLE, REPORT_NAME, report_name
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading print options" % str(e1))
        finally:
            self.close()

        if len(raw_list)==0:
            return ArrangementOptionsAndGroupOrder.create_empty()

        raw_item = raw_list[0]## only one record

        print(raw_item)

        as_dict = dict(columns = raw_item[0],
                       method = raw_item[1],
                       group_order = raw_item[2])
        print(as_dict)
        return   ArrangementOptionsAndGroupOrder.from_dict_of_str(as_dict)

    def write(
        self, arrange_options: ArrangementOptionsAndGroupOrder, report_name: str
    ):
        try:
            if self.table_does_not_exist(LIST_OF_ARRANGEMENTS_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (LIST_OF_ARRANGEMENTS_TABLE,
                                                                  REPORT_NAME, report_name))

            as_dict = arrange_options.as_dict_of_str()

            insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?, ?, ?, ?)" % (
                    LIST_OF_ARRANGEMENTS_TABLE,
                    REPORT_NAME,
                    REPORT_ARRANGEMENT_COLUMNS,
                    REPORT_ARRANGEMENT_METHOD,
                    REPORT_GROUP_ORDER)

            self.cursor.execute(insertion,
                                    (report_name, as_dict['columns'],
                                     as_dict['method'],
                                     as_dict['group_order']))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to print options for report name %s" % (str(e1), report_name))
        finally:
            self.close()

    def create_table(self):


        table_creation_query = """
                    CREATE TABLE %s (
                    %s STR, %s STR, %s STR, %s STR
                    );
                """ % (LIST_OF_ARRANGEMENTS_TABLE,
                       REPORT_NAME,
                        REPORT_ARRANGEMENT_COLUMNS,
                       REPORT_ARRANGEMENT_METHOD,
                       REPORT_GROUP_ORDER
                       )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (
           INDEX_LIST_OF_ARRANGEMENTS_TABLE,
           LIST_OF_ARRANGEMENTS_TABLE,
            REPORT_NAME
)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating print options table" % str(e1))
        finally:
            self.close()

