from typing import List, Dict

from app.data_access.sql.cadets import SqlDataListOfCadets
from app.data_access.sql.volunteers import SqlDataListOfVolunteers
from app.data_access.sql.cadets import CADETS_TABLE
from app.data_access.sql.volunteers import VOLUNTEERS_TABLE
from app.data_access.sql.club_dinghies import CLUB_DINGHIES_TABLE, SqlDataListOfClubDinghies
from app.objects.cadets import Cadet
from app.objects.club_dinghies import ClubDinghy
from app.objects.composed.people_at_event_with_club_dinghies import DictOfPeopleAndClubDinghiesAtEvent, \
    DictOfDaysAndClubDinghiesAtEventForPerson
from app.objects.volunteers import ListOfVolunteers, Volunteer
from app.objects.volunteers_and_cades_at_event_with_club_boat_with_ids import (
    ListOfCadetAtEventWithIdAndClubDinghies, ListOfVolunteerAtEventWithIdAndClubDinghies, CadetAtEventWithClubDinghyWithId,
VolunteerAtEventWithClubDinghyWithId
)
from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.day_selectors import Day

"""
CADETS AT EVENT WITH CLUB DINGHIES
"""

CADETS_AND_CLUB_DINGHIES_TABLE = "cadets_and_club_dinghies_table"
INDEX_NAME_CADETS_AND_CLUB_DINGHIES_TABLE = "cadets_and_club_dinghies_table_index"


class SqlDataDictOfPeopleAndClubDinghiesAtEvent(
    GenericSqlData
):
    def get_dict_of_people_and_club_dinghies_at_event(self) -> DictOfPeopleAndClubDinghiesAtEvent:
        pass




