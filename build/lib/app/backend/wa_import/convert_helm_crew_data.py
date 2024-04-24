import datetime
from copy import copy

from app.backend.data.cadets_at_event import load_list_of_cadets_at_event_with_dinghies, DEPRECATED_load_cadets_at_event, \
    get_cadet_at_event
from app.backend.data.mapped_events import DEPRECCATE_save_mapped_wa_event, DEPRECATE_load_mapped_wa_event
from app.backend.group_allocations.boat_allocation import update_boat_info_for_updated_cadets_at_event
from app.backend.wa_import.add_cadet_ids_to_mapped_wa_event_data import DEPRECATE_add_identified_cadet_and_row
from app.backend.wa_import.update_cadets_at_event import DEPRECATED_get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active, \
    DEPRECATE_add_new_cadet_to_event
from app.data_access.configuration.field_list import HELM_SURNAME, HELM_FIRST_NAME, CREW_SURNAME, CREW_FIRST_NAME, CADET_FIRST_NAME, CADET_SURNAME, CADET_DOUBLE_HANDED_PARTNER

from app.objects.cadets import Cadet, DEFAULT_DATE_OF_BIRTH
from app.objects.constants import missing_data
from app.objects.dinghies import ListOfCadetAtEventWithDinghies, CadetAtEventWithDinghy
from app.objects.events import Event
from app.objects.mapped_wa_event import MappedWAEvent, RowInMappedWAEvent, manual_add_status
from app.objects.utils import in_both_x_and_y

def convert_mapped_wa_event_potentially_with_joined_rows(mapped_wa_event: MappedWAEvent)-> MappedWAEvent:
    for row in mapped_wa_event:
        if does_row_contain_helm_and_crew(row):
            modify_row(row)
        else:
            continue

    return mapped_wa_event


def does_row_contain_helm_and_crew(row: RowInMappedWAEvent)-> bool:
    fields = list(row.keys())
    return len(in_both_x_and_y(fields, [HELM_SURNAME, HELM_FIRST_NAME, CREW_SURNAME, CREW_FIRST_NAME]))>0

def modify_row(row: RowInMappedWAEvent):

    helm_first_name = row.pop(HELM_FIRST_NAME)
    helm_surname = row.pop(HELM_SURNAME)

    crew_first_name = row.pop(CREW_FIRST_NAME)
    crew_surname = row.pop(CREW_SURNAME)

    crew_name = "%s %s" % (crew_first_name, crew_surname)

    ## no date of births, they will be blank

    row[CADET_FIRST_NAME] = helm_first_name
    row[CADET_SURNAME] = helm_surname
    row[CADET_DOUBLE_HANDED_PARTNER] = crew_name

def from_partner_name_to_cadet(partner_name: str) -> Cadet:
    if len(partner_name)>0:
        partner_name_split = partner_name.split(" ")
        if len(partner_name_split)>1:
            first_name = " ".join(partner_name_split[:-1])
            second_name = partner_name_split[-1]
        else:
            first_name = partner_name
            second_name = ""
    else:
        first_name = second_name = ""

    return Cadet(first_name=first_name, surname=second_name, date_of_birth=DEFAULT_DATE_OF_BIRTH)

def add_matched_partner_cadet_with_duplicate_registration_to_wa_mapped_data(original_cadet: Cadet,
                                                                            new_cadet: Cadet,
                                                                            event: Event):

    new_row = add_new_row_to_wa_event_data_and_return_row(original_cadet=original_cadet, new_cadet=new_cadet, event=event)
    DEPRECATE_add_identified_cadet_and_row(
        event=event, row_id=new_row.row_id, cadet_id=new_cadet.id
    )

    DEPRECATE_add_new_cadet_to_event(
        event=event, row_in_mapped_wa_event=new_row,
        cadet_id=new_cadet.id
    )

    add_two_handed_partnership_for_new_cadet_when_have_dinghy_for_existing_cadet(event=event, original_cadet=original_cadet, new_cadet=new_cadet)

def add_new_row_to_wa_event_data_and_return_row(original_cadet: Cadet,
                                                                            new_cadet: Cadet,
                                                                            event: Event) -> RowInMappedWAEvent:
    mapped_wa_event_data = DEPRECATE_load_mapped_wa_event(event)
    existing_row = DEPRECATED_get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active(
        cadet_id=original_cadet.id, event=event
    )
    new_row = modify_row_to_clone_for_new_cadet_partner(original_cadet=original_cadet, new_cadet=new_cadet, existing_row=existing_row)

    mapped_wa_event_data.append(new_row)
    DEPRECCATE_save_mapped_wa_event(mapped_wa_event_data=mapped_wa_event_data, event=event)

    return new_row

def modify_row_to_clone_for_new_cadet_partner(original_cadet: Cadet,
                                                                            new_cadet: Cadet,
                                                                            existing_row: RowInMappedWAEvent) -> RowInMappedWAEvent:
    new_row = copy(existing_row)

    new_row.registration_date =existing_row.registration_date + datetime.timedelta(0,9) ## otherwise get duplicate key
    new_row.registration_status = manual_add_status ## avoids it being deleted
    new_row[CADET_FIRST_NAME] = new_cadet.first_name
    new_row[CADET_SURNAME] = new_cadet.surname
    new_row[CADET_DOUBLE_HANDED_PARTNER] = original_cadet.name

    return new_row

def add_two_handed_partnership_for_new_cadet_when_have_dinghy_for_existing_cadet(event: Event, original_cadet: Cadet, new_cadet: Cadet, ):
    ## We only need to include the original cadet as will copy over
    list_of_cadets_at_event_with_dinghies=load_list_of_cadets_at_event_with_dinghies(event)
    original_cadet_with_dinghy = list_of_cadets_at_event_with_dinghies.object_with_cadet_id(original_cadet.id)
    assert original_cadet_with_dinghy is not missing_data

    original_cadet_with_dinghy.partner_cadet_id = new_cadet.id

    list_of_updated_cadets = ListOfCadetAtEventWithDinghies([original_cadet_with_dinghy])

    update_boat_info_for_updated_cadets_at_event(event=event, list_of_updated_cadets=list_of_updated_cadets)

def get_registered_two_handed_partner_name_for_cadet_at_event(event: Event, cadet: Cadet) -> str:
    cadet_at_event = get_cadet_at_event(event=event, cadet=cadet)
    return cadet_at_event.data_in_row.get(CADET_DOUBLE_HANDED_PARTNER, '')
