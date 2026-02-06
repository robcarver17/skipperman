from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.qualifications import SqlDataListOfQualifications
from app.data_access.sql.shared_column_names import *
from app.data_access.sql.tick_sheet_sub_stages import SqlDataListOfTickSubStages
from app.objects.composed.ticks_in_dicts import QualificationsAndTickItemsAsDict, TickSubStagesAsDict
from app.objects.qualifications import Qualification
from app.objects.substages import ListOfTickSheetItems, TickSheetItem
from app.objects.utilities.exceptions import arg_not_passed, MissingData, MultipleMatches, missing_data

TICK_SHEET_ITEM_TABLE = "tick_sheet_items"
INDEX_TICK_SHEET_ITEM_TABLE = "index_tick_sheet_items"

class SqlDataListOfTickSheetItems(GenericSqlData):
    def add_new_ticklistitem_to_qualification(
        self,
    substage_id: str,
    new_tick_list_name: str,
    ):
        if self.does_ticksheet_item_with_name_exist(tick_list_name=new_tick_list_name, substage_id=substage_id):
            raise Exception("Can't add %s as name already exists in the same substage" % (new_tick_list_name))

        new_tick = TickSheetItem(
            substage_id=substage_id,
            name=new_tick_list_name,
            id=str(self.next_available_id())
        )
        try:
            if self.table_does_not_exist(TICK_SHEET_ITEM_TABLE):
                self.create_table()

            self.add_ticksheet_item_without_committing_or_checking(new_tick)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing tick items" % str(e1))
        finally:
            self.close()


    def does_ticksheet_item_with_name_exist(self, tick_list_name: str,  substage_id: str):
        try:
            if self.table_does_not_exist(TICK_SHEET_ITEM_TABLE):
                return False
            cursor = self.cursor
            cursor.execute('''SELECT * FROM %s WHERE %s='%s' AND %s='%s' ''' % (
                TICK_SHEET_ITEM_TABLE,
                TICK_SHEET_ITEM_NAME,
                tick_list_name,
                TICK_SUBSTAGE_ID,
                int(substage_id)
            ))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading tick items" % str(e1))
        finally:
            self.close()

        return len(raw_list)>0

    def next_available_id(self) ->int:
        return self.last_used_id()+1

    def last_used_id(self)-> int:
        try:
            if self.table_does_not_exist(TICK_SHEET_ITEM_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                TICK_SHEET_ITEM_ID,
                TICK_SHEET_ITEM_TABLE
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading groups data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])


    def modify_ticksheet_item_name(
            self, existing_tick_item_id: str, new_item_name: str
    ):
        existing_item = self.get_tick_item_with_id(existing_tick_item_id, default=missing_data)
        if existing_item is missing_data:
            raise Exception("Can't modify non existent item with id %s" % existing_tick_item_id)

        if existing_item.name == new_item_name:
            return

        if self.does_ticksheet_item_with_name_exist(new_item_name, substage_id=existing_item.substage_id):
            raise Exception("Cannot change name from %s to %s as an item with that name already exists for this substage" % (existing_item.name, new_item_name))

        self._modify_ticksheet_item_name_without_checks(existing_tick_item_id=existing_tick_item_id, new_item_name=new_item_name)

    def _modify_ticksheet_item_name_without_checks(
            self, existing_tick_item_id: str, new_item_name: str
    ):
        try:
            if self.table_does_not_exist(TICK_SHEET_ITEM_TABLE):
                self.create_table()

            insertion = "UPDATE %s SET %s='%s' WHERE %s='%s'" % (
                TICK_SHEET_ITEM_TABLE,
                TICK_SHEET_ITEM_NAME,
                new_item_name,
                TICK_SHEET_ITEM_ID,
                int(existing_tick_item_id))

            self.cursor.execute(insertion)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing tick items" % str(e1))
        finally:
            self.close()


    def get_tick_item_with_id(self, tick_item_id: str, default=arg_not_passed):
        try:
            if self.table_does_not_exist(TICK_SHEET_ITEM_TABLE):
                if default is arg_not_passed:
                    raise MissingData("%s not found" % tick_item_id)
                else:
                    return default

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s WHERE %s='%s' ''' % (

                TICK_SHEET_ITEM_NAME,
                TICK_SUBSTAGE_ID,
                TICK_SHEET_ITEM_TABLE,
                TICK_SHEET_ITEM_ID,
                int(tick_item_id),
            ))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading tick items" % str(e1))
        finally:
            self.close()

        if len(raw_list)==0:
            if default is arg_not_passed:
                raise MissingData("%s not found" % tick_item_id)
            else:
                return default
        elif len(raw_list)>1:
            raise MultipleMatches("More than one %s matches" % tick_item_id)

        raw_item = raw_list[0]

        return TickSheetItem(name=str(raw_item[0]),
                          substage_id=str(raw_item[1]),
                          id=tick_item_id)


    def get_qualifications_and_tick_items_as_dict(self)->QualificationsAndTickItemsAsDict:
        raw_list = self.read()
        return QualificationsAndTickItemsAsDict(dict(
            [
                (qualification, self.get_substages_as_dict_for_qualification(qualification, raw_list=raw_list))
                for qualification in self.list_of_qualifications
            ])
        )

    def get_substages_as_dict_for_qualification(self, qualification: Qualification, raw_list: ListOfTickSheetItems) \
            -> TickSubStagesAsDict:
        new_dict = dict([(substage, ListOfTickSheetItems([])) for substage in self.list_of_substages if substage.stage_id == qualification.id])
        for raw_item in raw_list:
            substage_id = raw_item.substage_id
            substage = self.list_of_substages.substage_given_id(substage_id)
            qualification_id = substage.stage_id
            if not qualification_id==qualification.id:
                continue

            tick_name = raw_item.name
            tick_id = raw_item.id
            list_this_substage = new_dict.get(substage) ## prefilled
            list_this_substage.append(TickSheetItem(name=tick_name,
                                   substage_id=substage_id,
                                                    id=tick_id))

            new_dict[substage]= list_this_substage

        return TickSubStagesAsDict(new_dict)

    @property
    def list_of_substages(self):
        list_of_substages = getattr(self, "_list_of_substages", None)
        if list_of_substages is None:
            list_of_substages = self._list_of_substages = SqlDataListOfTickSubStages(self.db_connection).read()

        return list_of_substages

    @property
    def list_of_qualifications(self):
        list_of_qualifications = getattr(self, "_list_of_qualifications", None)
        if list_of_qualifications is None:
            list_of_qualifications = self._list_of_qualifications = SqlDataListOfQualifications(self.db_connection).read()

        return list_of_qualifications

    def read(self) -> ListOfTickSheetItems:
        try:
            if self.table_does_not_exist(TICK_SHEET_ITEM_TABLE):
                return ListOfTickSheetItems.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s''' % (

                TICK_SHEET_ITEM_NAME,
                TICK_SUBSTAGE_ID,
                TICK_SHEET_ITEM_ID,
                TICK_SHEET_ITEM_TABLE,
            ))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading tick items" % str(e1))
        finally:
            self.close()

        new_list = [
            TickSheetItem(name=str(raw_item[0]),
                          substage_id=str(raw_item[1]),
                          id=str(raw_item[2]))

            for raw_item in raw_list]

        return ListOfTickSheetItems(new_list)

    def write(self, list_of_tick_sheet_items: ListOfTickSheetItems):
        try:
            if self.table_does_not_exist(TICK_SHEET_ITEM_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (TICK_SHEET_ITEM_TABLE))

            for item in list_of_tick_sheet_items:
                self.add_ticksheet_item_without_committing_or_checking(item)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing tick items" % str(e1))
        finally:
            self.close()

    def add_ticksheet_item_without_committing_or_checking(self, item: TickSheetItem):
        name = item.name
        substage_id = int(item.substage_id)
        item_id = int(item.id)

        insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?,?,?)" % (
            TICK_SHEET_ITEM_TABLE,
            TICK_SHEET_ITEM_NAME,
            TICK_SUBSTAGE_ID,
            TICK_SHEET_ITEM_ID)

        self.cursor.execute(insertion, (
            name, substage_id, item_id))

    def create_table(self):
        try:
            self.cursor.execute("DROP TABLE %s"  % TICK_SHEET_ITEM_TABLE)
            self.conn.commit()
        except:
            pass

        table_creation_query = """
                        CREATE TABLE %s (
                            %s STR, 
                            %s INTEGER,
                            %s INTEGER
                        );
                    """ % (TICK_SHEET_ITEM_TABLE,
                           TICK_SHEET_ITEM_NAME,
                           TICK_SUBSTAGE_ID,
                           TICK_SHEET_ITEM_ID
                           )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (
            INDEX_TICK_SHEET_ITEM_TABLE, TICK_SHEET_ITEM_TABLE,
            TICK_SHEET_ITEM_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating substage table" % str(e1))
        finally:
            self.close()


