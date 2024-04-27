from app.objects.abstract_objects.abstract_lines import ListOfLines, Line

from app.backend.group_allocations.cadet_event_allocations import DEPRECATE_load_list_of_cadets_ids_with_group_allocations_active_cadets_only

from app.objects.abstract_objects.abstract_tables import PandasDFTable

from app.objects.events import Event

from app.backend.data.cadets_at_event import DEPRECATED_load_cadets_at_event, DEPERCATE_load_identified_cadets_at_event
from app.objects.mapped_wa_event import summarise_status
from app.backend.data.mapped_events import DEPRECATE_load_mapped_wa_event


def summarise_registrations_for_event(event: Event) -> ListOfLines:
    summary_data = ListOfLines([])
    mapped_data = DEPRECATE_load_mapped_wa_event(event)
    status_dict = summarise_status(mapped_data)
    summary_data.append(Line(print_dict_nicely("Registration status", status_dict)))
    if event.contains_cadets:
        identified_cadets = DEPERCATE_load_identified_cadets_at_event(event)
        cadets_at_event = DEPRECATED_load_cadets_at_event(event)
        cadet_dict = {'Identified': len(identified_cadets), 'In event data': len(cadets_at_event), 'Active in event data': len(cadets_at_event.list_of_active_cadets_at_event()) }

        if event.contains_groups:
            list_of_cadet_ids_with_groups = DEPRECATE_load_list_of_cadets_ids_with_group_allocations_active_cadets_only(event)
            cadet_dict['Allocated to group'] = len(list_of_cadet_ids_with_groups)

        summary_data.append(Line(print_dict_nicely("Cadet status", cadet_dict)))


    return summary_data

def print_dict_nicely(label, some_dict:dict) -> str:
    dict_str_list = ['%s: %s' % (key, value) for key, value in some_dict.items()]
    dict_str_list = ", ".join(dict_str_list)

    return label+"- "+dict_str_list