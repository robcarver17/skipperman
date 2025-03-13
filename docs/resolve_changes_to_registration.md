When updating with a new file, we can get conflicts between the original data stored in Skipperman, and the updated data in the uploaded file.

[TOC]

# Errors and warnings

## More than one active registration in the new file for a given sailor 

```
ACTION REQUIRED: Cadet John Smith (2000-01-01) Member appears more than once in WA file with multiple active registrations - ignoring any possible changes made to registration - go to WA and cancel one of the registrations please!
```

As it says, this means the cadet has been registered multiple times, but the duplicate registrations have not been cancelled. Any changes made to these registrations in Wild Apricot will be ignored by Skipperman. If you allow a duplicate registration to occur, the best thing to do is to cancel the duplicated registrations in Wild Apricot and then re-import the data. Make sure that the details in the remaining registration on Skipperman reflect what the parent actually wants to do.


## Missing sailor in registration file

```
Cadet John Smith (2000-01-01) Member was in imported data, now appears to be missing in latest file - possible data corruption of imported file or manual hacking - no changes in file will be reflected in Skipperman
```

This can happen if:

- You have [added a sailor manually](link_required.md) to Skipperman who has not been registered in Wild Apricot, and their status is not 'Manual'. You can ignore this message, but to make it go away eithier change the [registration status to manual](link_required.md) which would be appropriate for a free event like a racing series, or ask their parent to register them (required for a paid for event).
- For some stupid reason you have manually edited the data file exported from Wild Apricot and remove one or more rows. Unless you're an expert trying to debug something, don't do this. Instead, change the registration status to ['Cancelled'](link_required.md). Meanwhile, you can ignore this error.
- Wild Apricot themselves have changed their export output, or Skipperman has managed to corrupt it's own data. Please contact support - this is serious.

# Status and availability changes

The payment **status** of a registration can be eithier *active* (eg paid, unpaid, partially paid or manual) or *inactive* (eg cancelled). 
The **availability** of a registration is the days that a sailor is attending a given event. 

If the status or availability of a registration has changed, this will be flagged for confirmation. Other changes will not be made in the Skipperman data. As a rule, only changes to payment status and days attending should be made in Wild Apricot. 

## Changes to status

If the **status** of the registration changes, you will see a screen like this:

***
***
![cancelled_registration.png](/static/cancelled_registration.png)
***
***

Possible messages are:

**Sailor John Smith (2000-01-01) Member was cancelled; now active so probably new registration replacing the existing cancelled one**

The original registration was cancelled (eithier in Wild Apricot and/or Skipperman), and has now been 'un-cancelled', or a new registration has been made.

The status of the registration will be reset to the active status in Wild Apricot (eg paid, unpaid, partially paid); but **no other information will be updated**. That means if a new registration has been made where some of the details are different, Skipperman won't see the new details. You will have to edit Skipperman's [registration data](link_required.md) manually.

For this reason it's generally bad not to have parents make more than one registration for a given sailor. If a registration gets cancelled, it is better to 'un-cancel' it, than to have another registration put in. This also makes life easier for the BSC treasurer. 

Generally registrations should only be cancelled if the sailor is not attending, and then un-cancelled if they change their mind. Do not cancel registrations if there has been a mistake in the form. 

**Sailor John Smith (2000-01-01) Member was active now cancelled, so probably cancelled in original data**

The original registration has been cancelled in Wild Apricot, so we will update Skipperman to reflect this. This will remove the sailor from active participation in the event; if they have a sailing partner you will see a warning about the fact they will no longer have someone to sail with. Fix this in the [group allocation page](link_required.md).

**Sailor John Smith (2000-01-01) is still active but status has changed from unpaid/partially paid/paid to unpaid/partially paid/paid**

A payment has been made in Wild Apricot, which will move the status from unpaid, to partially paid, and eventually to paid. It's also possible that payment status can go backwards, if the treasurer voids the invoice for some reason. Skipperman will update it's payment status to reflect the change. 

**Sailor John Smith (2000-01-01) is still active but status has changed from manual to unpaid/partially paid/paid**

This happens when you manually add a sailor (eithier through the 'Add Name as new cadet' button on the [group allocation page](link_required.md) in the allocate two handed partner column, or the 'add a sailor' button on the same page or the [registration page](link_required.md)). Sailors added this way default to a status of 'Manual'. This is fine for racing events where members don't usually have to pay, but for a training event or Cadet Week you would probably want them to actually register. 

At the point where they do register, and this is reflected in the WA imported data, you will see this warning.

**IMPORTANT** No information in the WA registration will be updated in Skipperman, apart from the payment status and availability. So if the manual registration was wrong, you will need to fix it by [editing the registration in Skipperman](link_required.md).

**Existing sailorJohn Smith (2000-01-01) Member data was deleted (missing from event spreadsheet); now active so probably manual editing of import file has occured**  
**Sailor John Smith (2000-01-01) Member was deleted (missing from event spreadsheet); now cancelled so probably manual editing of import file has occured**  
**Sailor John Smith (2000-01-01) status change from X to Y, shouldn't happen! Check the registration very carefully!**  

If you see any of the above messages, contact support. They shouldn't happen.

## Changes to availability

If the days the cadet is available changes, you will see a screen like this:

![change_registration_days.png](/static/change_registration_days.png)

## Options

If you have the option to change availability and/or status, you then have three options:

- Use the original data in Skipperman (which ignores any updates made in Wild Apricot)
- Use the data in the form. You can select a different status and/or available days. If you don't make any changes in the form, choosing this button will be the same as using the new data from Wild Apricot, since the form is prepopulated with new data.
- Use the new data imported from Wild Apricot (recommended)
