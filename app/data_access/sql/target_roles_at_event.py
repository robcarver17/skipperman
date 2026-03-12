from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.composed.dict_of_volunteer_role_targets import DictOfTargetsForRolesAtEvent
from app.objects.composed.volunteer_roles import ListOfRolesWithSkills
from app.objects.volunteer_role_targets import (
    ListOfTargetForRoleWithIdAtEvent,
    TargetForRoleWithIdAtEvent,
)
from app.data_access.sql.shared_column_names import *

VOLUNTEER_TARGETS_AT_EVENT_TABLE = "volunteer_targets_at_event"
INDEX_VOLUNTEER_TARGETS_AT_EVENT_TABLE = "index_volunteer_targets_at_event"


class SqlDataListOfTargetForRoleAtEvent(GenericSqlData):
    def update_volunteer_target(self, event_id: str, role_id: str, target: int):
        if self.role_already_has_target(event_id=event_id, role_id=role_id):
            self._update_volunteer_target_without_checks(
                event_id=event_id, role_id=role_id, target=target
            )
        else:
            self._add_new_volunteer_target(
                event_id=event_id, role_id=role_id, target=target
            )

    def role_already_has_target(self, event_id: str, role_id: str):
        if self.table_does_not_exist(VOLUNTEER_TARGETS_AT_EVENT_TABLE):
            return False

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT * FROM %s WHERE %s=%d AND %s=%d """
                % (
                    VOLUNTEER_TARGETS_AT_EVENT_TABLE,
                    ROLE_ID,
                    int(role_id),
                    EVENT_ID,
                    int(event_id),
                )
            )

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception(
                "Error %s when reading volunteer targets at event" % str(e1)
            )
        finally:
            self.close()

        return len(raw_list) > 0

    def _update_volunteer_target_without_checks(
        self, event_id: str, role_id: str, target: int
    ):
        try:
            if self.table_does_not_exist(VOLUNTEER_TARGETS_AT_EVENT_TABLE):
                raise Exception("Can't update target if doesn't exist")

            insertion = "UPDATE %s SET %s=%d WHERE %s=%d AND %s=%d" % (
                VOLUNTEER_TARGETS_AT_EVENT_TABLE,
                VOLUNTEER_TARGET_NUMBER,
                int(target),
                EVENT_ID,
                int(event_id),
                ROLE_ID,
                int(role_id),
            )

            self.cursor.execute(insertion, (int(event_id), role_id, target))
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing volunteer targets at event" % str(e1)
            )
        finally:
            self.close()

    def _add_new_volunteer_target(self, event_id: str, role_id: str, target: int):
        try:
            if self.table_does_not_exist(VOLUNTEER_TARGETS_AT_EVENT_TABLE):
                self.create_table()

            self._add_target_without_commits_or_checks(
                event_id=event_id,
                target_with_role=TargetForRoleWithIdAtEvent(
                    role_id=role_id, target=target
                ),
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing volunteer targets at event" % str(e1)
            )
        finally:
            self.close()

    def get_dict_of_targets_for_roles_at_event(self, event_id: str) -> DictOfTargetsForRolesAtEvent:
        raw_list = self.read(event_id)
        new_dict =dict([(self.list_of_roles_with_skills.role_with_id(raw_item.role_id), raw_item.target) for raw_item in raw_list])

        return DictOfTargetsForRolesAtEvent(new_dict)

    @property
    def list_of_roles_with_skills(self) -> ListOfRolesWithSkills:
        return self.object_store.get(
            self.object_store.data_api.data_list_of_roles.read_list_of_roles_with_skills
        )

    def read(self, event_id: str) -> ListOfTargetForRoleWithIdAtEvent:
        if self.table_does_not_exist(VOLUNTEER_TARGETS_AT_EVENT_TABLE):
            return ListOfTargetForRoleWithIdAtEvent.create_empty()

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s  FROM %s WHERE %s=%d """
                % (
                    ROLE_ID,
                    VOLUNTEER_TARGET_NUMBER,
                    VOLUNTEER_TARGETS_AT_EVENT_TABLE,
                    EVENT_ID,
                    int(event_id),
                )
            )

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception(
                "Error %s when reading volunteer targets at event" % str(e1)
            )
        finally:
            self.close()

        new_list = [
            TargetForRoleWithIdAtEvent(role_id=str(item[0]), target=int(item[1]))
            for item in raw_list
        ]

        return ListOfTargetForRoleWithIdAtEvent(new_list)

    def write(
        self,
        list_of_targets_for_roles_at_event: ListOfTargetForRoleWithIdAtEvent,
        event_id: str,
    ):
        try:
            if self.table_does_not_exist(VOLUNTEER_TARGETS_AT_EVENT_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute(
                "DELETE FROM %s WHERE %s=%d"
                % (VOLUNTEER_TARGETS_AT_EVENT_TABLE, EVENT_ID, int(event_id))
            )

            for target_with_role in list_of_targets_for_roles_at_event:
                self._add_target_without_commits_or_checks(
                    event_id=event_id, target_with_role=target_with_role
                )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing volunteer targets at event" % str(e1)
            )
        finally:
            self.close()

    def _add_target_without_commits_or_checks(
        self, event_id: str, target_with_role: TargetForRoleWithIdAtEvent
    ):
        role_id = int(target_with_role.role_id)
        target = int(target_with_role.target)

        insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?,?,?)" % (
            VOLUNTEER_TARGETS_AT_EVENT_TABLE,
            EVENT_ID,
            ROLE_ID,
            VOLUNTEER_TARGET_NUMBER,
        )

        self.cursor.execute(insertion, (int(event_id), role_id, target))

    def create_table(self):
        # name: str
        # hidden: bool
        # id: str = arg_not_passed

        table_creation_query = """
                CREATE TABLE %s (
                    %s INTEGER, 
                    %s INTEGER, 
                    %s INTEGER
                );
            """ % (
            VOLUNTEER_TARGETS_AT_EVENT_TABLE,
            EVENT_ID,
            ROLE_ID,
            VOLUNTEER_TARGET_NUMBER,
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s)" % (
            INDEX_VOLUNTEER_TARGETS_AT_EVENT_TABLE,
            VOLUNTEER_TARGETS_AT_EVENT_TABLE,
            EVENT_ID,
            ROLE_ID,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating volunteer target table" % str(e1))
        finally:
            self.close()
