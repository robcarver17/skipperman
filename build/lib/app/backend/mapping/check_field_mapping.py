from typing import List

from app.data_access.store.object_store import ObjectStore


from app.backend.mapping.list_of_field_mappings import get_field_mapping_for_event
from app.backend.wild_apricot.load_wa_file import (
    does_raw_event_file_exist,
)
from app.backend.file_handling import load_spreadsheet_file_and_clear_nans
from app.backend.wild_apricot.load_wa_file import (
    get_staged_file_raw_event_filename,
)

from app.objects.events import Event
from app.data_access.configuration.field_list_groups import (
    ALL_FIELDS_EXPECTED_IN_WA_FILE_MAPPING,
)
from app.objects.utils import in_x_not_in_y
from app.objects.abstract_objects.abstract_text import bold
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)


def check_field_mapping(object_store: ObjectStore, event: Event) -> ListOfLines:
    if does_raw_event_file_exist(event):
        ## get the raw event file
        filename = get_staged_file_raw_event_filename(event)
        wa_as_df = load_spreadsheet_file_and_clear_nans(filename)
        fields_in_wa_file = list(wa_as_df.columns)
    else:
        fields_in_wa_file = []

    warning_list = list_of_warnings_about_fields(
        object_store=object_store, event=event, fields_in_wa_file=fields_in_wa_file
    )

    return warning_list


MAPPING_ADVICE_IF_NO_IMPORT_DONE = ListOfLines(
    [
        _______________,
        Line(
            bold(
                "Upload a WA file to check the field mapping is consistent with that file"
            )
        ),
        _______________,
    ]
)


def list_of_warnings_about_fields(
    object_store: ObjectStore,
    event: Event,
    fields_in_wa_file: List[str],
) -> ListOfLines:

    # Set up WA event mapping fields
    wa_field_mapping = get_field_mapping_for_event(
        event=event, object_store=object_store
    )

    in_mapping_not_in_wa_file = wa_field_mapping.wa_fields_missing_from_list(
        fields_in_wa_file
    )
    in_wa_file_not_in_mapping = wa_field_mapping.wa_fields_missing_from_mapping(
        fields_in_wa_file
    )
    expected_not_in_mapping = in_x_not_in_y(
        ALL_FIELDS_EXPECTED_IN_WA_FILE_MAPPING,
        wa_field_mapping.list_of_skipperman_fields,
    )
    unknown_fields = in_x_not_in_y(
        wa_field_mapping.list_of_skipperman_fields,
        ALL_FIELDS_EXPECTED_IN_WA_FILE_MAPPING,
    )

    output = []
    if len(fields_in_wa_file) > 0:
        if len(in_mapping_not_in_wa_file) > 0:
            in_mapping_not_in_wa_file_as_lines = [
                Line("-" + x) for x in in_mapping_not_in_wa_file
            ]
            output.append(
                Line(
                    bold(
                        "Following expected fields in the mapping file are missing from WA file; remove from the mapping file if not needed: "
                    )
                )
            )
            output += in_mapping_not_in_wa_file_as_lines
            output.append(_______________)

        if len(in_wa_file_not_in_mapping) > 0:
            in_wa_file_not_in_mapping_as_lines = [
                Line("-" + x) for x in in_wa_file_not_in_mapping
            ]
            output.append(
                bold(
                    "Following fields are in WA file but will not be imported, probably OK: "
                )
            )
            output += in_wa_file_not_in_mapping_as_lines
            output.append(_______________)

    else:
        output += MAPPING_ADVICE_IF_NO_IMPORT_DONE

    if len(expected_not_in_mapping) > 0:
        expected_not_in_mapping_as_lines = [
            Line("-" + x) for x in expected_not_in_mapping
        ]
        output.append(
            bold(
                "Following internal skipperman fields are not defined in mapping file, might be OK depending on event type but check: "
            )
        )
        output += expected_not_in_mapping_as_lines
        output.append(_______________)

    if len(unknown_fields) > 0:
        unknown_as_lines = [Line("-" + x) for x in unknown_fields]
        output.append(
            bold(
                "Following skipperman internal fields defined in mapping file are unknown to skipperman - will not be used - correct typos in the mapping file:"
            )
        )
        output += unknown_as_lines
        output.append(_______________)

    if len(output) == 0:
        output = [bold("No problems with mapping")]

    return ListOfLines(output).add_Lines()
