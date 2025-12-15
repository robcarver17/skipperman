
from dataclasses import dataclass
from typing import List, Callable

from app.data_access.store.object_definitions import DerivedObjectDefinition, UnderlyingObjectDefinition, \
    IterableObjectDefinition

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



@dataclass
class DEPRECATE_DefinitionWithArgs:
    object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition, IterableObjectDefinition]
    kwargs: dict

    def __repr__(self):
        return "Definition, object_defintion %s, kwarg keys %s" % ((self.object_definition), str(list(self.kwargs.keys())))

    @property
    def key(self):
        return DEPRECATE_get_store_key(self.object_definition, **self.kwargs)

    def __hash__(self):
        return hash(self.key)

@dataclass
class DEPRECATE_CachedDataItem:
    contents: [object, dict] ## dict if iterated
    definition_with_args: DEPRECATE_DefinitionWithArgs
    changed: bool = False

    def change_contents(self, contents:  [object, dict]):
        self.contents = contents
        self.changed = True

    def flag_as_saved_to_persistent(self):
        self.changed = False

    @property
    def object_definition(self):
        return self.definition_with_args.object_definition

    @property
    def kwargs(self):
        return self.definition_with_args.kwargs

    @property
    def key(self):
        return self.definition_with_args.key

    @property
    def is_underyling_object(self):
        return type(self.object_definition) is UnderlyingObjectDefinition


def DEPRECATE_get_store_key(
        object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition, IterableObjectDefinition],
        **kwargs
):
    key = object_definition.key + str(kwargs)

    return key

