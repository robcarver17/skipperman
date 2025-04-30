from typing import Tuple

from app.data_access.store.object_store import ObjectStore
from app.objects.volunteers import Volunteer

from app.backend.volunteers.list_of_volunteers import get_volunteer_from_id

from app.objects.day_selectors import Day
from app.frontend.shared.buttons import (
    is_button_of_type,
    get_button_value_given_type_and_attributes,
    get_attributes_from_button_pressed_of_known_type,
    is_button_volunteer_selection,
)


def last_button_pressed_was_volunteer_name_button(last_button: str) -> bool:
    return is_button_volunteer_selection(last_button)


def last_button_pressed_was_make_unavailable_button(last_button: str):
    on_specific_day = last_button_pressed_was_make_unavailable_for_specific_day_button(
        last_button
    )
    if on_specific_day:
        return True
    across_days = last_button_pressed_was_make_all_days_unavailable_for_volunteer(
        last_button
    )
    if across_days:
        return True

    return False


make_available_button_type = "MakeAvailable"


def last_button_pressed_was_make_available_button(last_button: str):
    return is_button_of_type(last_button, make_available_button_type)


def make_available_button_value_for_volunteer_on_day(
    volunteer_id: str, day: Day
) -> str:
    return generic_button_value_for_volunteer_id_and_day(
        button_type=make_available_button_type, volunteer_id=volunteer_id, day=day
    )


def volunteer_and_day_from_make_available_button(
    object_store: ObjectStore, button: str
):
    return from_known_button_to_volunteer_and_day(
        object_store=object_store,
        button_text=button,
        button_type=make_available_button_type,
    )


copy_over_button_type = "COPYOVER"


def copy_overwrite_button_value_for_volunteer_in_role_on_day(
    volunteer: Volunteer,
    day: Day,
) -> str:
    return generic_button_value_for_volunteer_id_and_day(
        button_type=copy_over_button_type, volunteer_id=volunteer.id, day=day
    )


def last_button_pressed_was_copyover_button(last_button: str):
    return is_button_of_type(last_button, copy_over_button_type)


def from_copyoverwrite_button_to_volunteer_and_day(
    object_store: ObjectStore, button_value: str
):
    return from_known_button_to_volunteer_and_day(
        object_store=object_store,
        button_text=button_value,
        button_type=copy_over_button_type,
    )


copy_fill_buton_type = "COPYFILL"


def copy_fill_button_value_for_volunteer_in_role_on_day(
    volunteer: Volunteer,
    day: Day,
) -> str:
    return generic_button_value_for_volunteer_id_and_day(
        button_type=copy_fill_buton_type, volunteer_id=volunteer.id, day=day
    )


def last_button_pressed_was_copyfill_button(last_button: str):
    return is_button_of_type(last_button, copy_fill_buton_type)


def from_copyfill_button_to_volunteer_and_day(
    object_store: ObjectStore, button_value: str
):
    return from_known_button_to_volunteer_and_day(
        object_store=object_store,
        button_text=button_value,
        button_type=copy_fill_buton_type,
    )


unavailable_across_button_type = "ACROSSUNAVAILABLE"


def last_button_pressed_was_make_all_days_unavailable_for_volunteer(
    last_button: str,
) -> bool:
    return is_button_of_type(last_button, unavailable_across_button_type)


def unavailable_button_value_for_volunteer_id_across_days(volunteer_id: str) -> str:
    return generic_button_value_for_volunteer_id(
        button_type=unavailable_across_button_type, volunteer_id=volunteer_id
    )


def volunteer_from_make_unavailable_across_days_button(
    object_store: ObjectStore, button: str
):
    return from_known_button_to_volunteer(
        object_store=object_store,
        button_type=unavailable_across_button_type,
        button_text=button,
    )


unavailable_specific_button_type = "UNAVAILABLE"


def last_button_pressed_was_make_unavailable_for_specific_day_button(last_button: str):
    return is_button_of_type(last_button, unavailable_specific_button_type)


def unavailable_button_value_for_volunteer_in_role_on_day(
    volunteer: Volunteer,
    day: Day,
) -> str:
    return generic_button_value_for_volunteer_id_and_day(
        button_type=unavailable_specific_button_type, volunteer_id=volunteer.id, day=day
    )


def volunteer_and_day_from_make_unavailable_on_specific_day_button(
    object_store: ObjectStore, button: str
):
    return from_known_button_to_volunteer_and_day(
        object_store=object_store,
        button_text=button,
        button_type=unavailable_specific_button_type,
    )


remove_role_across_button_type = "RemoveRoleAcross"


