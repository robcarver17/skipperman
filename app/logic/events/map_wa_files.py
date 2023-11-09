from app.data_access.data import data
from app.objects.events import Event
from app.logic.events.load_wa_file import get_event_id_from_wa_df, load_raw_wa_file
from app.objects.constants import FileError


def verify_and_if_required_add_wa_mapping(filename: str, event: Event):
    wa_as_df = load_raw_wa_file(filename)

    wa_id = get_event_id_from_wa_df(wa_as_df=wa_as_df)

    new_event = confirm_correct_wa_mapping_and_return_true_if_new_event(
        wa_id=wa_id, event=event
    )

    # Add the WA/Event id mapping to the relevant table unless we are updating an existing event
    if new_event:
        add_wa_to_event_mapping(event=event, wa_id=wa_id)


def confirm_correct_wa_mapping_and_return_true_if_new_event(
    event: Event, wa_id: str
) -> bool:

    event_id = event.id
    wa_event_mapping = data.data_wa_event_mapping.read()

    event_is_already_in_mapping_list = wa_event_mapping.is_event_in_mapping_list(
        event_id
    )

    if event_is_already_in_mapping_list:
        existing_wa_id = wa_event_mapping.get_wa_id_for_event(event_id)
        if existing_wa_id == wa_id:
            ## all fine as expected, and an existing event
            return False
        else:
            raise FileError(
                "Event %s is already mapped to a different existing WA id %s; but imported WA file has id %s - are you sure you have the right file?"
                % (str(event), existing_wa_id, wa_id)
            )

    wa_event_is_already_in_mapping_list = wa_event_mapping.is_wa_id_in_mapping_list(
        wa_id
    )

    if wa_event_is_already_in_mapping_list:
        existing_event_id = wa_event_mapping.get_event_id_for_wa(wa_id)
        if existing_event_id == event_id:
            # existing event mapped correctly - shouldn't get here, but for good order:
            return False
        else:
            raise FileError(
                "WA ID %s in file is already mapped to a different existing event with ID %s - are you sure you have the right file?"
                % (wa_id, existing_event_id)
            )

    ## not in eithier list, new mapping
    return True


def add_wa_to_event_mapping(event: Event, wa_id: str):

    event_id = event.id
    wa_event_mapping = data.data_wa_event_mapping.read()
    wa_event_mapping.add_event(event_id=event_id, wa_id=wa_id)
    data.data_wa_event_mapping.write(wa_event_mapping, )
