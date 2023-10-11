## Core function for gathering business logic
from data_access.api.csv_api import GenericDataApi
from interface.api.generic_api import GenericInterfaceApi

from logic.data_and_interface import DataAndInterface

from logic.cadets.view_cadets import view_list_of_cadets

from logic.events.create_new_event import create_new_event
from logic.events.view_events import view_list_of_events
from logic.events.import_new_wa_event import import_new_wa_event
from logic.events.update_existing_wa_event import update_existing_wa_event

from logic.allocation.allocate_unallocated_cadets import allocate_unallocated_cadets
from logic.allocation.change_allocated_cadets import change_allocated_cadets

from logic.reporting.report_group_allocations import report_group_allocations


class LogicApi:
    def __init__(self, data: GenericDataApi, interface: GenericInterfaceApi):
        self._data_and_interface = DataAndInterface(data=data, interface=interface)

    def run(self):
        ## Infinite loop around interface
        interface = self.data_and_interface.interface
        while True:
            func_name_from_interface = interface.get_menu_item()
            if interface.user_selected_exit_state():
                break
            try:
                func_to_run = getattr(self, func_name_from_interface)
            except:
                interface.message(
                    "Menu item points to method %s - not yet implemented"
                    % str(func_name_from_interface)
                )
                continue
            func_to_run()

        interface.message("Exiting Skipperman")

        return

    ### Here follows the long list of functions that the menu can call
    ### These are defined as values in the menu_define.py file
    ## Functions must have no arguments apart from self
    ## Called functions should almost certainly have no arguments apart from data_and_interface

    def view_master_list_of_cadets(self):
        view_list_of_cadets(self.data_and_interface)

    def view_list_of_events(self):
        view_list_of_events(self.data_and_interface)

    def create_new_event(self):
        create_new_event(self.data_and_interface)

    def import_new_wa_event(self):
        import_new_wa_event(self.data_and_interface)

    def update_existing_wa_event(self):
        update_existing_wa_event(self.data_and_interface)

    def allocate_unallocated_cadets(self):
        allocate_unallocated_cadets(self.data_and_interface)

    def change_allocated_cadets(self):
        change_allocated_cadets(self.data_and_interface)

    def report_group_allocations(self):
        report_group_allocations(self.data_and_interface)

    @property
    def data_and_interface(self) -> DataAndInterface:
        return self._data_and_interface
