

The [configuration file](/app/data_access/configuration/configuration.yaml) allows technically minded users of Skipperman to change certain defaults without needing to write any code (but they will need to know how to edit files on github and [pull them on to the cloud installation](installation.md#installation---existing-cloud-)).


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
