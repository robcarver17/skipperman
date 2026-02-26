from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.composed.volunteers_with_skills import (
    SkillsDict,
    DictOfVolunteersWithSkills,
)
from app.objects.volunteer_skills import ListOfSkills
from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.volunteers_with_skills_and_ids import (
    ListOfVolunteerSkillsWithIds,
    VolunteerSkillWithIds,
)
from app.data_access.sql.shared_column_names import *

VOLUNTEERS_WITH_SKILLS_TABLE = "volunteers_with_skills"
INDEX_VOLUNTEERS_WITH_SKILLS_TABLE = "index_volunteers_with_skills"


class SqlDataListOfVolunteerSkills(GenericSqlData):
    def remove_skill_for_volunteer(self, volunteer_id: str, skill_id: str):
        try:
            if self.table_does_not_exist(VOLUNTEERS_WITH_SKILLS_TABLE):
                return

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d AND %s=%d"
                % (
                    VOLUNTEERS_WITH_SKILLS_TABLE,
                    VOLUNTEER_ID,
                    int(volunteer_id),
                    SKILL_ID,
                    int(skill_id),
                )
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing volunteer skills" % str(e1))
        finally:
            self.close()

    def add_skill_for_volunteer(self, volunteer_id: str, skill_id: str):
        if self.does_volunteer_have_skill(volunteer_id=volunteer_id, skill_id=skill_id):
            return

        self._add_skill_for_volunteer_without_checks(
            volunteer_id=volunteer_id, skill_id=skill_id
        )

    def _add_skill_for_volunteer_without_checks(self, volunteer_id: str, skill_id: str):
        try:
            if self.table_does_not_exist(VOLUNTEERS_WITH_SKILLS_TABLE):
                self.create_table()

            volunteer_with_skill = VolunteerSkillWithIds(
                volunteer_id=volunteer_id, skill_id=skill_id
            )
            self._add_row_without_checks_or_commits(volunteer_with_skill)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing volunteer skills" % str(e1))
        finally:
            self.close()

    def does_volunteer_have_skill(self, volunteer_id: str, skill_id: str):
        if self.table_does_not_exist(VOLUNTEERS_WITH_SKILLS_TABLE):
            return False

        try:
            cursor = self.cursor
            statement = "SELECT * FROM %s WHERE %s=%d AND %s=%d" % (
                VOLUNTEERS_WITH_SKILLS_TABLE,
                VOLUNTEER_ID,
                int(volunteer_id),
                SKILL_ID,
                int(skill_id),
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading volunteer skills data" % str(e1))
        finally:
            self.close()

        return len(raw_list) > 0

    def delete_volunteer_skills(self, volunteer_id: str):
        try:
            if self.table_does_not_exist(VOLUNTEERS_WITH_SKILLS_TABLE):
                return

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d"
                % (VOLUNTEERS_WITH_SKILLS_TABLE, VOLUNTEER_ID, int(volunteer_id))
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing volunteer skills" % str(e1))
        finally:
            self.close()

    def update_skills_for_volunteer(
        self, volunteer: Volunteer, dict_of_skills: SkillsDict
    ):
        try:
            if self.table_does_not_exist(VOLUNTEERS_WITH_SKILLS_TABLE):
                self.create_table()

            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d"
                % (VOLUNTEERS_WITH_SKILLS_TABLE, VOLUNTEER_ID, int(volunteer.id))
            )

            for skill in dict_of_skills.list_of_held_skills():
                self._add_skill_for_volunteer_without_checks(
                    volunteer_id=volunteer.id, skill_id=skill.id
                )

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing volunteer skills" % str(e1))
        finally:
            self.close()

    def get_dict_of_volunteers_with_skills(self) -> DictOfVolunteersWithSkills:
        raw_data = self.read()
        new_dict = {}
        for raw_item in raw_data:
            volunteer_id = raw_item.volunteer_id
            skill_id = raw_item.skill_id

            volunteer = self.list_of_volunteers.volunteer_with_id(volunteer_id)
            skill = self.list_of_skills.skill_with_id(skill_id)

            skills_dict_this_volunteer = new_dict.get(volunteer, SkillsDict())
            skills_dict_this_volunteer[skill] = True
            new_dict[volunteer] = skills_dict_this_volunteer

        return DictOfVolunteersWithSkills(new_dict)

    @property
    def list_of_volunteers(self) -> ListOfVolunteers:
        return self.object_store.get(self.object_store.data_api.list_of_volunteers.read)

    def get_dict_of_existing_skills_for_volunteer(
        self, volunteer_id: str
    ) -> SkillsDict:
        if self.table_does_not_exist(VOLUNTEERS_WITH_SKILLS_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            statement = "SELECT %s FROM %s WHERE %s=%d" % (
                SKILL_ID,
                VOLUNTEERS_WITH_SKILLS_TABLE,
                VOLUNTEER_ID,
                int(volunteer_id),
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading volunteer skills data" % str(e1))
        finally:
            self.close()

        list_of_skill_ids = [str(raw_item[0]) for raw_item in raw_list]

        list_of_skills = self.list_of_skills

        skills_dict = dict(
            [(skill, skill.id in list_of_skill_ids) for skill in list_of_skills]
        )

        return SkillsDict(skills_dict)  ## ignore warning

    @property
    def list_of_skills(self) -> ListOfSkills:
        list_of_skills = self.object_store.get(
            self.object_store.data_api.data_list_of_skills.read
        )

        return list_of_skills

    def read(self) -> ListOfVolunteerSkillsWithIds:
        if self.table_does_not_exist(VOLUNTEERS_WITH_SKILLS_TABLE):
            return ListOfVolunteerSkillsWithIds.create_empty()

        try:
            cursor = self.cursor
            statement = "SELECT %s, %s FROM %s" % (
                VOLUNTEER_ID,
                SKILL_ID,
                VOLUNTEERS_WITH_SKILLS_TABLE,
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
                skill_id=str(raw_volunteer_with_skill[1]),
            )
            for raw_volunteer_with_skill in raw_list
        ]

        return ListOfVolunteerSkillsWithIds(list_of_volunteers_with_skills)

    def write(self, list_of_volunteer_skills: ListOfVolunteerSkillsWithIds):
        try:
            if self.table_does_not_exist(VOLUNTEERS_WITH_SKILLS_TABLE):
                self.create_table()

            self.cursor.execute("DELETE FROM %s" % (VOLUNTEERS_WITH_SKILLS_TABLE))

            for volunteer_with_skill in list_of_volunteer_skills:
                self._add_row_without_checks_or_commits(volunteer_with_skill)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing volunteer skills" % str(e1))
        finally:
            self.close()

    def _add_row_without_checks_or_commits(
        self, volunteer_with_skill: VolunteerSkillWithIds
    ):
        volunteer_id = int(volunteer_with_skill.volunteer_id)
        skill_id = int(volunteer_with_skill.skill_id)
        insertion = "INSERT INTO %s (%s, %s) VALUES (?,?)" % (
            VOLUNTEERS_WITH_SKILLS_TABLE,
            VOLUNTEER_ID,
            SKILL_ID,
        )

        self.cursor.execute(insertion, (volunteer_id, skill_id))

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
            """ % (
            VOLUNTEERS_WITH_SKILLS_TABLE,
            VOLUNTEER_ID,
            SKILL_ID,
        )

        index_creation_query = "CREATE INDEX %s ON %s (%s)" % (
            INDEX_VOLUNTEERS_WITH_SKILLS_TABLE,
            VOLUNTEERS_WITH_SKILLS_TABLE,
            VOLUNTEER_ID,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s creating volunteers with skills table" % str(e1))
        finally:
            self.close()
