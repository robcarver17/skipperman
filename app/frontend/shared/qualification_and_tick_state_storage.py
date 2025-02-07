from app.objects.exceptions import MissingData

from app.frontend.shared.cadet_state import get_cadet_from_state

from app.backend.qualifications_and_ticks.list_of_qualifications import (
    get_qualification_given_name,
    get_qualification_given_id,
)
from app.backend.groups.list_of_groups import get_group_with_name

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.groups import Group
from app.objects.qualifications import Qualification


GROUP_NAME = "group"
QUALIFICATION_NAME = "qualification"
CADET_ID = "cadet"


def get_group_from_state(interface: abstractInterface) -> Group:
    name = get_group_name_from_state(interface)
    group = get_group_with_name(object_store=interface.object_store, group_name=name)
    return group


def get_group_name_from_state(interface: abstractInterface) -> str:
    return interface.get_persistent_value(GROUP_NAME)


def update_state_for_group_name(interface: abstractInterface, group_name: str):
    interface.set_persistent_value(GROUP_NAME, group_name)


def get_qualification_from_state(interface: abstractInterface) -> Qualification:
    id = get_qualification_id_from_state(interface)
    return get_qualification_given_id(object_store=interface.object_store, id=id)


def get_qualification_id_from_state(interface: abstractInterface) -> str:
    return interface.get_persistent_value(QUALIFICATION_NAME)


def update_state_for_qualification_name(
    interface: abstractInterface, qualification_name: str
):
    qualification = get_qualification_given_name(
        interface.object_store, name=qualification_name
    )
    update_state_for_qualification(interface, qualification=qualification)


def update_state_for_qualification(
    interface: abstractInterface, qualification: Qualification
):
    interface.set_persistent_value(QUALIFICATION_NAME, qualification.id)


EDIT_STATE = "edit_state"
EDIT_DROPDOWN_STATE = "edit_dropdown"
EDIT_CHECKBOX_STATE = "edit_checkbox"
NO_EDIT_STATE = "no_edit"


def get_edit_state_of_ticksheet(interface: abstractInterface):
    return interface.get_persistent_value(EDIT_STATE, NO_EDIT_STATE)


def set_edit_state_of_ticksheet(interface: abstractInterface, state: str):
    assert state in [EDIT_CHECKBOX_STATE, EDIT_DROPDOWN_STATE, NO_EDIT_STATE]
    interface.set_persistent_value(EDIT_STATE, state)


def return_true_if_a_cadet_id_been_set(interface: abstractInterface):
    try:
        get_cadet_from_state(interface)
        return True
    except MissingData:
        return False


def not_editing(interface: abstractInterface):
    state = get_edit_state_of_ticksheet(interface)
    return state == NO_EDIT_STATE
