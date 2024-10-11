from typing import Union

from app.OLD_backend.rota.warnings import (
    warn_on_volunteer_qualifications,
)
from app.backend.OLD_patrol_boats.patrol_boat_warnings import warn_on_pb2_drivers
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_lines import ListOfLines, DetailListOfLines

from app.objects.abstract_objects.abstract_interface import abstractInterface


def warn_on_all_volunteers_in_patrol_boats(
    interface: abstractInterface,
) -> Union[DetailListOfLines, str]:
    event = get_event_from_state(interface)
    qualification_warnings = warn_on_volunteer_qualifications(cache=interface.cache, event=event)
    pb2driver_warnings = warn_on_pb2_drivers(interface)

    all_warnings = qualification_warnings + pb2driver_warnings

    if len(all_warnings) == 0:
        return ""

    return DetailListOfLines(ListOfLines(all_warnings).add_Lines(), name="Warnings")
