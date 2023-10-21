from dataclasses import dataclass

from app.data_access import GenericDataApi
from app.interface import GenericInterfaceApi


@dataclass
class DataAndInterface:
    data: GenericDataApi
    interface: GenericInterfaceApi
