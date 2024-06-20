from typing import Union

from app.backend.volunteers.warnings import warn_on_all_volunteers_availability, warn_on_all_volunteers_group, \
    warn_on_all_volunteers_unconnected, warn_on_cadets_which_should_have_volunteers, warn_on_volunteer_qualifications
from app.objects.abstract_objects.abstract_lines import ListOfLines, DetailListOfLines

from app.objects.abstract_objects.abstract_interface import abstractInterface


def warn_on_all_volunteers(interface: abstractInterface) -> Union[DetailListOfLines, str]:
    available_warnings = warn_on_all_volunteers_availability(interface)
    group_warnings = warn_on_all_volunteers_group(interface)
    missing_cadets = warn_on_all_volunteers_unconnected(interface)
    cadets_with_no_volunteer = warn_on_cadets_which_should_have_volunteers(interface)
    qualification_warnings = warn_on_volunteer_qualifications(interface)

    all_warnings = available_warnings+group_warnings+missing_cadets+cadets_with_no_volunteer+qualification_warnings

    if len(all_warnings)==0:
        return ''

    return DetailListOfLines(ListOfLines(all_warnings).add_Lines(), name="Warnings")


