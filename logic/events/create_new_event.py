import datetime
from logic.data_and_interface import DataAndInterface

from objects.events import Event, EventType

def create_new_event(data_and_interface: DataAndInterface):
    data = data_and_interface.data
    interface = data_and_interface.interface
    ## get basic event details or clone an existing event [seperate menu option]
    event = get_basic_event_details(data_and_interface)
    okay_to_add = interface.return_true_if_answer_is_yes("OK to add event?")

    if okay_to_add:
        try:
            data.data_list_of_events.add(event)
        except Exception as e:
            interface.message("Can't add event, error %s" % str(e))

    ## ... further steps ...
    pass

def get_basic_event_details(data_and_interface: DataAndInterface) -> Event:
    invalid = True
    interface = data_and_interface.interface
    while invalid:
        event_name = _get_name_of_event(data_and_interface)
        event_type = interface.get_input_from_user_and_convert_to_type("Type of Event", type_expected=EventType)
        start_date, end_date = _get_valid_start_and_end_dates(data_and_interface)

        event = Event(event_name=event_name,
              event_type=event_type,
              start_date=start_date,
              end_date= end_date)

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

def _get_name_of_event_copied_from_previous(data_and_interface: DataAndInterface) -> str:
    data = data_and_interface.data
    interface = data_and_interface.interface

    previous_events = data.data_list_of_events.read()
    interface.display_df(previous_events.to_df())

    previous_event = interface.get_choice_from_adhoc_menu(previous_events.list_of_event_names)

    return previous_event

def _get_name_of_event_as_text(data_and_interface: DataAndInterface):
    interface = data_and_interface.interface
    event_name = interface.get_input_from_user_and_convert_to_type("Name of Event?",
                                                      type_expected=str,
                                                      allow_default=False)

    return event_name


def _get_event_type(data_and_interface: DataAndInterface) -> EventType:
    interface = data_and_interface.interface
    event_type = interface.get_input_from_user_and_convert_to_type("Type of Event", type_expected=EventType)

    return event_type


def _get_valid_start_and_end_dates(data_and_interface: DataAndInterface):
    interface = data_and_interface.interface

    invalid = True
    while invalid:
        start_date = interface.get_input_from_user_and_convert_to_type("Start date:", type_expected=datetime.date)
        end_date = interface.get_input_from_user_and_convert_to_type("End date:", type_expected=datetime.date)

        try:
            assert end_date >= start_date
            break
        except:
            interface.message("Dates %s to %s don't make sense" % (str(start_date), str(end_date)))

    return start_date, end_date
