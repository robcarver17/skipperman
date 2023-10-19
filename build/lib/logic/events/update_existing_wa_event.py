from logic.data_and_interface import DataAndInterface
from logic.events.import_wa_event import import_wa_event_without_checking


def update_existing_wa_event(data_and_interface: DataAndInterface):
    ## Get data from a WA .csv

    ## Get data from a WA .csv
    interface = data_and_interface.interface
    okay_to_import = interface.return_true_if_answer_is_yes(
        "Have you already created the event in skipperman and imported WA data at least once?"
    )
    if not okay_to_import:
        interface.message(
            "You need to create the event and import from WA data before updating existing WA data"
        )
        return

    import_wa_event_without_checking(
        data_and_interface=data_and_interface, update_existing=True
    )