def remove_role_button_value_for_volunteer_in_role_across_days(
    volunteer: Volunteer,
) -> str:
    return generic_button_value_for_volunteer_id(
        button_type=remove_role_across_button_type, volunteer_id=volunteer.id
    )


def volunteer_from_remove_role_across_days_button(
    object_store: ObjectStore, button: str
):
    return from_known_button_to_volunteer(
        object_store=object_store,
        button_text=button,
        button_type=remove_role_across_button_type,
    )


remove_role_button_type = "RemoveRole"


def remove_role_button_value_for_volunteer_in_role_on_day(
    volunteer: Volunteer,
    day: Day,
) -> str:
    return generic_button_value_for_volunteer_id_and_day(
        button_type=remove_role_button_type, volunteer_id=volunteer.id, day=day
    )


def volunteer_and_day_from_remove_role_on_specific_day_button(
    object_store: ObjectStore, button: str
):
    return from_known_button_to_volunteer_and_day(
        object_store=object_store,
        button_text=button,
        button_type=remove_role_button_type,
    )


def last_button_pressed_was_remove_role_button(last_button: str):
    return is_button_of_type(last_button, remove_role_button_type) or is_button_of_type(
        last_button, remove_role_across_button_type
    )


previous_role_button_type = "prevRoleCopy"


def from_previous_role_copy_button_to_volunteer(
    object_store: ObjectStore,
    previous_role_copy_button_name: str,
) -> Volunteer:
    volunteer = from_known_button_to_volunteer(
        object_store,
        previous_role_copy_button_name,
        button_type=previous_role_button_type,
    )

    return volunteer


def copy_previous_role_button_name_from_volunteer_id(volunteer_id: str):
    return generic_button_value_for_volunteer_id(
        previous_role_button_type, volunteer_id
    )


def last_button_was_copy_previous_role(last_button: str):
    return is_button_of_type(last_button, previous_role_button_type)


location_button_type = "locationButtonCopy"


def location_button_name_from_volunteer_id(volunteer_id: str):
    return generic_button_value_for_volunteer_id(
        location_button_type, volunteer_id=volunteer_id
    )


def from_location_button_to_volunteer(
    object_store: ObjectStore, location_button_name: str
) -> Volunteer:
    volunteer = from_known_button_to_volunteer(
        object_store, location_button_name, button_type=location_button_type
    )

    return volunteer


def last_button_pressed_was_location_button(last_button: str) -> bool:
    return is_button_of_type(last_button, location_button_type)


skills_button_type = "skillsButton"


def from_skills_button_to_volunteer(
    object_store: ObjectStore, skills_button_name: str
) -> Volunteer:
    volunteer = from_known_button_to_volunteer(
        object_store, skills_button_name, button_type=skills_button_type
    )

    return volunteer


def skills_button_name_from_volunteer_id(volunteer_id):
    return generic_button_value_for_volunteer_id(skills_button_type, volunteer_id)


def last_button_pressed_was_skill_button(last_button: str):
    return is_button_of_type(last_button, skills_button_type)


## Generics


def generic_button_value_for_volunteer_id_and_day(
    button_type: str, volunteer_id: str, day: Day
) -> str:
    return get_button_value_given_type_and_attributes(
        button_type, volunteer_id, day.name
    )


def generic_button_value_for_volunteer_id(button_type: str, volunteer_id: str) -> str:
    return get_button_value_given_type_and_attributes(
        button_type,
        volunteer_id,
    )


def from_known_button_to_volunteer(
    object_store: ObjectStore, button_text: str, button_type: str
) -> Volunteer:
    volunteer_id = from_known_button_to_volunteer_id(
        button_text, button_type=button_type
    )
    volunteer = get_volunteer_from_id(
        object_store=object_store, volunteer_id=volunteer_id
    )

    return volunteer


def from_known_button_to_volunteer_and_day(
    object_store: ObjectStore, button_text: str, button_type: str
) -> Tuple[Volunteer, Day]:
    id, day = from_known_button_to_volunteer_id_and_day(
        button_text, button_type=button_type
    )
    volunteer = get_volunteer_from_id(object_store=object_store, volunteer_id=id)

    return volunteer, day


def from_known_button_to_volunteer_id_and_day(
    button_text: str, button_type: str
) -> Tuple[str, Day]:
    id, day_name = get_attributes_from_button_pressed_of_known_type(
        type_to_check=button_type, value_of_button_pressed=button_text
    )

    return id, Day[day_name]


def from_known_button_to_volunteer_id(button_text: str, button_type: str) -> str:
    id = get_attributes_from_button_pressed_of_known_type(
        type_to_check=button_type, value_of_button_pressed=button_text
    )
    return id
