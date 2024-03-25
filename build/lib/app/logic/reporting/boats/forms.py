from app.backend.reporting.boat_report.boat_report_parameters import AdditionalParametersForBoatReport
from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_form import  yes_no_radio
from app.objects.abstract_objects.abstract_interface import abstractInterface


from app.logic.reporting.boats.processes import load_additional_parameters_for_boat_report, EXCLUDE_UNALLOCATED, EXCLUDE_LAKE, EXCLUDE_RIVER_TRAIN, DISPLAY_FULL_NAMES
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________


def explain_additional_parameters_for_boat_report(interface: abstractInterface,
    additional_parameters: AdditionalParametersForBoatReport
) -> ListOfLines:

    event = get_event_from_state(interface)
    if event.contains_groups:
        lake_text = "Exclude lake groups" if additional_parameters.exclude_lake_groups else "Include lake groups"
        river_text = "Exclude river training groups" if additional_parameters.exclude_river_training_groups else "Include river training groups"
        unallocated = "Exclude sailors with no group" if additional_parameters.exclude_unallocated_groups else "Include sailors with no group"
    else:
        lake_text = river_text = unallocated = ""

    full_names = "Display sailors full names" if additional_parameters.display_full_names else "Show only initials and surnames"

    return ListOfLines([full_names, lake_text, river_text, unallocated])

def reporting_options_form_for_boat_additional_parameters(
    interface: abstractInterface,
) -> ListOfLines:
    additional_parameters = load_additional_parameters_for_boat_report(interface)
    display_full_names =yes_no_radio(input_name=DISPLAY_FULL_NAMES, input_label="Display cadet full first name?", default_is_yes=additional_parameters.display_full_names)

    event = get_event_from_state(interface)
    if event.contains_groups:
        exclude_lake = yes_no_radio(input_name=EXCLUDE_LAKE, input_label="Exclude lake sailors?", default_is_yes=additional_parameters.exclude_lake_groups)
        exclude_river = yes_no_radio(input_name=EXCLUDE_RIVER_TRAIN, input_label="Exclude sailors in river training groups (won't apply to racers)?", default_is_yes=additional_parameters.exclude_river_training_groups)
        exclude_unallocated =yes_no_radio(input_name=EXCLUDE_UNALLOCATED, input_label="Exclude sailors not allocated to groups?", default_is_yes=additional_parameters.exclude_unallocated_groups)
    else:
        exclude_lake =exclude_river = exclude_unallocated= ""

    my_options = ListOfLines(
        [
            display_full_names,
            exclude_lake,
            exclude_river,
            exclude_unallocated,
            _______________,
        ]
    )
    return my_options

