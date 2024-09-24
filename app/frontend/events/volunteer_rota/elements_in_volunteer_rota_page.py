from app.OLD_backend.forms.form_utils import checked_and_labels_dict_for_skills_form
from app.OLD_backend.rota.sorting_and_filtering import RotaSortsAndFilters, get_explanation_of_sorts_and_filters

from app.frontend.events.volunteer_rota.volunteer_rota_buttons import get_all_volunteer_sort_buttons, apply_filter_button, \
    clear_filter_button, get_buttons_after_rota_table_if_not_swapping, get_buttons_after_rota_table_if_swapping
from app.objects_OLD.volunteers_in_roles import FILTER_OPTIONS
from app.OLD_backend.forms.swaps import is_ready_to_swap
from app.objects_OLD.abstract_objects.abstract_buttons import (
    ButtonBar,
)
from app.objects_OLD.abstract_objects.abstract_form import (
    MaterialAroundTable,
    checkboxInput,
    dropDownInput,
)
from app.objects_OLD.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects_OLD.day_selectors import Day
from app.objects_OLD.events import Event


def get_filters_and_buttons(
    interface: abstractInterface, event: Event, sorts_and_filters: RotaSortsAndFilters
) -> MaterialAroundTable:

    if is_ready_to_swap(interface):
        before_table = null_list_of_lines
        after_table =  ListOfLines([get_buttons_after_rota_table_if_swapping()])
    else:
        before_table = get_before_material_if_not_swapping(event=event, sorts_and_filters=sorts_and_filters)
        after_table =  ListOfLines([get_buttons_after_rota_table_if_not_swapping()])

    return MaterialAroundTable(before_table=before_table, after_table=after_table)


def get_before_material_if_not_swapping(
     event: Event, sorts_and_filters: RotaSortsAndFilters
) -> ListOfLines:
    explain_all_sorts_and_filters = get_explanation_of_sorts_and_filters(
        sorts_and_filters
    )

    sort_buttons = get_all_volunteer_sort_buttons()
    skills_filter = get_volunteer_skills_filter(sorts_and_filters=sorts_and_filters)
    availablility_filter = get_availability_for_volunteers_filter(event=event)

    pre_table_button_bar = ButtonBar([apply_filter_button, clear_filter_button, ""] + sort_buttons)

    before_table = ListOfLines(
        [
            pre_table_button_bar,
            skills_filter,
            availablility_filter,
            explain_all_sorts_and_filters,
            _______________,
        ]
    ).add_Lines()

    return before_table


def get_availability_for_volunteers_filter(event: Event) -> Line:
    days_in_event = event.weekdays_in_event()
    availability_filters = [
        get_available_filter_for_day(day=day) for day in days_in_event
    ]

    return Line(
        ["   Choose daily availability / allocation status to filter volunteers by"]
        + availability_filters
    )


def get_available_filter_for_day(day: Day):
    list_of_options = [construct_filter_entry(day, option) for option in FILTER_OPTIONS]
    dict_of_options = dict([(option, option) for option in list_of_options])
    return dropDownInput(
        input_name=get_available_filter_name_for_day(day),
        dict_of_options=dict_of_options,
        input_label="",
    )


def get_available_filter_name_for_day(day: Day):
    return "filterAv_" + day.name


def construct_filter_entry(day: Day, option: str) -> str:
    return "%s:%s" % (day.name, option)


def from_filter_entry_to_option(filter_entry: str) -> str:
    return filter_entry.split(":")[1]


null_list_of_lines = ListOfLines([_______________])


def get_volunteer_skills_filter( sorts_and_filters: RotaSortsAndFilters):
    skills_filter = sorts_and_filters.skills_filter
    skills_dict_checked, dict_of_labels = checked_and_labels_dict_for_skills_form(skills_filter)


    return checkboxInput(
        input_label="Filter for volunteers with these skills",
        dict_of_checked=skills_dict_checked,
        dict_of_labels=dict_of_labels,
        input_name=SKILLS_FILTER,
        line_break=False,
    )


SKILLS_FILTER = "skills_filter"


