- To see the volunteer warnings for an event, from the **main menu** choose **Events**, then select an event, then click on **Volunteers**; finally choose the ► Active Warnings and/or ► Ignored warnings

- To access the cadet warnings for an event, from the **main menu** select **Events**, choose your event, and then click on **Edit sailors registration data**; finally choose the ► Active Warnings and/or ► Ignored warnings 

___


[TOC]

# Overview of warnings

Warnings are generated in two ways:

- When an import is done
- Based on the current data in the system

The latter can be *cleared* (by changing the data) or *ignored* (if the warning doesn't bother you), whilst the former can only be *ignored*.

## Active warnings

Warnings that are active (not ignored) will appear here. Warnings appear sorted by priority, and then by category.

You can eithier *clear* warnings (eg if someone is not qualified as a DI, add them as a DI), or click on them to be *ignored* (and then press `Save changes to warnings`). Remember, if a warning is generated during the registration import, it has to be ignored, it can't be cleared.

Alternatively, you can ignore a group of warnings (same priority and category) by pressing the relevant button above the group. That will also save any changes to warning checkboxes.

Once warnings are ignored, they appear in the `Ignored warnings` section.

## Ignored warnings

Warnings that have been ignored appear here. You can 'unignore' them by clicking the checkbox and pressing `Save changes to warnings`.

Alternatively, you can unignore a group of warnings (same priority and category) by pressing the relevant button above the group. That will also save any changes to warning checkboxes.

# Warnings on import - cadets

- Permanently skipped rows
- Assumed identity in imported record
- Duplicate registrations
- Mysteriously missing cadets

## Permanently skipped rows

```
Permanently skipping cadet Jon Doe row id ...
```
This just means you have skipped a test row; it's useful to know this if you find a registration has 'vanished' from Skipperman it could be an accidental skip.

## Assumed identity

If the cadet in the registration is very similar to a single existing cadet, then Skipperman will add it but flag it like this:

```
Found cadet John Doe (2001-10-01) Member, looks a very close match for Jon Doe (2025-01-10) Unconfirmed member in registration data. If not correct, replace in edit registration page.
```

This is to avoid common problems with mismatches causing annoying requests to check cadet details:

- using the current year for the date of birth instead of the actual one (as above)
- getting day and month mixed up in a date entry field (as above)
- slightly misspelling the name (as above)
- for racing events, not including the date of birth on the entry form

It won't deal with names that are very different. 

- if they are the right cadet, ignore the error
- if they are not, then from the [registration edit page](registration_editing_help.md) change their status to cancelled. Then [add a new registration](registration_editing_help.md#adding-a-sailor-manually).

## Duplicated registrations

```
ACTION REQUIRED: Cadet NAME appears more than once in imported file with an active registration - using the first registration found - go to WA and cancel all but one of the registrations please, and then check details here are correct!
```

As it says, this means the cadet has been registered multiple times, but the duplicate registrations have not been cancelled. Any registrations found in the file after the first one that is loaded in will be ignored.

To avoid this, strongly discourage parents from re-registering cadets if they have made a mistake (something they are typically going to do because Wild Apricot doesn't allow you to edit a registration, with good reason). Instead:

- if the change will modify the amount to be paid (eg number of days attending), make the change yourself in Wild Apricot
- if the change won't affect payment, make the change in Skipperman itself.

Any registrations found in the file after the first one that is loaded in will be ignored.  If you allow a duplicate registration to occur, the best thing to do is to cancel the duplicated registrations in Wild Apricot and then re-import the data. Make sure that the details in the remaining registration on Skipperman reflect what the parent actually wants to do. Then you can ignore the error.

After an event update you might see this error:

```
ACTION REQUIRED: Cadet NAME appears more than once in WA file with multiple active registrations - ignoring any possible changes made to registration - go to WA and cancel one of the registrations please!
```

... which has the same symptoms and treatment.


## Mysteriously vanishing cadets

```
ACTION REQUIRED: Cadet Name vanished from raw registration data file - should not happen: contact support"
```
This should not happen - contact support!

After an update to an event you might see:

```
Cadet Name was in imported data, now appears to be missing in latest file - possible data corruption of imported file or manual hacking - no changes in file will be reflected in Skipperman
```

This can happen if:

- For some stupid reason you have manually edited the data file exported from Wild Apricot and remove one or more rows. Unless you're an expert trying to debug something, don't do this. Instead, change the registration status to ['Cancelled'](registration_editing_help.md). Meanwhile, you can ignore this error.
- Wild Apricot themselves have changed their export output, or Skipperman has managed to corrupt it's own data. Please contact support - this is serious!!!

# Warnings on import - volunteers

For each volunteer attending an event, we will get warnings if:

- a very similar volunteer was added
- A volunteer says they cannot help (if "Volunteer status" [field](List_and_explanation_of_skipperman_fields.md) used in event, and is correctly populated, eg contains 'cannot' or 'unable')
- volunteer availability is inconsistent across registrations (eg if they are associated with more than one cadet)
- volunteer duty preference is inconsistent over multiple registrations

## A volunteer that was not precisely identified

```
Assumed volunteer John Doe was identical to volunteer Jon Doe in registration data"
```

- If the correct voluteer has been idenitifed, click on ignore.
- If the wrong volunteer has been identified: [delete the volunteer](volunteer_rota_help.md#removing-a-volunteer-from-an-event) and [add the correct volunteer](volunteer_rota_help.md#add-a-volunteer).


## A volunteer that cannot help

If the [skipperman field](List_and_explanation_of_skipperman_fields.md) 'Volunteer status' is used for an event, and that field contains 'unable' or 'cannot', then the volunteer will be marked as unable to help.

```
Volunteer Jon Smith says they are unable to volunteer, according to at least one registration: ...
```

They will appear in the rota but with no days selected as available.

- if the volunteer really can't help: ignore the warning. You may also want to [remove them from the event](volunteer_rota_help.md#removing-a-volunteer-from-an-event)
- if the volunteer can help; click to ignore the warning. [Select the days they are available in the rota](volunteer_rota_help.md#adding-removing-and-changing-volunteer-availability)

## Conflicts with availablity

```
Inconsistency between availability for Jon Smith across registrations for different sailors: Saturday, Sunday OR Saturday
```

Check with the volunteer, then once you know their availability click ignore and [select the days they are available in the rota](volunteer_rota_help.md#adding-removing-and-changing-volunteer-availability)

## Duty preference conflicts

```
Inconsistency on preferred duties across registrations for volunteer  
Inconsistency on same/different duties across registrations for volunteer
```

These can probably be safely ignored unless their preference is critical; contact the volunteer to clarify, and add notes in the [rota](volunteer_rota_help.md)


# Warnings based on current data

## Cadet registration page

In the [cadet registration page](registration_editing_help.md#warnings), you will see the following warnings based on current data:

- Cadets which have been skipped temporarily in registration import
- Cadets which were added manually
- Cadets without appropriate adults
- Cadets without confirmed dates of birth


### Temporarily skipped cadets in registration import

```
On import, temporarily skipped identifying sailor registered as Jane Doe in row with ID 2023/05/25 08:00:42.000000_doe_jon 
```

To clear the error, go back to the [import registration data](import_registration_data_help.md) screen and click on 'Update data using current WA file'. Then for the relevant cadets, eithier:

- mark as permanently skipped (test entry)
- mark as an existing Cadet
- add as a new Cadet

You can also ignore the error, but there should be no good reason to do this.

### Cadets which were added manually

```
Cadet Jonny Doe has been registered manually - OK if no training and unpaid event
```

This will happen if you add a cadet manually on the [group allocation](group_allocation_help.md) or [edit registration](registration_editing_help.md) pages, or click on 'Add a sailing partner' in the [group allocation page](group_allocation_help.md). Eithier:

- If it's a racing event without payment and no registration is required, ignore.
- To clear, ensure the cadet is registered in WA then [import the updated registration data](import_registration_data_help.md#updating-an-event). 

### Cadets without adults

```
Cadet Name is too young to be at the event by themselves but has no connected volunteer (Declared volunteer status: ...)
```

- they have a volunteer at the event, but they are not formally connected: click on the location button next to the volunteer name in the [rota](volunteer_rota_help.md) and add the connected cadet; or [edit the volunteer](view_individual_volunteer_help.md). This will clear the warning.
- they have an adult who is not volunteering, but will be on site. [Add them as a volunteer](volunteer_rota_help.md#add-a-volunteer) - select 'Parent on site, not volunteering' from the dropdown before you click add or select the relevant volunteer. In the rota they should show as having no available days; make a note of what you have. This will clear the error.

This should ideally never be ignored.

### Cadets without confirmed dates of birth

```
Cadet Name has unknown date of birth - needs confirming
```

If a cadet has an unconfirmed date of birth, this can be cleared by adding their actual date of birth in the [editing sailors page](view_and_edit_individual_cadet_help.md). You can also ignore it for now - it will come up again at the next event they do.


## Volunteer rota

In the [volunteer rota](volunteer_rota_help.md#warnings) you will see the following warnings based on data:

- Volunteer temporarily skipped on import
- Unqualified volunteers
- Cadets without appropriate adults
- Volunteers who are at the lake with one or more connected cadets, or worse still allocated to a sailing group that their cadet is in. 
- A mismatch between cadet availability and volunteer availability 
- A volunteer without any connected cadets

## A volunteer that was temporarily skipped

```
Temporarily skipping volunteer probably called Jon Doe in row 2023/05/25 08:00:42.000000_doe_jon id 0
```

Go back to the import page, and re-import the data. Then eithier:

- mark the volunteer as permanently skipped
- identify with an existing volunteer
- add as a completely new volunteer

## Unqualified volunteers

```
Name is not qualified for role(s): for RoleName needs: list of skills
```

- if you are **SURE** they actually qualified, click on the skills button next to the volunteer in the [rota](volunteer_rota_help.md) and add the relevant skills. This will clear the warning.
- move them to another job they are qualified for, in the [rota](volunteer_rota_help.md#changing-roles-and-groups)

This should ideally never be ignored.

## Cadets without appropriate adults

```
Cadet name is too young to be at the event by themselves but has no connected volunteer (Declared volunteer status: ...)
```

- they have a volunteer at the event, but they are not formally connected: click on the location button next to the volunteer name in the [rota](volunteer_rota_help.md) and add the connected cadet; or [edit the volunteer](view_individual_volunteer_help.md). This will clear the warning.
- they have an adult who is not volunteering, but will be on site. [Add them as a volunteer](volunteer_rota_help.md#add-a-volunteer) - select 'Parent on site, not volunteering' from the dropdown before you click add or select the relevant volunteer. In the rota they should show as having no available days; make a note of what you have. This will clear the error.

This should ideally never be ignored.

## Volunteers who are at the lake with one or more connected cadets, or allocated to a sailing group that their cadet is in

```
Volunteer Name is in lake role, but has cadet at lake
Volunteer Name and cadet are both in group .... 
```

- [Change the volunteer to a different location/role/group](volunteer_rota_help.md#changing-roles-and-groups). This will clear the error.
- Or if you don't care, ignore the warning.

## Availability mismatch

```
Volunteer name: On SUNDAY, sailors are attending but volunteer is not: Sailor name
Volunteer name: On SATURDAY volunteer attending; but associated sailors Sailor are not attending
```

Check with the volunteer that this is correct. 

- if the availability for the cadet is wrong, go to the edit registration page for the event and update it. You may also want to get the registration changed in WA if this will generate an invoice change.
- if the availability for the volunteer is wrong, [change it in the rota](volunteer_rota_help.md#adding-removing-and-changing-volunteer-availability)

## No connected cadets

```
Volunteer name is not connected to any active (not cancelled) cadets at this event
```

 This could be because they have agreed to help anyway, but it could also be because the cadet has cancelled their registration and you haven't removed the volunteer - check with the volunteer if you aren't sure.
 
- they really have no cadets - click ignore.
- they have a cadet registered but they are not formally connected: click on the location button next to the volunteer name in the [rota](volunteer_rota_help.md) and add the connected cadet; or [edit the volunteer](view_individual_volunteer_help.md). This will clear the warning.
- they have cadets at the event without an active registration. Eithier [add them manually](registration_editing_help.md#adding-a-sailor-manually), or get them to register in WA and [import the updated registration data](import_registration_data_help.md). This will clear the warning.
