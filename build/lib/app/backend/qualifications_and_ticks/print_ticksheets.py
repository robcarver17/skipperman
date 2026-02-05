from app.backend.club_boats.people_with_club_dinghies_at_event import (
    is_a_club_dinghy_allocated_for_list_of_cadets_on_any_day_at_event,
)
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_health_notes_for_list_of_cadets_at_event,
)
from app.backend.groups.cadets_with_groups_at_event import (
    get_joint_attendance_matrix_for_cadets_in_group_at_event,
)
from app.backend.qualifications_and_ticks.ticksheets import (
    get_ticksheet_data_for_cadets_at_event_in_group_with_qualification,
)

from app.objects.qualifications import Qualification

from app.data_access.store.object_store import ObjectStore

from app.objects.composed.labelled_tick_sheet import (
    LabelledTickSheet,
    labelled_tick_sheet_from_ticksheet_data,
)
from app.objects.events import Event
from app.objects.groups import Group


def get_labelled_ticksheet_df_for_group_at_event(
    object_store: ObjectStore,
    event: Event,
    group: Group,
    qualification: Qualification,
    include_attendance_columns: bool = True,
    add_header: bool = True,
    sailors_in_columns: bool = True,
    asterix_club_boats: bool = True,
    medical_notes: bool = True,
) -> LabelledTickSheet:
    labelled_ticksheet = (
        get_labelled_ticksheet_df_for_cadets_in_group_at_event_for_qualification(
            object_store=object_store,
            event=event,
            qualification=qualification,
            group=group,
        )
    )

    if add_header:
        labelled_ticksheet = labelled_ticksheet.add_qualification_and_group_header()

    if include_attendance_columns:
        attendance_matrix = get_joint_attendance_matrix_for_cadets_in_group_at_event(
            object_store=object_store,
            event=event,
            group=group,
            list_of_cadets=labelled_ticksheet.list_of_cadets,
        )
        labelled_ticksheet = labelled_ticksheet.add_attendance_data(attendance_matrix)

    if asterix_club_boats:
        list_of_club_boat_bool = (
            is_a_club_dinghy_allocated_for_list_of_cadets_on_any_day_at_event(
                object_store=object_store,
                event=event,
                list_of_cadets=labelled_ticksheet.list_of_cadets,
            )
        )

        labelled_ticksheet = labelled_ticksheet.add_club_boat_asterix(
            list_of_club_boat_bool
        )
    if medical_notes:
        health_notes = get_health_notes_for_list_of_cadets_at_event(
            object_store=object_store,
            event=event,
            list_of_cadets=labelled_ticksheet.list_of_cadets,
        )
        labelled_ticksheet = labelled_ticksheet.add_health_notes(health_notes)

    if sailors_in_columns:
        labelled_ticksheet = labelled_ticksheet.transpose()

    return labelled_ticksheet


def get_labelled_ticksheet_df_for_cadets_in_group_at_event_for_qualification(
    object_store: ObjectStore,
    event: Event,
    group: Group,
    qualification: Qualification,
) -> LabelledTickSheet:
    ticksheet_data = get_ticksheet_data_for_cadets_at_event_in_group_with_qualification(
        object_store=object_store,
        event=event,
        group=group,
        qualification=qualification,
    )

    return labelled_tick_sheet_from_ticksheet_data(
        ticksheet_data=ticksheet_data, group=group
    )
