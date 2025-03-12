
For each volunteer attending an event, Skipperman will check:

- that the volunteer availability is consistent across registrations (eg if they are associated with more than one cadet)
- that the information the volunteer has put down about their duty preference is consistent over multiple registrations
- that the volunteer is attending on days when none of their sailors is not attending (note we don't check to see if the reverse is true - eg a volunteer not coming for all the days their sailor is attending)

You will see a screen like this:

***
***
![volunteer_registration_confirm.png](/static/volunteer_registration_confirm.png)
***
***

At the top of the page you will see all the warnings highlighting what the issues are.

Next we can see all the relevant registration data. If a volunteer is associated with more than one sailor at the event, you will see the registration information for each sailor.

Availability is shown for both sailors and volunteers. If the sailor did not indicate any availability as this was not an option in the form (typically for Cadet week and racing events), it is assumed they are available for the entire event. If a volunteer did not indicate availability, it is assumed they can attend when a cadet attends.

To resolve any discrepancies, you need to confirm with the volunteer what they are actually doing in terms of availability, and clarify their duty preferences. It might be that they have specified the reasons for the discrepancy in other information, or you might know what their real preferences are. In which case:

- Make changes to their availability by modifying the check-boxes under 'Confirm availability for volunteer'. If you leave all the boxes blank, we assume the volunteer isn't attending. You can also click on the button 'This volunteer is not available at this event'.
- Make changes to their preferred duties
- Make changes to their 'same or different' preference. This is optional, and is only used for events with many days (eg Cadet Week)

If you can't resolve the problem immediately, then make a note of the issue in the 'Enter any notes about the volunteer' box, and click save changes. Make sure you return to the volunteer once you have clarification.



# Issues when updating event data

## Volunteer warnings

If the registration for a cadet changes, you may get a warning and a form displayed to resolve any issues. For example, 

You should also check the [warnings on the volunteer rota page](volunteer_rota_help.md#warnings) to double-check that there is no inconsistency between when volunteers and attending, and when sailors are around.

## Duplicate registrations on update

```
ACTION REQUIRED: Cadet John Smith (2000-01-01) Member appears more than once in WA file with multiple active registrations - ignoring any possible changes made to registration - go to WA and cancel one of the registrations please!
```

As it says, this means the cadet has been registered multiple times, but the duplicate registrations have not been cancelled. Any changes made to these registrations will be ignored. If you allow a duplicate registration to occur, the best thing to do is to cancel the duplicated registrations in Wild Apricot and then re-import the data. Make sure that the details in the remaining registration on Skipperman reflect what the parent actually wants to do.

## Missing registrations on update

```
Cadet John Smith (2000-01-01) Member was in imported data, now appears to be missing in latest file - possible data corruption of imported file or manual hacking - no changes in file will be reflected in Skipperman
```

This can happen if:

- You have [added a sailor manually](link_required.md) to Skipperman who has not been registered in Wild Apricot, and their status is not 'Manual'. You can ignore this message, but to make it go away eithier change the [registration status to manual](link_required.md) which would be appropriate for a free event like a racing series, or ask their parent to register them.
- For some stupid reason you have manually edited the data file exported from Wild Apricot and remove one or more rows. Unless you're an expert trying to debug something, don't do this. Instead, change the registration status to ['Cancelled'](link_required.md). Meanwhile, you can ignore this error.
- Wild Apricot themselves have changed their export output, or Skipperman has managed to corrupt it's own data. Please contact support - this is serious.



