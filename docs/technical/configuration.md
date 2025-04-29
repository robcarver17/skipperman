

The [configuration file](/app/data_access/configuration/configuration.yaml) allows technically minded users of Skipperman to change certain defaults without needing to write any code (but they will need to know how to edit files on github and [pull them on to the cloud installation](installation.md#installation---existing-cloud-)).

# Websites, files and directories

homepage: "https://bsccadetskipper.pythonanywhere.com/"
#homepage: http://127.0.0.1:5000/
datapath: "skipperman_data" ## directory in users home directory where data stored; only change for test purposes
backuppath: "skipperman_backup"
userdata: "skipperman_user_data" ## special directory for username and password hashes (plus maybe user specific config)
download_subdirectory: "Downloads" ## non public downloads
public_reporting_subdirectory: "public" ## make sure mapped and exposed in pythonanywhere
uploads: "uploads" ## directory in users home directory where uploads are temporarily stored; only change for test purposes
WA_field_list_file: WA_field_list.xlsx
weblink_for_qualifications: "https://docs.google.com/spreadsheets/d/1a0ov-KN8zzG2mdFQCfLK-I6AD1tLihU-z_3tPF2vlV4/edit?usp=sharing"



# Filtering cadet inputs
similarity_level_to_warn_when_comparing_names_on_event_import: 0.7 # change if too many/too few similars coming through
similarity_level_to_match_a_very_similar_cadet_first_name_on_event_import: 0.9 # probably shouldn't change
similarity_level_to_warn_when_comparing_names_in_membership_list: 0.6
#
# volunteer inputs
similarity_level_to_warn_when_comparing_volunteer_names_on_event_import: 0.7
similarity_level_to_match_a_very_similar_volunteer_name_on_event_import: 0.85
#

# Only change the following whenclub rules change
minimum_cadet_age: 7
maximium_cadet_age: 19
minimum_age_when_cadet_can_be_at_event_without_parent: 11
min_colour_groups_to_distribute: 6
cadet_committee_shirt_colour: "Navy Blue"

support_email: rob@systematicmoney.org
#
#
## needs to be large enough to upload a zip with everything - ## this is in Megabytes
max_file_size: 20
#
upload_extensions: ".csv, .xls, .zip"
number_of_backups_to_keep: 10
#


# Wild Apricot status fields

This maps from WA status fields to Skipperman status. Note that it's possible for more than one WA field to map to a Skipperman status field, eg there are two Cancelled fields due to a difference in spelling between WA versions.

```
wild_apricot_payment_fields_which_are_active_and_paid_status:
  - "Paid"
  - "Free"
  - "No invoice"
wild_apricot_payment_fields_which_are_unpaid_status:
  - "Unpaid"
wild_apricot_payment_fields_which_are_part_paid_status:
  - "Partially paid"
wild_apricot_payment_fields_which_are_cancelled_status:
  - "Canceled"
  - "Cancelled"
```

They will need changing if WA changes it's status fields, or a new status is added to Skipperman.

wild_apricot_event_id: "Event ID"
allowed_upload_file_types: ".csv, .xls"

if_volunteer_unable_to_volunteer_contains:
  - 'unable' ## if volunteer status contains this, can't volunteer
  - 'cannot'


# Import skills csv

First two columns are volunteer name, then date format in standard Python strptime lingo. Then are each of the skills. The skills must match the names of Skipperman skills.

For each skill we can eithier specify:

- for a qualification with a fixed expiry, the explicit column name for the expiry date
- for a qualification with a start date but no end date (eg AI), the 'valid from' date
- for a qualification with a fixed expiry but where the spreadsheet has the start date (eg First Aid), the 'starts from' date and the number of years it lasts for.

```
import_skills_csv: ## names have to correspond to configuration names
  first_name: 'First Name'
  last_name: 'Last Name'
  date_format: '%d-%b-%Y'
  skills:
    DI:
      expires: 'Dinghy Instructor (DI) '
    SI:
      expires: 'Senior Instructor (SI)'
    RCL2:
      expires: 'Racing Coach 2 (RC)'
    AI:
      valid_from: 'Assistant Instructor (AI)'
    First aid:
      starts_from: 'First Aid (FA)'
      expiry_limit_years: 3
```

pytz_timezone: 'GB'