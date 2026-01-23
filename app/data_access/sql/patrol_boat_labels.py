from app.data_access.sql.shared_column_names import *
from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.day_selectors import Day

PATROL_BOATS_LABELS_TABLE = "patrol_boats_labels_table"
INDEX_PATROL_BOATS_LABELS_TABLE = "index_patrol_boats_labels_table"

from app.objects.patrol_boats import ListOfPatrolBoatLabelsAtEvents, PatrolBoatLabelAtEvent


class SqlDataListOfPatrolBoatLabelsAtEvent(
    GenericSqlData
):
    def read(self) -> ListOfPatrolBoatLabelsAtEvents:
        if self.table_does_not_exist(PATROL_BOATS_LABELS_TABLE):
            return PatrolBoatLabelAtEvent.create_empty()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s  FROM %s  ''' % (
                EVENT_ID, PATROL_BOAT_ID, DAY, PATROL_BOAT_LABEL,
                PATROL_BOATS_LABELS_TABLE))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading patrol boat labels at event" % str(e1))
        finally:
            self.close()

        new_list = [
            PatrolBoatLabelAtEvent(
                event_id=str(raw_item[0]),
                boat_id=str(raw_item[1]),
                day=Day[raw_item[2]],
                label=str(raw_item[3])
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
                event_id = int(boat_label.event_id)
                day= boat_label.day.name
                boat_id = int(boat_label.boat_id)
                label = str(boat_label.label)

                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                    PATROL_BOATS_LABELS_TABLE,
                    EVENT_ID, PATROL_BOAT_ID, DAY, PATROL_BOAT_LABEL)

                self.cursor.execute(insertion, (
                    event_id, boat_id, day, label))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing volunteers on patrol boats at event" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
                CREATE TABLE %s (
                    %s INTEGER, 
                    %s INTEGER,
                    %s INTEGER,
                    %s STR
                );
            """ % (PATROL_BOATS_LABELS_TABLE,
                   EVENT_ID,  PATROL_BOAT_ID, DAY, PATROL_BOAT_LABEL)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (INDEX_PATROL_BOATS_LABELS_TABLE,
            PATROL_BOATS_LABELS_TABLE,
                                                                              EVENT_ID, PATROL_BOAT_ID, DAY)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()

        except Exception as e1:
            raise Exception("Error %s when creating patrol boats at event table" % str(e1))
        finally:
            self.close()

