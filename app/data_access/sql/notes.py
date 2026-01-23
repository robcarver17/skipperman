
from app.data_access.sql.generic_sql_data import GenericSqlData, date2int, bool2int, int2date, int2bool
from app.data_access.sql.shared_column_names import *
from app.data_access.sql.volunteers import SqlDataListOfVolunteers
from app.objects.composed.notes_with_volunteers import ListOfNotesWithVolunteers, NoteWithVolunteer
from app.objects.notes import ListOfNotes, Note
from app.objects.volunteers import Volunteer, ListOfVolunteers

NOTES_TABLE = "SM_notes_table"
INDEX_NOTES_TABLE = "index_SM_notes_table"

class SqlDataListOfNotes( GenericSqlData):
    def read_list_of_volunteers_with_notes(self)-> ListOfNotesWithVolunteers:
        volunteers_with_id_and_notes = self.read()
        new_list = [
            NoteWithVolunteer(
                author_volunteer=self.volunteer_from_id(note_and_volunteer_with_id.author_volunteer_id),
                completed=note_and_volunteer_with_id.completed,
                assigned_volunteer=self.volunteer_from_id(note_and_volunteer_with_id.assigned_volunteer_id),
                text=note_and_volunteer_with_id.text,
                priority=note_and_volunteer_with_id.priority,
                created_datetime=note_and_volunteer_with_id.created_datetime,
                id=note_and_volunteer_with_id.id
            )
            for note_and_volunteer_with_id in volunteers_with_id_and_notes
        ]

        return ListOfNotesWithVolunteers(new_list)

    def volunteer_from_id(self, volunteer_id: str):
        return self.list_of_volunteers.volunteer_with_id(volunteer_id)

    @property
    def list_of_volunteers(self) -> ListOfVolunteers:
        list_of_volunteers = getattr(self, "_list_of_volunteers", None)
        if list_of_volunteers is None:
            self._list_of_volunteers = list_of_volunteers = SqlDataListOfVolunteers(self.db_connection).read()

        return list_of_volunteers

    def update_note_with_new_data(
            self,
            note_id: str,
            priority: str,
            completed: bool,
            text: str,
            assigned_volunteer: Volunteer,
    ):
        try:
            insertion = "UPDATE %s SET %s=?, %s=?, %s=?, %s=? WHERE %s=?" % (
                NOTES_TABLE,
                NOTE_PRIORITY_STR,
                NOTE_COMPLETED,
                NOTE_TEXT,
                ASSIGNED_VOLUNTEER_ID,
                NOTE_ID
            )

            self.cursor.execute(insertion, (
                str(priority),
                bool2int(completed),
                str(text),
                int(assigned_volunteer.id),
                int(note_id)
            ))

            self.conn.commit()

        except Exception as e1:
            raise Exception(str(e1))

        finally:
            self.close()


    def add_quick_note(self, text: str, volunteer_author: Volunteer):

            note = Note.new_quick_note(
                text=text,
                author_volunteer_id=volunteer_author.id,
            )
            note.id = self.next_id()
            try:
                if self.table_does_not_exist(NOTES_TABLE):
                    self.create_table()

                self.insert_note_and_do_not_commit(note)

                self.conn.commit()
            except Exception as e1:
                raise Exception("Error %s when writing  notes" % str(e1))
            finally:
                self.close()

    def next_id(self) -> str:
        return str(self.last_used_id()+1)

    def last_used_id(self)-> int:
        try:
            if self.table_does_not_exist(NOTES_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                NOTE_ID,
                NOTES_TABLE,
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading cadet data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])

    def read(self) -> ListOfNotes:
        try:
            if self.table_does_not_exist(NOTES_TABLE):
                return ListOfNotes.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s, %s, %s, %s FROM %s''' % (
                NOTE_TEXT,
                AUTHOR_VOLUNTEER_ID,
                NOTE_CREATED_DATETIME,
                ASSIGNED_VOLUNTEER_ID,
                NOTE_PRIORITY_STR,
                NOTE_COMPLETED,
                NOTE_ID,
                NOTES_TABLE
             ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading notes" % str(e1))
        finally:
            self.close()

        new_list = [Note(
            text=str(ans[0]),
            author_volunteer_id=str(ans[1]),
            created_datetime=int2date(ans[2]),
            assigned_volunteer_id=str(ans[3]),
            priority=str(ans[4]),
            completed=int2bool(ans[5]),
            id=str(ans[6])
        ) for ans in raw_list
                    ]

        return ListOfNotes(new_list)


    def write(self, list_of_notes: ListOfNotes):
        try:
            if self.table_does_not_exist(NOTES_TABLE):
                self.create_table()

            self.cursor.execute("DELETE FROM %s" % (NOTES_TABLE))

            for note in list_of_notes:
                self.insert_note_and_do_not_commit(note)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing  notes" % str(e1))
        finally:
            self.close()

    def insert_note_and_do_not_commit(self, note: Note):
        text = str(note.text)
        author_volunteer_id = int(note.author_volunteer_id)
        created_datetime = date2int(note.created_datetime)
        assigned_volunteer_id = int(note.assigned_volunteer_id)
        priority = str(note.priority)
        completed = bool2int(note.completed)
        note_id = int(note.id)

        insertion = "INSERT INTO %s (%s, %s, %s, %s, %s, %s, %s) VALUES (?,?,?,?,?,?,?)" % (
            NOTES_TABLE,

            NOTE_TEXT,
            AUTHOR_VOLUNTEER_ID,
            NOTE_CREATED_DATETIME,
            ASSIGNED_VOLUNTEER_ID,
            NOTE_PRIORITY_STR,
            NOTE_COMPLETED,
            NOTE_ID)

        self.cursor.execute(insertion, (
            text,
            author_volunteer_id,
            created_datetime,
            assigned_volunteer_id,
            priority,
            completed,
            note_id))

    def create_table(self):

        # name: str
        # hidden: bool
        # id: str = arg_not_passed

        table_creation_query = """
                        CREATE TABLE %s (
                            %s STR,
                            %s INTEGER,
                            %s INTEGER,
                            %s INTEGER,
                            %s STR,
                            %s INTEGER,
                            %s INTEGER
                        );
                    """ % (NOTES_TABLE,

                        NOTE_TEXT,
                           AUTHOR_VOLUNTEER_ID,
                           NOTE_CREATED_DATETIME,
                           ASSIGNED_VOLUNTEER_ID,
                           NOTE_PRIORITY_STR,
                           NOTE_COMPLETED,
                           NOTE_ID)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (
            INDEX_NOTES_TABLE, NOTES_TABLE,
        NOTE_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating notes table" % str(e1))
        finally:
            self.close()

