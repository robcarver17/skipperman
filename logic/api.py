## Core function for gathering business logic
from data_access.api.csv_api import GenericDataApi
from interface.api.generic_api import GenericInterfaceApi


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
            func_to_run = getattr(self, func_name_from_interface)
            func_to_run()

        self.interface.message("Exiting Skipperman")

        return

    def view_master_list_of_cadets(self):
        master_list = self.data.data_list_of_cadets.read()
        self.interface.display_df(master_list.to_df())

    @property
    def data(self) -> GenericDataApi:
        return self._data

    @property
    def interface(self) -> GenericInterfaceApi:
        return self._interface
