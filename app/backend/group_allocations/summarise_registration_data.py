from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.abstract_objects.abstract_lines import ListOfLines, Line

from app.backend.group_allocations.cadet_event_allocations import \
    DEPRECATE_load_list_of_cadets_ids_with_group_allocations_active_cadets_only, \
    load_list_of_cadets_ids_with_group_allocations_active_cadets_only, count_of_cadet_ids_allocated_to_group_by_day

from app.objects.abstract_objects.abstract_tables import PandasDFTable

from app.objects.events import Event

from app.backend.data.cadets_at_event import DEPRECATED_load_cadets_at_event, DEPERCATE_load_identified_cadets_at_event, \
    CadetsAtEventData
from app.objects.mapped_wa_event import summarise_status
from app.backend.data.mapped_events import DEPRECATE_load_mapped_wa_event


def summarise_registrations_for_event(interface: abstractInterface, event: Event) -> ListOfLines:
    summary_data = ListOfLines([])
    mapped_data = DEPRECATE_load_mapped_wa_event(event)
    status_dict = summarise_status(mapped_data)
    summary_data.append(Line(print_dict_nicely("Registration status", status_dict)))
    if event.contains_cadets:
        identified_cadets = DEPERCATE_load_identified_cadets_at_event(event)
        cadets_at_event = DEPRECATED_load_cadets_at_event(event)
        cadet_dict = {'Identified': len(identified_cadets), 'In event data': len(cadets_at_event), 'Active in event data': len(cadets_at_event.list_of_active_cadets_at_event()) }

        if event.contains_groups:
            list_of_cadet_ids_with_groups = count_of_cadet_ids_allocated_to_group_by_day(interface=interface, event=event)
            for day, count in list_of_cadet_ids_with_groups.items():
                cadet_dict['Allocated to groups on %s' % day.name] =count

        summary_data.append(Line(print_dict_nicely("Cadet status", cadet_dict)))


    return summary_data

def print_dict_nicely(label, some_dict:dict) -> str:
    dict_str_list = ['%s: %s' % (key, value) for key, value in some_dict.items()]
    dict_str_list = ", ".join(dict_str_list)

    return label+"- "+dict_str_list

def identify_birthdays(interface: abstractInterface, event: Event) -> list:
    cadets_at_event_data = CadetsAtEventData(interface.data)
    active_cadets = cadets_at_event_data.list_of_active_cadets_at_event(event)
    dates_in_event = event.dates_in_event()

    matching_cadets = []
    for event_day in dates_in_event:
        cadets_matching_today = [cadet for cadet in active_cadets if cadet.day_and_month_of_birth_matches_other_data(event_day)]
        matching_cadets+=cadets_matching_today

    descr_str_list = ["Cadet %s has birthday during event!" % cadet for cadet in matching_cadets]

    return descr_str_list