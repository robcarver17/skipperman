import pandas as pd
from app.data_access.csv.generic_csv_data import GenericCsvData

from app.data_access.classes.volunteers import *
from app.objects.volunteers_at_event import ListOfVolunteersAtEvent


class CsvDataListOfVolunteers(GenericCsvData, DataListOfVolunteers):

    def read(self) -> ListOfVolunteers:
        path_and_filename = self.path_and_filename()
        try:
            list_as_df = pd.read_csv(path_and_filename)
        except:
            return ListOfVolunteers.create_empty()
        list_of_volunteers = ListOfVolunteers.from_df_of_str(list_as_df)

        return list_of_volunteers

    def write(self, list_of_volunteers: ListOfVolunteers):
        df = list_of_volunteers.to_df()
        path_and_filename = self.path_and_filename()

        df.to_csv(path_and_filename, index=False)

    def path_and_filename(self):
        return self.get_path_and_filename_for_named_csv_file(
            "list_of_volunteers"
        )

class CsvDataListOfVolunteerSkills(GenericCsvData, DataListOfVolunteerSkills):

    def read(self) -> ListOfVolunteerSkills:
        path_and_filename = self.path_and_filename()
        try:
            list_as_df = pd.read_csv(path_and_filename)
        except:
            return ListOfVolunteerSkills.create_empty()
        list_of_volunteer_skills = ListOfVolunteerSkills.from_df_of_str(list_as_df)

        return list_of_volunteer_skills

    def write(self, list_of_volunteer_skills: ListOfVolunteerSkills):
        df = list_of_volunteer_skills.to_df()
        path_and_filename = self.path_and_filename()

        df.to_csv(path_and_filename, index=False)

    def path_and_filename(self):
        return self.get_path_and_filename_for_named_csv_file(
            "list_of_volunteer_skills"        )


class CsvDataListOfCadetVolunteerAssociations(GenericCsvData, DataListOfCadetVolunteerAssociations):

    def read(self) -> ListOfCadetVolunteerAssociations:
        path_and_filename = self.path_and_filename()
        try:
            list_as_df = pd.read_csv(path_and_filename)
        except:
            return ListOfCadetVolunteerAssociations.create_empty()
        list_of_cadet_volunteer_associations = ListOfCadetVolunteerAssociations.from_df_of_str(list_as_df)

        return list_of_cadet_volunteer_associations

    def write(self, list_of_cadet_volunteer_associations: ListOfCadetVolunteerAssociations):
        df = list_of_cadet_volunteer_associations.to_df()
        path_and_filename = self.path_and_filename()

        df.to_csv(path_and_filename, index=False)

    def path_and_filename(self):
        return self.get_path_and_filename_for_named_csv_file(
            "list_of_cadet_volunteer_associations"
        )


class CsvDataListOfVolunteersAtEvent(GenericCsvData, DataListOfVolunteersAtEvent):

    def read(self, event_id: str) -> ListOfVolunteersAtEvent:
        path_and_filename = self.path_and_filename_for_event(event_id=event_id)
        try:
            list_as_df = pd.read_csv(path_and_filename)
        except:
            return ListOfVolunteersAtEvent.create_empty()
        list_of_volunteers_at_event = ListOfVolunteersAtEvent.from_df_of_str(list_as_df)

        return list_of_volunteers_at_event

    def write(self, list_of_volunteers_at_event: ListOfVolunteersAtEvent, event_id: str):
        df = list_of_volunteers_at_event.to_df()
        path_and_filename = self.path_and_filename_for_event(event_id)

        df.to_csv(path_and_filename, index=False)

    def path_and_filename_for_event(self, event_id: str):
        return self.get_path_and_filename_for_named_csv_file(
            "list_of_volunteers_at_event",
            additional_file_identifiers=event_id,
        )
