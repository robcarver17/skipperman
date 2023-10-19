from data_access.api.csv_api import GenericDataApi
from interface.api.generic_api import GenericInterfaceApi
from logic.api import LogicApi


class GenericLauncher(object):
    def __init__(self, data: GenericDataApi, interface: GenericInterfaceApi):
        logic_api = LogicApi(data=data, interface=interface)
        self._logic = logic_api
        self._interface = interface

    def run(self):
        self.logic.run()

    @property
    def logic(self) -> LogicApi:
        return self._logic
