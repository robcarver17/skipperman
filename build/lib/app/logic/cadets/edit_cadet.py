import datetime
from app.logic.data import DataAndInterface
from app.objects import Cadet


def edit_provided_cadet_details(
    cadet: Cadet,
    data_and_interface: DataAndInterface,
    edit_firstname: bool = True,
    edit_surname: bool = True,
    edit_dob: bool = True,
) -> Cadet:
    ## does not save cadet details to .csv
    data_and_interface = data_and_interface.interface
    firstname = cadet.first_name
    surname = cadet.surname
    dob = cadet.date_of_birth

    if edit_firstname:
        firstname = data_and_interface.get_input_from_user_and_convert_to_type(
            "First name?",
            allow_default=True,
            default_value=firstname,
            type_expected=str,
        )

    if edit_surname:
        surname = data_and_interface.get_input_from_user_and_convert_to_type(
            "Surname?", allow_default=True, default_value=surname, type_expected=str
        )
    if edit_dob:
        dob = data_and_interface.get_input_from_user_and_convert_to_type(
            "Date of birth?",
            allow_default=True,
            default_value=dob,
            type_expected=datetime.date,
        )

    return Cadet(first_name=firstname, surname=surname, date_of_birth=dob)
