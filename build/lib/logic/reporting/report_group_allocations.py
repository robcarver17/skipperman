import pandas as pd
from data_access.configuration.configuration import ALL_GROUPS

from interface.reporting.create_column_pdf_report_from_df import (
    create_column_pdf_report_from_df_and_return_filename,
)
from logic.data_and_interface import DataAndInterface
from logic.events.choose_event import choose_event
from logic.allocation.load_and_save_allocations_for_events import (
    load_allocation_for_event,
)
from logic.allocation.allocation_data import (
    get_unallocated_cadets,
    get_list_of_cadets_with_groups,
)
from logic.reporting.choose_reporting_options import choose_reporting_options

from interface.reporting.reporting_options import MarkedUpListFromDfParameters

from objects.groups import CADET_NAME, GROUP_STR_NAME


def report_group_allocations(data_and_interface: DataAndInterface):
    event = choose_event("Event to report for", data_and_interface=data_and_interface)

    df = get_df_for_reporting(data_and_interface=data_and_interface, event=event)
    report_group_allocations_with_df(
        data_and_interface=data_and_interface, df=df, event=event
    )


def get_df_for_reporting(data_and_interface: DataAndInterface, event):
    ## NOTE DOESN'T DEAL WITH WAITING LISTS
    ##   is a waiting list cadet unallocated, or allocated with a * against their name?
    ##   at some point report would include club boats

    display_full_names = data_and_interface.interface.return_true_if_answer_is_yes(
        "Show full names? (no to include first initial and surname only)"
    )
    include_unallocated = data_and_interface.interface.return_true_if_answer_is_yes(
        "Include unallocated cadets?"
    )

    list_of_cadet_ids_with_groups = load_allocation_for_event(
        event=event, data_and_interface=data_and_interface
    )
    if include_unallocated:
        unallocated_cadets = get_unallocated_cadets(
            event=event,
            data_and_interface=data_and_interface,
            list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
        )
        list_of_cadet_ids_with_groups.add_list_of_unallocated_cadets(unallocated_cadets)

    list_of_cadets_with_groups = get_list_of_cadets_with_groups(
        list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
        data_and_interface=data_and_interface,
    )
    df = list_of_cadets_with_groups.to_df_of_str(display_full_names=display_full_names)

    return df


def report_group_allocations_with_df(
    data_and_interface: DataAndInterface, df: pd.DataFrame, event
):

    default_title = "Group allocation for %s (%s)" % (
        event.event_name,
        str(event.event_year),
    )

    default_markuplist_from_df_options = (
        default_markuplist_from_df_options_for_group_allocation
    )
    report_options = choose_reporting_options(
        data_and_interface=data_and_interface,
        df=df,
        default_title=default_title,
        default_markuplist_from_df_options=default_markuplist_from_df_options,
    )

    filename = create_column_pdf_report_from_df_and_return_filename(
        df=df, report_options=report_options
    )

    data_and_interface.interface.process_pdf_report(filename)


default_markuplist_from_df_options_for_group_allocation = MarkedUpListFromDfParameters(
    entry_columns=[CADET_NAME],
    group_by_column=GROUP_STR_NAME,
    include_group_as_header=True,
    first_value_in_group_is_key=False,
    passed_group_order=ALL_GROUPS,
    prepend_group_name=False,
)
