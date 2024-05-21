from app.backend.data.mapped_events import  save_mapped_wa_event
from app.backend.wa_import.convert_helm_crew_data import convert_mapped_wa_event_potentially_with_joined_rows
from app.backend.wa_import.map_wa_fields import map_wa_fields_in_df_for_event
from app.backend.wa_import.map_wa_files import verify_and_if_required_add_wa_mapping
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import Event


def process_uploaded_wa_event_file(filename: str, interface: abstractInterface, event:Event):
    ## add WA mapping
    verify_and_if_required_add_wa_mapping(filename=filename, event=event, interface=interface)

    ## do field mapping
    mapped_wa_event_data_raw = map_wa_fields_in_df_for_event(interface=interface, event=event, filename=filename)
    mapped_wa_event_data_without_empty = mapped_wa_event_data_raw.remove_empty_status()
    mapped_wa_event_data = convert_mapped_wa_event_potentially_with_joined_rows(mapped_wa_event_data_without_empty)

    save_mapped_wa_event(interface=interface, mapped_wa_event_data=mapped_wa_event_data, event=event)
