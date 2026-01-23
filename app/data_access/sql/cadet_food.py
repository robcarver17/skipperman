from app.data_access.sql.generic_sql_data import GenericSqlData, bool2int, int2bool
from app.data_access.sql.shared_column_names import *

from app.objects.food import ListOfCadetsWithFoodRequirementsAtEvent, CadetWithFoodRequirementsAtEvent, FoodRequirements

CADET_FOOD_REQUIRED_TABLE = "cadet_food_requirements"
INDEX_CADET_FOOD_REQUIRED_TABLE = "index_cadet_food_requirements"


class SqlDataListOfCadetsWithFoodRequirementsAtEvent(
    GenericSqlData
):
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
                cadet_id = int(cadet_with_food.cadet_id)
                food_required = cadet_with_food.food_requirements
                other_value = food_required.other
                as_dict_not_other =  food_required.as_dict_except_other_field()
                as_dict_not_other[OTHER_KEY] = other_value

                for key, value in as_dict_not_other.items():
                    if key == OTHER_KEY:
                        bool_value = 0
                        text_value = value
                    else:
                        bool_value = bool2int(value)
                        text_value=""


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

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing cadet food at event" % str(e1))
        finally:
            self.close()

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