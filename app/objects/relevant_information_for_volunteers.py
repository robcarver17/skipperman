from dataclasses import dataclass

from app.objects.day_selectors import DaySelector


@dataclass
class RelevantInformationForVolunteerIdentification:
    passed_name: str
    cadet_id: str
    cadet_surname: str
    registered_by_firstname: str
    self_declared_status: str
    any_other_information: str ## information only - double counted as required twice


@dataclass
class RelevantInformationForVolunteerDetails: ##copied across
    food_preference: str
    any_other_information: str ## information only - double counted as required twice

@dataclass
class RelevantInformationForVolunteerAvailability:
    day_availability: str
    weekend_availability: str
    cadet_availability: DaySelector
    preferred_duties: str ## information only
    same_or_different: str ## information only
    any_other_information: str ## information only - double counted as required twice


@dataclass
class RelevantInformationForVolunteer:
    identify: RelevantInformationForVolunteerIdentification
    availability: RelevantInformationForVolunteerAvailability
    details: RelevantInformationForVolunteerDetails


