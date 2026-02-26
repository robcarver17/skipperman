from typing import List

from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.utilities.transform_data import int2date
from app.objects.cadet_volunteer_connections_with_ids import (
    ListOfCadetVolunteerAssociationsWithIds,
    CadetVolunteerAssociationWithIds,
)
from app.data_access.sql.shared_column_names import *
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.composed.cadet_volunteer_associations import (
    DictOfCadetsAssociatedWithVolunteer,
)
from app.objects.membership_status import MembershipStatus
from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.data_access.sql.cadets import CADETS_TABLE
from app.data_access.sql.volunteers import VOLUNTEERS_TABLE

CADET_VOLUNTEER_CONNECTIONS_TABLE = "cadet_volunteer_associations"
INDEX_CADET_VOLUNTEER_CONNECTIONS_TABLE = "index_cadet_volunteer_associations"
INDEX_VOLUNTEER_CADET_CONNECTIONS_TABLE = "index_volunteer_cadet_associations"


class SqlDataListOfCadetVolunteerAssociations(GenericSqlData):
    def get_dict_of_cadets_associated_with_volunteers(
        self,
    ) -> DictOfCadetsAssociatedWithVolunteer:
        raw_list = self.read()
        raw_dict = {}
        for raw_item in raw_list:
            volunteer = self.list_of_volunteers.volunteer_with_id(raw_item.volunteer_id)
            cadet = self.list_of_cadets.cadet_with_id(raw_item.cadet_id)
            list_this_volunteer = raw_dict.get(volunteer, ListOfCadets.create_empty())
            list_this_volunteer.append(cadet)
            list_this_volunteer = ListOfCadets(list_this_volunteer)
            raw_dict[volunteer] = list_this_volunteer

        return DictOfCadetsAssociatedWithVolunteer(raw_dict)

    @property
    def list_of_volunteers(self) -> ListOfVolunteers:
        return self.object_store.get(
            self.object_store.data_api.data_list_of_volunteers.read
        )

    @property
    def list_of_cadets(self) -> ListOfCadets:
        return self.object_store.get(
            self.object_store.data_api.data_list_of_cadets.read
        )

    def delete_all_connections_for_volunteer(self, volunteer: Volunteer):
        if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
            return

        try:
            cursor = self.cursor
            cursor.execute(
                "DELETE FROM %s WHERE %s=%d"
                % (
                    CADET_VOLUNTEER_CONNECTIONS_TABLE,
                    VOLUNTEER_ID,
                    int(volunteer.id),
                )
            )
            self.conn.commit()
        except Exception as e1:
            raise e1
        finally:
            self.close()

    def delete_all_connections_for_cadet(self, cadet: Cadet):
        if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
            return

        try:
            cursor = self.cursor
            cursor.execute(
                "DELETE FROM %s WHERE %s=%d"
                % (
                    CADET_VOLUNTEER_CONNECTIONS_TABLE,
                    CADET_ID,
                    int(cadet.id),
                )
            )
            self.conn.commit()
        except Exception as e1:
            raise e1
        finally:
            self.close()

    def add_volunteer_connection_to_cadet(self, cadet: Cadet, volunteer: Volunteer):
        if self.is_cadet_associated_with_volunteer(cadet=cadet, volunteer=volunteer):
            return
        try:
            if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
                self.create_table()

            self._add_row_without_commits_or_checks(
                CadetVolunteerAssociationWithIds(
                    cadet_id=cadet.id, volunteer_id=volunteer.id
                )
            )
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing connections" % str(e1))
        finally:
            self.close()

    def delete_cadet_connection(self, cadet: Cadet, volunteer: Volunteer):
        if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
            return

        try:
            cursor = self.cursor
            cursor.execute(
                "DELETE FROM %s WHERE %s=%d AND %s=%d"
                % (
                    CADET_VOLUNTEER_CONNECTIONS_TABLE,
                    CADET_ID,
                    int(cadet.id),
                    VOLUNTEER_ID,
                    int(volunteer.id),
                )
            )
            self.conn.commit()
        except Exception as e1:
            raise e1
        finally:
            self.close()

    def is_cadet_associated_with_volunteer(self, volunteer: Volunteer, cadet: Cadet):
        try:
            if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
                return False

            cursor = self.cursor
            cursor.execute(
                """SELECT * FROM %s WHERE %s=%d AND %s=%d """
                % (
                    CADET_VOLUNTEER_CONNECTIONS_TABLE,
                    CADET_ID,
                    int(cadet.id),
                    VOLUNTEER_ID,
                    int(volunteer.id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading connections" % str(e1))
        finally:
            self.close()

        return len(raw_list) > 0

    def get_list_of_cadets_associated_with_volunteer(
        self, volunteer_id: str
    ) -> ListOfCadets:
        raw_list = self.get_list_of_cadet_ids_associated_with_volunteer(volunteer_id)

        return self.list_of_cadets.subset_from_list_of_ids_retaining_order(
            list_of_ids=raw_list
        )

    def get_list_of_cadet_ids_associated_with_volunteer(
        self, volunteer_id: str
    ) -> List[str]:
        try:
            if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
                return []

            cursor = self.cursor
            cursor.execute(
                """SELECT %s FROM %s WHERE %s=%d """
                % (
                    # select
                    CADET_ID,
                    VOLUNTEERS_TABLE,
                    VOLUNTEER_ID,  # equals
                    int(volunteer_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading connections" % str(e1))
        finally:
            self.close()

        return [item[0] for item in raw_list]

    def get_list_of_volunteers_associated_with_cadet(
        self, cadet_id: str
    ) -> ListOfVolunteers:
        raw_list = self.get_list_of_volunteer_ids_associated_with_cadet(cadet_id)

        return self.list_of_volunteers.subset_from_list_of_ids_retaining_order(raw_list)

    def get_list_of_volunteer_ids_associated_with_cadet(
        self, cadet_id: str
    ) -> List[str]:
        try:
            if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
                return []

            cursor = self.cursor
            cursor.execute(
                """SELECT %s FROM %s WHERE %s=%d """
                % (
                    # select
                    VOLUNTEER_ID,
                    VOLUNTEERS_TABLE,
                    CADET_ID,  # equals
                    int(cadet_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading connections" % str(e1))
        finally:
            self.close()

        return [item[0] for item in raw_list]

    def read(self) -> ListOfCadetVolunteerAssociationsWithIds:
        try:
            if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
                return ListOfCadetVolunteerAssociationsWithIds([])

            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s FROM %s"""
                % (CADET_ID, VOLUNTEER_ID, CADET_VOLUNTEER_CONNECTIONS_TABLE)
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading connections" % str(e1))
        finally:
            self.close()

        new_list = []
        for raw_connection in raw_list:
            connection = CadetVolunteerAssociationWithIds(
                cadet_id=str(raw_connection[0]), volunteer_id=str(raw_connection[1])
            )
            new_list.append(connection)

        return ListOfCadetVolunteerAssociationsWithIds(new_list)

    def write(
        self,
        list_of_cadet_volunteer_associations: ListOfCadetVolunteerAssociationsWithIds,
    ):
        try:
            if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
                self.create_table()

            self.cursor.execute("DELETE FROM %s" % (CADET_VOLUNTEER_CONNECTIONS_TABLE))

            for cadet_volunteer_association in list_of_cadet_volunteer_associations:
                self._add_row_without_commits_or_checks(cadet_volunteer_association)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing connections" % str(e1))
        finally:
            self.close()

    def _add_row_without_commits_or_checks(
        self, cadet_volunteer_association: CadetVolunteerAssociationWithIds
    ):
        cadet_id = int(cadet_volunteer_association.cadet_id)
        volunteer_id = int(cadet_volunteer_association.volunteer_id)

        insertion = "INSERT INTO %s (%s, %s) VALUES (?,?)" % (
            CADET_VOLUNTEER_CONNECTIONS_TABLE,
            CADET_ID,
            VOLUNTEER_ID,
        )

        self.cursor.execute(insertion, (cadet_id, volunteer_id))

    def create_table(self):
        table_creation_query = """
            CREATE TABLE %s (
                %s INTEGER,
                %s INTEGER
            );
        """ % (
            CADET_VOLUNTEER_CONNECTIONS_TABLE,
            CADET_ID,
            VOLUNTEER_ID,
        )

        index_creation_query = "CREATE INDEX %s ON %s (%s)" % (
            INDEX_CADET_VOLUNTEER_CONNECTIONS_TABLE,
            CADET_VOLUNTEER_CONNECTIONS_TABLE,
            CADET_ID,
        )
        index_creation_query2 = "CREATE INDEX %s ON %s (%s)" % (
            INDEX_VOLUNTEER_CADET_CONNECTIONS_TABLE,
            CADET_VOLUNTEER_CONNECTIONS_TABLE,
            VOLUNTEER_ID,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.cursor.execute(index_creation_query2)
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when creating volunteer connections table" % str(e1)
            )
        finally:
            self.close()
