from typing import List

from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.utilities.transform_data import bool2int, int2bool
from app.objects.composed.volunteer_roles import ListOfRolesWithSkills, RoleWithSkills
from app.objects.composed.volunteers_with_skills import SkillsDict
from app.objects.roles_and_teams import ListOfRolesWithSkillIds, RolesWithSkillIds
from app.objects.volunteer_skills import ListOfSkills
from app.data_access.sql.shared_column_names import *


ROLES_TABLE = "roles"
INDEX_ROLES_TABLE = "index_roles_table"

ROLES_SKILLS_TABLE = "roles_and_skills"
INDEX_ROLES_SKILLS_TABLE = "index_roles_and_skills_table"


class SqlDataListOfRoles(GenericSqlData):
    def add_role_with_skill(self, new_role: RoleWithSkills):
        if self.does_role_with_name_already_exist(new_role.name):
            raise Exception("Can't add as name %s already exists" % new_role.name)
        self._add_role_with_skill_without_checks(new_role)

    def _add_role_with_skill_without_checks(self, new_role: RoleWithSkills):
        try:
            if self.table_does_not_exist(ROLES_TABLE):
                self.create_table()

            new_role_with_ids = new_role.as_role_with_skill_ids()
            new_role_with_ids.id = str(self.next_available_id())
            idx = self.next_available_idx()

            self._write_row_without_checks_or_commits(idx, new_role_with_ids)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing roles" % str(e1))
        finally:
            self.close()

    def next_available_id(self) -> int:
        return self.last_used_id() + 1

    def last_used_id(self) -> int:
        try:
            if self.table_does_not_exist(ROLES_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                ROLE_ID,
                ROLES_TABLE,
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading roles data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])

    def next_available_idx(self) -> int:
        return self.last_used_idx() + 1

    def last_used_idx(self) -> int:
        try:
            if self.table_does_not_exist(ROLES_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                ROLE_ORDER,
                ROLES_TABLE,
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading roles data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])

    def update_role_with_skill(
        self,
        existing_role_with_skills: RoleWithSkills,
        new_role_with_skills: RoleWithSkills,
    ):
        if existing_role_with_skills.name == new_role_with_skills.name:
            pass
        else:
            if self.does_role_with_name_already_exist(new_role_with_skills.name):
                raise Exception(
                    "Can't rename %s to %s as new name already exists"
                    % (existing_role_with_skills.name, new_role_with_skills.name)
                )

        self._update_role_with_skill_without_checks(
            existing_role_with_skills=existing_role_with_skills,
            new_role_with_skills=new_role_with_skills,
        )

    def does_role_with_name_already_exist(self, role_name: str):
        try:
            if self.table_does_not_exist(ROLES_TABLE):
                return False

            cursor = self.cursor
            cursor.execute(
                """SELECT * FROM %s WHERE %s='%s' """
                % (ROLES_TABLE, ROLE_NAME, role_name)
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading roles with skills" % str(e1))
        finally:
            self.close()

        return len(raw_list) > 0

    def _update_role_with_skill_without_checks(
        self,
        existing_role_with_skills: RoleWithSkills,
        new_role_with_skills: RoleWithSkills,
    ):
        role_id = existing_role_with_skills.id

        try:
            if self.table_does_not_exist(ROLES_TABLE):
                raise Exception("Cannot modify as table dropped")

            name = new_role_with_skills.name
            hidden = bool2int(new_role_with_skills.hidden)
            protected = bool2int(new_role_with_skills.protected)
            associate_sailing_group = bool2int(
                new_role_with_skills.associate_sailing_group
            )

            self.cursor.execute(
                "UPDATE %s SET %s=?, %s=?, %s=?, %s=? WHERE %s=%d"
                % (
                    ROLES_TABLE,
                    ROLE_NAME,
                    HIDDEN,
                    PROTECTED,
                    ASSOCIATE_SAILING_GROUP,
                    ROLE_ID,
                    int(role_id),
                ),
                (
                    name,
                    hidden,
                    protected,
                    associate_sailing_group,
                ),
            )

            skill_ids_required = new_role_with_skills.list_of_skill_ids()
            self._write_roles_and_skills_without_commit(
                role_id=role_id, list_of_skill_ids=skill_ids_required
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing roles" % str(e1))
        finally:
            self.close()

    def read_list_of_roles_with_skills(self) -> ListOfRolesWithSkills:
        if self.table_does_not_exist(ROLES_TABLE):
            return ListOfRolesWithSkills()

        list_of_skills_with_ids = self.read()

        new_list = [
            RoleWithSkills(
                name=skill_with_id.name,
                hidden=skill_with_id.hidden,
                protected=skill_with_id.protected,
                associate_sailing_group=skill_with_id.associate_sailing_group,
                skills_dict=self.padded_skills_dict_from_list_of_skill_ids(
                    skill_with_id.skill_ids_required
                ),
                id=skill_with_id.id,
            )
            for skill_with_id in list_of_skills_with_ids
        ]

        return ListOfRolesWithSkills(new_list)

    def padded_skills_dict_from_list_of_skill_ids(
        self, list_of_skill_ids: List[str]
    ) -> SkillsDict:
        list_of_skills = self.list_of_skills
        list_of_skills_this_dict = ListOfSkills(
            [list_of_skills.skill_with_id(skill_id) for skill_id in list_of_skill_ids]
        )
        skills_dict = SkillsDict.from_list_of_skills(list_of_skills_this_dict)
        skills_dict.pad_with_missing_skills(self.list_of_skills)

        return skills_dict

    @property
    def list_of_skills(self) -> ListOfSkills:
        list_of_skills = self.object_store.get(
            self.object_store.data_api.data_list_of_skills.read
        )

        return list_of_skills

    def read(self) -> ListOfRolesWithSkillIds:
        try:
            if self.table_does_not_exist(ROLES_TABLE):
                return ListOfRolesWithSkillIds.create_empty()

            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s, %s, %s, %s FROM %s ORDER BY %s"""
                % (
                    ROLE_NAME,
                    HIDDEN,
                    PROTECTED,
                    ASSOCIATE_SAILING_GROUP,
                    ROLE_ID,
                    ROLES_TABLE,
                    ROLE_ORDER,
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading roles with skills" % str(e1))
        finally:
            self.close()

        roles_with_skills = []
        for raw_role_data in raw_list:
            name = str(raw_role_data[0])
            hidden = int2bool(raw_role_data[1])
            protected = int2bool(raw_role_data[2])
            associate_sailing_group = int2bool(raw_role_data[3])
            role_id = str(raw_role_data[4])
            skill_ids = self._read_skill_ids_for_role(role_id)

            roles_with_skills.append(
                RolesWithSkillIds(
                    name=name,
                    hidden=hidden,
                    protected=protected,
                    associate_sailing_group=associate_sailing_group,
                    skill_ids_required=skill_ids,
                    id=role_id,
                )
            )

        return ListOfRolesWithSkillIds(roles_with_skills)

    def _read_skill_ids_for_role(self, role_id):
        ## no closed done inside above
        cursor = self.cursor
        cursor.execute(
            """SELECT %s FROM %s WHERE %s=%d"""
            % (SKILL_ID, ROLES_SKILLS_TABLE, ROLE_ID, int(role_id))
        )
        raw_list = cursor.fetchall()

        return [str(skill_id[0]) for skill_id in raw_list]

    def write(self, list_of_roles: ListOfRolesWithSkillIds):
        try:
            if self.table_does_not_exist(ROLES_TABLE):
                self.create_table()

            self.cursor.execute("DELETE FROM %s" % (ROLES_TABLE))

            for idx, role in enumerate(list_of_roles):
                self._write_row_without_checks_or_commits(idx, role)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing roles" % str(e1))
        finally:
            self.close()

    def _write_row_without_checks_or_commits(self, idx: int, role: RolesWithSkillIds):
        name = role.name
        hidden = bool2int(role.hidden)
        protected = bool2int(role.protected)
        associate_sailing_group = bool2int(role.associate_sailing_group)

        id = int(role.id)

        insertion = "INSERT INTO %s (%s, %s, %s, %s, %s, %s) VALUES (?,?,?,?,?,?)" % (
            ROLES_TABLE,
            ROLE_NAME,
            HIDDEN,
            PROTECTED,
            ASSOCIATE_SAILING_GROUP,
            ROLE_ID,
            ROLE_ORDER,
        )

        self.cursor.execute(
            insertion, (name, hidden, protected, associate_sailing_group, id, idx)
        )

        skill_ids_required = role.skill_ids_required
        self._write_roles_and_skills_without_commit(
            role_id=role.id, list_of_skill_ids=skill_ids_required
        )

    def _write_roles_and_skills_without_commit(
        self, role_id, list_of_skill_ids: List[str]
    ):
        ## no commit or closed done inside above

        self.cursor.execute(
            "DELETE FROM %s WHERE %s=%d" % (ROLES_SKILLS_TABLE, ROLE_ID, int(role_id))
        )

        for skill_id in list_of_skill_ids:
            insertion = "INSERT INTO %s (%s, %s) VALUES (?,?)" % (
                ROLES_SKILLS_TABLE,
                ROLE_ID,
                SKILL_ID,
            )

            self.cursor.execute(insertion, (int(role_id), int(skill_id)))

    def delete_table(self):
        self.conn.execute("DROP TABLE %s" % ROLES_TABLE)
        self.conn.execute("DROP TABLE %s" % ROLES_SKILLS_TABLE)
        self.conn.commit()
        self.close()

    def create_table(self):
        table_creation_query = """
                CREATE TABLE %s (
                    %s STR, 
                    %s INTEGER,
                    %s INTEGER,
                    %s INTEGER,
                    %s INTEGER,
                    %s INTEGER
                );
            """ % (
            ROLES_TABLE,
            ROLE_NAME,
            HIDDEN,
            PROTECTED,
            ASSOCIATE_SAILING_GROUP,
            ROLE_ID,
            ROLE_ORDER,
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (
            INDEX_ROLES_TABLE,
            ROLES_TABLE,
            ROLE_ID,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self._create_role_skill_id_mapping_table()

            self.conn.commit()

        except Exception as e1:
            raise Exception("Error %s when creating roles and skills table" % str(e1))
        finally:
            self.close()

    def _create_role_skill_id_mapping_table(self):
        table_creation_query = """
                CREATE TABLE %s (
                    %s INTEGER,
                    %s INTEGER
                );
            """ % (
            ROLES_SKILLS_TABLE,
            ROLE_ID,
            SKILL_ID,
        )

        index_creation_query = "CREATE INDEX %s ON %s (%s)" % (
            INDEX_ROLES_SKILLS_TABLE,
            ROLES_SKILLS_TABLE,
            ROLE_ID,
        )

        self.cursor.execute(table_creation_query)
        self.cursor.execute(index_creation_query)
