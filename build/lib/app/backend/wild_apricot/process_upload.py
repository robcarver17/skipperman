from app.backend.registration_data.raw_mapped_registration_data import (
    update_raw_mapped_registration_data,
)
from app.data_access.store.object_store import ObjectStore

from app.backend.mapping.convert_helm_crew_data import (
    convert_mapped_wa_event_potentially_with_joined_rows,
)
from app.backend.mapping.map_wa_fields import (
    map_wa_fields_in_df_for_event_and_add_special_fields,
)
from app.backend.mapping.event_mapping import verify_and_if_required_add_wa_mapping
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import Event


def process_uploaded_wa_event_file(
        interface: abstractInterface, filename: str, event: Event
):
    object_store = interface.object_store
    ## add WA mapping
    verify_and_if_required_add_wa_mapping(
        filename=filename, event=event, interface=interface
    )

    ## do field mapping
    mapped_wa_event_data_raw = map_wa_fields_in_df_for_event_and_add_special_fields(
        object_store=object_store, event=event, filename=filename
    )
    mapped_wa_event_data_without_empty = mapped_wa_event_data_raw.remove_empty_status()
    mapped_wa_event_data = convert_mapped_wa_event_potentially_with_joined_rows(
        mapped_wa_event_data_without_empty
    )

    update_raw_mapped_registration_data(
        object_store=object_store, registration_data=mapped_wa_event_data, event=event
    )
