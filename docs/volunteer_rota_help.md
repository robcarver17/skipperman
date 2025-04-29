To access the rota for an event, from the **main menu** choose **Events**, then select an event, then click on **Volunteers**.
___

The volunteer rota page is used to allocate volunteers to jobs. Only volunteers who have been added to the event can be allocated. Volunteers are normally added when an event is imported, but you can also manually add them here. You can also allocate volunteers in [patrol boat mode](patrol_boat_help.md): this makes most sense for rescue boat drivers. Make sure you are not in [read only](main-menu#read-only) mode if you want to make changes - use read only mode for experimenting.

[TOC]

# Overview


***
***
![Volunteer rota screen](/static/volunteer_rota_overview.png)
***
***

- The first thing we see is the navigation bar with options to 'cancel' (exit this screen without saving any recent changes), 'Add new volunteer' and so on.
- Then we have a confirmation of which event we are editing.
- There are some expand triangle buttons ► to see summaries and warnings
- Then some very brief instructions.
- Then there are sorts and filter options. 

Finally, at the bottom of the screen you can see the list of volunteers, 

Each row shows a volunteer who has been imported to the event automatically. You can see, from left to right:

- The volunteers name.  
- The location of the sailor(s) that the volunteer is connected to: not in groups, lake training, river training or MG racing; or no connected sailors. This will only be populated once the cadets have been allocated to groups. This is useful to know if a cadet and parent are likely to be in the same place.
- Preferred duties: the duties that the volunteer wants to do, from their registration form. NOTE: If someone says they have a PB2 or instructor qualification, it does not mean they do!
- Same / different preferences: for some events (primarily cadet week), volunteers can say if they want to do one role or several.
- Skills recorded in the Skipperman database. This is more likely to accurate, but you should still check it.
- Previous volunteer role at the last event they did - very helpful for allocating.
- For each day the role they are doing, and the buttons you can use to give them roles.
- Notes which you can edit.
- Other information from their registration form.

# Typical workflow

A typical workflow for a training weekend would be: 

- allocate instructors (DI, RCL and AI)
- allocate lake manager if no deputy skipper
- allocate bridge, if cadet's controlling the bridge
- allocate rescue boat drivers, and possibly a safety lead
- allocate other key people, eg ramp lead and welfare people. Note ramp spotters are only required if cadets are not running the bridge.
- allocate lake helpers
- allocate ramp helpers

This would be broadly similar for a racing weekend (although the rota here tends to be a bit ad hoc on the day):

- allocate lead positions: Race officer, Ramp lead
- allocate bridge (as advised by race officer) 
- allocate race coaches
- allocate rescue boat drivers
- allocate ramp including ramp lead, and ramp welfare

For Cadet Week we'd do things slightly differently:

- allocate lead positions: Race officer, Ramp lead, Safety lead, Galley lead, SI, Lake manager / deputy skipper
- allocate Bridge (based on a list provided by the race officer and/or what people have put on their form)
- allocate instructors (DI, RCL and AI) in discussion with SI
- allocate rescue boat drivers in discussion with safety lead
- allocate Galley in co-ordination with Galley lead
- allocate other key people, eg ramp spotters and welfare people
- allocate lake helpers 
- allocate ramp and rescue crew

Given the workflow above it can be useful to see what kinds of volunteers are available with a given skills, and which haven't yet been allocated. You can use [skills filtering](#skills-filtering) and [allocation/available filtering](#availabilty--allocation-filtering) to do this.

- for instructors: filter to see only AI, DI and RCL2
- for safety boat drivers: filter to see only those with PB2, and filter for unallocated and available (so it excludes the rescue boat drivers)

At each stage it can also be useful to share the list of volunteers with others, the easiest way of doing this is to click the 'Download spreadsheet of volunteer information', which will give you detailed information on who is available with what skill, given the filtering you have already done.

# Allocating roles and groups

## Giving someone a role

To give someone a job, click on the down selection arrow next to `No role allocated` and choose a *role*. You can then click on `Save changes` in the navigation bar. You can add roles to multiple volunteers before clicking save.

***
***
![Volunteer allocate role](/static/volunteer_allocate_role.png)
***
***

PS Skipperman won't check to see if someone is qualified to do this job when you allocate them to a role, but if you click on [warnings](#warnings) you can see if there are any apparently unqualified people. 

Note by convention a lake or river 'helm' is just someone who has the relevant PB2 certificate so there can be more than one helm on a boat.


## Allocating a group

Certain roles (all instructors, and lake helpers) can be associated with a specific training group (eg Jolly sailors, Laser MG). You can see that the person with the coaches job now has another dropdown with `Unallocated`. Click on that to select a group, and then press save: 

***
***
![Volunteer allocate role](/static/volunteer_allocate_group.png)
***
***

## The role or group I want isn't shown

You can change these in the [configuration](configuration_help.md) pages from the main menu. It might be that your role / group is hidden, or you need to add a new one.

## Changing roles and groups

To change someone's role or group, simply click on the down arrow next to the role or group, choose another option, and then press save.

## Removing roles and groups

You can remove a role from someone on a specific day by clicking on the &#174; symbol or choosing the 'No role allocated' from the role dropdown and pressing save. This will also remove any group they are attached to.

You can remove all roles someone has by clicking on the &#174; symbol under their name in the first column.

You can remove a group from someone on a specific day by choosing the 'Unallocated' option from the group dropdown menu and clicking save. This won't remove their role.



# Adding, removing and changing volunteer availability

## Availability

Volunteers can choose which days they are available on registration. Sometimes these will change, or they will make a mistake.

To make someone available on a given day, just click the 'Make available' button in the appropriate column.
To make someone unavailable on a given day, click on the umbrella button in the appropriate column (because it's a 'rain check' - get it?), or choosing the `UNAVAILABLE` option in the role drop down.

If you want to remove a volunteer completely, you should do this by [clicking on the umbrella under their name in the first column](#removing-a-volunteer-from-an-event).

If a volunteer is a parent who has to be on site, but can't help, then you should remove their availability from each day but keep them in the event. Otherwise, there will be a [warning](resolve_warnings.md#cadets-without-appropriate-adults).

## Add a volunteer

Perhaps there is a non parent helping, a parent on site who can't help but needs to be there, or a parent who couldn't originally volunteer now can. You can add them manually. Click on the `Add new volunteer to rota` option in the navigation bar:

***
***
![Volunteer add](/static/volunteer_add_to_rota.png)
***
***

At this stage you can select an existing volunteer by just pressing the button with their name on. You can sort the list of volunteers by first or last name. If you think you know vaguely what the volunteer is called, then you can put your best guess in, and click on `Sort by similarity with name`, The volunteers that are most like this person will appear first. 

Alternatively, if the volunteer is new to the club, you can enter their name in the fields shown, and then click on `Please check these volunteer details for me`:

***
***
![Volunteer add](/static/volunteer_add_to_rota_warning.png)
***
***

Skipperman doesn't like duplicate volunteers, so it will prompt you if it looks like the person you are adding is very similar to someone who already exists. If you have made a mistake, and the volunteer already exists, click on `See similar volunteers only` and click on their name to add them.

Alternatively if this is genuinely a new person, then click on `Yes these details are correct - add a new volunteer`. This will add a new volunteer to Skipperman, and to the event.

If the volunteer is a parent who will be on site, but not actually helping, select that option from the dropdown BEFORE you cick on the relevant volunteer or click to add a new volunteer. This is to avoid issues with [warnings about cadets being on site by themselves](resolve_warnings.md#cadets-without-appropriate-adults). They will be added with no days available. Otherwise, the volunteer will be added with all days available. You can change the days they are available once they are in the rota.

If you change your mind about adding a volunteer, just press cancel.



## Removing a volunteer from an event

Click on the umbrella button under their name (because they are taking a 'rain check').

# Copying

## Copying individual volunteers

For a multi day event, people will often be doing the same role every day. There are two types of copying you can do to copy roles (and groups if used) across all days and avoid tiresome re-entry.

- 'Copy and fill &#8646;' - this will copy from the relevant day where the button is located, and copy the same role (and group if relevant) to every day when there is currently no role allocated.
- 'Copy and overwrite &#10234;' - this will copy from the relevant day where the button is located, and copy the same role (and group if relevant) to every single day irrespective of whether there is already a role allocated.

Note that the swap button moves roles 'up and down' between volunteers on the same day, whilst the copy button moves them 'left and right' across days for the same volunteer. The overwrite button is thicker, think of it has covering the existing days.


For example suppose we begin with this situation:

***
***
![Volunteer rota before copying](/static/volunteer_pre_copy.png)
***
***

- For Beth we can do both kinds of copy. For example a copy and fill &#8646; from Saturday would allocate 'River crew' to Monday; whilst a copy and overwrite button &#10234; from Sunday would make all three days 'Lake crew'
- Richard has only a copy and fill option shown on Saturday &#8646; as he has no other existing roles to overwrite. Pressing this would allocate 'Coach/Topper MG' to all three days.
- Ronan has no copy buttons shown since he is only available on one day, so there is nowhere to copy to.
- Zoie has only copy and fill options shown on &#8646; for Saturday and Sunday - since both roles match there is nothing to overwrite. Pressing eithier of these would allocate 'Lake crew' to her free day on Monday.
- Jake does not have any copy and fill options shown since he has no free days to fill in. A copy and overwrite &#10234;; from Saturday or Monday would make all three days Lake helm, the same from Sunday would make all days River helm.


## Global copy
You can also access two 'global' copy buttons by clicking on the 'Copy and/or overwrite roles from first available day' button. This will bring up a menu page.
These buttons are equivalent to pressing the &#10234; or &#8646; buttons on the *earliest day a given volunteer has a role*, but for every single volunteer. This can be quite useful for a multiday event if you want to give everyone the same role/group; just fill them in on the first day and then press the copy/fill button. Then you can fine tune people who will be on different roles for different days. Be very careful with the 'Click to copy earliest role and also overwrite all existing allocations...' button since if you have a lot of changes in allocation they will be lost. Again it's more likely to be useful when you are first putting together a rota.

### Global copy and fill 

For example if we start with the rota shown in the previous image, and then press 'Click to copy earliest role into any days when the volunteer does not have a role allocated' button, we get:

![volunteer_after_global_fill.png](/static/volunteer_after_global_fill.png)

- Beth's river crew role on the first day has been filled in for Monday; Sunday is unchanged.
- Richard's coach role on Saturday has been filled in all three days
- Ronan is unaffected as he has no free days.
- Zoie's lake role on Saturday has been filled in on Monday.
- Jake is unaffected as he has no free days.

Note that if a specific volunteer didn't have a role on Saturday, we would copy from the next day when one was set. For example if we started with this:

![volunteer_global_fill_pre_no_first_role.png](/static/volunteer_global_fill_pre_no_first_role.png)

After pressing 'Click to copy earliest role...' Beth would be a lake crew on Saturday - the earliest available role allocated (on Sunday).

### Global copy, fill and overwrite

If instead we start with the rota in the previous section, and this time press 'Click to copy ... and also overwrite existing allocations', we get this:

![volunteer_After_global_overwrite.png](/static/volunteer_After_global_overwrite.png)

## Previous role copy

Finally, if a volunteer is doing the same job as at their last event, then pressing the button in the previous role column will *copy and overwrite* that role across all days when a volunteer is available. Eg if we press the previous role for Beth, it would put 'Ramp' for all 3 days, irrespective of what was already there.

# Swaps

The swap button &#8693; allows you to swap round two volunteers. Note that a swap button moves roles 'up and down' between volunteers on the same day, whilst a copy moves them 'left and right' across days for the same volunteer. For example suppose we start with this:

***
***
![Volunteer rota before copying](/static/volunteer_pre_copy.png)
***
***

If we then press the &#8693; button for Beth on Saturday, we enter 'Swap mode':

***
***
![volunteer_pressed_swap.png](/static/volunteer_pressed_swap.png)
***
***

In 'Swap mode' we can only do one of two things, swap a volunteer with someone else, or cancel the swap. All the other buttons and functions are temporarily unavailable. Clicking on the button for the volunteer we wanted to swap (Beth) would obviously cancel the swap. Alternatively if we clicked on the 'Swap role with me' button for Richard we get:

***
***
![volunteer_post_swap.png](/static/volunteer_post_swap.png)
***
***





# Sorts and filters

By default, all volunteers are shown, and they are in the order they were added to the event in (which can be quite useful - if you go to the end of the event after it's been updated, you can see straight away which new volunteers you have). We can use sorting and filtering to change the order and only see a subset of volunters.

***
***
![sorts_and_filters_volunteers.png](/static/sorts_and_filters_volunteers.png)
***
***

## Sorts

Using the three 'Sort by buttons' we can sort by:

- Cadet location (lake first, then river training, then MG groups) - this is useful to get a feel for the pool of volunteers who you would want to allocate away from the lake
- Volunteer surname
- Volunteer first name

You can also click on the name of each day at the top of the main volunteer table. This will sort by the allocated role, and for groups within roles, for a given day; putting unallocated and unavailable volunteers near the end. This can be useful to get a feel for who is in each group of volunteers without having to do a full report.

## Filters

You can filter either by skill, or by availability/allocation, or both.

### Skills filtering

Check the skills boxes to only include volunteers with a given skill (not their self declared skills from preferred duties - whatever is stored in Skipperman), or combination of skills. Click on apply filters once you have chosen the skillset you want to see, and then clear filters when you want to see all volunteers. This is very useful when deciding who your instructors and PB2 drivers are.
Skill filters are 'or', so if you click say PB2 and DI you will see people with a DI *or* a PB2 skill.

### Availabilty / Allocation filtering

For each day you can choose only to see volunteers who meet certain criteria, by clicking on the filter dropdown for a given day and selecting one of:

- All volunteers
- Available volunteers
- Available and unalloacated (very useful to see which volunteers you still need to give jobs to)
- Available and allocated
- Unavailable 

Note that the dropdowns will default back to 'All' unless they are reset when any button is clicked after the filter is applied (so you don't need to click 'clear filter' to remove an available/allocation filter). You can mix and match filters for different days, and combine with a skills filter. 

# Hidden details

Once you have entered some roles you will see two new &#17; options on the screen, for a total of four:

***
***
![volunteer_expandable.png](/static/volunteer_expandable.png)
***
***

Click on the ► to expand them and see the hidden details.

## Summaries

Click on ► Summary by ..., and we can see three summaries of the numbers of volunteers allocated, one breaks down into very granular detail; the second sums up over teams and groups, and the third is for instructors.

### Instructor / group summary table

***
***
![group_notes.png](/static/group_notes.png)
***
***

This is helpful if you want to see if you have the right number of instructors. There is one row for each group. The first two columns are the cadets assigned on each day. Then you have the names of people in each of the relevant instructor roles. Finally there are some notes, and then an instructor count by day.

You can make notes for each group, and save them.

## Role numbers and targets

It can be quite useful to have a target number in mind when allocating, so you don't forget to fill a specialist role like ramp welfare, or end up the wrong number of rescue boat crews and helm. Click on ► Role numbers and targets:

***
***
![volunteer_targets.png](/static/volunteer_targets.png)
***
***

For each role we can see the numbers allocated on each day, the target (which can be edited - and there is a save button at the bottom of the table), and the 'worst shortfall'. This is the biggest difference between the target number for a role, and the total number of volunteers on a given day. If it's negative, then we exceeed the target on every day and you could look at redeploying volunteers if you need them elsewhere.

Usually the target is set by the cadet skipper or whoever is the principal organiser for the event, which the deputy skipper or whoever is controlling the rota can then work towards.


## Warnings

Warnings are things that could be problematic for your volunteer rota; to see them click ► Active Warnings and ► Ignored warnings.

For more help on warnings, see [resolving registration issues](resolve_warnings.md).

# Misc

## Qualifications

Clicking on the button for each volunteer under the skills button will allow you to edit the skills they have. *DO NOT TAKE THE VOLUNTEERS WORD FOR IT* - always check the linked sailing school spreadsheet ('qualifications table') if you are unsure. If someone claims to have a certificate which is not recorded, ask them for their paper work and send to the sailing school manager; only tick their skills of in Skipperman once they have been added to the official spreadsheet.

By convention the first aid certificate here doesn't have to be an RYA one (which all instructors will have), it's basically a confirmation they are suitable for a welfare type role.

Similarly, DBS only applies to DBS applied for through the BSC.

Expiry dates for certificates are not stored in Skipperman, so it's a good idea at the start of each season to [refresh the qualifications from the official BSC spreadsheet](refresh_skills_with_import_help.md). Also check the qualifications table and note if any instructors have lapsed or will lapse during the year. 

## Cadet connections

It's useful to know where the cadets are who are connected to volunteers to avoid putting cadets and parents together, and to be aware of any repercussions for the rota if for example the cadet's registration is cancelled, and this is shown in the Cadet location button for each volunteer. Cadets are automatically connected to volunteers when the registration forms are imported if the volunteer is listed against a cadets name. Note that this is a permanent connection which will apply to all events.

Clicking on the location button will allow you to see the connected cadets, their groups, and permanently modify the cadet connections for the volunteer:

***
***
![volunteer_modify_connections.png](/static/volunteer_modify_connections.png)
***
***

You can delete the connection, or add a new one by choosing from the dropdown list. The top of the list will include cadets that are most likely to be connected, eg with the same surname.

## Other useful functions

- You can see more information about the previous roles a volunteer performed by clicking on their name; click their name again to remove this information.
- The 'other information' from registration column on the far right can be useful if volunteers have told you about their availability in more detail.
- You can enter notes about the volunteer in the notes column; typically this would be around issues or finer preferences on roles, or availability constraints not captured by just which day they are around. Remember under GDPR they have the right to see them, so be careful!
- Click on 'download spreadsheet of volunteer information' in the navigation bar to get a spreadsheet version of what you can see on the screen; useful for sharing with other people without needing to do a [rota report](volunteer_rota_report_help.md).

# Quick reports

If you choose the 'quick report' option in the menu, you can run a [volunteer rota report](volunteer_rota_report_help.md). This report will run with the printing options currently set up, and it **will not be published to the public**. If you want to publish it, or change the report settings, go to the relevant part of the [reports menu.](reporting_help.md).