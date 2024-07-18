import os
from typing import Union

import pandas as pd
from app.logic.events.ENTRY_view_events import display_list_of_events_with_buttons

from app.OLD_backend.data.cadets import CadetData

from app.data_access.file_access import download_directory

from app.OLD_backend.wa_import.map_wa_fields import DEPRECATE_get_list_of_template_names, get_template, \
    write_mapping_to_temp_csv_file_and_return_filename
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_form import (
    Form,
    File, NewForm, )
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_buttons import CANCEL_BUTTON_LABEL, Button, ButtonBar, main_menu_button
from app.logic.abstract_logic_api import initial_state_form
from app.OLD_backend.data.qualification import QualificationData
from app.objects.qualifications import ListOfNamedCadetsWithQualifications


def display_form_for_expected_qualifications_report(interface: abstractInterface):

    ## LIST OF EVENTS AS TILES, THEN FROM THAT DOWNLOAD EXPECTED QUALIFICATIONS FOR EVENT
    event_buttons = display_list_of_events_with_buttons(interface)
    contents_of_form = ListOfLines(
        [
            ButtonBar([main_menu_button, cancel_button]),
            event_buttons
        ]
    )

    return Form(contents_of_form)

MAKE_REPORT = "Download list of qualifications"
cancel_button = Button(CANCEL_BUTTON_LABEL, nav_button=True)


def post_form_for_expected_qualifications_report(
    interface: abstractInterface,
) -> Union[File, Form, NewForm]:
    last_button = interface.last_button_pressed()

    if last_button == CANCEL_BUTTON_LABEL:
        return previous_form(interface)
    elif last_button == MAKE_REPORT:
        filename = write_qualifications_to_temp_csv_file_and_return_filename(interface)
        return File(filename)

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(post_form_for_expected_qualifications_report)



def write_qualifications_to_temp_csv_file_and_return_filename(interface: abstractInterface) -> str:
    qualification_data = QualificationData(interface.data)
    cadet_data = CadetData(interface.data)

    list_of_cadets_with_qualification= qualification_data.get_list_of_cadets_with_qualifications()
    list_of_qualifications = qualification_data.load_list_of_qualifications()
    list_of_cadets = cadet_data.get_list_of_cadets()

    list_of_cadet_names_with_qualifications = ListOfNamedCadetsWithQualifications.from_id_lists(
        list_of_cadets_with_qualifications=list_of_cadets_with_qualification,
        list_of_cadets=list_of_cadets,
        list_of_qualifications=list_of_qualifications
    )

    list_of_cadet_names_with_qualifications = list_of_cadet_names_with_qualifications.sort_by_date()
    df_of_qualifications = list_of_cadet_names_with_qualifications.as_df_of_str()

    filename = temp_file_name()

    df_of_qualifications.to_csv(filename, index=False)

    return filename


def temp_file_name() -> str:
    return os.path.join(download_directory, "temp_file.csv")
