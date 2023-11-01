import datetime
from app.data_access.api.generic_api import GenericDataApi
from app.data_access.configuration.configuration import SIMILARITY_LEVEL_TO_WARN_NAME, SIMILARITY_LEVEL_TO_WARN_DATE
from app.objects.events import Event

def verify_event_and_warn(data: GenericDataApi, event: Event)->str:
    warn_text = ""
    if len(event.event_name)<5:
        warn_text+="Event name seems a bit short. "
    if event.start_date<datetime.date.today():
        warn_text+="Event started in the past. "
    if event.end_date<event.start_date:
        warn_text+="Event ends before it starts. "
    if event.end_date==event.start_date:
        warn_text+="Event is only one day long. "

    warn_text+=warning_for_similar_events(data=data, event=event)

    if len(warn_text)>0:
        warn_text="DOUBLE CHECK BEFORE ADDING: "+warn_text

    return warn_text


def warning_for_similar_events(data: GenericDataApi, event: Event) -> str:
    existing_events = data.data_list_of_events.read()
    similar_events = existing_events.similar_events(
        event,
        name_threshold=SIMILARITY_LEVEL_TO_WARN_NAME,
        date_threshold=SIMILARITY_LEVEL_TO_WARN_DATE
    )

    if len(similar_events) > 0:
        similar_events_str = ", ".join([str(other_event) for other_event in similar_events])
        return "Following events look awfully similar:\n %s" % similar_events_str
    else:
        return ""


def add_new_verified_event(event: Event, data: GenericDataApi):
    data.data_list_of_events.add(event)

"""
import datetime
from app.logic.data import DataAndInterface

from app.objects import Event, EventType


def create_new_event(data_and_interface: DataAndInterface):
    data = data_and_interface.data
    interface = data_and_interface.interface

    trying = True
    while trying:
        # FIXME WHEN HAVE MORE EVENT METADATA E.G. LIST OF GROUPS WILL WANT THE OPTION TO ADD THIS NOW,
        #    AND ALSO TO CLONE AN EXISTING EVENT

        event = get_basic_event_details(data_and_interface)
        okay_to_add = interface.return_true_if_answer_is_yes("OK to add event?")

        if okay_to_add:
            try:
                data.data_list_of_events.add(event)
                return
            except Exception as e:
                interface.message("Can't add event, error %s" % str(e))

        try_again = interface.return_true_if_answer_is_yes("Try again?")

        if not try_again:
            return


def get_basic_event_details(data_and_interface: DataAndInterface) -> Event:
    invalid = True
    interface = data_and_interface.interface
    while invalid:
        event_name = _get_name_of_event(data_and_interface)
        event_type = interface.get_input_from_user_and_convert_to_type(
            "Type of Event", type_expected=EventType
        )
        start_date, end_date = _get_valid_start_and_end_dates(data_and_interface)

        event = Event(
            event_name=event_name,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
        )

        interface.message("Event created %s" % event.verbose_repr)
        event_okay = interface.return_true_if_answer_is_yes("Happy with event?")
        if event_okay:
            invalid = False

    return event


def _get_name_of_event(data_and_interface: DataAndInterface):
    interface = data_and_interface.interface
    copy_existing = interface.return_true_if_answer_is_yes("Copy name from old event?")
    if copy_existing:
        event_name = _get_name_of_event_copied_from_previous(data_and_interface)
    else:
        event_name = _get_name_of_event_as_text(data_and_interface)

    return event_name


def _get_name_of_event_copied_from_previous(
    data_and_interface: DataAndInterface,
) -> str:
    data = data_and_interface.data
    interface = data_and_interface.interface

    previous_events = data.data_list_of_events.read()
    interface.display_df(previous_events.to_df())

    previous_event = interface.get_choice_from_adhoc_menu(
        previous_events.list_of_event_names
    )

    return previous_event


def _get_name_of_event_as_text(data_and_interface: DataAndInterface):
    interface = data_and_interface.interface
    event_name = interface.get_input_from_user_and_convert_to_type(
        "Name of Event?", type_expected=str, allow_default=False
    )

    return event_name


def _get_event_type(data_and_interface: DataAndInterface) -> EventType:
    interface = data_and_interface.interface
    event_type = interface.get_input_from_user_and_convert_to_type(
        "Type of Event", type_expected=EventType
    )

    return event_type


def _get_valid_start_and_end_dates(data_and_interface: DataAndInterface):
    interface = data_and_interface.interface

    invalid = True
    while invalid:
        start_date = interface.get_input_from_user_and_convert_to_type(
            "Start date:", type_expected=datetime.date
        )
        end_date = interface.get_input_from_user_and_convert_to_type(
            "End date:", type_expected=datetime.date
        )

        try:
            assert end_date >= start_date
            break
        except:
            interface.message(
                "Dates %s to %s don't make sense" % (str(start_date), str(end_date))
            )

    return start_date, end_date
"""