from app.objects.food import ListOfVolunteersWithFoodRequirementsAtEvent, VolunteerWithFoodRequirementsAtEvent, \
    FoodRequirements
from app.data_access.sql.generic_sql_data import GenericSqlData, bool2int, int2bool
from app.data_access.sql.shared_column_names import *

VOLUNTEER_FOOD_REQUIRED_TABLE = "volunteer_food_required"
INDEX_VOLUNTEER_FOOD_REQUIRED_TABLE = "index_volunteer_food_required"

class SqlDataListOfVolunteersWithFoodRequirementsAtEvent(
    GenericSqlData
):
    def read(self, event_id: str) -> ListOfVolunteersWithFoodRequirementsAtEvent:
        if self.table_does_not_exist(VOLUNTEER_FOOD_REQUIRED_TABLE):
            return ListOfVolunteersWithFoodRequirementsAtEvent.create_empty()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s,%s,%s  FROM %s WHERE %s='%s' ''' % (
                VOLUNTEER_ID,
                FOOD_REQUIRED_KEY,
                FOOD_REQUIRED_BOOL_VALUE,
                FOOD_REQUIRED_VALUE,

            VOLUNTEER_FOOD_REQUIRED_TABLE,

            EVENT_ID,
            int(event_id)))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteer food at event" % str(e1))
        finally:
            self.close()

        new_dict = {}
        for raw_item in raw_list:
            volunteer_id=str(raw_item[0])
            food_required_key = raw_item[1]
            food_required_bool_vale = int2bool(raw_item[2])
            food_required_text_vale = raw_item[3]
            food_requirements_this_volunteer = new_dict.get(volunteer_id, VolunteerWithFoodRequirementsAtEvent(
                volunteer_id=volunteer_id,
                food_requirements=FoodRequirements()
            ))

            if food_required_key==OTHER_KEY:
                food_requirements_this_volunteer.food_requirements.other = food_required_text_vale
            else:
                setattr(food_requirements_this_volunteer.food_requirements, food_required_key, food_required_bool_vale)

            new_dict[volunteer_id] = food_requirements_this_volunteer

        return ListOfVolunteersWithFoodRequirementsAtEvent(list(new_dict.values()))


    def write(
        self,
        list_of_volunteers_with_food: ListOfVolunteersWithFoodRequirementsAtEvent,
        event_id: str,
    ):
        try:
            if self.table_does_not_exist(VOLUNTEER_FOOD_REQUIRED_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (VOLUNTEER_FOOD_REQUIRED_TABLE,
                                                                  EVENT_ID,
                                                                  int(event_id)))

            for volunteer_with_food in list_of_volunteers_with_food:
                volunteer_id = int(volunteer_with_food.volunteer_id)
                food_required = volunteer_with_food.food_requirements
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
                        VOLUNTEER_FOOD_REQUIRED_TABLE,
                        EVENT_ID,
                        VOLUNTEER_ID,
                        FOOD_REQUIRED_KEY,
                        FOOD_REQUIRED_BOOL_VALUE,
                        FOOD_REQUIRED_VALUE
                    )

                    self.cursor.execute(insertion, (
                        int(event_id),
                        volunteer_id,
                        key,
                        bool_value,
                        text_value
                    ))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing food at event" % str(e1))
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
                    """ % (VOLUNTEER_FOOD_REQUIRED_TABLE,
                           EVENT_ID,
                           VOLUNTEER_ID,
                           FOOD_REQUIRED_KEY,
                           FOOD_REQUIRED_BOOL_VALUE,
                           FOOD_REQUIRED_VALUE)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (INDEX_VOLUNTEER_FOOD_REQUIRED_TABLE,
                                                                              VOLUNTEER_FOOD_REQUIRED_TABLE,
                                                                              EVENT_ID,
                                                                              VOLUNTEER_ID,
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
