from typing import Union

from app.backend.volunteers.warnings import warn_on_all_volunteers_group, \
    warn_on_all_volunteers_unconnected, warn_on_cadets_which_should_have_volunteers, warn_on_volunteer_qualifications, \
    warn_on_pb2_drivers
from app.objects.abstract_objects.abstract_lines import ListOfLines, DetailListOfLines

from app.objects.abstract_objects.abstract_interface import abstractInterface


def warn_on_all_volunteers_in_patrol_boats(interface: abstractInterface) -> Union[DetailListOfLines, str]:
    qualification_warnings = warn_on_volunteer_qualifications(interface)
    pb2driver_warnings = warn_on_pb2_drivers(interface)

    all_warnings = qualification_warnings+pb2driver_warnings

    if len(all_warnings)==0:
        return ''

    return DetailListOfLines(ListOfLines(all_warnings).add_Lines(), name="Warnings")

