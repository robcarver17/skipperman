import pandas as pd
from logic.data_and_interface import DataAndInterface
from logic.events.map_wa_fields import map_wa_fields_in_df
from objects.events import Event


def import_new_wa_event(data_and_interface: DataAndInterface):
    ## Get data from a WA .csv

    ## Get data from a WA .csv
    interface = data_and_interface.interface
    okay_to_import = interface.return_true_if_answer_is_yes("Have you already created the event in skipperman?")
    if not okay_to_import:
        interface.message('You need to create the event before importing from WA')
        return
    # Step one: Select the event to do the import for (has to be an existing event)
    event = choose_event(data_and_interface)

    # Step two: Read in the WA file and get the WA id (config of global WA fields)
    wa_as_df = choose_and_load_raw_wa_file(data_and_interface)
    if wa_as_df is NO_VALID_FILE:
        return

    wa_id = get_event_id_from_wa_df(wa_as_df=wa_as_df, data_and_interface=data_and_interface)
    if wa_id is NO_VALID_ID:
        return

    # Step three: Check the WA id doesn't already exist in the list of existing event/WA mappings - if so then point user to update
    any_duplicates = confirm_no_duplicate_mapping(data_and_interface=data_and_interface,
                                          wa_id=wa_id,
                                          event=event)
    if not any_duplicates:
        return

    # Step four: Add the WA/Event id mapping to the relevant table
    add_wa_to_event_mapping(data_and_interface=data_and_interface, event=event, wa_id=wa_id)

    # Step five: Set up WA event mapping fields
    wa_mapping_dict = get_wa_field_mapping_dict(wa_as_df=wa_as_df,
                                                event=event,
                                                data_and_interface=data_and_interface)

    # Step six: Do the field mapping
    # need to think about what happens if a field is missing
    mapped_wa_data = map_wa_fields_in_df(wa_as_df=wa_as_df, wa_mapping_dict=wa_mapping_dict)

    # Step seven: Save the mapped data as WA imported
    save_mapped_wa_event(mapped_wa_data=mapped_wa_data, event=event, data_and_interface=data_and_interface)

    # Step eight: Identify cadets, and if required create new cadets; write in cadet ID
    #

    # Step nine: ---- for volunteers -----

    # Step ten: create cadet/event, volunteer/event tables
    pass

def choose_event(data_and_interface: DataAndInterface) -> Event:
    data = data_and_interface.data
    interface = data_and_interface.interface

    list_of_events = data.data_list_of_events.read()
    event_names = [str(event) for event in list_of_events]
    interface.message('Choose event to import from')
    option = interface.get_choice_from_adhoc_menu(event_names)
    option_index = event_names.index(option)
    event = list_of_events[option_index]

    return event

NO_VALID_FILE = pd.DataFrame(["not valid file"])

def choose_and_load_raw_wa_file(data_and_interface: DataAndInterface) -> pd.DataFrame:
    interface = data_and_interface.interface

    wa_filename = interface.select_file("Select raw WA file to upload")
    try:
        wa_as_df = pd.read_excel(wa_filename)
    except:
        try:
            wa_as_df = pd.read_csv(wa_filename)
        except:
            interface.message("%s is not a readable .csv or .xls file; maybe try loading .xls and saving as .csv" % wa_filename)
            return NO_VALID_FILE

    return wa_as_df

WA_EVENT_ID_FIELD = 'Event ID'
NO_VALID_ID = "No valid ID"

def get_event_id_from_wa_df(wa_as_df: pd.DataFrame,
                            data_and_interface: DataAndInterface) -> str:
    interface = data_and_interface.interface

    try:
        series_of_id = wa_as_df[WA_EVENT_ID_FIELD]
    except KeyError:
        interface.message("Expected to find a column called %s in WA file - eithier not a WA file or WA have changed their format" % (
            WA_EVENT_ID_FIELD))
        return NO_VALID_ID

    unique_id = series_of_id[0]
    all_id_match_in_file = all([id==unique_id for id in series_of_id])

    if not all_id_match_in_file:
        interface.message("Column labelled %s in WA value does not contain all identical values - probably not a WA file" %
                          (WA_EVENT_ID_FIELD))
        return NO_VALID_ID

    return unique_id

def confirm_no_duplicate_mapping(data_and_interface: DataAndInterface,
      event: Event, wa_id: str) -> bool:
    data = data_and_interface.data
    interface = data_and_interface.interface
    event_id = event.id
    wa_event_mapping = data.data_wa_event_mapping.read()

    if wa_event_mapping.is_event_in_mapping_list(event_id):
        existing_wa_id= wa_event_mapping.get_wa_id_for_event(event_id)
        if existing_wa_id == wa_id:
            interface.message("Event %s is already mapped to WA id %s - you want to UPDATE not IMPORT NEW WA file" % (
                event_id, wa_id
            ))
            ## fix me - call import function?
            return False
        else:
            interface.message("Event %s is already mapped to an existing WA id %s - are you sure you have the right file?" % (
                event_id, existing_wa_id
            ))
            return False

    if wa_event_mapping.is_wa_id_in_mapping_list(wa_id):
        existing_event_id = wa_event_mapping.get_wa_id_for_event(wa_id)
        if existing_event_id == event_id:
            interface.message("Event %s is already mapped to WA id %s - you want to UPDATE not IMPORT NEW WA file" % (
                event_id, wa_id
            ))
            ## fix me - call import function?
            return False

        else:
            interface.message("WA ID %s is already mapped to an existing event %s - are you sure you have the right file?" % (
                wa_id, existing_event_id
            ))
            return False

    return True


def add_wa_to_event_mapping(data_and_interface: DataAndInterface,
      event: Event, wa_id: str) -> bool:
    data = data_and_interface.data
    event_id = event.id
    wa_event_mapping = data.data_wa_event_mapping.read()
    wa_event_mapping.add_event(event_id=event_id, wa_id=wa_id)

def get_wa_field_mapping_dict(wa_as_df: pd.DataFrame,
                              event: Event,
                              data_and_interface: DataAndInterface):
    """
    Want to end up with a dict of WA event field <-> my field name
    ... all WA event fields required by dict must exist in event
    .... needs to be a master dict somewhere of possible field names and perhaps default mapping

    Starting point; event template - cadet week / training event / ...

    Can create with .csv file

    Can create with field picker

    Need to check all fields correct

    For now keep it simple: we use a .csv file
    """

    data = data_and_interface.data
    wa_mapping_dict = data.data_wa_field_mapping.read(event.id)

    return wa_mapping_dict

def save_mapped_wa_event(mapped_wa_data, event: Event, data_and_interface: DataAndInterface):
    data = data_and_interface.data
    data.data_mapped_wa_event.write(mapped_wa_event=mapped_wa_data, event_id=event.id)