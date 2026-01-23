from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.substages import ListOfTickSheetItems, TickSheetItem

TICK_SHEET_ITEM_TABLE = "tick_sheet_items"
INDEX_TICK_SHEET_ITEM_TABLE = "index_tick_sheet_items"

class SqlDataListOfTickSheetItems(GenericSqlData):
    def read(self) -> ListOfTickSheetItems:
        try:
            if self.table_does_not_exist(TICK_SHEET_ITEM_TABLE):
                return ListOfTickSheetItems.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s,%s,%s FROM %s''' % (

                TICK_SHEET_ITEM_NAME,
                QUALIFICATION_ID,
                TICK_SUBSTAGE_ID,
                TICK_SHEET_ITEM_ID,
                TICK_SHEET_ITEM_TABLE,
            ))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading tick items" % str(e1))
        finally:
            self.close()

        new_list = [
            TickSheetItem(name=str(raw_item[0]),
                          stage_id=str(raw_item[1]),
                          substage_id=str(raw_item[2]),
                          id=str(raw_item[3]))

            for raw_item in raw_list]

        return ListOfTickSheetItems(new_list)

    def write(self, list_of_tick_sheet_items: ListOfTickSheetItems):
        try:
            if self.table_does_not_exist(TICK_SHEET_ITEM_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (TICK_SHEET_ITEM_TABLE))

            for item in list_of_tick_sheet_items:
                name = item.name
                stage_id = int(item.stage_id)
                substage_id = int(item.substage_id)
                item_id = int(item.id)

                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                    TICK_SHEET_ITEM_TABLE,
                    TICK_SHEET_ITEM_NAME,
                    QUALIFICATION_ID,
                    TICK_SUBSTAGE_ID,
                    TICK_SHEET_ITEM_ID)

                self.cursor.execute(insertion, (
                    name, stage_id, substage_id, item_id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing tick items" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
                        CREATE TABLE %s (
                            %s STR, 
                            %s INTEGER,
                            %s INTEGER,
                            %s INTEGER
                        );
                    """ % (TICK_SHEET_ITEM_TABLE,
                           TICK_SHEET_ITEM_NAME,
                           QUALIFICATION_ID,
                           TICK_SUBSTAGE_ID,
                           TICK_SHEET_ITEM_ID
                           )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (
            INDEX_TICK_SHEET_ITEM_TABLE, TICK_SHEET_ITEM_TABLE,
            TICK_SHEET_ITEM_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating substage table" % str(e1))
        finally:
            self.close()


