

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
