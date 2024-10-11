from dataclasses import dataclass

from app.OLD_backend.data.dinghies import DinghiesData
from app.data_access.configuration.groups import all_groups_names
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet
from app.objects.cadet_at_event_with_club_boat_with_ids import ListOfCadetAtEventWithClubDinghies
from app.objects.exceptions import missing_data
from app.objects.events import Event
from app.objects_OLD.cadets_with_groups import CadetWithGroupOnDay
from app.objects.cadet_with_id_with_group_at_event import GROUP_STR_NAME
from app.OLD_backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)

specific_parameters_for_allocation_report = SpecificParametersForTypeOfReport(
    #    entry_columns=[CADET_NAME],
    group_by_column=GROUP_STR_NAME,
    passed_group_order=all_groups_names,
    report_type="Allocation report",
)


@dataclass
class AdditionalParametersForAllocationReport:
    display_full_names: bool
    include_unallocated_cadets: bool
    add_asterix_for_club_boats: bool


def add_club_boat_asterix(
    interface: abstractInterface, list_of_cadets_with_groups, event: Event
):
    club_dinghy_data = DinghiesData(interface.data)
    list_of_cadets_at_event_with_club_dinghies = (
        club_dinghy_data.get_list_of_cadets_at_event_with_club_dinghies(event)
    )

    for cadet_with_group in list_of_cadets_with_groups:
        add_club_boat_asterix_to_cadet(
            cadet_with_group=cadet_with_group,
            list_of_cadets_at_event_with_club_dinghies=list_of_cadets_at_event_with_club_dinghies,
        )

    return list_of_cadets_with_groups


def add_club_boat_asterix_to_cadet(
    cadet_with_group: CadetWithGroupOnDay,
    list_of_cadets_at_event_with_club_dinghies: ListOfCadetAtEventWithClubDinghies,
):
    cadet = cadet_with_group.cadet
    cadet_id = cadet.id
    day = cadet_with_group.day
    dinghy = list_of_cadets_at_event_with_club_dinghies.dinghy_for_cadet_id_on_day(
        cadet_id=cadet.id, day=day
    )

    if dinghy is not missing_data:
        cadet_with_group.cadet = Cadet(
            first_name=cadet.first_name,
            surname=cadet.surname + "*",
            date_of_birth=cadet.date_of_birth,
            id=cadet_id,
        )
