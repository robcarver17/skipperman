from typing import List

from app.backend.volunteers.connected_cadets import (
    get_list_of_cadets_with_those_with_name_similar_to_volunteer_with_listed_first,
)
from app.backend.cadets.list_of_cadets import get_cadet_from_id

from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    back_menu_button,
    Button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_form import Form, dropDownInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.volunteers import Volunteer


def form_to_edit_connections(
    volunteer: Volunteer,
    existing_connected_cadets: ListOfCadets,
    header_text: ListOfLines,
    list_of_cadets_to_choose_from: ListOfCadets,
) -> Form:
    existing_entries = rows_for_existing_entries(
        existing_connected_cadets=existing_connected_cadets
    )
    new_entries = row_for_new_entries(
        volunteer=volunteer,
        connected_cadets=existing_connected_cadets,
        list_of_cadets_to_choose_from=list_of_cadets_to_choose_from,
    )
    footer_buttons = ButtonBar([back_menu_button, help_button])

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


help_button = HelpButton("view_individual_volunteer_help")


def rows_for_existing_entries(existing_connected_cadets: List[Cadet]) -> ListOfLines:
    return ListOfLines(
        [get_row_for_connected_cadet(cadet) for cadet in existing_connected_cadets]
    )


def get_row_for_connected_cadet(cadet: Cadet) -> Line:
    return Line(
        [
            str(cadet),
            Button(
                label=button_label_for_deletion(cadet),
                value=button_name_for_deletion(cadet),
            ),
        ]
    )


def button_label_for_deletion(cadet: Cadet):
    return "Delete %s" % str(cadet)


def button_name_for_deletion(cadet: Cadet):
    return "DELETE_%s" % cadet.id


def cadet_from_button_name(interface: abstractInterface, button_name: str) -> Cadet:
    cadet_id = button_name.split("_")[1]
    return get_cadet_from_id(object_store=interface.object_store, cadet_id=cadet_id)


def row_for_new_entries(
    volunteer: Volunteer,
    connected_cadets: ListOfCadets,
    list_of_cadets_to_choose_from: ListOfCadets,
) -> Line:
    dict_of_options = get_dict_of_options_for_new_entry_dropdown(
        connected_cadets=connected_cadets,
        volunteer=volunteer,
        list_of_cadets_to_choose_from=list_of_cadets_to_choose_from,
    )
    drop_down = dropDownInput(
        input_label="Add new connection",
        default_label=CADET_FILLER,
        dict_of_options=dict_of_options,
        input_name=CONNECTION,
    )
    return Line([drop_down, add_connection_button])


def get_dict_of_options_for_new_entry_dropdown(
    volunteer: Volunteer,
    connected_cadets: ListOfCadets,
    list_of_cadets_to_choose_from: ListOfCadets,
) -> dict:
    list_of_cadets_similar_to_name_first = (
        get_list_of_cadets_similar_to_name_first_excluding_already_connected(
            volunteer=volunteer,
            connected_cadets=connected_cadets,
            from_list_of_cadets=list_of_cadets_to_choose_from,
        )
    )
    dict_of_options = dict(
        [
            (from_cadet_to_string_in_dropdown(cadet), cadet.id)
            for cadet in list_of_cadets_similar_to_name_first
        ]
    )
    filler_row = {CADET_FILLER: CADET_FILLER}
    dict_of_options = {**filler_row, **dict_of_options}

    return dict_of_options


def get_list_of_cadets_similar_to_name_first_excluding_already_connected(
    volunteer: Volunteer,
    connected_cadets: ListOfCadets,
    from_list_of_cadets: ListOfCadets,
) -> ListOfCadets:
    list_of_cadets_to_pick_from = from_list_of_cadets.excluding_cadets_from_other_list(
        list_of_cadets=connected_cadets
    )
    list_of_cadets_similar_to_name_first = (
        get_list_of_cadets_with_those_with_name_similar_to_volunteer_with_listed_first(
            volunteer=volunteer, from_list_of_cadets=list_of_cadets_to_pick_from
        )
    )

    return list_of_cadets_similar_to_name_first


ADD_CONNECTION_BUTTON_LABEL = "Add connection"
DELETE_CONNECTION_BUTTON_LABEL = "Delete connection"
CONNECTION = "connection"
add_connection_button = Button(ADD_CONNECTION_BUTTON_LABEL)


def from_cadet_to_string_in_dropdown(cadet: Cadet) -> str:
    return str(cadet)


CADET_FILLER = "Choose sailor from dropdown and hit add to add connection"


def get_list_of_delete_cadet_buttons_given_connected_cadets(connected_cadets: list):
    return [button_name_for_deletion(cadet) for cadet in connected_cadets]


def get_cadet_from_button_pressed(interface: abstractInterface) -> Cadet:
    button = interface.last_button_pressed()
    cadet = cadet_from_button_name(interface=interface, button_name=button)

    return cadet


from app.objects.utilities.exceptions import CadetNotSelected, MISSING_FROM_FORM


def get_selected_cadet_from_form(interface: abstractInterface) -> Cadet:
    selected_cadet_id = interface.value_from_form(CONNECTION, default=MISSING_FROM_FORM)
    if selected_cadet_id is MISSING_FROM_FORM:
        raise "Can't get cadet from form"

    selected_cadet = get_cadet_from_id(
        object_store=interface.object_store, cadet_id=selected_cadet_id
    )

    return selected_cadet


def get_cadet_id_to_add_from_dropdown(interface: abstractInterface):
    selected_cadet_id = interface.value_from_form(CONNECTION)
    if selected_cadet_id == CADET_FILLER:
        raise CadetNotSelected

    return selected_cadet_id
