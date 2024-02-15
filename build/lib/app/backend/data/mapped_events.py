from app.data_access.data import data
from app.objects.events import Event
from app.objects.mapped_wa_event import MappedWAEvent, RowInMappedWAEvent



def save_mapped_wa_event(
    mapped_wa_event_data: MappedWAEvent,
    event: Event,
):
    data.data_mapped_wa_event.write(
        mapped_wa_event=mapped_wa_event_data, event_id=event.id
    )


def load_mapped_wa_event(
    event: Event,
) -> MappedWAEvent:
    return data.data_mapped_wa_event.read(event.id)

def get_row_in_mapped_event_data_given_id(event: Event, row_id: str) -> RowInMappedWAEvent:
    mapped_data = load_mapped_wa_event(event)
    return mapped_data.get_row_with_rowid(row_id)
