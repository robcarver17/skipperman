from typing import List, Dict

from app.data_access.sql.cadets import SqlDataListOfCadets
from app.data_access.sql.cadets_with_qualifications import SqlListOfCadetsWithQualifications
from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.qualifications import SqlDataListOfQualifications
from app.data_access.sql.shared_column_names import *
from app.data_access.sql.tick_sheet_sub_stages import SqlDataListOfTickSubStages
from app.objects.cadets import ListOfCadets
from app.objects.composed.ticks_for_qualification import TicksForQualification, DictOfTickSheetItemsAndTicksForCadet
from app.objects.composed.ticksheet import DictOfCadetsWithQualificationsAndTicks, QualificationsAndTicksForCadet
from app.objects.qualifications import ListOfQualifications, Qualification, ListOfCadetsWithIdsAndQualifications
from app.objects.substages import ListOfTickSubStages, ListOfTickSheetItems
from app.objects.ticks import ListOfTickListItemsAndTicksForSpecificCadet, CadetIdWithTickListItemIds, Tick, \
    DictOfTicksWithItem, no_tick

TICKS_FOR_CADET_TABLE = "ticks_for_cadet"
INDEX_TICKS_FOR_CADET_TABLE = "index_ticks_for_cadet_table"


from app.data_access.sql.tick_sheet_items import SqlDataListOfTickSheetItems

