from app.backend.data.qualification import QualificationData

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.groups import Group
from app.objects.qualifications import Qualification

GROUP_NAME = "group"
QUALIFICATION_NAME = "qualification"
def get_group_from_state(interface: abstractInterface) -> Group:
    name = get_group_name_from_state(interface)
    return Group(name)

def get_group_name_from_state(interface: abstractInterface) -> str:
    return interface.get_persistent_value(GROUP_NAME)

def update_state_for_group_name(interface: abstractInterface, group_name: str):
    interface.set_persistent_value(GROUP_NAME, group_name)


def get_qualification_from_state(interface: abstractInterface) -> Qualification:
    id = get_qualification_id_from_state(interface)
    qual_data = QualificationData(interface.data)
    return qual_data.get_qualification_given_id(id)

def get_qualification_id_from_state(interface: abstractInterface) -> str:
    return interface.get_persistent_value(QUALIFICATION_NAME)

def update_state_for_qualification(interface: abstractInterface, qualification: Qualification):
    interface.set_persistent_value(QUALIFICATION_NAME, qualification.id)

def update_state_for_qualification_name(interface: abstractInterface, qualification_name):
    qual_data = QualificationData(interface.data)
    qualification = qual_data.get_qualification_given_name(qualification_name)
    interface.set_persistent_value(QUALIFICATION_NAME, qualification.id)

EDIT_STATE="edit_state"
EDIT_DROPDOWN_STATE = "edit_dropdown"
EDIT_CHECKBOX_STATE = "edit_checkbox"
NO_EDIT_STATE = "no_edit"

def get_edit_state_of_ticksheet(interface: abstractInterface):
    return interface.get_persistent_value(EDIT_STATE, NO_EDIT_STATE)

def set_edit_state_of_ticksheet(interface: abstractInterface, state: str):
    assert state in [EDIT_CHECKBOX_STATE, EDIT_DROPDOWN_STATE, NO_EDIT_STATE]
    interface.set_persistent_value(EDIT_STATE, state)