class SqlDataListOfCadetAtEventWithClubDinghies(
    GenericSqlData
):
    def is_a_club_dinghy_allocated_for_cadet_on_any_day_at_event(
            self, event_id: str, cadet_id: str
    ) -> bool:
        if self.table_does_not_exist(CADETS_AND_CLUB_DINGHIES_TABLE):
            return False

        try:
            cursor = self.cursor
            cursor.execute('''SELECT * FROM %s WHERE %s='%s' AND %s='%s' ''' % (
                CADETS_AND_CLUB_DINGHIES_TABLE,
                EVENT_ID, int(event_id),
                CADET_ID, int(cadet_id)))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets and dinghies at event" % str(e1))
        finally:
            self.close()

        return len(raw_list)>0

    def read_dict_of_cadets_and_club_dinghies_at_event(self, event_id: str) -> DictOfPeopleAndClubDinghiesAtEvent:
        list_of_cadets_at_event_with_dinghies = self.read(event_id)
        new_dict = {}
        for cadet_with_id_and_dinghy in list_of_cadets_at_event_with_dinghies:
            cadet = self.list_of_cadets.cadet_with_id(cadet_with_id_and_dinghy.cadet_id)
            day = cadet_with_id_and_dinghy.day
            dinghy = self.list_of_club_dinghies.club_dinghy_with_id(cadet_with_id_and_dinghy.club_dinghy_id)
            existing_dict_of_days = new_dict.get(cadet, DictOfDaysAndClubDinghiesAtEventForPerson())
            existing_dict_of_days[day] = dinghy
            new_dict[cadet] = existing_dict_of_days

        return DictOfPeopleAndClubDinghiesAtEvent(new_dict)

    @property
    def list_of_cadets(self):
        list_of_cadets = getattr(self, "_list_of_cadets", None)
        if list_of_cadets is None:
            list_of_cadets = self._list_of_cadets = SqlDataListOfCadets(self.db_connection).read()

        return list_of_cadets

    @property
    def list_of_club_dinghies(self):
        list_of_club_dinghies = getattr(self, "_list_of_club_dinghies", None)
        if list_of_club_dinghies is None:
            list_of_club_dinghies = self._list_of_club_dinghies =  SqlDataListOfClubDinghies(self.db_connection).read()

        return list_of_club_dinghies

    def read(self, event_id: str) -> ListOfCadetAtEventWithIdAndClubDinghies:
        if self.table_does_not_exist(CADETS_AND_CLUB_DINGHIES_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s  FROM %s WHERE %s='%s' ''' % (
                CADET_ID, DAY, DINGHY_ID,
                CADETS_AND_CLUB_DINGHIES_TABLE,
                EVENT_ID, int(event_id)))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets and dinghies at event" % str(e1))
        finally:
            self.close()

        new_list = []
        for raw_cadet_with_id_at_event in raw_list:
            cadet_with_id_at_event = CadetAtEventWithClubDinghyWithId(
                cadet_id=str(raw_cadet_with_id_at_event[0],
                             ),
                day=Day[raw_cadet_with_id_at_event[1]],
                club_dinghy_id=str(raw_cadet_with_id_at_event[2])
            )
            new_list.append(cadet_with_id_at_event)

        return ListOfCadetAtEventWithIdAndClubDinghies(new_list) ## IGNORE warning


    def write(
        self,
        people_and_boats: ListOfCadetAtEventWithIdAndClubDinghies,
        event_id: str,
    ):
        try:
            if self.table_does_not_exist(CADETS_AND_CLUB_DINGHIES_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (CADETS_AND_CLUB_DINGHIES_TABLE,
                                                                 EVENT_ID,
                                                                 int(event_id)))

            for idx, cadet_and_boat in enumerate(people_and_boats):
                cadet_id = cadet_and_boat.cadet_id
                day = cadet_and_boat.day.name
                club_dinghy_id = cadet_and_boat.club_dinghy_id

                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                    CADETS_AND_CLUB_DINGHIES_TABLE,
                    EVENT_ID, CADET_ID, DAY, DINGHY_ID)

                self.cursor.execute(insertion, (
                    int(event_id), int(cadet_id), day,  int(club_dinghy_id)))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing club dinghies at event" % str(e1))
        finally:
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
                %s INTEGER
            );
        """ % (CADETS_AND_CLUB_DINGHIES_TABLE,
               EVENT_ID, CADET_ID, DAY, DINGHY_ID)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (INDEX_NAME_CADETS_AND_CLUB_DINGHIES_TABLE,
                                                                      CADETS_AND_CLUB_DINGHIES_TABLE,
                                                                      EVENT_ID, CADET_ID, DAY)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating club dinghies and cadets table" % str(e1))
        finally:
            self.close()


VOLUNTEERS_AND_CLUB_DINGHIES_TABLE = "volunteers_and_club_dinghies_table"
INDEX_NAME_VOLUNTEERS_AND_CLUB_DINGHIES_TABLE = "volunteers_and_club_dinghies_table_index"

class SqlDataListOfVolunteersAtEventWithClubDinghies(
    GenericSqlData
):
    def read_dict_of_volunteers_and_club_dinghies_at_event(self, event_id: str) ->  DictOfPeopleAndClubDinghiesAtEvent:
        list_of_volunteers_at_event_with_dinghies = self.read(event_id)
        new_dict = {}
        for volunteer_with_id_and_dinghy in list_of_volunteers_at_event_with_dinghies:
            volunteer = self.list_of_volunteers.volunteer_with_id(volunteer_with_id_and_dinghy.volunteer_id)
            day = volunteer_with_id_and_dinghy.day
            dinghy = self.list_of_club_dinghies.club_dinghy_with_id(volunteer_with_id_and_dinghy.club_dinghy_id)
            existing_dict_of_days = new_dict.get(volunteer, DictOfDaysAndClubDinghiesAtEventForPerson())
            existing_dict_of_days[day] = dinghy
            new_dict[volunteer] = existing_dict_of_days

        return  DictOfPeopleAndClubDinghiesAtEvent(new_dict)

    @property
    def list_of_volunteers(self):
        list_of_volunteers = getattr(self, "_list_of_volunteers", None)
        if list_of_volunteers is None:
            list_of_volunteers = self._list_of_volunteers = SqlDataListOfVolunteers(self.db_connection).read()

        return list_of_volunteers

    @property
    def list_of_club_dinghies(self):
        list_of_club_dinghies = getattr(self, "_list_of_club_dinghies", None)
        if list_of_club_dinghies is None:
            list_of_club_dinghies = self._list_of_club_dinghies =  SqlDataListOfClubDinghies(self.db_connection).read()

        return list_of_club_dinghies


    def read(self, event_id: str) -> ListOfVolunteerAtEventWithIdAndClubDinghies:
        if self.table_does_not_exist(VOLUNTEERS_AND_CLUB_DINGHIES_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s  FROM %s WHERE %s='%s' ''' % (
                VOLUNTEER_ID, DAY, DINGHY_ID,
                VOLUNTEERS_AND_CLUB_DINGHIES_TABLE,
                EVENT_ID, int(event_id)))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteers and dinghies at event" % str(e1))
        finally:
            self.close()

        new_list = []
        for raw_volunteer_with_id_at_event in raw_list:
            volunteer_with_id_at_event = VolunteerAtEventWithClubDinghyWithId(
                volunteer_id=str(raw_volunteer_with_id_at_event[0],
                             ),
                day=Day[raw_volunteer_with_id_at_event[1]],
                club_dinghy_id=str(raw_volunteer_with_id_at_event[2])
            )
            new_list.append(volunteer_with_id_at_event)

        return ListOfVolunteerAtEventWithIdAndClubDinghies(new_list) ## ignore warning


    def write(
        self,
        people_and_boats: ListOfVolunteerAtEventWithIdAndClubDinghies,
        event_id: str,
    ):
        try:
            if self.table_does_not_exist(VOLUNTEERS_AND_CLUB_DINGHIES_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (VOLUNTEERS_AND_CLUB_DINGHIES_TABLE,
                                                                 EVENT_ID,
                                                                 int(event_id)))

            for idx, volunteer_and_boat in enumerate(people_and_boats):
                volunteer_id = volunteer_and_boat.volunteer_id
                day = volunteer_and_boat.day.name
                club_dinghy_id = volunteer_and_boat.club_dinghy_id

                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                    VOLUNTEERS_AND_CLUB_DINGHIES_TABLE,
                    EVENT_ID, VOLUNTEER_ID, DAY, DINGHY_ID)

                self.cursor.execute(insertion, (
                    int(event_id), int(volunteer_id), day,  int(club_dinghy_id)))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing club dinghies and volunteers at event" % str(e1))
        finally:
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
                %s INTEGER
            );
        """ % (VOLUNTEERS_AND_CLUB_DINGHIES_TABLE,
               EVENT_ID, VOLUNTEER_ID, DAY, DINGHY_ID)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (INDEX_NAME_VOLUNTEERS_AND_CLUB_DINGHIES_TABLE,
                                                                      VOLUNTEERS_AND_CLUB_DINGHIES_TABLE,
                                                                      EVENT_ID, VOLUNTEER_ID, DAY)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating club dinghies and volunteers table" % str(e1))
        finally:
            self.close()


