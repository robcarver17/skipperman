from dataclasses import dataclass
from typing import Callable, Dict

from app.objects.exceptions import arg_not_passed


class MissingFormName(Exception):
    pass


@dataclass
class FormNameFunctionNameMapping(object):
    mapping_dict: Dict[str, Callable]  ## form_name, function

    def get_form_name_for_function(self, func: Callable):
        possible_form_names = [
            form_name
            for form_name, func_in_dict in self.mapping_dict.items()
            if func_in_dict == func
        ]
        if len(possible_form_names) == 0:
            raise MissingFormName("Function %s not found in mapping" % str(func))
        elif len(possible_form_names) > 1:
            raise MissingFormName(
                "Function %s found multiple times in mapping" % str(func)
            )

        form_name = possible_form_names[0]
        return form_name

    def get_function_for_form_name(self, form_name: str) -> Callable:
        func = self.mapping_dict.get(form_name, None)
        if func is None:
            raise MissingFormName("Form name %s not found in mapping" % str(form_name))

        return func


INITIAL_STATE = "Initial form"


"""
A nested dict looks like this:

nested_dict={(display_form_view_of_cadets, post_form_view_of_cadets): {
    (display_form_add_cadet, post_form_add_cadets): '',
    (display_form_view_individual_cadet, post_form_view_individual_cadet): {
            (display_form_delete_individual_cadet, post_form_delete_individual_cadet): '',
            (display_form_edit_individual_cadet, post_form_edit_individual_cadet): '',
        }

    }

}

and this is the output product:
DisplayAndPostFormFunctionMaps(
    display_mappings= FormNameFunctionNameMapping(mapping_dict={

        INITIAL_STATE: display_form_view_of_cadets,
        'display_form_view_individual_cadet': display_form_view_individual_cadet,
        'display_form_add_cadet':display_form_add_cadet,
        'display_form_delete_individual_cadet':display_form_delete_individual_cadet,
        'display_form_edit_individual_cadet': display_form_edit_individual_cadet
        },
    parent_child_dict={
    display_form_view_of_cadets: (display_form_view_individual_cadet, display_form_add_cadet),
    display_form_view_individual_cadet: (display_form_edit_individual_cadet, display_form_delete_individual_cadet)

    }),

    post_mappings= FormNameFunctionNameMapping({INITIAL_STATE: post_form_view_of_cadets,
        'display_form_add_cadet': post_form_add_cadets,
        'display_form_view_individual_cadet': post_form_view_individual_cadet,
        'display_form_delete_individual_cadet': post_form_delete_individual_cadet,
        'display_form_edit_individual_cadet': post_form_edit_individual_cadet}))


"""

DISPLAY_IDX = 0
POST_IDX = 1

FUNCTION_KEY = "function"


