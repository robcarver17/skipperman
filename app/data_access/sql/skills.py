from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.utilities.transform_data import bool2int, int2bool
from app.objects.volunteer_skills import ListOfSkills, Skill
from app.data_access.sql.shared_column_names import *

LIST_OF_SKILLS_TABLE = "list_of_skills"
INDEX_LIST_OF_SKILLS_TABLE = "index_list_of_skills"


class SqlDataListOfSkills(GenericSqlData):
    def add_new_skill(self, new_skill: Skill):
        if self.does_skill_with_name_exist(new_skill.name):
            raise Exception("Skill with name %s already exists" % new_skill.name)

        self._add_new_skill_without_checks(new_skill)

    def _add_new_skill_without_checks(self, new_skill: Skill):
        idx = self.next_available_idx()
        new_skill.id = str(self.next_available_id())
        try:
            if self.table_does_not_exist(LIST_OF_SKILLS_TABLE):
                self.create_table()

            self._add_row_without_commits_or_checks(idx, skill=new_skill)

            self.conn.commit()

        except Exception as e1:
            raise Exception("Error %s when writing skills" % str(e1))
        finally:
            self.close()

    def modify_skill(self, original_skill: Skill, new_skill: Skill):
        if original_skill.name == new_skill.name:
            pass
        else:
            if self.does_skill_with_name_exist(new_skill.name):
                raise Exception("skill with name %s already exists" % new_skill.name)

        self._modify_skill_without_checks(
            original_skill=original_skill, new_skill=new_skill
        )

    def _modify_skill_without_checks(self, original_skill: Skill, new_skill: Skill):
        name = str(new_skill.name)
        protected = bool2int(new_skill.protected)
        id = int(original_skill.id)

        try:
            if self.table_does_not_exist(LIST_OF_SKILLS_TABLE):
                self.create_table()

            self.cursor.execute(
                "UPDATE %s SET %s=%s, %s=%d WHERE %s=%d"
                % (
                    LIST_OF_SKILLS_TABLE,
                    SKILL_NAME,
                    name,
                    PROTECTED,
                    protected,
                    SKILL_ID,
                    id,
                )
            )

            self.conn.commit()

        except Exception as e1:
            raise Exception("Error %s when writing skills" % str(e1))
        finally:
            self.close()

    def does_skill_with_name_exist(self, skill_name: str):
        try:
            if self.table_does_not_exist(LIST_OF_SKILLS_TABLE):
                return False

            cursor = self.cursor
            cursor.execute(
                """SELECT * FROM %s WHERE %s='%s' """
                % (LIST_OF_SKILLS_TABLE, SKILL_NAME, str(skill_name))
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading skills" % str(e1))
        finally:
            self.close()

        return len(raw_list) > 0

    def next_available_idx(self) -> int:
        return self.last_used_idx() + 1

    def last_used_idx(self) -> int:
        try:
            if self.table_does_not_exist(LIST_OF_SKILLS_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                SKILL_ORDER,
                LIST_OF_SKILLS_TABLE,
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading skills data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])

    def next_available_id(self) -> int:
        return self.last_used_id() + 1

    def last_used_id(self) -> int:
        try:
            if self.table_does_not_exist(LIST_OF_SKILLS_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                SKILL_ID,
                LIST_OF_SKILLS_TABLE,
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading skills data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])

    def read(self) -> ListOfSkills:
        try:
            if self.table_does_not_exist(LIST_OF_SKILLS_TABLE):
                return ListOfSkills.create_empty()

            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s, %s FROM %s ORDER BY %s"""
                % (SKILL_NAME, PROTECTED, SKILL_ID, LIST_OF_SKILLS_TABLE, SKILL_ORDER)
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading skills" % str(e1))
        finally:
            self.close()

        new_list = [
            Skill(
                name=raw_skill[0],
                protected=int2bool(raw_skill[1]),
                id=str(raw_skill[2]),
            )
            for raw_skill in raw_list
        ]

        return ListOfSkills(new_list)

    def write(self, list_of_skills: ListOfSkills):
        try:
            if self.table_does_not_exist(LIST_OF_SKILLS_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (LIST_OF_SKILLS_TABLE))

            for idx, skill in enumerate(list_of_skills):
                self._add_row_without_commits_or_checks(idx, skill)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing skills" % str(e1))
        finally:
            self.close()

    def _add_row_without_commits_or_checks(self, idx: int, skill: Skill):
        name = skill.name
        protected = bool2int(skill.protected)
        id = int(skill.id)

        insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
            LIST_OF_SKILLS_TABLE,
            SKILL_NAME,
            PROTECTED,
            SKILL_ID,
            SKILL_ORDER,
        )

        self.cursor.execute(insertion, (name, protected, id, idx))

    def create_table(self):
        table_creation_query = """
            CREATE TABLE %s (
                %s STR, 
                %s INTEGER,
                %s INTEGER,
                %s INTEGER
            );
        """ % (
            LIST_OF_SKILLS_TABLE,
            SKILL_NAME,
            SKILL_ID,
            PROTECTED,
            SKILL_ORDER,
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (
            INDEX_LIST_OF_SKILLS_TABLE,
            LIST_OF_SKILLS_TABLE,
            SKILL_ID,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating groups table" % str(e1))
        finally:
            self.close()
