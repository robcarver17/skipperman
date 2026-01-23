from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.group_notes_at_event import ListOfGroupNotesAtEventWithIds, GroupNotesAtEventWithIds
from app.data_access.sql.shared_column_names import *

GROUP_NOTES_AT_EVENT_TABLE = "group_notes_at_event"
INDEX_GROUP_NOTES_AT_EVENT_TABLE = "index_group_notes_at_event"

class SqlDataListOfGroupNotesAtEvent(GenericSqlData):
    def read(self) -> ListOfGroupNotesAtEventWithIds:
        try:
            if self.table_does_not_exist(GROUP_NOTES_AT_EVENT_TABLE):
                return ListOfGroupNotesAtEventWithIds.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s''' % (
                EVENT_ID, GROUP_ID, GROUP_NOTES,
                GROUP_NOTES_AT_EVENT_TABLE
             ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading group notes" % str(e1))
        finally:
            self.close()

        new_list = [GroupNotesAtEventWithIds(event_id =str(raw_item[0]),
                                             group_id = str(raw_item[1]),
                                                            notes=str(raw_item[2])) for raw_item in raw_list
                    ]

        return ListOfGroupNotesAtEventWithIds(new_list)


    def write(self, list_of_group_notes_with_ids: ListOfGroupNotesAtEventWithIds):
        try:
            if self.table_does_not_exist(GROUP_NOTES_AT_EVENT_TABLE):
                self.create_table()

            self.cursor.execute("DELETE FROM %s" % (GROUP_NOTES_AT_EVENT_TABLE))

            for note in list_of_group_notes_with_ids:
                event_id = int(note.event_id)
                group_id = int(note.group_id)
                notes = str(note.notes)

                insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?,?,?)" % (
                    GROUP_NOTES_AT_EVENT_TABLE,
                    EVENT_ID, GROUP_ID, GROUP_NOTES)

                self.cursor.execute(insertion, (
                    event_id, group_id, notes))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing group notes" % str(e1))
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
                """ % (GROUP_NOTES_AT_EVENT_TABLE,
                       EVENT_ID,
                       GROUP_ID,
                       GROUP_NOTES)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s)" % (
            INDEX_GROUP_NOTES_AT_EVENT_TABLE,
        GROUP_NOTES_AT_EVENT_TABLE,
        EVENT_ID,
        GROUP_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating GROUP notes table" % str(e1))
        finally:
            self.close()
