from app.backend.data.resources import load_list_of_cadets_at_event_with_club_dinghies, load_list_of_club_dinghies, save_list_of_cadets_at_event_with_club_dinghies
from app.objects.events import Event
from app.objects.club_dinghies import NO_BOAT

def update_club_boat_allocation_for_cadet_at_event(boat_name: str, cadet_id: str, event: Event):
    cadets_with_club_dinghies_at_event = load_list_of_cadets_at_event_with_club_dinghies(event)
    if boat_name==NO_BOAT:
        cadets_with_club_dinghies_at_event.delete_allocation_for_cadet(cadet_id)
    else:
        club_dinghies = load_list_of_club_dinghies()
        boat_id = club_dinghies.id_given_name(boat_name)
        cadets_with_club_dinghies_at_event.update_allocation_for_cadet(cadet_id=cadet_id, club_dinghy_id=boat_id)

    save_list_of_cadets_at_event_with_club_dinghies(event=event, cadets_with_club_dinghies_at_event=cadets_with_club_dinghies_at_event)
