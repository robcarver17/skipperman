
from app.objects.cadet_at_event_with_boat_class_and_partners_with_ids import (
    ListOfCadetAtEventWithBoatClassAndPartnerWithIds, CadetAtEventWithBoatClassAndPartnerWithIds,
)
from app.data_access.sql.cadets import SqlDataListOfCadets
from app.data_access.sql.boat_classes import SqlDataListOfDinghies
from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.cadets import ListOfCadets
from app.objects.boat_classes import ListOfBoatClasses
from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import DictOfCadetsAndBoatClassAndPartners, \
    compose_raw_dict_of_cadets_and_boat_classes_and_partners
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.partners import from_partner_id_to_int, from_int_to_partner_id
from app.objects.utilities.exceptions import arg_not_passed, MissingData, MultipleMatches
from app.objects.utilities.transform_data import make_id_as_int_str

"""
CADETS AT EVENT WITH DINGHIES
"""

CADETS_AND_DINGHIES_TABLE = "cadets_and_dinghies_table"
INDEX_NAME_CADETS_AND_DINGHIES_TABLE = "cadets_and_dinghies_table_index"



class SqlDataListOfCadetAtEventWithDinghies(
    GenericSqlData


):
    def add_two_handed_partnership_on_day_for_new_cadet_when_have_dinghy_for_existing_cadet(self,
        event_id:str,
        day: Day,
        original_cadet_id: str,
        new_cadet_id: str
    ):
        original_cadet_details = self.get_cadet_at_event_with_boat_class_and_partner_with_ids(
            event_id=event_id,
            day=day,
            cadet_id=original_cadet_id,
        default=None)

        if original_cadet_details is None:
            raise Exception("Can't find original cadet details")

        self.replace_or_add_cadet_cloned_from_partner(original_cadet_details=original_cadet_details,
                                                      event_id=event_id, day=day, cadet_id_to_replace=new_cadet_id)

        ## update existing just parnter
        self.update_existing_cadet_at_event_with_new_partner(
            event_id=event_id,
            cadet_id=original_cadet_id,
            partner_cadet_id=new_cadet_id,
            day=day
        )

    def replace_or_add_cadet_cloned_from_partner(self, original_cadet_details: CadetAtEventWithBoatClassAndPartnerWithIds,
                                                 event_id: str,
                                                 day: Day,
                                                 cadet_id_to_replace: str):

        self.delete_existing_data_for_cadet(event_id=event_id, day=day, cadet_id=cadet_id_to_replace)

        new_cadet_and_boat = CadetAtEventWithBoatClassAndPartnerWithIds(
            cadet_id=cadet_id_to_replace,
            partner_cadet_id=original_cadet_details.cadet_id,
            boat_class_id=original_cadet_details.boat_class_id,
            sail_number=original_cadet_details.sail_number,
            day=day
        )
        # try except etc
        try:
            if self.table_does_not_exist(CADETS_AND_DINGHIES_TABLE):
                self.create_table()

            self.insert_cadet_and_boat_without_commit(cadet_and_boat=new_cadet_and_boat, event_id=event_id)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing dinghies" % str(e1))
        finally:
            self.close()


    def delete_existing_data_for_cadet(self,  event_id: str,
                                                                day: Day,
                                                                cadet_id: str):

        try:
            if self.table_does_not_exist(CADETS_AND_DINGHIES_TABLE):
                return

            self.cursor.execute("DELETE FROM %s WHERE %s='%s' AND %s='%s' AND %s='%s'" % (CADETS_AND_DINGHIES_TABLE,
                                                                 EVENT_ID,
                                                                 int(event_id),
                                                                CADET_ID, int(cadet_id),
                                                                                          DAY, day.name))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing dinghies" % str(e1))
        finally:
            self.close()

    def update_cadet_at_event_with_new_partner(self, event_id: str, day: Day, cadet_id: str, partner_cadet_id: str):
        if self.is_cadet_already_in_data_on_day(event_id=event_id, day=day, cadet_id=cadet_id):
            pass
        else:
            self.add_cadet_to_event_on_day(event_id=event_id, day=day, cadet_id=cadet_id)

        self.update_existing_cadet_at_event_with_new_partner(
            event_id=event_id,
            day=day,
            cadet_id=cadet_id,
            partner_cadet_id=partner_cadet_id
        )

    def update_existing_cadet_at_event_with_new_partner(self, event_id: str, day: Day, cadet_id: str, partner_cadet_id: str):
        try:
            if self.table_does_not_exist(CADETS_AND_DINGHIES_TABLE):
                raise MissingData("Can't update partner for non existent ")

            insertion = "UPDATE %s SET %s='%s' WHERE %s='%s' AND %s='%s' AND %s='%s'" % (
                CADETS_AND_DINGHIES_TABLE,
                PARTNER_CADET_ID,
                int(partner_cadet_id),
                EVENT_ID,
                int(event_id),
                CADET_ID,
                int(cadet_id),
                DAY,
                day.name)

            self.cursor.execute(insertion)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing dinghies" % str(e1))
        finally:
            self.close()

    def add_cadet_to_event_on_day(self, event_id: str, cadet_id: str, day: Day):
        new_cadet_and_boat = CadetAtEventWithBoatClassAndPartnerWithIds(
            cadet_id=cadet_id,
            day=day
        )
        # try except etc
        try:
            if self.table_does_not_exist(CADETS_AND_DINGHIES_TABLE):
                self.create_table()

            self.insert_cadet_and_boat_without_commit(cadet_and_boat=new_cadet_and_boat, event_id=event_id)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing cadets with dinghies" % str(e1))
        finally:
            self.close()

    def is_cadet_already_in_data_on_day(self,  event_id: str,
                                                                day: Day,
                                                                cadet_id: str):
        existing_cadet = self.get_cadet_at_event_with_boat_class_and_partner_with_ids(
            event_id=event_id,
            day=day,
            cadet_id=cadet_id,
            default=None
        )
        if existing_cadet is None:
            return False
        else:
            return True

    def get_cadet_at_event_with_boat_class_and_partner_with_ids(self,
                                                                event_id: str,
                                                                day: Day,
                                                                cadet_id: str,
                                                                default = arg_not_passed
                                                                ) -> CadetAtEventWithBoatClassAndPartnerWithIds:

        if self.table_does_not_exist(CADETS_AND_DINGHIES_TABLE):
            if default is arg_not_passed:
                raise MissingData("%s %s %s not found in cadets and dinghies table" % (event_id, cadet_id, day))
            else:
                return default

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s WHERE %s='%s' AND %s='%s' AND %s='%s' ''' % (
                SAIL_NUMBER, PARTNER_CADET_ID, DINGHY_ID,
                CADETS_AND_DINGHIES_TABLE,
                EVENT_ID, int(event_id),
                CADET_ID, int(cadet_id),
                DAY, day.name
            ))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets and dinghies at event" % str(e1))
        finally:
            self.close()

        if len(raw_list)==0:
            if default is arg_not_passed:
                raise MissingData("%s %s %s not found in cadets and dinghies table" % (event_id, cadet_id, day))
            else:
                return default

        if len(raw_list)>1:
            error="More than one %s %s %s found in cadets and dinghies table" % (event_id, cadet_id, day)
            raise MultipleMatches(error)

        raw_cadet_with_id_at_event = raw_list[0]
        cadet_with_id_at_event = CadetAtEventWithBoatClassAndPartnerWithIds(
                cadet_id=str(cadet_id
                             ),
                day=day,
                sail_number=make_id_as_int_str(raw_cadet_with_id_at_event[0]),
                partner_cadet_id=from_int_to_partner_id(raw_cadet_with_id_at_event[1]),
                boat_class_id=str(raw_cadet_with_id_at_event[2])
            )

        return cadet_with_id_at_event



    def get_dict_of_cadets_and_boat_classes_and_partners_at_events(
            self, event: Event
    ) -> DictOfCadetsAndBoatClassAndPartners:
        raw_data = self.read(event.id)
        new_dict = compose_raw_dict_of_cadets_and_boat_classes_and_partners(
            list_of_cadets=self.list_of_cadets,
            list_of_boat_classes=self.list_of_boat_classes,
            list_of_cadets_at_event_with_boat_class_and_partners_with_ids=raw_data
        )

        return DictOfCadetsAndBoatClassAndPartners(new_dict)

    @property
    def list_of_cadets(self) -> ListOfCadets:
        list_of_cadets = getattr(self, "_list_of_cadets", None)
        if list_of_cadets is None:
            list_of_cadets = self._list_of_cadets = SqlDataListOfCadets(self.db_connection).read()

        return list_of_cadets

    @property
    def list_of_boat_classes(self) -> ListOfBoatClasses:
        list_of_boat_classes = getattr(self, "_list_of_boat_classes", None)
        if list_of_boat_classes is None:
            list_of_boat_classes = self._list_of_boat_classes = SqlDataListOfDinghies(self.db_connection).read()

        return list_of_boat_classes

    def read(self, event_id: str) -> ListOfCadetAtEventWithBoatClassAndPartnerWithIds:
        if self.table_does_not_exist(CADETS_AND_DINGHIES_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s, %s FROM %s WHERE %s='%s' ''' % (
                CADET_ID, DAY, SAIL_NUMBER, PARTNER_CADET_ID, DINGHY_ID,
                CADETS_AND_DINGHIES_TABLE,
                EVENT_ID, int(event_id)))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets and dinghies at event" % str(e1))
        finally:
            self.close()

        new_list = []
        for raw_cadet_with_id_at_event in raw_list:
            cadet_with_id_at_event = CadetAtEventWithBoatClassAndPartnerWithIds(
                cadet_id=str(raw_cadet_with_id_at_event[0],
                             ),
                day=Day[raw_cadet_with_id_at_event[1]],
                sail_number=make_id_as_int_str(raw_cadet_with_id_at_event[2]),
                partner_cadet_id=from_int_to_partner_id(raw_cadet_with_id_at_event[3]),
                boat_class_id=str(raw_cadet_with_id_at_event[4])
            )
            new_list.append(cadet_with_id_at_event)

        return ListOfCadetAtEventWithBoatClassAndPartnerWithIds(new_list) ## ignore type warning


    def write(
        self,
        people_and_boats: ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
        event_id: str,
    ):
        try:
            if self.table_does_not_exist(CADETS_AND_DINGHIES_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (CADETS_AND_DINGHIES_TABLE,
                                                                 EVENT_ID,
                                                                 int(event_id)))

            for cadet_and_boat in people_and_boats:
                self.insert_cadet_and_boat_without_commit(cadet_and_boat=cadet_and_boat, event_id=event_id)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing dinghies" % str(e1))
        finally:
            self.close()

    def insert_cadet_and_boat_without_commit(self, event_id: str, cadet_and_boat: CadetAtEventWithBoatClassAndPartnerWithIds):
        cadet_id = cadet_and_boat.cadet_id
        day = cadet_and_boat.day.name
        sail_number = cadet_and_boat.sail_number
        partner_cadet_id = from_partner_id_to_int(cadet_and_boat.partner_cadet_id)
        boat_class_id = cadet_and_boat.boat_class_id

        insertion = "INSERT INTO %s (%s, %s, %s, %s, %s, %s) VALUES (?,?,?,?, ?, ?)" % (
            CADETS_AND_DINGHIES_TABLE,
            EVENT_ID, CADET_ID, DAY, SAIL_NUMBER, PARTNER_CADET_ID, DINGHY_ID)

        self.cursor.execute(insertion, (
            int(event_id), int(cadet_id), day, sail_number, int(partner_cadet_id), int(boat_class_id)))

    def delete_table(self):
        self.conn.execute("DROP TABLE %s" % CADETS_AND_DINGHIES_TABLE)
        self.conn.commit()
        self.close()

    def create_table(self):

        #name: str
        #hidden: bool
        #id: str = arg_not_passed

        table_creation_query = """
            CREATE TABLE %s (
                %s INTEGER, 
                %s INTEGER,
                %s STR,
                %s STR,
                %s INTEGER,
                %s INTEGER
            );
        """ % (CADETS_AND_DINGHIES_TABLE,
               EVENT_ID, CADET_ID, DAY, SAIL_NUMBER, PARTNER_CADET_ID, DINGHY_ID)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (INDEX_NAME_CADETS_AND_DINGHIES_TABLE,
                                                                      CADETS_AND_DINGHIES_TABLE,
                                                                      EVENT_ID, CADET_ID, DAY)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating dinghies and cadets table" % str(e1))
        finally:
            self.close()

