import os
from copy import copy

import pandas as pd
from app.objects.qualifications import Qualification

from app.backend.qualifications_and_ticks.print_ticksheets import get_labelled_ticksheet_df_for_group_at_event
from app.objects.abstract_objects.abstract_form import File

from app.frontend.shared.events_state import get_event_from_state

from app.frontend.shared.qualification_and_tick_state_storage import (
    get_qualification_from_state,
    get_group_from_state,
)

from app.data_access.file_access import download_directory

from app.objects.events import Event

from app.objects.groups import Group

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.composed.labelled_tick_sheet import LabelledTickSheet


def download_labelled_ticksheet_and_return_file(interface: abstractInterface) -> File:
    event = get_event_from_state(interface)
    group = get_group_from_state(interface)
    qualification = get_qualification_from_state(interface)
    filename = download_labelled_ticksheet_and_return_filename(
        interface=interface,
        event=event,
        group=group,
        qualification=qualification,
    )

    return File(filename)


def download_labelled_ticksheet_and_return_filename(
    interface: abstractInterface,
    event: Event,
    group: Group,
    qualification: Qualification,
    ## FIXME MAKE THESE CONFIGURABLE AT SOME POINT
    include_attendance_columns: bool = True,
    add_header: bool = True,
    sailors_in_columns: bool = True,
    asterix_club_boats: bool = True,
    medical_notes: bool = True,
):
    labelled_ticksheet = get_labelled_ticksheet_df_for_group_at_event(
        object_store=interface.object_store,
        event=event,
        group=group,
        qualification = qualification,
        include_attendance_columns=include_attendance_columns,
        add_header=add_header,
        sailors_in_columns=sailors_in_columns,
        asterix_club_boats=asterix_club_boats,
        medical_notes=medical_notes,
    )
    filename = temp_file_name(
        event=event, group=group, qualification=qualification
    )
    write_ticksheet_to_excel(labelled_ticksheet=labelled_ticksheet, filename=filename)

    return filename


def write_ticksheet_to_excel(
    labelled_ticksheet: LabelledTickSheet, filename: str
):
    title = labelled_ticksheet.qualification_name
    if len(title) == 0:
        title = " "
    df = labelled_ticksheet.df
    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
        df.style.apply(align_center, axis=0).to_excel(
            writer, merge_cells=True, sheet_name=title
        )


def align_center(x):
    return ["text-align: center" for x in x]


def temp_file_name(event: Event, group: Group, qualification: Qualification) -> str:
    filename = "ticksheet_%s_%s_%s.xlsx" % (str(event), group.name, qualification.name)
    filename = clean_up_filename(filename)
    full_filename = os.path.join(
        download_directory,
        filename
    )

    return full_filename

def clean_up_filename(filename: str):
    filename = filename.replace("/", "_")
    filename = filename.replace(" ", "_")
    return filename