import pandas as pd
from app.data_access.csv.generic_csv_data import GenericCsvData

from app.data_access.classes.volunteers import *
from app.objects.volunteers_at_event import ListOfVolunteersAtEvent

LIST_OF_VOLUNTEERS_FILE_ID = "list_of_volunteers"

class CsvDataListOfVolunteers(GenericCsvData, DataListOfVolunteers):

    def read(self) -> ListOfVolunteers:
        list_of_volunteers = self.read_and_return_object_of_type(ListOfVolunteers, file_identifier=LIST_OF_VOLUNTEERS_FILE_ID)

        return list_of_volunteers

    def write(self, list_of_volunteers: ListOfVolunteers):
        self.write_object(list_of_volunteers, file_identifier=LIST_OF_VOLUNTEERS_FILE_ID)

LIST_OF_VOLUNTEER_SKILLS_FILE_ID = "list_of_volunteer_skills"

class CsvDataListOfVolunteerSkills(GenericCsvData, DataListOfVolunteerSkills):

    def read(self) -> ListOfVolunteerSkills:
        list_of_volunteer_skills = self.read_and_return_object_of_type(ListOfVolunteerSkills, file_identifier=LIST_OF_VOLUNTEER_SKILLS_FILE_ID)

        return list_of_volunteer_skills

    def write(self, list_of_volunteer_skills: ListOfVolunteerSkills):
        self.write_object(list_of_volunteer_skills, file_identifier=LIST_OF_VOLUNTEER_SKILLS_FILE_ID)

LIST_OF_VOLUNTEER_ASSOCIATIONS_FILE_ID ="list_of_cadet_volunteer_associations"

class CsvDataListOfCadetVolunteerAssociations(GenericCsvData, DataListOfCadetVolunteerAssociations):

    def read(self) -> ListOfCadetVolunteerAssociations:
        list_of_cadet_volunteer_associations = self.read_and_return_object_of_type(ListOfCadetVolunteerAssociations,
                                                                                   file_identifier=LIST_OF_VOLUNTEER_ASSOCIATIONS_FILE_ID)

        return list_of_cadet_volunteer_associations

    def write(self, list_of_cadet_volunteer_associations: ListOfCadetVolunteerAssociations):
        self.write_object(list_of_cadet_volunteer_associations, file_identifier=LIST_OF_VOLUNTEER_ASSOCIATIONS_FILE_ID)


LIST_OF_VOLUNTEERS_AT_EVENT_FILE_ID = "list_of_volunteers_at_event"

class CsvDataListOfVolunteersAtEvent(GenericCsvData, DataListOfVolunteersAtEvent):

    def read(self, event_id: str) -> ListOfVolunteersAtEvent:
        list_of_volunteers_at_event = self.read_and_return_object_of_type(ListOfVolunteersAtEvent,
                                                                          file_identifier=LIST_OF_VOLUNTEERS_AT_EVENT_FILE_ID,
                                                                          additional_file_identifiers=event_id)

        return list_of_volunteers_at_event

    def write(self, list_of_volunteers_at_event: ListOfVolunteersAtEvent, event_id: str):
        self.write_object(list_of_volunteers_at_event,
                          file_identifier=LIST_OF_VOLUNTEERS_AT_EVENT_FILE_ID,
                          additional_file_identifiers=event_id)

LIST_OF_CADETS_WITHOUT_VOLUNTEERS_AT_EVENT_FILE_ID = "list_of_cadets_without_volunteers_at_event"

class CsvDataListOfCadetsWithoutVolunteersAtEvent(GenericCsvData, DataListOfCadetsWithoutVolunteersAtEvent):

    def read(self) -> ListOfCadetsWithoutVolunteersAtEvent:
        return self.read_and_return_object_of_type(ListOfCadetsWithoutVolunteersAtEvent,
                                                    file_identifier=LIST_OF_CADETS_WITHOUT_VOLUNTEERS_AT_EVENT_FILE_ID)


    def write(self, list_of_cadets_without_volunteers_at_event: ListOfCadetsWithoutVolunteersAtEvent):
        self.write_object(list_of_cadets_without_volunteers_at_event,
                          file_identifier=LIST_OF_CADETS_WITHOUT_VOLUNTEERS_AT_EVENT_FILE_ID)

