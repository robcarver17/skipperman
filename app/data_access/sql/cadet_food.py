from app.data_access.sql.cadets import SqlDataListOfCadets
from app.data_access.sql.generic_sql_data import GenericSqlData, bool2int, int2bool
from app.data_access.sql.shared_column_names import *
from app.objects.cadets import ListOfCadets
from app.objects.composed.food_at_event import DictOfCadetsWithFoodRequirementsAtEvent

from app.objects.food import ListOfCadetsWithFoodRequirementsAtEvent, CadetWithFoodRequirementsAtEvent, FoodRequirements

CADET_FOOD_REQUIRED_TABLE = "cadet_food_requirements"
INDEX_CADET_FOOD_REQUIRED_TABLE = "index_cadet_food_requirements"


class SqlDataListOfCadetsWithFoodRequirementsAtEvent(
    GenericSqlData
):
    def is_cadet_with_already_at_event_with_food(
            self, event_id: str, cadet_id: str
    ) -> bool:
        if self.table_does_not_exist(CADET_FOOD_REQUIRED_TABLE):
            return False

        try:
            cursor = self.cursor
            cursor.execute('''SELECT *  FROM %s WHERE %s='%s' AND %s='%s' ''' % (
            CADET_FOOD_REQUIRED_TABLE,
            CADET_ID,
            int(cadet_id),
            EVENT_ID,
            int(event_id)))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadet food at event" % str(e1))
        finally:
            self.close()

        return len(raw_list)>0

    def add_new_cadet_with_food_to_event(
            self, event_id: str, cadet_id: str,
        food_requirements: FoodRequirements,
    ):
        if self.is_cadet_with_already_at_event_with_food(event_id=event_id, cadet_id=cadet_id):
            raise Exception("Can't write food for cadet already at event with food")

        try:
            if self.table_does_not_exist(CADET_FOOD_REQUIRED_TABLE):
                self.create_table()

            self.write_cadet_with_food_without_committing(
                cadet_with_food=CadetWithFoodRequirementsAtEvent(
                cadet_id=cadet_id,
                food_requirements=food_requirements
            ), event_id=event_id)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing cadet food at event" % str(e1))
        finally:
            self.close()



    def remove_food_requirements_for_cadet_at_event(
            self, event_id: str, cadet_id: str,
    ):
        try:
            if self.table_does_not_exist(CADET_FOOD_REQUIRED_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s' AND %s='%s'" % (CADET_FOOD_REQUIRED_TABLE,
                                                                  EVENT_ID,
                                                                  int(event_id),
                                                                    CADET_ID,
                                                                    int(cadet_id)))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing cadet food at event" % str(e1))
        finally:
            self.close()

    def update_cadet_food_data(
            self, event_id: str, cadet_id: str,            new_food_requirements: FoodRequirements,
    ):
        self.remove_food_requirements_for_cadet_at_event(cadet_id=cadet_id,
                                                         event_id=event_id)
        self.add_new_cadet_with_food_to_event(event_id=event_id,
                                               cadet_id=cadet_id,
                                              food_requirements=new_food_requirements
                                              )

    def get_dict_of_cadets_with_food_requirements_at_event(
            self, event_id: str
    ) -> DictOfCadetsWithFoodRequirementsAtEvent:
        raw_list = self.read(event_id)
        return DictOfCadetsWithFoodRequirementsAtEvent(
            [
                (self.list_of_cadets.cadet_with_id(raw_item.cadet_id),
                 raw_item.food_requirements)
                for raw_item in raw_list
            ]
        )

    @property
    def list_of_cadets(self) -> ListOfCadets:
        list_of_cadets = getattr(self, "_list_of_cadets", None)
        if list_of_cadets is None:
            list_of_cadets = self._list_of_cadets = SqlDataListOfCadets(self.db_connection).read()

        return list_of_cadets

    def read(self, event_id: str) -> ListOfCadetsWithFoodRequirementsAtEvent:
        if self.table_does_not_exist(CADET_FOOD_REQUIRED_TABLE):
            return ListOfCadetsWithFoodRequirementsAtEvent.create_empty()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s,%s,%s  FROM %s WHERE %s='%s' ''' % (
                CADET_ID,
                FOOD_REQUIRED_KEY,
                FOOD_REQUIRED_BOOL_VALUE,
                FOOD_REQUIRED_VALUE,

            CADET_FOOD_REQUIRED_TABLE,

            EVENT_ID,
            int(event_id)))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteer targets at event" % str(e1))
        finally:
            self.close()

        new_dict = {}
        for raw_item in raw_list:
            cadet_id=str(raw_item[0])
            food_required_key = raw_item[1]
            food_required_bool_vale = int2bool(raw_item[2])
            food_required_text_vale = raw_item[3]
            food_requirements_this_cadet = new_dict.get(cadet_id, CadetWithFoodRequirementsAtEvent(
                cadet_id=cadet_id,
                food_requirements=FoodRequirements()
            ))

            if food_required_key==OTHER_KEY:

                food_requirements_this_cadet.food_requirements.other = food_required_text_vale
            else:
                setattr(food_requirements_this_cadet.food_requirements, food_required_key, food_required_bool_vale)

            new_dict[cadet_id] = food_requirements_this_cadet

        return ListOfCadetsWithFoodRequirementsAtEvent(list(new_dict.values()))

    def write(
        self,
        list_of_cadets_with_food: ListOfCadetsWithFoodRequirementsAtEvent,
        event_id: str,
    ):
        try:
            if self.table_does_not_exist(CADET_FOOD_REQUIRED_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (CADET_FOOD_REQUIRED_TABLE,
                                                                  EVENT_ID,
                                                                  int(event_id)))

            for cadet_with_food in list_of_cadets_with_food:
                self.write_cadet_with_food_without_committing(cadet_with_food=cadet_with_food, event_id=event_id)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing cadet food at event" % str(e1))
        finally:
            self.close()

    def write_cadet_with_food_without_committing(self, event_id: str, cadet_with_food: CadetWithFoodRequirementsAtEvent):
        cadet_id = int(cadet_with_food.cadet_id)
        food_required = cadet_with_food.food_requirements
        other_value = food_required.other
        as_dict_not_other = food_required.as_dict_except_other_field()
        as_dict_not_other[OTHER_KEY] = other_value

        for key, value in as_dict_not_other.items():
            if key == OTHER_KEY:
                bool_value = 0
                text_value = value
            else:
                bool_value = bool2int(value)
                text_value = ""

            insertion = "INSERT INTO %s (%s, %s, %s, %s, %s) VALUES (?,?,?,?,?)" % (
                CADET_FOOD_REQUIRED_TABLE,
                EVENT_ID,
                CADET_ID,
                FOOD_REQUIRED_KEY,
                FOOD_REQUIRED_BOOL_VALUE,
                FOOD_REQUIRED_VALUE
            )

            self.cursor.execute(insertion, (
                int(event_id),
                cadet_id,
                key,
                bool_value,
                text_value
            ))

    def create_table(self):

        # name: str
        # hidden: bool
        # id: str = arg_not_passed

        table_creation_query = """
                CREATE TABLE %s (
                    %s INTEGER, 
                    %s INTEGER, 
                    %s STR, 
                    %s INTEGER,
                    %s STR
                    
                );
            """ % (CADET_FOOD_REQUIRED_TABLE,
                   EVENT_ID,
                   CADET_ID,
                   FOOD_REQUIRED_KEY,
                   FOOD_REQUIRED_BOOL_VALUE,
                   FOOD_REQUIRED_VALUE)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (INDEX_CADET_FOOD_REQUIRED_TABLE,
                                                                          CADET_FOOD_REQUIRED_TABLE,
                                                                          EVENT_ID,
                                                                          CADET_ID,
                                                                          FOOD_REQUIRED_KEY)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating food required table" % str(e1))
        finally:
            self.close()

OTHER_KEY = "other_food_field"