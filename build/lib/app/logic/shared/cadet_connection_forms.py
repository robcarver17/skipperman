from typing import List

from app.OLD_backend.cadets import get_cadet_from_id, \
    get_list_of_cadets_with_those_with_name_similar_to_volunteer_with_listed_first

from app.objects.abstract_objects.abstract_buttons import ButtonBar, back_menu_button, Button
from app.objects.abstract_objects.abstract_form import Form, dropDownInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________, Line
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.primtive_with_id.volunteers import Volunteer


def form_to_edit_connections(
    volunteer: Volunteer,
    connected_cadets: ListOfCadets,
    header_text: ListOfLines,
    from_list_of_cadets: ListOfCadets,
) -> Form:
    existing_entries = rows_for_existing_entries(connected_cadets=connected_cadets)
    new_entries = row_for_new_entries(
        volunteer=volunteer,
        connected_cadets=connected_cadets,
        from_list_of_cadets=from_list_of_cadets,
    )
    footer_buttons = ButtonBar([back_menu_button])

    return Form(
        [
            ListOfLines(
                [
                    header_text,
                    _______________,
                    existing_entries,
                    new_entries,
                    _______________,
                    footer_buttons,
                ]
            )
        ]
    )


def rows_for_existing_entries(connected_cadets: List[Cadet]) -> ListOfLines:
    return ListOfLines(
        [get_row_for_connected_cadet(cadet) for cadet in connected_cadets]
    )


def get_row_for_connected_cadet(cadet: Cadet) -> Line:
    return Line([str(cadet), Button(label=button_label_for_deletion(cadet),value=button_name_for_deletion(cadet))])


def button_label_for_deletion(cadet: Cadet):
    return "Delete %s" % str(cadet)


def button_name_for_deletion(cadet: Cadet):
    return "DELETE_%s" % cadet.id


def cadet_from_button_name(interface: abstractInterface, button_name: str) -> Cadet:
    cadet_id = button_name.split("_")[1]
    return get_cadet_from_id(data_layer=interface.data, cadet_id=cadet_id)


def row_for_new_entries(
    volunteer: Volunteer,
    connected_cadets: ListOfCadets,
    from_list_of_cadets: ListOfCadets,
) -> Line:
    list_of_cadets_to_pick_from = from_list_of_cadets.excluding_cadets_from_other_list(
        list_of_cadets=connected_cadets
    )
    list_of_cadets_similar_to_name_first = get_list_of_cadets_with_those_with_name_similar_to_volunteer_with_listed_first(
        volunteer=volunteer, from_list_of_cadets=list_of_cadets_to_pick_from
    )

    dict_of_options = dict(
        [
            (from_cadet_to_string_in_dropdown(cadet), cadet.id)
            for cadet in list_of_cadets_similar_to_name_first
        ]
    )
    filler_row = {CADET_FILLER: CADET_FILLER}
    dict_of_options = {**filler_row, **dict_of_options}

    drop_down = dropDownInput(
        input_label="Add new connection",
        default_label=CADET_FILLER,
        dict_of_options=dict_of_options,
        input_name=CONNECTION,
    )
    return Line([drop_down, add_connection_button])


ADD_CONNECTION_BUTTON_LABEL = "Add connection"
DELETE_CONNECTION_BUTTON_LABEL = "Delete connection"
CONNECTION = "connection"
add_connection_button = Button(ADD_CONNECTION_BUTTON_LABEL)


def from_cadet_to_string_in_dropdown(cadet: Cadet) -> str:
    return str(cadet)


CADET_FILLER = "Choose cadet from dropdown and hit add to add connection"


def get_list_of_delete_cadet_buttons_given_connected_cadets(connected_cadets: list):
    return [button_name_for_deletion(cadet) for cadet in connected_cadets]


def get_cadet_from_button_pressed(interface: abstractInterface) -> Cadet:
    button = interface.last_button_pressed()
    cadet = cadet_from_button_name(interface=interface, button_name=button)

    return cadet

from app.objects.exceptions import CadetNotSelected

def get_selected_cadet_from_form(interface: abstractInterface) -> Cadet:
    selected_cadet_id = interface.value_from_form(CONNECTION)

    selected_cadet = get_cadet_from_id(
        data_layer=interface.data, cadet_id=selected_cadet_id
    )

    return selected_cadet

def get_cadet_id_to_add_from_dropdown(interface: abstractInterface):
    selected_cadet_id = interface.value_from_form(CONNECTION)
    if selected_cadet_id == CADET_FILLER:
        raise CadetNotSelected

    return selected_cadet_id