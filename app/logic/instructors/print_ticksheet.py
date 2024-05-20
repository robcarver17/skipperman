import os
from copy import copy

import pandas as pd

from app.backend.ticks_and_qualifications.create_ticksheets import get_labelled_ticksheet_df_for_group_at_event
from app.objects.abstract_objects.abstract_form import File

from app.logic.events.events_in_state import get_event_from_state

from app.logic.instructors.state_storage import get_qualification_from_state, get_group_from_state

from app.data_access.uploads_and_downloads import download_directory

from app.objects.events import Event

from app.objects.groups import Group

from app.backend.data.ticksheets import TickSheetsData

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.ticks import LabelledTickSheetWithCadetIds

def download_labelled_ticksheet_and_return_file(interface: abstractInterface) -> File:
    event = get_event_from_state(interface)
    group = get_group_from_state(interface)
    qualification = get_qualification_from_state(interface)
    filename = download_labelled_ticksheet_and_return_filename(interface=interface,
                                                               event=event,
                                                               group=group,
                                                               qualification_stage_id=qualification.id)

    return File(filename)

def download_labelled_ticksheet_and_return_filename(interface: abstractInterface,
                           event: Event,
                           group: Group,
                           qualification_stage_id: str,
                                                    ## FIXME MAKE THESE CONFIGURABLE AT SOME POINT
                            include_attendance_columns: bool = True,
                           add_header: bool = True,
                           sailors_in_columns: bool = True,
                           asterix_club_boats: bool = True,
                           medical_notes: bool = True):
    labelled_ticksheet = get_labelled_ticksheet_df_for_group_at_event(
        interface=interface,
        event=event,
        group=group,
        qualification_stage_id=qualification_stage_id,
        include_attendance_columns=include_attendance_columns,
        add_header=add_header,
        sailors_in_columns=sailors_in_columns,
        asterix_club_boats=asterix_club_boats,
        medical_notes=medical_notes
    )
    filename =temp_file_name(event=event, group=group, qualification_stage_id=qualification_stage_id)
    write_ticksheet_to_excel(labelled_ticksheet=labelled_ticksheet, filename=filename)

    return filename


def write_ticksheet_to_excel(labelled_ticksheet:LabelledTickSheetWithCadetIds, filename: str):
    title = labelled_ticksheet.qualification_name
    if len(title)==0:
        title = ' '
    df = labelled_ticksheet.df
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        df.style.apply(align_center, axis=0).to_excel(
            writer,
            merge_cells=True,
            sheet_name=title
        )

def align_center(x):
    return ['text-align: center' for x in x]


def temp_file_name(event: Event,
                           group: Group,
                           qualification_stage_id: str) -> str:
    use_group_name = copy(group.group_name)
    use_group_name = use_group_name.replace('/', '_')
    filename= os.path.join(download_directory, "ticksheet_%s_%s_%s.xlsx"% (event.id, use_group_name, qualification_stage_id))

    return filename
