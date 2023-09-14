## Core function for gathering business logic
from data_access.api.csv_api import GenericDataApi
from interface.api.generic_api import GenericInterfaceApi

from logic.cadets.view_cadets import view_list_of_cadets
from logic.events.create_new_event import create_new_event
from logic.events.view_events import view_list_of_events

class LogicApi:
    def __init__(self, data: GenericDataApi, interface: GenericInterfaceApi):
        self._data = data
        self._interface = interface

    def run(self):
        ## Infinite loop around interface
        while True:
            func_name_from_interface = self.interface.get_menu_item()
            if self.interface.user_selected_exit_state():
                break
            try:
                func_to_run = getattr(self, func_name_from_interface)
            except:
                self.interface.message(
                    "Menu item points to method %s - not yet implemented"
                    % str(func_name_from_interface)
                )
                continue
            func_to_run()

        self.interface.message("Exiting Skipperman")

        return

    def view_master_list_of_cadets(self):
        view_list_of_cadets(data = self.data, interface=self.interface)

    def view_list_of_events(self):
        view_list_of_events(data = self.data, interface=self.interface)

    def create_new_event(self):
        create_new_event(data = self.data, interface=self.interface)

    @property
    def data(self) -> GenericDataApi:
        return self._data

    @property
    def interface(self) -> GenericInterfaceApi:
        return self._interface
