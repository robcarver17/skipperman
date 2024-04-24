import pandas as pd
from app.objects.ticks import half_tick, full_tick, no_tick,  Tick, DictOfTicksWithItem, CadetWithTickListItems, TickWithItem, ListOfCadetsWithTickListItems
from app.data_access.data import DEPRECATED_data

def input_old_tick_sheets():
    input_file = pd.read_csv('/home/rob/skipperman_tests/ticksheet_input.csv')
    file_columns= input_file.columns
    file_columns=file_columns.drop('cadet_id')

    list_of_cadets_with_tick_lists =[]
    for i in range(len(input_file)):
        row = input_file.iloc[i]
        list_of_cadets_with_tick_lists.append(process_row(row, file_columns=file_columns))

    full_ticksheet = ListOfCadetsWithTickListItems(list_of_cadets_with_tick_lists)
    DEPRECATED_data.data_list_of_cadets_with_tick_list_items.write(full_ticksheet)

def process_row(row: pd.Series, file_columns: list):
    cadet_id = row.cadet_id
    list_of_ticks_with_items = [
                             tick_item(row=row,column=column) for column in file_columns]

    tick_list = DictOfTicksWithItem.from_list_of_ticks_with_items(list_of_ticks_with_items)

    return CadetWithTickListItems(cadet_id=cadet_id, dict_of_ticks_with_items=tick_list)

def tick_item(row: pd.Series, column: str) -> TickWithItem:
    tick = process_tick(row[column])

    return TickWithItem(tick_item_id=column, tick=tick)

def process_tick(item: str) -> Tick:
    if item =='x' or item=='X':
        return full_tick
    elif item =='.' or item=="*":
        return half_tick
    return no_tick

