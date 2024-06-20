The volunteer rota page is used to allocate volunteers to jobs. Only volunteers who have been added to the event can be allocated. Volunteers are normally added when an event is imported, but you can also manually add them here. You can also allocate volunteers in [patrol boat mode](patrol_boat_help): this makes most sense for rescue boat drivers. Make sure you are not in [read only](main-menu#read-only) mode if you want to make changes - use read only mode for experimenting.

[TOC]

# Overview

After an event has been imported, you will be presented with a screen like this:

***
***
![Volunteer rota screen](/static/volunteer_rota_overview.png)
***
***

- The first thing we see is the navigation bar with options to 'cancel' (exit this screen without saving any recent changes), 'Add new volunteer' and so on.
- Then we have a confirmation of which event we are editing.
- There are some expand triangle buttons to see summaries and warnings
- There are some very brief instructions.
- Then there are sorts and filter options. 

Finally, at the bottom of the screen you can see the list of volunteers, 

Each row shows a volunteer who has been imported to the event automatically. You can see, from left to right:

- The volunteers name.  
- The location of the cadet(s) that the volunteer is connected to: lake training, river training or MG racing. This will only be populated once the cadets have been allocated to groups. This is useful to know if a cadet and parent are likely to be in the same place
- Preferred duties: the duties that the volunteer wants to do, from their registration form. NOTE: If someone says they have a PB2 or instructor qualification, it does not mean they do!
- Same / different preferences: for some events (primarily cadet week), volunteers can say if they want to do one role or several.
- Skills recorded in the Skipperman database. This is more likely to accurate, but you should still check it.
- Previous volunteer role at the last event they did - very helpful for allocating.
- For each day the role they are doing, and the buttons you can use to give them roles.
- Notes and other information from registration

# Allocating roles and groups

## Giving someone a role

To give someone a job, click on the down selection arrow next to 'No role allocated' and choose a *role*. You can then click on 'Save changes' in the navigation bar. You can add roles to multiple volunteers before clicking save.

***
***
![Volunteer allocate role](/static/volunteer_allocate_role.png)
***
***

PS Skipperman won't check to see if someone is qualified to do this job when you allocate them to a role, but if you click on [warnings](#warnings) you can see if there are any apparently unqualified people. 

Note by convention a lake or river 'helm' is just someone who has the relevant PB2 certificate so there can be more than one helm on a boat.


## Allocating a group

Certain roles (all instructors, and lake helpers) can be associated with a specific training group (eg Jolly sailors, Laser MG). You can see that the person with the coaches job now has another dropdown with 'Unallocated'. Click on that to select a group, and then press save: 

***
***
![Volunteer allocate role](/static/volunteer_allocate_group.png)
***
***

## The role or group I want isn't shown

Contact the administrator for now - in a future version of Skipperman you will be able to add these yourself.

## Changing roles and groups

To change someone's role or group, simply click on the down arrow next to the role or group, choose another option, and then press save.

## Removing roles and groups

You can remove a role from someone by clicking on the &#174; symbol or choosing the 'No role allocated' from the role dropdown and pressing save.

You can remove a group from someone by choosing the 'Unallocated' option from the group dropdown menu and clicking save.

# Adding, removing and changing volunteer availability

## Availability

Volunteers can choose which days they are available on registration. Sometimes these will change, or they will make a mistake.

To make someone available on a given day, just click the 'Make available' button in the appropriate column.
To make someone unavailable on a given day, click on the umbrella button in the appropriate column (because it's a 'rain check' - get it?), or choosing the '**UNAVAILABLE**' option in the role drop down.

You can also change availability by clicking on a volunteers name, changing the day selection ticks, and pressing save. 

Note: if you want to remove a volunteer completely, you should usually do this by [clicking on their name](#removing-a-volunteer-from-an-event) rather than making them unavailable on all days - this will keep them on the screen (which might make sense if you're not sure if they can come, but you want to keep them in mind).

## Add a volunteer

Perhaps there is a non parent helping, or a parent who couldn't originally volunteer now can. You can add them manually. Click on the 'Add new volunteer to rota' option in the navigation bar:

***
***
![Volunteer add](/static/volunteer_add_to_rota.png)
***
***

At this stage you can select an existing volunteer by just pressing the button with their name on.

Alternativley, if the volunteer is new to the club, you can enter their name in the fields shown, and then click on 'Please check these volunteer details for me':

***
***
![Volunteer add](/static/volunteer_add_to_rota_warning.png)
***
***

Skipperman doesn't like duplicate volunteers, so it will prompt you if it looks like the person you are adding is very similar to someone who already exists. You can make changes and then click on 'Please check...' to check again, or click on 'Yes these details are correct - add a new volunteer'. This will add a new volunteer to Skipperman, and to the event.

If you change your mind about adding a volunteer, just press cancel.

## Removing a volunteer from an event

Click on a volunteers name and press 'Remove volunteer from event'

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

- For Beth we can do both kinds of copy. For example a copy and fill &#8646; from Saturday would allocate 'River crew' to Monday; whilst a copy and overwrite button &#10234 from Sunday would make all three days 'Lake crew'
- Richard has only a copy and fill option shown on Saturday &#8646; as he has no other existing roles to overwrite. Pressing this would allocate 'Coach/Topper MG' to all three days.
- Ronan has no copy buttons shown since he is only available on one day, so there is nowhere to copy to.
- Zoie has only copy and fill options shown on &#8646; for Saturday and Sunday - since both roles match there is nothing to overwrite. Pressing eithier of these would allocate 'Lake crew' to her free day on Monday.
- Jake does not have any copy and fill options shown since he has no free days to fill in. A copy and overwrite &#10234;; from Saturday or Monday would make all three days Lake helm, the same from Sunday would make all days River helm.


## Global copy

There are also two 'global' copy buttons in the navigation bar which are equivalent to pressing the &#10234; or &#8646; buttons on the *earliest day a given volunteer has a role*, but for every single volunteer. This can be quite useful for a multiday event if you want to give everyone the same role/group; just fill them in on the first day and then press the copy/fill button. Then you can fine tune people who will be on different roles for different days. Be very careful with the 'Copy from the earliest allocated role and overwrite existing roles' button since if you have a lot of changes in allocation they will be lost. Again it's more likely to be useful when you are first putting together a rota.

### Global copy and fill 

For example if we start with the rota shown in the previous image, and then press 'Copy from earliest allocated role to fill all roles', we get:

![volunteer_after_global_fill.png](/static/volunteer_after_global_fill.png)

- Beth's river crew role on the first day has been filled in for Monday; Sunday is unchanged.
- Richard's coach role on Saturday has been filled in all three days
- Ronan is unaffected as he has no free days.
- Zoie's lake role on Saturday has been filled in on Monday.
- Jake is unaffected as he has no free days.

Note that if a specific volunteer didn't have a role on Saturday, we would copy from the next day when one was set. For example if we started with this:

![volunteer_global_fill_pre_no_first_role.png](/static/volunteer_global_fill_pre_no_first_role.png)

After pressing 'Copy from earliest allocated role to fill...' Beth would be a lake crew on Saturday - the earliest available role allocated (on Sunday).

### Global copy, fill and overwrite

If instead we start with the rota in the previous section, and this time press 'Copy from earliest allocated role to fill empty and overwrite existing roles', we get this:

![volunteer_After_global_overwrite.png](/static/volunteer_After_global_overwrite.png)

## Previous role copy

Finally, If a volunteer is doing the same job as at their last event, then pressing the button in the previous role column will *copy and overwrite* that role across all days when a volunteer is available. Eg if we press the previous role for Beth, it would put 'Ramp' for all 3 days, irrespective of what was already there.

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

By default all volunteers are shown, and they are in the order they were added to the event in (which can be quite useful - if you go to the end of the event after it's been updated, you can see straight away which new volunteers you have). We can use sorting and filtering to change the order and only see a subset of volunters.

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

You can filter eithier by skill, or by availability/allocation, or both.

### Skills filtering

Check the skills boxes to only include volunteers with a given skill (not their self declared skills from preferred duties - whatever is stored in Skipperman), or combination of skills. Click on apply filters once you have chosen the skillset you want to see, and then clear filters when you want to see all volunteers. This is very useful when deciding who your instructors and PB2 drivers are.

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

Click on the &#17; to expand them and see the hidden details.

## Summaries

Click on &#17;Summary by ..., and we can see two summaries of the numbers of volunteers allocated, one breaks down into very granular detail; the second sums up over teams and groups. The latter is probably more useful for seeing, for example, that there are the right number of AI/DI in total for a given group.

## Role numbers and targets

It can be quite useful to have a target number in mind when allocating, so you don't forget to fill a specialist role like ramp welfare, or end up the wrong number of rescue boat crews and helm. Click on &#17;Role numbers and targets:

***
***
![volunteer_targets.png](/static/volunteer_targets.png)
***
***

For each role we can see the numbers allocated on each day, the target (which can be edited - and there is a save button at the bottom of the table), and the 'worst shortfall'. This is the biggest difference between the target number for a role, and the total number of volunteers on a given day. If it's negative, then we exceeed the target on every day and you could look at redeploying volunteers if you need them elsewhere.

Usually the target is set by the cadet skipper or whoever is the principal organiser for the event, which the deputy skipper or whoever is controlling the rota can then work towards.


## Warnings

Warnings are things that could be problematic for your volunteer rota; to see them click &#17;Warnings. They come into the following categories:

- A mismatch between cadet availability and volunteer availability - make sure the volunteer really can do those days and record in the notes.
- A volunteer without any connected cadets - this could be because they have agreed to help, but it could also be because the cadet has cancelled their registration and you haven't removed the volunteer - check with the volunteer, and then record in the notes what they said.
- Volunteers who are at the lake with one or more connected cadets, or worse still allocated to a sailing group that their cadet is in. Make sure you are happy with this.
- Is every volunteer qualified for their role?

# Misc

## Qualifications

Clicking on the button for each volunteer under the skills button will allow you to edit the skills they have. *DO NOT TAKE THE VOLUNTEERS WORD FOR IT* - always check the linked sailing school spreadsheet ('qualifications table') if you are unsure. If someone claims to have a certificate which is not recorded, ask them for their paper work and send to the sailing school manager; only tick their skills of in Skipperman once they have been added to the official spreadsheet.

By convention the first aid certificate here doesn't have to be an RYA one (which all instructors will have), it's basically a confirmation they are suitable for a welfare type role.

Similarly, DBS only applies to DBS applied for through the BSC

Expiry dates for certificates are not stored in Skipperman, so it's a good idea at the start of each season to check the qualifications table and note if any instructors have lapsed or will lapse during the year. 

## Cadet connections

It's useful to know where the cadets are who are connected to volunteers to avoid putting cadets and parents together, and to be aware of any repercussions for the rota if for example the cadet's registration is cancelled, and this is shown in the Cadet location button for each volunteer. Cadets are connected to volunteers on the registration form. Note that this is a temporary connection for this event only; and this isn't the same as permanent connection (see FIXME for more details).

Clicking on the location button will allow you to modify the temporary event connections for the volunteer:

***
***
![volunteer_modify_connections.png](/static/volunteer_modify_connections.png)
***
***

You can delete the connection, or add a new one by choosing from the dropdown list. The top of the list will include cadets that are most likely to be connected, eg with the same surname or a permanent connection.

## Other useful functions

- You can see more information about the previous roles a volunteer performed by clicking on their name; click cancel to go back.
- The 'other information' from registration column on the far right can be useful if volunteers have told you about their availability in more detail.
- You can enter notes about the volunteer in the notes column; typically this would be around issues or finer preferences on roles, or availability constraints not captured by just which day they are around. Remember under GDPR they have the right to see them, so be careful!

