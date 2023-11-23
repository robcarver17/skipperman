import pandas as pd
from app.data_access.data import data
from app.objects.events import Event
from app.objects.wa_field_mapping import WAFieldMapping
from app.objects.mapped_wa_event_no_ids import MappedWAEventNoIDs
from app.logic.events.backend.load_wa_file import load_raw_wa_file


def map_wa_fields_in_df_for_event(event: Event, filename: str) -> MappedWAEventNoIDs:

    wa_as_df = load_raw_wa_file(filename)
    # Set up WA event mapping fields
    wa_field_mapping = get_wa_field_mapping_dict(wa_as_df=wa_as_df, event=event)

    # Do the field mapping
    # need to think about what happens if a field is missing
    mapped_wa_event_data = map_wa_fields_in_df(
        wa_as_df=wa_as_df,
        wa_field_mapping=wa_field_mapping,
    )

    return mapped_wa_event_data


def map_wa_fields_in_df(
    wa_as_df: pd.DataFrame,
    wa_field_mapping: WAFieldMapping,
) -> MappedWAEventNoIDs:

    # FIXME THINK ABOUT HOW TO HANDLE MISSING FIELDS

    ## Return dataframe with new columns; but don't map non existent
    """
    _warn_user_about_fields(
        data_and_interface=data_and_interface,
        wa_as_df=wa_as_df,
        wa_field_mapping=wa_field_mapping,
    )
    """
    mapped_wa_event_data = _map_wa_fields_in_df_no_warnings(
        wa_as_df=wa_as_df, wa_field_mapping=wa_field_mapping
    )
    return mapped_wa_event_data


"""
def _warn_user_about_fields(
    data_and_interface: DataAndInterface,
    wa_as_df: pd.DataFrame,
    wa_field_mapping: WAFieldMapping,
):

    fields_in_wa_file = list(wa_as_df.columns)
    in_mapping_not_in_wa_file = wa_field_mapping.wa_fields_missing_from_list(
        fields_in_wa_file
    )
    in_wa_file_not_in_mapping = wa_field_mapping.wa_fields_missing_from_mapping(
        fields_in_wa_file
    )

    interface = data_and_interface.interface
    if len(in_mapping_not_in_wa_file) > 0:
        interface.message(
            "Following fields are missing from WA file; may cause problems later: %s"
            % str(in_mapping_not_in_wa_file)
        )

    if len(in_wa_file_not_in_mapping) > 0:
        interface.message(
            "Following fields are in WA file but will not be imported, probably OK: %s"
            % (str(in_wa_file_not_in_mapping))
        )
"""


def _map_wa_fields_in_df_no_warnings(
    wa_as_df: pd.DataFrame, wa_field_mapping: WAFieldMapping
) -> MappedWAEventNoIDs:

    fields_in_wa_file = list(wa_as_df.columns)
    matching_wa_fields = wa_field_mapping.matching_wa_fields(fields_in_wa_file)
    dict_of_mapped_data = {}
    for wa_fieldname in matching_wa_fields:
        my_fieldname = wa_field_mapping.skipperman_field_given_wa_field(wa_fieldname)
        dict_of_mapped_data[my_fieldname] = wa_as_df[wa_fieldname]

    mapped_wa_event_data = MappedWAEventNoIDs.from_dict(dict_of_mapped_data)

    return mapped_wa_event_data


def get_wa_field_mapping_dict(
    wa_as_df: pd.DataFrame,
    event: Event,
):
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

    wa_mapping_dict = data.data_wa_field_mapping.read(event.id)
    if len(wa_mapping_dict) == 0:
        raise Exception(
            "No mapping found - set up the mapping and then re-import"
        )  ### NEEDS TO BE MUCH MORE VERBOSE

    return wa_mapping_dict
