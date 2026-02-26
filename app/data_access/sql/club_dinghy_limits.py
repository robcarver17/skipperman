from typing import List, Dict

from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.club_dinghies import (
    ListOfClubDinghyLimits,
    ClubDinghyWithLimitAtEvent,
    OLD_event_id_for_generic_limit,
    event_id_for_generic_limit,
    ClubDinghyAndGenericLimit,
    ListOfClubDinghies,
    ClubDinghy,
)
from app.objects.utilities.exceptions import missing_data, MultipleMatches

CLUB_DINGHY_LIMIT_TABLE = "club_dinghy_limits"
INDEX_CLUB_DINGHY_LIMIT_TABLE = "index_club_dinghy_limits"


class SqlDataListOfClubDinghyLimits(GenericSqlData):
    def get_list_of_boats_and_generic_limits(
        self,
    ) -> List[ClubDinghyAndGenericLimit]:
        dict_of_club_boats_and_generic_limits = (
            self.get_dict_of_club_boats_and_limits_at_event(event_id_for_generic_limit)
        )

        new_list = [
            ClubDinghyAndGenericLimit(
                club_dinghy=boat,
                limit=dict_of_club_boats_and_generic_limits.get(boat, 0),
            )
            for boat in self.club_boats
        ]

        return new_list

    def get_dict_of_names_and_limits_for_all_visible_club_boats_at_event(
        self, event_id: str
    ) -> Dict[str, int]:
        dict_of_club_boats_and_limits_at_event = (
            self.get_dict_of_club_boats_and_limits_at_event(event_id)
        )
        generic_dict_of_club_boats_and_limits = (
            self.get_dict_of_club_boats_and_limits_at_event(event_id_for_generic_limit)
        )

        visible_boats = self.visible_club_boats

        new_dict = dict(
            [
                (
                    boat.name,
                    dict_of_club_boats_and_limits_at_event.get(
                        boat, generic_dict_of_club_boats_and_limits.get(boat, 0)
                    ),
                )
                for boat in visible_boats
            ]
        )

        return new_dict

    def get_dict_of_club_boats_and_limits_at_event(
        self, event_id: str
    ) -> Dict[ClubDinghy, int]:
        raw_limits = self.get_list_of_club_boats_and_limits_at_event(event_id=event_id)
        new_dict = dict(
            [
                (
                    self.club_boats.club_dinghy_with_id(
                        raw_boat_and_limit.club_dinghy_id
                    ),
                    raw_boat_and_limit.limit,
                )
                for raw_boat_and_limit in raw_limits
            ]
        )

        return new_dict

    def get_list_of_club_boats_and_limits_at_event(
        self, event_id: str
    ) -> ListOfClubDinghyLimits:
        try:
            if self.table_does_not_exist(CLUB_DINGHY_LIMIT_TABLE):
                return ListOfClubDinghyLimits.create_empty()

            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s FROM %s WHERE %s=%d """
                % (
                    DINGHY_ID,
                    CLUB_DINGHY_LIMIT,
                    CLUB_DINGHY_LIMIT_TABLE,
                    EVENT_ID,
                    int(event_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception(
                "Error %s when reading dinghy limits table at event" % str(e1)
            )
        finally:
            self.close()

        new_list = [
            ClubDinghyWithLimitAtEvent(
                event_id=event_id,
                club_dinghy_id=str(raw_item[0]),
                limit=int(raw_item[1]),
            )
            for raw_item in raw_list
        ]

        return ListOfClubDinghyLimits(new_list)

    @property
    def club_boats(self) -> ListOfClubDinghies:
        list_of_club_dinghies = self.object_store.get(
            self.object_store.data_api.data_List_of_club_dinghies.read
        )

        return list_of_club_dinghies

    @property
    def visible_club_boats(self) -> ListOfClubDinghies:
        list_of_club_dinghies = self.object_store.get(
            self.object_store.data_api.data_List_of_club_dinghies.get_list_of_visible_club_dinghies
        )

        return list_of_club_dinghies

    def clear_and_set_generic_limit(self, club_dinghy_id: str, new_limit: int):
        self.update_limit_for_club_dinghy_at_event(
            event_id=event_id_for_generic_limit,
            club_dinghy_id=club_dinghy_id,
            new_limit=new_limit,
        )

    def add_generic_limit_for_club_dinghy(self, club_dinghy_id: str):
        self.update_limit_for_club_dinghy_at_event(
            club_dinghy_id=club_dinghy_id,
            event_id=event_id_for_generic_limit,
            new_limit=0,
        )

    def _add_limit_for_club_dinghy_without_checks(
        self, event_id: str, club_dinghy_id: str, limit: int
    ):
        event_id = event_id_for_generic_limit
        try:
            if self.table_does_not_exist(CLUB_DINGHY_LIMIT_TABLE):
                self.create_table()

            self._add_row_without_checks_or_commits(
                ClubDinghyWithLimitAtEvent(
                    event_id=event_id, club_dinghy_id=club_dinghy_id, limit=limit
                )
            )

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to dinghy limits table event" % str(e1)
            )
        finally:
            self.close()

    def update_limit_for_club_dinghy_at_event(
        self, event_id: str, club_dinghy_id: str, new_limit: int
    ):
        if self.does_limit_already_exist(
            event_id=event_id, club_dinghy_id=club_dinghy_id
        ):
            self._update_limit_for_club_dinghy_at_event_without_checks(
                event_id=event_id, club_dinghy_id=club_dinghy_id, new_limit=new_limit
            )
        else:
            self._add_limit_for_club_dinghy_without_checks(
                event_id=event_id, club_dinghy_id=club_dinghy_id, limit=new_limit
            )

    def _update_limit_for_club_dinghy_at_event_without_checks(
        self, event_id: str, club_dinghy_id: str, new_limit: int
    ):
        try:
            if self.table_does_not_exist(CLUB_DINGHY_LIMIT_TABLE):
                raise Exception("table undefined")

            update = "UPDATE %s SET %s=%d WHERE %s=%d AND %s=%d" % (
                CLUB_DINGHY_LIMIT_TABLE,
                CLUB_DINGHY_LIMIT,
                int(new_limit),
                EVENT_ID,
                int(event_id),
                DINGHY_ID,
                int(club_dinghy_id),
            )
            self.cursor.execute(update)

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to dinghy limits table event" % str(e1)
            )
        finally:
            self.close()

    def does_limit_already_exist(self, event_id: str, club_dinghy_id: str):
        existing_limit = self.get_limit_for_event_and_dinghy(
            event_id=event_id, club_dinghy_id=club_dinghy_id, default=missing_data
        )
        if existing_limit is missing_data:
            return False

        return True

    def get_limit_for_event_and_dinghy(
        self, event_id: str, club_dinghy_id: str, default=missing_data
    ):
        try:
            if self.table_does_not_exist(CLUB_DINGHY_LIMIT_TABLE):
                return default

            cursor = self.cursor
            cursor.execute(
                """SELECT  %s FROM %s  WHERE %s=%d AND %s=%d """
                % (
                    CLUB_DINGHY_LIMIT,
                    CLUB_DINGHY_LIMIT_TABLE,
                    EVENT_ID,
                    int(event_id),
                    DINGHY_ID,
                    int(club_dinghy_id),
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception(
                "Error %s when reading dinghy limits table at event" % str(e1)
            )
        finally:
            self.close()

        if len(raw_list) == 0:
            return default
        elif len(raw_list) > 1:
            raise MultipleMatches

        return int(raw_list[0][0])

    def read(self) -> ListOfClubDinghyLimits:
        try:
            if self.table_does_not_exist(CLUB_DINGHY_LIMIT_TABLE):
                return ListOfClubDinghyLimits.create_empty()

            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s, %s FROM %s """
                % (EVENT_ID, DINGHY_ID, CLUB_DINGHY_LIMIT, CLUB_DINGHY_LIMIT_TABLE)
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception(
                "Error %s when reading dinghy limits table at event" % str(e1)
            )
        finally:
            self.close()

        new_list = [
            ClubDinghyWithLimitAtEvent(
                event_id=str(raw_item[0]),
                club_dinghy_id=str(raw_item[1]),
                limit=int(raw_item[2]),
            )
            for raw_item in raw_list
        ]

        return ListOfClubDinghyLimits(new_list)

    def write(self, list_of_boats: ListOfClubDinghyLimits):
        try:
            if self.table_does_not_exist(CLUB_DINGHY_LIMIT_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (CLUB_DINGHY_LIMIT_TABLE))

            for limit_for_boat_at_event in list_of_boats:
                self._add_row_without_checks_or_commits(limit_for_boat_at_event)

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to dinghy limits table event" % str(e1)
            )
        finally:
            self.close()

    def _add_row_without_checks_or_commits(
        self, limit_for_boat_at_event: ClubDinghyWithLimitAtEvent
    ):
        club_dinghy_id = int(limit_for_boat_at_event.club_dinghy_id)
        limit = int(limit_for_boat_at_event.limit)
        event_id = int(limit_for_boat_at_event.event_id)

        insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?, ?,?)" % (
            CLUB_DINGHY_LIMIT_TABLE,
            EVENT_ID,
            DINGHY_ID,
            CLUB_DINGHY_LIMIT,
        )
        self.cursor.execute(insertion, (event_id, club_dinghy_id, limit))

    def _transfer(self, list_of_boats: ListOfClubDinghyLimits):
        try:
            if self.table_does_not_exist(CLUB_DINGHY_LIMIT_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (CLUB_DINGHY_LIMIT_TABLE))

            for limit_for_boat_at_event in list_of_boats:
                club_dinghy_id = int(limit_for_boat_at_event.club_dinghy_id)
                limit = int(limit_for_boat_at_event.limit)
                event_id = limit_for_boat_at_event.event_id

                if club_dinghy_id > 9:
                    continue
                elif club_dinghy_id < 0:
                    continue

                ## FIXME OLD DATA CAN REMOVE
                if event_id == OLD_event_id_for_generic_limit:
                    event_id = int(event_id_for_generic_limit)
                else:
                    event_id = int(event_id)

                insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?, ?,?)" % (
                    CLUB_DINGHY_LIMIT_TABLE,
                    EVENT_ID,
                    DINGHY_ID,
                    CLUB_DINGHY_LIMIT,
                )
                self.cursor.execute(insertion, (event_id, club_dinghy_id, limit))

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to dinghy limits table event" % str(e1)
            )
        finally:
            self.close()

    def create_table(self):
        table_creation_query = """
                            CREATE TABLE %s (
                                %s INT, 
                                %s INT,
                                %s INT
                            );
                        """ % (
            CLUB_DINGHY_LIMIT_TABLE,
            EVENT_ID,
            DINGHY_ID,
            CLUB_DINGHY_LIMIT,
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s,  %s)" % (
            INDEX_CLUB_DINGHY_LIMIT_TABLE,
            CLUB_DINGHY_LIMIT_TABLE,
            EVENT_ID,
            DINGHY_ID,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when creating club dinghy limits at event table" % str(e1)
            )
        finally:
            self.close()
