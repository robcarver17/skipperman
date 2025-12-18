from app.data_access.sql.generic_sql_data import GenericSqlData, bool2int, int2bool
from app.objects.volunteer_skills import ListOfSkills, Skill
from app.data_access.sql.shared_column_names import *

LIST_OF_SKILLS_TABLE = "list_of_skills"
INDEX_LIST_OF_SKILLS_TABLE = "index_list_of_skills"

class SqlDataListOfSkills(GenericSqlData):
    def read(self) -> ListOfSkills:
        try:
            if self.table_does_not_exist(LIST_OF_SKILLS_TABLE):
                return ListOfSkills.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s ORDER BY %s''' % (
                SKILL_NAME, PROTECTED, SKILL_ID,
                LIST_OF_SKILLS_TABLE,
                SKILL_ORDER
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading skills" % str(e1))
        finally:
            self.close()

        new_list = [
        Skill(name=raw_skill[0],
              protected=int2bool(raw_skill[1]),
              id=str(raw_skill[2]))
        for raw_skill in raw_list]

        return ListOfSkills(new_list)


    def write(self, list_of_skills: ListOfSkills):
        try:
            if self.table_does_not_exist(LIST_OF_SKILLS_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (LIST_OF_SKILLS_TABLE))

            for idx, skill in enumerate(list_of_skills):
                name = skill.name
                protected = bool2int(skill.protected)
                id = int(skill.id)

                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                LIST_OF_SKILLS_TABLE,
                SKILL_NAME,PROTECTED, SKILL_ID, SKILL_ORDER)

                self.cursor.execute(insertion, (
                    name, protected, id, idx))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing skills" % str(e1))
        finally:
            self.close()



    def create_table(self):

        table_creation_query = """
            CREATE TABLE %s (
                %s STR, 
                %s INTEGER,
                %s INTEGER,
                %s INTEGER
            );
        """ % (LIST_OF_SKILLS_TABLE,
               SKILL_NAME, SKILL_ID, PROTECTED, SKILL_ORDER)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (INDEX_LIST_OF_SKILLS_TABLE, LIST_OF_SKILLS_TABLE, SKILL_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating groups table" % str(e1))
        finally:
            self.close()





