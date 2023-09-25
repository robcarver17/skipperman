from dataclasses import dataclass

from data_access.api.generic_api import GenericDataApi
from interface.api.generic_api import GenericInterfaceApi


@dataclass
class DataAndInterface:
    data: GenericDataApi
    interface: GenericInterfaceApi