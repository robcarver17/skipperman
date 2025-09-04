
from dataclasses import dataclass
from typing import List

from app.data_access.store.object_definitions import DerivedObjectDefinition, UnderlyingObjectDefinition, \
    IterableObjectDefinition

NO_OBJECT = object()


@dataclass
class DefinitionWithArgs:
    object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition, IterableObjectDefinition]
    kwargs: dict

    def __repr__(self):
        return "Definition, object_defintion %s, kwarg keys %s" % ((self.object_definition), str(list(self.kwargs.keys())))

    @property
    def key(self):
        return get_store_key(self.object_definition, **self.kwargs)

    def __hash__(self):
        return hash(self.key)

@dataclass
class CachedDataItem:
    contents: [object, dict] ## dict if iterated
    definition_with_args: DefinitionWithArgs
    changed: bool = False
    changed_vs_persistent: bool = False

    def change_contents(self, contents:  [object, dict]):
        self.contents = contents
        self.changed = True
        self.changed_vs_persistent = True

    def revert_change_mode(self):
        self.changed = False

    def flag_as_saved_to_persistent(self):
        self.changed_vs_persistent = False

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

    @property
    def is_depended_on_by(self):
        return getattr(self, "_depended_on_by", [])

    @is_depended_on_by.setter
    def is_depended_on_by(self, list_of_dependents: List[DefinitionWithArgs]):
        setattr(self, "_depended_on_by", list_of_dependents)

    def add_dependents(self, new_thing_depending_on_us: DefinitionWithArgs):
        depended_on_list =self.is_depended_on_by
        depended_on_list.append(new_thing_depending_on_us)
        self.is_depended_on_by = depended_on_list

    def drop_dependents(self, thing_depending_on_us_which_we_are_deleting: DefinitionWithArgs):
        depended_on_list =self.is_depended_on_by
        depended_on_list.remove(thing_depending_on_us_which_we_are_deleting)
        self.is_depended_on_by = depended_on_list

def get_store_key(
        object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition, IterableObjectDefinition],
        **kwargs
):
    key = object_definition.key + str(kwargs)

    return key
