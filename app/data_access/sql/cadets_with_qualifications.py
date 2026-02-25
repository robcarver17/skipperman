import datetime


from app.data_access.sql.generic_sql_data import GenericSqlData, int2date, date2int
from app.data_access.sql.shared_column_names import *
from app.objects.cadets import  ListOfCadets
from app.objects.composed.cadets_with_qualifications import   QualificationsForCadet, \
    QualificationAndDate, DictOfQualificationsForCadets
from app.objects.qualifications import ListOfCadetsWithIdsAndQualifications, CadetWithIdAndQualification, ListOfQualifications

CADETS_WITH_QUALIFICATION_TABLE = "cadets_with_qualifications_table"
INDEX_NAME_CADETS_WITH_QUALIFICATION_TABLE = "cadets_with_qualifications_id"


class SqlListOfCadetsWithQualifications(
    GenericSqlData
):
    def apply_qualification_to_cadet(
            self,
            cadet_id:str,
            qualification_id:str,
            awarded_by: str,
    ):
        if self.does_cadet_have_qualification(cadet_id=cadet_id, qualification_id=qualification_id):
            raise Exception("Cadet already has qualification")

        cadet_with_qualifications = CadetWithIdAndQualification(
            cadet_id=cadet_id,
            qualification_id=qualification_id,
            awarded_by=awarded_by,
            date=datetime.date.today()
        )

        try:
            if self.table_does_not_exist(CADETS_WITH_QUALIFICATION_TABLE):
                self.create_table()

            self._write_qualification_for_cadet_without_checks_or_commit(
                    cadet_with_qualifications
                )

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to cadet with qualifications table" % str(e1))
        finally:
            self.close()

    def remove_qualification_from_cadet(
            self,
            cadet_id: str,
            qualification_id: str,

    ):
        try:
            if self.table_does_not_exist(CADETS_WITH_QUALIFICATION_TABLE):
                return

            self.cursor.execute("DELETE FROM %s WHERE %s=%d AND %s=%d " %
                                (CADETS_WITH_QUALIFICATION_TABLE,
                                 CADET_ID,
                                 int(cadet_id),
                                 QUALIFICATION_ID,
                                 int(qualification_id)))


            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to cadet with qualifications table" % str(e1))
        finally:
            self.close()

    def delete_all_qualifications_for_cadet(
            self,
            cadet_id: str,
    ):
        try:
            if self.table_does_not_exist(CADETS_WITH_QUALIFICATION_TABLE):
                return

            self.cursor.execute("DELETE FROM %s WHERE %s=%d " %
                                (CADETS_WITH_QUALIFICATION_TABLE,
                                 CADET_ID,
                                 int(cadet_id),
                                 ))


            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to cadet with qualifications table" % str(e1))
        finally:
            self.close()

    def does_cadet_have_qualification(self, cadet_id:str, qualification_id: str):
        if self.table_does_not_exist(CADETS_WITH_QUALIFICATION_TABLE):
            return False

        try:
            cursor = self.cursor
            cursor.execute('''SELECT * FROM %s WHERE %s=%d AND %s=%d ''' % (
                CADETS_WITH_QUALIFICATION_TABLE, CADET_ID, int(cadet_id),
                QUALIFICATION_ID, int(qualification_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets with qualifications" % str(e1))
        finally:
            self.close()

        return len(raw_list)>0


    def get_dict_of_qualifications_for_all_cadets(
            self,
    ) -> DictOfQualificationsForCadets:
        list_of_cadets = self.list_of_cadets
        return DictOfQualificationsForCadets(
            dict(
                [
                    (cadet, self.get_ordered_list_of_qualifications_for_cadet(cadet)) for cadet in list_of_cadets
                ]
            )
        )


    def get_ordered_list_of_qualifications_for_cadet(
            self, cadet_id: str
    ) -> QualificationsForCadet:
        list_of_qualifications_for_cadet = self.get_unordered_qualifications_for_cadet(cadet_id)
        list_of_qualifications = self.list_of_qualifications

        return list_of_qualifications_for_cadet.order_by(list_of_qualifications)

    @property
    def list_of_qualifications(self) -> ListOfQualifications:
        return self.object_store.get(self.object_store.data_api.data_list_of_qualifications.read)

    @property
    def list_of_cadets(self) -> ListOfCadets:
        list_of_cadets = self.object_store.get(self.object_store.data_api.data_list_of_cadets.read)

        return list_of_cadets

    def get_unordered_qualifications_for_cadet(self, cadet_id: str) ->  QualificationsForCadet:
        raw_list = self.get_qualifications_for_cadet_with_ids(cadet_id)

        return QualificationsForCadet([
            QualificationAndDate(
                qualification=self.list_of_qualifications.qualification_given_id(raw_item.qualification_id),
                date_achieved=raw_item.date,
                awarded_by=raw_item.awarded_by
            ) for raw_item in raw_list
        ])


    def get_qualifications_for_cadet_with_ids(self, cadet_id: str) -> ListOfCadetsWithIdsAndQualifications:
        if self.table_does_not_exist(CADETS_WITH_QUALIFICATION_TABLE):
            return ListOfCadetsWithIdsAndQualifications([])

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s,  %s, %s FROM %s  WHERE %s=%d ''' % (
                QUALIFICATION_ID,
                QUALIFICATION_DATE, AWARDED_BY, CADETS_WITH_QUALIFICATION_TABLE,
                CADET_ID,
                int(cadet_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets with qualifications" % str(e1))
        finally:
            self.close()

        new_list = [
            CadetWithIdAndQualification(
                cadet_id=cadet_id,
                qualification_id=str(raw_cadet_with_qual[0]),
                date=int2date(raw_cadet_with_qual[1]),
                awarded_by=str(raw_cadet_with_qual[2])
            ) for raw_cadet_with_qual in raw_list
        ]

        return ListOfCadetsWithIdsAndQualifications(new_list) ## ignore warning

    def read(self) -> ListOfCadetsWithIdsAndQualifications:
        if self.table_does_not_exist(CADETS_WITH_QUALIFICATION_TABLE):
            return ListOfCadetsWithIdsAndQualifications([])

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s FROM %s  ''' % (
                CADET_ID, QUALIFICATION_ID, QUALIFICATION_DATE, AWARDED_BY, CADETS_WITH_QUALIFICATION_TABLE
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets with qualifications" % str(e1))
        finally:
            self.close()

        new_list = [
            CadetWithIdAndQualification(
                cadet_id=str(raw_cadet_with_qual[0]),
                qualification_id=str(raw_cadet_with_qual[1]),
                date=int2date(raw_cadet_with_qual[2]),
                awarded_by=str(raw_cadet_with_qual[3])
            ) for raw_cadet_with_qual in raw_list
        ]

        return ListOfCadetsWithIdsAndQualifications(new_list) ## ignore warning

    def delete_table(self):
        self.conn.execute("DROP TABLE %s" % CADETS_WITH_QUALIFICATION_TABLE)
        self.conn.commit()
        self.close()

    def write(
        self, list_of_cadets_with_qualifications: ListOfCadetsWithIdsAndQualifications
    ):
        try:
            if self.table_does_not_exist(CADETS_WITH_QUALIFICATION_TABLE):
                self.create_table()

            self.cursor.execute("DELETE FROM %s" % (CADETS_WITH_QUALIFICATION_TABLE))

            for cadet_with_qualifications in list_of_cadets_with_qualifications:
                self._write_qualification_for_cadet_without_checks_or_commit(
                    cadet_with_qualifications
                )

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to cadet with qualifications table" % str(e1))
        finally:
            self.close()

    def _write_qualification_for_cadet_without_checks_or_commit(self, cadet_with_qualifications: CadetWithIdAndQualification):
        cadet_id = int(cadet_with_qualifications.cadet_id)
        qualification_id = int(cadet_with_qualifications.qualification_id)
        qualification_date = date2int(cadet_with_qualifications.date)
        awarded_by = str(cadet_with_qualifications.awarded_by)

        insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?, ?,?,?)" % (
            CADETS_WITH_QUALIFICATION_TABLE,
            CADET_ID, QUALIFICATION_ID, QUALIFICATION_DATE, AWARDED_BY
        )
        self.cursor.execute(insertion,
                            (cadet_id, qualification_id, qualification_date, awarded_by))

    def create_table(self):
        table_creation_query = """
            CREATE TABLE %s (
                %s INTEGER, 
                %s INTEGER,
                %s INTEGER,
                %s STR
            );
        """ % (CADETS_WITH_QUALIFICATION_TABLE, CADET_ID, QUALIFICATION_ID, QUALIFICATION_DATE, AWARDED_BY)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s)" % (INDEX_NAME_CADETS_WITH_QUALIFICATION_TABLE,
                                                                              CADETS_WITH_QUALIFICATION_TABLE,
                                                                              CADET_ID, QUALIFICATION_ID)
        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating cadets with qualification table" % str(e1))