class SqlDataListOfCadetsWithTickListItems(
    GenericSqlData
):

    def delete_ticks_for_cadet(
            self, cadet_id:str
    ):

        try:
            if self.table_does_not_exist(TICKS_FOR_CADET_TABLE):
                return

            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (TICKS_FOR_CADET_TABLE, CADET_ID, int(cadet_id)))
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing ticks" % str(e1))
        finally:
            self.close()

    def save_ticksheet_edits_for_specific_tick(
            self, new_tick: Tick, cadet_id:str, tick_item_id: str
    ):
        if self.does_tick_exist(tick_item_id=tick_item_id, cadet_id=cadet_id):
            return self.modify_existing_tick(new_tick=new_tick, cadet_id=cadet_id, tick_item_id=tick_item_id)

        try:
            if self.table_does_not_exist(TICKS_FOR_CADET_TABLE):
                self.create_table()

            self.write_tick_for_cadet_without_checks_or_commit(
                    tick=new_tick,
                    tick_id=tick_item_id,
                    cadet_id=cadet_id
                )

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing ticks" % str(e1))
        finally:
            self.close()


    def modify_existing_tick(self, new_tick: Tick, cadet_id:str, tick_item_id: str):
        try:
            if self.table_does_not_exist(TICKS_FOR_CADET_TABLE):
                self.create_table()

            insertion = "UPDATE %s SET %s='%s' WHERE %s='%s' AND %s='%s'" % (
                TICKS_FOR_CADET_TABLE,
                TICK_VALUE,
                new_tick.name,
                CADET_ID,
                int(cadet_id),
                TICK_SHEET_ITEM_ID,
                int(tick_item_id))

            self.cursor.execute(insertion)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing ticks" % str(e1))
        finally:
            self.close()

    def does_tick_exist(self, cadet_id: str, tick_item_id: str):
        try:
            if self.table_does_not_exist(TICKS_FOR_CADET_TABLE):
                return False

            cursor = self.cursor
            cursor.execute('''SELECT * FROM %s WHERE %s="%s" AND %s="%s" ''' % (
                TICKS_FOR_CADET_TABLE,
                CADET_ID,
                int(cadet_id),
                TICK_SHEET_ITEM_ID,
                int(tick_item_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading attendance" % str(e1))
        finally:
            self.close()

        return len(raw_list)>0

    def get_dict_of_cadets_with_qualifications_and_ticks(
            self, list_of_cadet_ids: List[str]
    ) -> DictOfCadetsWithQualificationsAndTicks:
        return DictOfCadetsWithQualificationsAndTicks(
            [
                (self.list_of_cadets.cadet_with_id(cadet_id),
                 self.qualifications_and_ticks_for_cadet(cadet_id))
                for cadet_id in list_of_cadet_ids
            ]
        )

    def qualifications_and_ticks_for_cadet(self, cadet_id:str) -> QualificationsAndTicksForCadet:
        raw_ticks_for_cadet = self.ticks_and_ticksheet_items_for_cadet(cadet_id)
        return QualificationsAndTicksForCadet(
            [
                (qualification,
                 self.ticks_for_qualification_for_cadet(cadet_id=cadet_id, qualification=qualification,
                                                        raw_ticks_for_cadet=raw_ticks_for_cadet))
                for qualification in self.list_of_qualifications
            ]
        )

    def ticks_for_qualification_for_cadet(self, cadet_id: str, qualification: Qualification, raw_ticks_for_cadet: Dict[str, Tick])-> TicksForQualification:
        already_qualified = self.list_of_cadets_with_qualifications.cadet_has_qualification(
            cadet_id=cadet_id, qualification_id=qualification.id
        )
        return TicksForQualification(
            dict([
                (substage,
                 self.dict_of_ticks_for_qualification_and_substage_for_cadet(
                     substage_id=substage.id,
                     raw_ticks_for_cadet=raw_ticks_for_cadet
                 ))
                for substage in self.list_of_substages.substages_for_qualification_id(qualification.id)
            ]),
            qualification=qualification,
            already_qualified=already_qualified
        )

    def dict_of_ticks_for_qualification_and_substage_for_cadet(self,
                                                               substage_id,
                                                               raw_ticks_for_cadet: Dict[str, Tick]) -> DictOfTickSheetItemsAndTicksForCadet:

        return DictOfTickSheetItemsAndTicksForCadet(
            [
                (tick_sheet_item,
                 raw_ticks_for_cadet.get(tick_sheet_item.id, no_tick)
                 )
                for tick_sheet_item in self.list_of_tick_sheet_items.subset_for_substage_id(
                substage_id=substage_id
            )
            ]
        )

    def ticks_and_ticksheet_items_for_cadet(self, cadet_id: str) -> Dict[str, Tick]:
        try:
            if self.table_does_not_exist(TICKS_FOR_CADET_TABLE):
                return {}

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s WHERE %s="%s" ''' % (
                TICK_SHEET_ITEM_ID,
                TICK_VALUE,
                TICKS_FOR_CADET_TABLE,
                CADET_ID,
                int(cadet_id),
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading attendance" % str(e1))
        finally:
            self.close()

        if len(raw_list)==0:
            return {}

        new_dict = dict([
            (str(raw_item[0]), Tick[raw_item[1]])
            for raw_item in raw_list
        ])

        return new_dict

    @property
    def list_of_tick_sheet_items(self)-> ListOfTickSheetItems:
        list_of_tick_sheet_items =getattr(self, "_list_of_tick_sheet_items", None)
        if list_of_tick_sheet_items is None:
            list_of_tick_sheet_items = self._list_of_tick_sheet_items = SqlDataListOfTickSheetItems(self.db_connection).read()

        return list_of_tick_sheet_items

    @property
    def list_of_cadets_with_qualifications(self) -> ListOfCadetsWithIdsAndQualifications:
        list_of_cadets_with_qualifications = getattr(self, "_list_of_cadets_with_qualifications", None)
        if list_of_cadets_with_qualifications is None:
            list_of_cadets_with_qualifications = self._list_of_cadets_with_qualifications = SqlListOfCadetsWithQualifications(self.db_connection).read()

        return list_of_cadets_with_qualifications

    @property
    def list_of_substages(self) -> ListOfTickSubStages:
        list_of_substages =getattr(self, "_list_of_substages", None)
        if list_of_substages is None:
            list_of_substages = self._list_of_substages = SqlDataListOfTickSubStages(self.db_connection).read()

        return list_of_substages

    @property
    def list_of_qualifications(self) ->ListOfQualifications:
        list_of_qualifications = getattr(self, "_list_of_qualifications", None)
        if list_of_qualifications is None:
            list_of_qualifications = self._list_of_qualifications = SqlDataListOfQualifications(self.db_connection).read()

        return list_of_qualifications

    @property
    def list_of_cadets(self) -> ListOfCadets:
        list_of_cadets = getattr(self, "_list_of_cadets", None)
        if list_of_cadets is None:
            list_of_cadets = self._list_of_cadets = SqlDataListOfCadets(self.db_connection).read()

        return list_of_cadets

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
                self.write_tick_for_cadet_without_checks_or_commit(
                    tick=tick,
                    tick_id=tick_id,
                    cadet_id=cadet_id
                )

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing ticks" % str(e1))
        finally:
            self.close()

    def write_tick_for_cadet_without_checks_or_commit(self, tick: Tick, tick_id: str, cadet_id: str):
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

