from logic.data_and_interface import DataAndInterface
from objects.cadets import Cadet
from objects.groups import (
    ListOfCadetIdsWithGroups,
    ALL_GROUPS_INCLUDING_UNALLOCATED,
    Group,
)


def allocate_cadet(
    cadet: Cadet,
    list_of_cadets_with_groups: ListOfCadetIdsWithGroups,
    data_and_interface: DataAndInterface,
):
    # add supporting information: previous group, levels (self reported and stored), experience (self reported)
    #    running total in each group
    previous_group = list_of_cadets_with_groups.group_for_cadet(cadet)
    previous_group_name = previous_group.group_name

    interface = data_and_interface.interface
    interface.message(
        "Cadet %s, currently in group %s" % (cadet.name, previous_group_name)
    )
    interface.message("Choose group to allocate into")

    chosen_group_name = interface.get_choice_from_adhoc_menu(
        ALL_GROUPS_INCLUDING_UNALLOCATED
    )
    chosen_group = Group(chosen_group_name)

    list_of_cadets_with_groups.update_group_for_cadet(
        cadet=cadet, chosen_group=chosen_group
    )
