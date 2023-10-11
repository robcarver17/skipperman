from logic.data_and_interface import DataAndInterface
from logic.events.choose_event import choose_event
from logic.allocation.load_and_save_allocations_for_events import (
    load_allocation_for_event,
)
from logic.allocation.allocation_data import (
    get_unallocated_cadets,
    get_list_of_cadets_with_groups,
)


def report_group_allocations(data_and_interface: DataAndInterface):
    event = choose_event("Event to report for", data_and_interface=data_and_interface)
    ## NOTE DOESN'T DEAL WITH WAITING LISTS
    ##   is a waiting list cadet unallocated, or allocated with a * against their name?
    ##   at some point report would include club boats

    display_fullnames = data_and_interface.interface.return_true_if_answer_is_yes(
        "Show full names? (no to include first initial and surname only)"
    )
    list_of_cadet_ids_with_groups = load_allocation_for_event(
        event=event, data_and_interface=data_and_interface
    )
    include_unallocated = data_and_interface.interface.return_true_if_answer_is_yes(
        "Include unallocated cadets?"
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

    list_of_cadets_with_groups_as_df = list_of_cadets_with_groups.to_df_of_str(
        display_full_names=display_fullnames
    )
