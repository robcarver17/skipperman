
from dataclasses import dataclass
from typing import List, Callable

NO_OBJECT = object()


@dataclass
class DefinitionWithArgsAndMethod:
    data_api_property_and_method: Callable
    kwargs: dict

    @property
    def key(self):
        return get_store_key(self.data_api_property_and_method, **self.kwargs)

    def __hash__(self):
        return hash(self.key)

def get_store_key(
        data_api_property_and_method: Callable,
        **kwargs):

    key = data_api_property_and_method.__qualname__+"_" + str(kwargs)

    return key

@dataclass
class CachedDataItem:
    contents: [object, dict] ## dict if iterated
    definition_with_args: DefinitionWithArgsAndMethod
    changed: bool = False

    @property
    def key(self):
        return self.definition_with_args.key

