from dataclasses import dataclass
from typing import Callable, Dict, Tuple

from app.objects.constants import arg_not_passed


class MissingFormName(Exception):
    pass
@dataclass
class FormNameFunctionNameMapping(object):
    mapping_dict: Dict[str, Callable] ## form_name, function
    parent_child_dict: dict = arg_not_passed ### parent_function: tuple(child functions) Dict[Callable, Tuple[Callable]]

    def get_form_name_for_parent_of_function(self, func: Callable):
        parent_func = next(parent_func for parent_func, child_functions in self.parent_child_dict.items() if func in child_functions)
        if parent_func is None:
            raise MissingFormName("Function %s not found in parent child mapping")
        form_name = self.get_form_name_for_function(parent_func)

        return form_name

    def get_form_name_for_function(self, func: Callable):
        form_name = next(form_name for form_name, func_in_dict in self.mapping_dict.items() if func_in_dict == func)
        if form_name is None:
            raise MissingFormName("Function %s not found in mapping" % str(func))
        return form_name

    def get_function_for_form_name(self, form_name: str) -> Callable:
        func= self.mapping_dict.get(form_name,None)
        if func is None:
            raise MissingFormName("Form name %s not found in mapping" % str(form_name))

        return func

@dataclass
class DisplayAndPostFormFunctionMaps:
    display_mappings: FormNameFunctionNameMapping
    post_mappings: FormNameFunctionNameMapping


"""
MAY COME IN USEFUL...
@dataclass
class Mapping:
    form_name: str
    function: Callable
    sub_functions: NestedDictOfMappings

FUNCTION_KEY= 'function'
class NestedDictOfMappings(object):
    def __init__(self, nested_dict):

    def flatten_dict(self) -> dict:
        all_items = {}
        for key, value in self.items():
            if type(value) is not dict:
                try:
                    assert key not in all_items.keys()
                except:
                    raise Exception("Nested dict must have unique keys")
                all_items[key] = value
            else:
                ## nested dict
                make_nested = NestedDictOfMappings(value)
                flattened = make_nested.flatten_dict()
                all_items.update(flattened)

        return all_items

    def parent_key_of_value(self, value_to_find):
        return parent_key_of_value(value_to_find, nested_dict=self)

VALUE_IS_AT_TOP_LEVEL = object()
def parent_key_of_value(value_to_find, nested_dict: NestedDictOfMappings, previous_key = VALUE_IS_AT_TOP_LEVEL):
    for key, value in nested_dict.items():
        if type(value) is dict:
            return parent_key_of_value(value_to_find=value_to_find, nested_dict=nested_dict[key], previous_key=key)
        if value == value_to_find:
            return previous_key

    raise Exception("Value %s not found" % str(value_to_find))
"""
