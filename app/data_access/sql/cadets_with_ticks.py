from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.ticks import ListOfTickListItemsAndTicksForSpecificCadet, CadetIdWithTickListItemIds, Tick, DictOfTicksWithItem

TICKS_FOR_CADET_TABLE = "ticks_for_cadet"
INDEX_TICKS_FOR_CADET_TABLE = "index_ticks_for_cadet_table"

class SqlDataListOfCadetsWithTickListItems(
    GenericSqlData
):
    def read(
        self, cadet_id: str
    ) -> ListOfTickListItemsAndTicksForSpecificCadet:
        try:
            if self.table_does_not_exist(TICKS_FOR_CADET_TABLE):
                return ListOfTickListItemsAndTicksForSpecificCadet.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s WHERE %s="%s" ''' % (

                TICK_SHEET_ITEM_ID,
                TICK_VALUE,
                TICKS_FOR_CADET_TABLE,
                CADET_ID,
                int(cadet_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading attendance" % str(e1))
        finally:
            self.close()

        dict_of_ticks = DictOfTicksWithItem(
            (str(raw_item[0]),
             Tick[raw_item[1]])
            for raw_item in raw_list
        )

        return ListOfTickListItemsAndTicksForSpecificCadet([
            CadetIdWithTickListItemIds(
                cadet_id=cadet_id,
                dict_of_ticks_with_items=dict_of_ticks
            )]
        ) ## ignore warning

    def write(
        self,
        list_of_cadets_with_tick_list_items: ListOfTickListItemsAndTicksForSpecificCadet,
        cadet_id: str,
    ):
        if len(list_of_cadets_with_tick_list_items)==0:
            return

        try:
            assert len(list_of_cadets_with_tick_list_items)==1
        except:
            raise Exception("Can only write one cadet ticks at a time")

        try:
            if self.table_does_not_exist(TICKS_FOR_CADET_TABLE):
                self.create_table()

            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (TICKS_FOR_CADET_TABLE, CADET_ID, int(cadet_id)))

            dict_of_ticks_this_item = list_of_cadets_with_tick_list_items[0].dict_of_ticks_with_items

            for tick_id, tick in dict_of_ticks_this_item.items():

                insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?,?,?)" % (
                    TICKS_FOR_CADET_TABLE,
                    CADET_ID,
                    TICK_SHEET_ITEM_ID,
                    TICK_VALUE)

                self.cursor.execute(insertion, (
                    int(cadet_id),
                    int(tick_id),
                    tick.name
                    ))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing ticks" % str(e1))
        finally:
            self.close()

    def create_table(self):

        # name: str
        # hidden: bool
        # id: str = arg_not_passed

        table_creation_query = """
                CREATE TABLE %s (
                    %s INTEGER,
                    %s INTEGER,
                    %s STR

                );
            """ % (TICKS_FOR_CADET_TABLE,
                   CADET_ID,
                   TICK_SHEET_ITEM_ID,
                   TICK_VALUE)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s)" % (
            INDEX_TICKS_FOR_CADET_TABLE,
            TICKS_FOR_CADET_TABLE,
            CADET_ID,
            TICK_SHEET_ITEM_ID
            )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating ticks table" % str(e1))
        finally:
            self.close()

