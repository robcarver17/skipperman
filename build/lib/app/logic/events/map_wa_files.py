import pandas as pd
from app.logic.data import DataAndInterface
from app.objects import Event
from app.logic.events.load_wa_file import (
    NO_VALID_ID,
    get_event_id_from_wa_df,
)


def verify_and_if_required_add_wa_mapping(
    data_and_interface: DataAndInterface,
    wa_as_df: pd.DataFrame,
    event: Event,
    update_existing: bool,
):

    wa_id = get_event_id_from_wa_df(
        wa_as_df=wa_as_df, data_and_interface=data_and_interface
    )
    if wa_id is NO_VALID_ID:
        return False

    wa_mapping_is_correct = confirm_correct_wa_mapping(
        data_and_interface=data_and_interface,
        wa_id=wa_id,
        event=event,
        update_existing=update_existing,
    )

    if not wa_mapping_is_correct:
        return False

    # Add the WA/Event id mapping to the relevant table unless we are updating
    new_event = not update_existing
    if new_event:
        add_wa_to_event_mapping(
            data_and_interface=data_and_interface, event=event, wa_id=wa_id
        )

    return True


def confirm_correct_wa_mapping(
    data_and_interface: DataAndInterface,
    event: Event,
    wa_id: str,
    update_existing: bool = False,
) -> bool:

    data = data_and_interface.data
    interface = data_and_interface.interface
    event_id = event.id
    wa_event_mapping = data.data_wa_event_mapping.read()

    event_is_already_in_mapping_list = wa_event_mapping.is_event_in_mapping_list(
        event_id
    )

    if event_is_already_in_mapping_list:
        existing_wa_id = wa_event_mapping.get_wa_id_for_event(event_id)
        if existing_wa_id == wa_id:
            if update_existing:
                ## all fine as expected
                return True
            else:
                ## SUPPOSED to be new but isn't
                interface.message(
                    "Event %s is already mapped to WA id %s - you want to UPDATE not IMPORT NEW WA file"
                    % (event_id, wa_id)
                )
                return False
        else:
            interface.message(
                "Event %s is already mapped to a different existing WA id %s; but imported WA file has id %s - are you sure you have the right file?"
                % (event_id, existing_wa_id, wa_id)
            )
            return False

    wa_event_is_already_in_mapping_list = wa_event_mapping.is_wa_id_in_mapping_list(
        wa_id
    )

    if wa_event_is_already_in_mapping_list:
        existing_event_id = wa_event_mapping.get_event_id_for_wa(wa_id)
        if existing_event_id == event_id:
            if update_existing:
                ## all fine as expected
                return True
            else:
                ## SUPPOSED to be new but isn't
                interface.message(
                    "Event %s is already mapped to WA id %s - you want to UPDATE not IMPORT NEW WA file"
                    % (event_id, wa_id)
                )
                return False

        else:
            interface.message(
                "WA ID %s in file is already mapped to a different existing event %s - are you sure you have the right file?"
                % (wa_id, existing_event_id)
            )
            return False

    ## not in eithier list, new mapping
    if update_existing:
        interface.message(
            "Event %d has not yet had a WA import so you can't update with new WA file"
        )
        return False
    else:
        return True


def add_wa_to_event_mapping(
    data_and_interface: DataAndInterface, event: Event, wa_id: str
):
    data = data_and_interface.data
    event_id = event.id
    wa_event_mapping = data.data_wa_event_mapping.read()
    wa_event_mapping.add_event(event_id=event_id, wa_id=wa_id)
    data.data_wa_event_mapping.write(wa_event_mapping)
