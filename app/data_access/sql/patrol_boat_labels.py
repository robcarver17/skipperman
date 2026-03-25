from typing import List

from app.data_access.sql.shared_column_names import *
from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.composed.volunteers_at_event_with_patrol_boats import (
    DictOfLabelsForEvent,
)
from app.objects.day_selectors import Day

PATROL_BOATS_LABELS_TABLE = "patrol_boats_labels_table"
INDEX_PATROL_BOATS_LABELS_TABLE = "index_patrol_boats_labels_table"

from app.objects.patrol_boats import (
    ListOfPatrolBoatLabelsAtEvents,
    PatrolBoatLabelAtEvent,
    ListOfPatrolBoats,
)


class SqlDataListOfPatrolBoatLabelsAtEvent(GenericSqlData):
    def get_dict_of_patrol_boat_labels_for_event(
        self, event_id: str
    ) -> DictOfLabelsForEvent:
        raw_list = self.read_for_event(event_id)
        list_of_patrol_boats = self.list_of_patrol_boats

        return DictOfLabelsForEvent.from_list_of_patrol_boat_labels_with_ids_for_event(
            list_of_patrol_boat_labels_with_ids=raw_list,
            list_of_patrol_boats=list_of_patrol_boats,
        )

    @property
    def list_of_patrol_boats(self) -> ListOfPatrolBoats:
        return self.object_store.get(
            self.object_store.data_api.data_list_of_patrol_boats.read
        )

    def update_patrol_boat_label_at_event(
        self, event_id: str, patrol_boat_id: str, label: str, day: Day
    ):
        if self.is_an_existing_patrol_boat_label_at_event(
            event_id=event_id, patrol_boat_id=patrol_boat_id, day=day
        ):
            self._modify_existing_patrol_boat_label_at_event_without_checks(
                event_id=event_id, patrol_boat_id=patrol_boat_id, day=day, label=label
            )
        else:
            self._add_patrol_boat_label_at_event_without_checks(
                event_id=event_id, patrol_boat_id=patrol_boat_id, day=day, label=label
            )

    def is_an_existing_patrol_boat_label_at_event(
        self, event_id: str, patrol_boat_id: str, day: Day
    ):
        if self.table_does_not_exist(PATROL_BOATS_LABELS_TABLE):
            return False

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT * FROM %s WHERE %s=%d AND %s=%d AND %s='%s' """
                % (
                    PATROL_BOATS_LABELS_TABLE,
                    EVENT_ID,
                    int(event_id),
                    PATROL_BOAT_ID,
                    int(patrol_boat_id),
                    DAY,
                    day.name,
                )
            )

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception(
                "Error %s when reading patrol boat labels at event" % str(e1)
            )
        finally:
            self.close()

        return len(raw_list) > 0

    def _modify_existing_patrol_boat_label_at_event_without_checks(
        self, event_id: str, patrol_boat_id: str, label: str, day: Day
    ):
        try:
            if self.table_does_not_exist(PATROL_BOATS_LABELS_TABLE):
                raise Exception("Can't modify if existing doesn't exist")

            insertion = "UPDATE %s SET %s=? WHERE %s=%d AND %s=%d AND %s='%s' " % (
                PATROL_BOATS_LABELS_TABLE,
                PATROL_BOAT_LABEL,
                EVENT_ID,
                int(event_id),
                PATROL_BOAT_ID,
                int(patrol_boat_id),
                DAY,
                day.name,
            )

            self.cursor.execute(insertion, (label,))

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing volunteers on patrol boats at event" % str(e1)
            )
        finally:
            self.close()

    def _add_patrol_boat_label_at_event_without_checks(
        self, event_id: str, patrol_boat_id: str, label: str, day: Day
    ):
        try:
            if self.table_does_not_exist(PATROL_BOATS_LABELS_TABLE):
                self.create_table()
            boat_label = PatrolBoatLabelAtEvent(
                event_id=event_id, boat_id=patrol_boat_id, day=day, label=label
            )
            self._add_patrol_boat_label_without_checks_or_commits(boat_label)
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing volunteers on patrol boats at event" % str(e1)
            )
        finally:
            self.close()

    def get_list_of_unique_labels(self) -> List[str]:
        return self.read().unique_set_of_labels()

    def read_for_event(self, event_id: str) -> ListOfPatrolBoatLabelsAtEvents:
        if self.table_does_not_exist(PATROL_BOATS_LABELS_TABLE):
            return PatrolBoatLabelAtEvent.create_empty()

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s, %s  FROM %s WHERE %s=%d """
                % (
                    PATROL_BOAT_ID,
                    DAY,
                    PATROL_BOAT_LABEL,
                    PATROL_BOATS_LABELS_TABLE,
                    EVENT_ID,
                    int(event_id),
                )
            )

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception(
                "Error %s when reading patrol boat labels at event" % str(e1)
            )
        finally:
            self.close()

        new_list = [
            PatrolBoatLabelAtEvent(
                event_id=event_id,
                boat_id=str(raw_item[0]),
                day=Day[raw_item[1]],
                label=str(raw_item[2]),
            )
            for raw_item in raw_list
        ]

        return ListOfPatrolBoatLabelsAtEvents(new_list)

    def read(self) -> ListOfPatrolBoatLabelsAtEvents:
        if self.table_does_not_exist(PATROL_BOATS_LABELS_TABLE):
            return PatrolBoatLabelAtEvent.create_empty()

        try:
            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s, %s, %s  FROM %s  """
                % (
                    EVENT_ID,
                    PATROL_BOAT_ID,
                    DAY,
                    PATROL_BOAT_LABEL,
                    PATROL_BOATS_LABELS_TABLE,
                )
            )

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception(
                "Error %s when reading patrol boat labels at event" % str(e1)
            )
        finally:
            self.close()

        new_list = [
            PatrolBoatLabelAtEvent(
                event_id=str(raw_item[0]),
                boat_id=str(raw_item[1]),
                day=Day[raw_item[2]],
                label=str(raw_item[3]),
            )
            for raw_item in raw_list
        ]

        return ListOfPatrolBoatLabelsAtEvents(new_list)

    def write(self, list_of_patrol_boat_labels: ListOfPatrolBoatLabelsAtEvents):
        try:
            if self.table_does_not_exist(PATROL_BOATS_LABELS_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % PATROL_BOATS_LABELS_TABLE)

            for boat_label in list_of_patrol_boat_labels:
                self._add_patrol_boat_label_without_checks_or_commits(boat_label)
            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing volunteers on patrol boats at event" % str(e1)
            )
        finally:
            self.close()

    def _add_patrol_boat_label_without_checks_or_commits(
        self, boat_label: PatrolBoatLabelAtEvent
    ):
        event_id = int(boat_label.event_id)
        day = boat_label.day.name
        boat_id = int(boat_label.boat_id)
        label = str(boat_label.label)

        insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
            PATROL_BOATS_LABELS_TABLE,
            EVENT_ID,
            PATROL_BOAT_ID,
            DAY,
            PATROL_BOAT_LABEL,
        )

        self.cursor.execute(insertion, (event_id, boat_id, day, label))

    def create_table(self):
        table_creation_query = """
                CREATE TABLE %s (
                    %s INTEGER, 
                    %s INTEGER,
                    %s INTEGER,
                    %s STR
                );
            """ % (
            PATROL_BOATS_LABELS_TABLE,
            EVENT_ID,
            PATROL_BOAT_ID,
            DAY,
            PATROL_BOAT_LABEL,
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (
            INDEX_PATROL_BOATS_LABELS_TABLE,
            PATROL_BOATS_LABELS_TABLE,
            EVENT_ID,
            PATROL_BOAT_ID,
            DAY,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()

        except Exception as e1:
            raise Exception(
                "Error %s when creating patrol boats at event table" % str(e1)
            )
        finally:
            self.close()
