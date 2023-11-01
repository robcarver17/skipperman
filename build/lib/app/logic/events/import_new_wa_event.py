from app.logic.data import DataAndInterface
from app.logic.events import import_wa_event_without_checking


def import_new_wa_event(data_and_interface: DataAndInterface):
    interface = data_and_interface.interface
    okay_to_import = interface.return_true_if_answer_is_yes(
        "Have you already created the event in skipperman?"
    )
    if not okay_to_import:
        interface.message("You need to create the event before importing from WA")
        return

    import_wa_event_without_checking(
        data_and_interface=data_and_interface, update_existing=False
    )
