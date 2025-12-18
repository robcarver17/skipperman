from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.composed.volunteers_with_skills import SkillsDict
from app.objects.volunteers import Volunteer
from app.objects.volunteers_with_skills_and_ids import ListOfVolunteerSkillsWithIds, VolunteerSkillWithIds
from app.data_access.sql.shared_column_names import *
from app.data_access.sql.skills import  SqlDataListOfSkills

VOLUNTEERS_WITH_SKILLS_TABLE = "volunteers_with_skills"
INDEX_VOLUNTEERS_WITH_SKILLS_TABLE = "index_volunteers_with_skills"

class SqlDataListOfVolunteerSkills(GenericSqlData):
    def save_skills_for_volunteer(
            self, volunteer: Volunteer, dict_of_skills: SkillsDict
    ):
        volunteer_id = int(volunteer.id)
        try:
            list_of_skills = self.list_of_skills
            if self.table_does_not_exist(VOLUNTEERS_WITH_SKILLS_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s=%d" % (VOLUNTEERS_WITH_SKILLS_TABLE, VOLUNTEER_ID, volunteer_id))

            for skill in list_of_skills:
                if dict_of_skills.has_skill(skill):
                    skill_id = int(skill.id)
                    insertion = "INSERT INTO %s (%s, %s) VALUES (?,?)" % (
                        VOLUNTEERS_WITH_SKILLS_TABLE,
                        VOLUNTEER_ID, SKILL_ID)

                    self.cursor.execute(insertion, (
                        volunteer_id, skill_id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing volunteer skills" % str(e1))
        finally:
            self.close()


    def get_dict_of_existing_skills_for_volunteer(
            self, volunteer_id: str
    ) -> SkillsDict:# padded

        if self.table_does_not_exist(VOLUNTEERS_WITH_SKILLS_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            statement = "SELECT %s FROM %s WHERE %s=%d" % (
                SKILL_ID, VOLUNTEERS_WITH_SKILLS_TABLE,
                VOLUNTEER_ID, int(volunteer_id)
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading volunteer skills data" % str(e1))
        finally:
            self.close()

        list_of_skill_ids = [str(raw_item[0]) for raw_item in raw_list]

        list_of_skills =self.list_of_skills

        skills_dict = dict(
            [skill, skill.id in list_of_skill_ids]
            for skill in list_of_skills
        )

        return SkillsDict(skills_dict)

    @property
    def list_of_skills(self):
        list_of_skills  =getattr(self, "_list_of_skills", None)
        if list_of_skills is None:
            self._list_of_skills = list_of_skills =   SqlDataListOfSkills(self.db_connection).read()

        return list_of_skills

    def read(self) -> ListOfVolunteerSkillsWithIds:
        if self.table_does_not_exist(VOLUNTEERS_WITH_SKILLS_TABLE):
            return ListOfVolunteerSkillsWithIds.create_empty()

        try:
            cursor = self.cursor
            statement = "SELECT %s, %s FROM %s" % (
                VOLUNTEER_ID, SKILL_ID, VOLUNTEERS_WITH_SKILLS_TABLE
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading volunteer skills data" % str(e1))
        finally:
            self.close()

        list_of_volunteers_with_skills = [
            VolunteerSkillWithIds(
                volunteer_id=str(raw_volunteer_with_skill[0]),
                skill_id=str(raw_volunteer_with_skill[1])
            )
            for raw_volunteer_with_skill in raw_list
        ]

        return ListOfVolunteerSkillsWithIds(list_of_volunteers_with_skills)

    def write(self, list_of_volunteer_skills: ListOfVolunteerSkillsWithIds):
        try:
            if self.table_does_not_exist(VOLUNTEERS_WITH_SKILLS_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (VOLUNTEERS_WITH_SKILLS_TABLE))

            for volunteer_with_skill in list_of_volunteer_skills:
                volunteer_id=int(volunteer_with_skill.volunteer_id)
                skill_id= int(volunteer_with_skill.skill_id)
                insertion = "INSERT INTO %s (%s, %s) VALUES (?,?)" % (
                    VOLUNTEERS_WITH_SKILLS_TABLE,
                    VOLUNTEER_ID, SKILL_ID)

                self.cursor.execute(insertion, (
                    volunteer_id, skill_id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing volunteer skills" % str(e1))
        finally:
            self.close()

    def delete_table(self):
        self.conn.execute("DROP TABLE %s" % VOLUNTEERS_WITH_SKILLS_TABLE)
        self.conn.commit()
        self.close()


    def create_table(self):

        table_creation_query = """
                CREATE TABLE %s (
                    %s INTEGER,
                    %s INTEGER
                );
            """ % (VOLUNTEERS_WITH_SKILLS_TABLE, VOLUNTEER_ID, SKILL_ID)

        index_creation_query = "CREATE INDEX %s ON %s (%s)" % (
            INDEX_VOLUNTEERS_WITH_SKILLS_TABLE, VOLUNTEERS_WITH_SKILLS_TABLE, VOLUNTEER_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s creating volunteers with skills table" % str(e1))
        finally:
            self.close()