class NestedDictOfMappings(object):
    def __init__(self, nested_dict: dict, top_level: bool = True):
        if top_level:
            try:
                assert len(nested_dict) == 1
            except:
                raise Exception("Top level must only have one key tuple")

        self.nested_dict = nested_dict

    def parent_child_dict_mapping_back_to_display_parent(
        self,
        current_dict: dict = arg_not_passed,
        current_parent: Callable = arg_not_passed,
    ) -> dict:
        if current_parent is arg_not_passed:
            at_top_level = True

            current_parent = self.get_top_level_tuple()[
                DISPLAY_IDX
            ]  ## parents are always the display as that is what we want back
            assert current_dict is arg_not_passed
            current_dict = {current_parent: []}
        else:
            at_top_level = False

        for key, value in self.nested_dict.items():
            relevant_display_function = key[DISPLAY_IDX]
            relevant_post_function = key[POST_IDX]
            if type(value) is not dict:
                if at_top_level:
                    ## corner case when no children, should return empty dict if only one key
                    return {}
                else:
                    current_dict[current_parent].append(relevant_post_function)
                    current_dict[current_parent].append(relevant_display_function)

            else:
                ## nested dict
                current_dict[current_parent].append(relevant_post_function)
                current_dict[current_parent].append(relevant_display_function)
                make_nested = NestedDictOfMappings(value, top_level=False)
                new_parent = relevant_display_function
                current_dict[new_parent] = []

                make_nested.parent_child_dict_mapping_back_to_display_parent(
                    current_dict=current_dict,
                    current_parent=new_parent,
                )

        return current_dict

    def get_display_mapping_dict(self) -> Dict[(str, Callable)]:
        return self._get_mapping_dict_given_index(DISPLAY_IDX)

    def get_post_mapping_dict(self) -> Dict[(str, Callable)]:
        return self._get_mapping_dict_given_index(POST_IDX)

    def _get_mapping_dict_given_index(
        self, which_index: int = DISPLAY_IDX
    ) -> Dict[(str, Callable)]:
        mapping_dict = {}
        top_level_key_func = self.get_top_level_tuple()[which_index]

        all_tuples = self.get_list_of_all_nestedkeys_at_tuples()
        for some_tuple in all_tuples:
            relevant_func = some_tuple[which_index]
            display_func = some_tuple[DISPLAY_IDX]
            if relevant_func is top_level_key_func:
                func_name = INITIAL_STATE
            else:
                func_name = display_func.__name__
            mapping_dict[func_name] = relevant_func

        return mapping_dict

    def get_top_level_tuple(self) -> tuple:
        all_keys_at_top_level = list(self.nested_dict.keys())

        return all_keys_at_top_level[0]

    def get_list_of_all_nestedkeys_at_tuples(self) -> list:
        all_items = []

        for key, value in self.nested_dict.items():
            if type(value) is not dict:
                try:
                    assert key not in all_items
                except:
                    raise Exception("Nested dict must have unique keys")
                all_items.append(key)
            else:
                ## nested dict
                all_items.append(key)
                make_nested = NestedDictOfMappings(value, top_level=False)
                flattened = make_nested.get_list_of_all_nestedkeys_at_tuples()
                all_items = all_items + flattened

        return all_items


@dataclass
class DisplayAndPostFormFunctionMaps:
    display_mappings: FormNameFunctionNameMapping
    post_mappings: FormNameFunctionNameMapping
    parent_child_mapping: dict

    def get_display_form_name_for_parent_of_function(self, func: Callable) -> str:
        parent_display_func = [
            parent_func
            for parent_func, list_of_children in self.parent_child_mapping.items()
            if func in list_of_children
        ]
        if len(parent_display_func) == 0:
            raise MissingFormName("Can't find parent of function %s" % str(func))
        if len(parent_display_func) > 1:
            raise MissingFormName("Multiple instances of parents for %s" % str(func))

        display_form_name = self.display_mappings.get_form_name_for_function(
            parent_display_func[0]
        )

        return display_form_name

    def get_form_name_for_function(self, func: Callable):
        try:
            return self.display_mappings.get_form_name_for_function(func)
        except Exception as e1:
            try:
                return self.post_mappings.get_form_name_for_function(func)
            except Exception as e2:
                raise MissingFormName(
                    "Can't find function %s in display or post mappings, errors %s and %s"
                    % (str(func), str(e1), str(e2))
                )

    def get_display_function_for_form_name(self, form_name: str):
        return self.display_mappings.get_function_for_form_name(form_name)

    def get_post_function_for_form_name(self, form_name: str):
        return self.post_mappings.get_function_for_form_name(form_name)

    @classmethod
    def from_nested_dict_of_functions(cls, nested_dict: NestedDictOfMappings):
        display_mapping_dict = nested_dict.get_display_mapping_dict()
        post_mapping_dict = nested_dict.get_post_mapping_dict()
        parent_child_mapping = (
            nested_dict.parent_child_dict_mapping_back_to_display_parent()
        )

        display_mappings = FormNameFunctionNameMapping(
            mapping_dict=display_mapping_dict
        )
        post_mappings = FormNameFunctionNameMapping(mapping_dict=post_mapping_dict)

        return cls(
            display_mappings=display_mappings,
            post_mappings=post_mappings,
            parent_child_mapping=parent_child_mapping,
        )
