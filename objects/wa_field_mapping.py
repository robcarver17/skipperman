import pandas as pd

SKIPPERMAN_FIELD_COLUMN_VALUE = "skipperman_field"
WA_FIELD_COLUMN_KEY = "wa_field"

class WAFieldMapping(dict):
       @classmethod
       def from_df(cls, df: pd.DataFrame):
              try:
                     skipperman_field_values = df[SKIPPERMAN_FIELD_COLUMN_VALUE]
                     wa_field_values = df[WA_FIELD_COLUMN_KEY]
              except KeyError:
                     raise Exception("WA field dataframe must contain %s and %s" % (
                            SKIPPERMAN_FIELD_COLUMN_VALUE,
                            WA_FIELD_COLUMN_KEY
                     ))

              list_of_mapping = \
                     [(wa_field_key,
                       skipper_man_field_value)
                     for wa_field_key, skipper_man_field_value in zip(
                            wa_field_values,
                            skipperman_field_values
                     )
              ]

              return cls(list_of_mapping)

       def to_df(self) -> pd.DataFrame:
              skipperman_field_values = list(self.values())
              wa_field_values = list(self.keys())
              return pd.DataFrame(
                     {
                            WA_FIELD_COLUMN_KEY: wa_field_values,
                            SKIPPERMAN_FIELD_COLUMN_VALUE: skipperman_field_values
                     }
              )



required_wa_fields = [

]

contact_wa_fields = [
'First name', 'Last name',
       'Email for Club Communications', 'Primary Telephone Contact',
'Named Responsible Adult for the event',
       'Emergency Contact Number'
]

volunteer_wa_fields = [
'Can you or someone else volunteer as an adult helper?',
       'Adult Helper 1 Full Name', 'Adult helper 1 preferred duties',
       'Adult helper 1: Would you rather do the same type of duty all week or varied?',
       'Adult Helper 1 Availability',
       'Adult Helper 1 Food Preferences/Allergies', 'Adult Helper 2 Full Name',
       'Adult helper 2 preferred duties', 'Adult Helper 2 Availability',
       'Adult helper 2: Would you rather do the same type of duty all week or varied?',
       'Adult Helper 2 Food Preferences/Allergies']

temp_membership = [
'Temporary membership names',
       'Number of temporary memberships required']

cadet_details = [
'Cadet First Name',
       'Cadet Last Name', 'Cadet Date of Birth', 'Cadet Tee Shirt Size',
       'Highest qualification achieved', 'Group preference',
       'Cadet Do you have your own boat?', 'Cadet Own Boat Sail Number',
       'Cadet Own Boat Class', 'Alternative club boat if available',
       'If sailing double-handed, please enter the name of who you are sailing with',
       'Cadet Can you swim at least 25 metres?',
       'Cadet Do you have a suitable buoyancy aid?',
       'Cadet Details of Any Medical Conditions',
       'Cadet Food Preferences/Allergies',
       'Cadet Any other information about this cadet including medical conditions?']

food_tickets =[
       'Weekly food ticket for child under 16',
       'Weekly food ticket(s) for adult who is not volunteering',
       'Weekly food ticket for adult who is volunteering for one day',
       'Weekly food ticket for adult who is volunteering for two days',
       'Gala dinner only tickets']\


registration_details = [
       'Total fee incl. extra costs and guests registration fees',
       'Payment state',
       'Event registration date',
           'Member'],
