from app.data_access.sql.generic_sql_data import GenericSqlData, int2date
from app.objects.cadet_volunteer_connections_with_ids import ListOfCadetVolunteerAssociationsWithIds, CadetVolunteerAssociationWithIds
from app.data_access.sql.shared_column_names import *
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.membership_status import MembershipStatus
from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.data_access.sql.cadets import CADETS_TABLE
from app.data_access.sql.volunteers import VOLUNTEERS_TABLE

CADET_VOLUNTEER_CONNECTIONS_TABLE = "cadet_volunteer_associations"
INDEX_CADET_VOLUNTEER_CONNECTIONS_TABLE = "index_cadet_volunteer_associations"
INDEX_VOLUNTEER_CADET_CONNECTIONS_TABLE = "index_volunteer_cadet_associations"


class SqlDataListOfCadetVolunteerAssociations(
    GenericSqlData
):
    def delete_all_connections_for_volunteer(
             self, volunteer: Volunteer
    ):
        if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
            return

        try:

            cursor = self.cursor
            cursor.execute("DELETE FROM %s WHERE %s=%d" % (
                CADET_VOLUNTEER_CONNECTIONS_TABLE,
                VOLUNTEER_ID, int(volunteer.id),
            ))
            self.conn.commit()
        except Exception as e1:
            raise e1
        finally:
            self.close()

    def delete_all_connections_for_cadet(
            self, cadet: Cadet
    ):
        if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
            return

        try:

            cursor = self.cursor
            cursor.execute("DELETE FROM %s WHERE %s=%d" % (
                CADET_VOLUNTEER_CONNECTIONS_TABLE,
                CADET_ID, int(cadet.id),
            ))
            self.conn.commit()
        except Exception as e1:
            raise e1
        finally:
            self.close()


    def add_volunteer_connection_to_cadet_in_master_list_of_volunteers(
            self, cadet: Cadet, volunteer: Volunteer
    ):

        if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
            self.create_table()

        if self.is_cadet_associated_with_volunteer(cadet=cadet, volunteer=volunteer):
            return
        try:
            cadet_id = int(cadet.id)
            volunteer_id = int(volunteer.id)

            insertion = "INSERT INTO %s (%s, %s) VALUES (?,?)" % (
                CADET_VOLUNTEER_CONNECTIONS_TABLE, CADET_ID, VOLUNTEER_ID)

            self.cursor.execute(insertion, (
                cadet_id, volunteer_id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing connections" % str(e1))
        finally:
            self.close()




    def delete_cadet_connection(
            self, cadet: Cadet, volunteer: Volunteer
    ):
        if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
            return

        try:

            cursor = self.cursor
            cursor.execute("DELETE FROM %s WHERE %s=%d AND %s=%d" % (
                CADET_VOLUNTEER_CONNECTIONS_TABLE,
                CADET_ID, int(cadet.id),
                VOLUNTEER_ID, int(volunteer.id)
            ))
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
            cursor.execute('''SELECT * FROM %s WHERE %s=%d AND %s=%d''' % (
                CADET_VOLUNTEER_CONNECTIONS_TABLE, CADET_ID, int(cadet.id), VOLUNTEER_ID, int(volunteer.id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading connections" % str(e1))
        finally:
            self.close()

        return len(raw_list)>0

    def get_list_of_cadets_associated_with_volunteer(
            self, volunteer_id:str) -> ListOfCadets:
        try:
            if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
                return ListOfCadets.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s.%s, %s.%s, %s.%s, %s.%s, %s.%s FROM %s JOIN %s ON %s.%s=%s.%s WHERE %s.%s=%s''' % (
                #select
                CADETS_TABLE, CADET_FIRST_NAME,
                CADETS_TABLE, CADET_SURNAME,
                CADETS_TABLE, CADET_DOB,
                CADETS_TABLE, CADET_MEMBERSHIP_STATUS,
                CADETS_TABLE, CADET_ID, # from
                CADET_VOLUNTEER_CONNECTIONS_TABLE, #join
                CADETS_TABLE, #on
                CADET_VOLUNTEER_CONNECTIONS_TABLE, CADET_ID, # equals
                CADETS_TABLE, CADET_ID, #where
                CADET_VOLUNTEER_CONNECTIONS_TABLE,VOLUNTEER_ID, #equals
                int(volunteer_id)
                ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading connections" % str(e1))
        finally:
            self.close()

        list_of_cadets = [
            Cadet(first_name=raw_cadet[0],
                  surname=raw_cadet[1],
                  date_of_birth=int2date(raw_cadet[2]),
                  membership_status=MembershipStatus[raw_cadet[3]],
                  id=str(raw_cadet[4]))
            for raw_cadet in raw_list
        ]

        return ListOfCadets(list_of_cadets)


    def get_list_of_volunteers_associated_with_cadet(
            self, cadet_id:str) -> ListOfVolunteers:
        try:
            if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
                return ListOfVolunteers.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s.%s, %s.%s, %s.%s FROM %s JOIN %s ON %s.%s=%s.%s WHERE %s.%s=%s''' % (
                #select
                VOLUNTEERS_TABLE, VOLUNTEER_FIRST_NAME,
                VOLUNTEERS_TABLE, VOLUNTEER_SURNAME,
                VOLUNTEERS_TABLE, VOLUNTEER_ID, # from
                CADET_VOLUNTEER_CONNECTIONS_TABLE, #join
                VOLUNTEERS_TABLE, #on
                CADET_VOLUNTEER_CONNECTIONS_TABLE, VOLUNTEER_ID, # equals
                VOLUNTEERS_TABLE, VOLUNTEER_ID, #where
                CADET_VOLUNTEER_CONNECTIONS_TABLE,CADET_ID, #equals
                int(cadet_id)
                ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading connections" % str(e1))
        finally:
            self.close()

        list_of_volunteers = [
            Volunteer(first_name=raw_volunteer[0],
                  surname=raw_volunteer[1],
                    id=raw_volunteer[2])
            for raw_volunteer in raw_list
        ]

        return ListOfVolunteers(list_of_volunteers)

    def read(self) -> ListOfCadetVolunteerAssociationsWithIds:
        try:
            if self.table_does_not_exist(CADET_VOLUNTEER_CONNECTIONS_TABLE):
                return ListOfCadetVolunteerAssociationsWithIds([])

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s''' % (
                CADET_ID, VOLUNTEER_ID, CADET_VOLUNTEER_CONNECTIONS_TABLE
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading connections" % str(e1))
        finally:
            self.close()

        new_list = []
        for raw_connection in raw_list:
            connection= CadetVolunteerAssociationWithIds(
                cadet_id=str(raw_connection[0]),
                volunteer_id=str(raw_connection[1])
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

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (CADET_VOLUNTEER_CONNECTIONS_TABLE))

            for cadet_volunteer_association in list_of_cadet_volunteer_associations:
                cadet_id = int(cadet_volunteer_association.cadet_id)
                volunteer_id = int(cadet_volunteer_association.volunteer_id)

                insertion = "INSERT INTO %s (%s, %s) VALUES (?,?)" % (
                    CADET_VOLUNTEER_CONNECTIONS_TABLE, CADET_ID, VOLUNTEER_ID)

                self.cursor.execute(insertion, (
                    cadet_id, volunteer_id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing connections" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
            CREATE TABLE %s (
                %s INTEGER,
                %s INTEGER
            );
        """ % (CADET_VOLUNTEER_CONNECTIONS_TABLE,
               CADET_ID,
               VOLUNTEER_ID)

        index_creation_query = "CREATE INDEX %s ON %s (%s)" % (INDEX_CADET_VOLUNTEER_CONNECTIONS_TABLE, CADET_VOLUNTEER_CONNECTIONS_TABLE, CADET_ID)
        index_creation_query2 = "CREATE INDEX %s ON %s (%s)" % (INDEX_VOLUNTEER_CADET_CONNECTIONS_TABLE, CADET_VOLUNTEER_CONNECTIONS_TABLE, VOLUNTEER_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.cursor.execute(index_creation_query2)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating volunteer connections table" % str(e1))
        finally:
            self.close()

