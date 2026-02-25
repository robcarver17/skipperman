
from app.data_access.sql.generic_sql_data import GenericSqlData, bool2int, int2bool
from app.data_access.sql.shared_column_names import *
from app.objects.composed.roles_and_teams import DictOfTeamsWithRoles
from app.objects.composed.volunteer_roles import ListOfRolesWithSkills
from app.objects.composed.volunteer_with_group_and_role_at_event import RoleAndGroup, DictOfDaysRolesAndGroups, \
    DictOfDaysRolesAndGroupsAndTeams, \
    RoleAndGroupAndTeam, DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups
from app.objects.day_selectors import Day


from app.objects.volunteer_roles_and_groups_with_id import ListOfVolunteersWithIdInRoleAtEvent, VolunteerWithIdInRoleAtEvent
from app.objects.groups import UNALLOCATED_GROUP_ID
from app.objects.roles_and_teams import NO_ROLE_ALLOCATED_ID

VOLUNTEERS_IN_ROLES_TABLE = "volunteers_in_roles"
INDEX_VOLUNTEERS_IN_ROLES_TABLE = "index_volunteers_in_roles"




class SqlDataListOfVolunteersInRolesAtEvent(
    GenericSqlData
):
    def  update_role_only_at_event_for_volunteer_on_day(
    self,
        event_id:str,
        volunteer_id:str,
        day: Day,
        new_role_id: str,
            allow_replacement: bool,

    ):
        if new_role_id==str(NO_ROLE_ALLOCATED_ID):
            self.delete_role_at_event_for_volunteer_on_day(event_id=event_id, volunteer_id=volunteer_id, day=day)
        elif self.volunteer_already_has_role_on_day(event_id=event_id, volunteer_id=volunteer_id, day=day):
            if allow_replacement:
                self._update_role_at_event_for_volunteer_on_day_without_checks(event_id=event_id, volunteer_id=volunteer_id,
                                                                               day=day,
                                                                                         new_role_id=new_role_id)
        else:
            self._add_role_and_group_at_event_for_volunteer_on_day(event_id=event_id, volunteer_id=volunteer_id, day=day,
                                                                   new_role_id=new_role_id, new_group_id=UNALLOCATED_GROUP_ID)

    def update_role_and_group_at_event_for_volunteer_on_day(
    self,
        event_id:str,
        volunteer_id:str,
        day: Day,
        new_role_id: str,
        new_group_id: str,
            allow_replacement: bool,

    ):
        if new_role_id==str(NO_ROLE_ALLOCATED_ID):
            self.delete_role_at_event_for_volunteer_on_day(event_id=event_id, volunteer_id=volunteer_id, day=day)
        elif self.volunteer_already_has_role_on_day(event_id=event_id, volunteer_id=volunteer_id, day=day):
            if allow_replacement:
                self._update_role_and_group_at_event_for_volunteer_on_day_without_checks(event_id=event_id, volunteer_id=volunteer_id, day=day,
                                                                                         new_role_id=new_role_id, new_group_id=new_group_id)
        else:
            self._add_role_and_group_at_event_for_volunteer_on_day(event_id=event_id, volunteer_id=volunteer_id, day=day,
                                                                                     new_role_id=new_role_id, new_group_id=new_group_id)

    def _update_role_at_event_for_volunteer_on_day_without_checks(
    self,
        event_id:str,
        volunteer_id:str,
        day: Day,
        new_role_id: str,
    ):
        try:
            if self.table_does_not_exist(VOLUNTEERS_IN_ROLES_TABLE):
                return

            self.cursor.execute("UPDATE %s SET %s=%d WHERE %s=%d AND %s=%d AND %s='%s'" % (
                VOLUNTEERS_IN_ROLES_TABLE,
                ROLE_ID, int(new_role_id),
                                                                  EVENT_ID, int(event_id),
                                                                          VOLUNTEER_ID,int(volunteer_id),
                                                                        DAY, day.name
                                                                  ))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to volunteers in roles at event table event# %s" % (str(e1), event_id))
        finally:
            self.close()


    def _update_role_and_group_at_event_for_volunteer_on_day_without_checks(
    self,
        event_id:str,
        volunteer_id:str,
        day: Day,
        new_role_id: str,
        new_group_id: str
    ):
        try:
            if self.table_does_not_exist(VOLUNTEERS_IN_ROLES_TABLE):
                return

            self.cursor.execute("UPDATE %s SET %s=%d AND %s=%d WHERE %s=%d AND %s=%d AND %s='%s'" % (
                VOLUNTEERS_IN_ROLES_TABLE,
                ROLE_ID, int(new_role_id),
                GROUP_ID, int(new_group_id),
                                                                  EVENT_ID, int(event_id),
                                                                          VOLUNTEER_ID,int(volunteer_id),
                                                                        DAY, day.name
                                                                  ))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to volunteers in roles at event table event# %s" % (str(e1), event_id))
        finally:
            self.close()

    def _add_role_and_group_at_event_for_volunteer_on_day(
    self,
        event_id:str,
        volunteer_id:str,
        day: Day,
        new_role_id: str,
        new_group_id: str
    ):
        try:
            if self.table_does_not_exist(VOLUNTEERS_IN_ROLES_TABLE):
                self.create_table()

            self._write_row_of_volunteer_data_without_checks_or_commit(
                event_id=event_id,
                volunteer_in_role=VolunteerWithIdInRoleAtEvent(
                    volunteer_id=volunteer_id,
                    day=day,
                    role_id=new_role_id,
                    group_id=new_group_id
                )
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to volunteers in roles at event table event# %s" % (str(e1), event_id))
        finally:
            self.close()

    def volunteer_already_has_role_on_day(self, event_id:str,
        day: Day,
        volunteer_id: str) -> bool:
        if self.table_does_not_exist(VOLUNTEERS_IN_ROLES_TABLE):
            return False

        try:
            cursor = self.cursor
            cursor.execute('''SELECT * FROM %s WHERE %s=%d AND %s=%d AND %s='%s' ''' % (
                VOLUNTEERS_IN_ROLES_TABLE,
                EVENT_ID, int(event_id),
                VOLUNTEER_ID, int(volunteer_id),
                DAY, day.name
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteers in role at event %s" % (str(e1), event_id))
        finally:
            self.close()

        return len(raw_list)>0

    def delete_role_at_event_for_volunteer_on_day(self,
        event_id:str,
        day: Day,
        volunteer_id: str
    ):
        try:
            if self.table_does_not_exist(VOLUNTEERS_IN_ROLES_TABLE):
                return

            self.cursor.execute("DELETE FROM %s WHERE %s=%d AND %s=%d AND %s='%s'" % (VOLUNTEERS_IN_ROLES_TABLE,
                                                                  EVENT_ID, int(event_id),
                                                                          VOLUNTEER_ID,int(volunteer_id),
                                                                        DAY, day.name
                                                                  ))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to volunteers in roles at event table event# %s" % (str(e1), event_id))
        finally:
            self.close()

    def get_dict_of_volunteers_with_roles_and_groups_at_event(self, event_id: str) -> DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups:
        raw_list = self.read(event_id)
        new_dict = {}
        for raw_item in raw_list:

            volunteer_id = raw_item.volunteer_id
            day = raw_item.day
            group_id = raw_item.group_id
            role_id = raw_item.role_id

            group = self.list_of_groups.group_with_id(group_id)
            raw_role = self.list_of_roles.object_with_id(role_id)
            role_with_skill = self.list_of_roles_with_skills.role_with_id(raw_role.id)
            list_of_team_and_index = self.dict_of_teams_and_roles.list_of_teams_and_index_given_role(role_with_skill)

            role_and_group_and_team = RoleAndGroupAndTeam(
                role=role_with_skill,
                group=group,
                list_of_team_and_index=list_of_team_and_index
            )

            volunteer = self.list_of_volunteers.volunteer_with_id(volunteer_id)

            entry_for_volunteer = new_dict.get(volunteer, DictOfDaysRolesAndGroupsAndTeams())
            entry_for_volunteer[day] = role_and_group_and_team
            new_dict[volunteer] = entry_for_volunteer

        return DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups(new_dict)

    @property
    def list_of_roles_with_skills(self) ->  ListOfRolesWithSkills:
        list_of_roles_with_skills =  self.object_store.get(self.object_store.data_api.data_list_of_roles.read_list_of_roles_with_skills)

        return list_of_roles_with_skills

    @property
    def dict_of_teams_and_roles(self) -> DictOfTeamsWithRoles:
        dict_of_teams_and_roles = self.object_store.get(self.object_store.data_api.data_list_of_teams_and_roles_with_ids.get_dict_of_teams_and_roles)

        return dict_of_teams_and_roles

    @property
    def list_of_volunteers(self):
        list_of_volunteers =self.object_store.get(self.object_store.data_api.data_list_of_volunteers.read)

        return list_of_volunteers

    def get_role_and_groups_for_event_and_volunteer(self, event_id:str,
    volunteer_id:str) -> DictOfDaysRolesAndGroups:
        if self.table_does_not_exist(VOLUNTEERS_IN_ROLES_TABLE):
            return DictOfDaysRolesAndGroups({})

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s WHERE %s=%d AND %s=%d ''' % (
                 DAY,ROLE_ID, GROUP_ID,
                VOLUNTEERS_IN_ROLES_TABLE,
                EVENT_ID, int(event_id),
                VOLUNTEER_ID, int(volunteer_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteers in role at event %s" % (str(e1), event_id))
        finally:
            self.close()

        new_dict = dict(
            [
                (
                    Day[raw_data[0]], RoleAndGroup(
                        role=self.list_of_roles.object_with_id(str(raw_data[1])),
                        group=self.list_of_groups.object_with_id(str(raw_data[2]))
                    ),
                ) for raw_data in raw_list
            ]
        )

        return DictOfDaysRolesAndGroups(new_dict)


    @property
    def list_of_groups(self):
        list_of_groups = self.object_store.get(self.object_store.data_api.data_list_of_groups.read)

        return list_of_groups

    @property
    def list_of_roles(self):
        list_of_roles =  self.object_store.get(self.object_store.data_api.data_list_of_roles.read)

        return list_of_roles


    def read(self, event_id: str) -> ListOfVolunteersWithIdInRoleAtEvent:
        if self.table_does_not_exist(VOLUNTEERS_IN_ROLES_TABLE):
            return ListOfVolunteersWithIdInRoleAtEvent.create_empty()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s FROM %s WHERE %s=%d ''' % (
                VOLUNTEER_ID, DAY, GROUP_ID, ROLE_ID, VOLUNTEERS_IN_ROLES_TABLE, EVENT_ID, int(event_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteers in role at event %s" % (str(e1), event_id))
        finally:
            self.close()

        list_of_volunteers_in_roles = [
            VolunteerWithIdInRoleAtEvent(
                volunteer_id=str(raw_data[0]),
                day = Day[raw_data[1]],
                group_id=str(raw_data[2]),
                role_id=str(raw_data[3])
            )
            for raw_data in raw_list
        ]

        return ListOfVolunteersWithIdInRoleAtEvent(list_of_volunteers_in_roles)


    def write(
        self,
        list_of_volunteers_in_roles_at_event: ListOfVolunteersWithIdInRoleAtEvent,
        event_id: str,
    ):
        try:
            if self.table_does_not_exist(VOLUNTEERS_IN_ROLES_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s=%d" % (VOLUNTEERS_IN_ROLES_TABLE, EVENT_ID, int(event_id)))

            for volunteer_in_role in list_of_volunteers_in_roles_at_event:
                self._write_row_of_volunteer_data_without_checks_or_commit(event_id=event_id, volunteer_in_role=volunteer_in_role)


            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to volunteers in roles at event table event# %s" % (str(e1), event_id))
        finally:
            self.close()

    def _write_row_of_volunteer_data_without_checks_or_commit(self, event_id: str, volunteer_in_role: VolunteerWithIdInRoleAtEvent):
        volunteer_id = int(volunteer_in_role.volunteer_id)
        day = volunteer_in_role.day.name
        group_id = int(volunteer_in_role.group_id)
        role_id = int(volunteer_in_role.role_id)
        insertion = "INSERT INTO %s (%s, %s, %s, %s, %s) VALUES (?, ?,?,?, ?)" % (
            VOLUNTEERS_IN_ROLES_TABLE,
            EVENT_ID,
            VOLUNTEER_ID,
            DAY,
            GROUP_ID,
            ROLE_ID)
        self.cursor.execute(insertion,
                            (int(event_id), volunteer_id, day, group_id, role_id))

    def create_table(self):
        table_creation_query = """
                CREATE TABLE %s (
                    %s INTEGER, 
                    %s INTEGER, 
                    %s STR,
                                        %s INTEGER,
                    %s INTEGER

                );
            """ % (VOLUNTEERS_IN_ROLES_TABLE,
                   EVENT_ID,
                   VOLUNTEER_ID,
                   DAY,
                   GROUP_ID,
                   ROLE_ID
                   )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (INDEX_VOLUNTEERS_IN_ROLES_TABLE,
                                                                          VOLUNTEERS_IN_ROLES_TABLE,
                                                                          EVENT_ID, VOLUNTEER_ID, DAY
                                                                          )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating volunteers in roles table" % str(e1))
        finally:
            self.close()
