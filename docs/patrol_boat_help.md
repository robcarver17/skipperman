To access the patrol boat rota, from the **main menu**, select **Events**, choose an event, and then click on **Patrol boats** in the menu.
___

The patrol boat rota page is used to allocate volunteers to patrol boats. Only volunteers who have been added to the event can be allocated - if you want to add a volunteer, you will need the main [volunteer rota page](volunteer_rota_help.md#add-a-volunteer). Make sure you are not in [read only](main-menu.md#read-only) mode if you want to make changes - use read only mode for experimenting.

[TOC]

# Overview


***
***
![patrol_boat_overview.png](/static/patrol_boat_overview.png)
***
***


# Boats

## Adding a boat

The first thing we need to do is add a boat. Select a boat from the drop down and click `Add new boat`. If the boat you want isn't listed, you will need to make it visible or add it via the [configuration](configuration_help.md#patrol-boats) pages. You can add as many boats as you like to an event, but each boat can only be added once.

![boat_added.png](/static/boat_added.png)

## Labelling a boat with a designation

You might want to label boats with a specific designation, eg 'Dedicated safety', 'Coach boat', 'Safety / coach'. Enter the designation, or use the drop down arrow to choose previously used labels. Designation needs to be set for each day. To change a designation just delete it, you will then see the dropdown arrow again, or you can type in any value.

Designation is used to sort boats in the [patrol boat report from the main menu](patrol_boats_rota_report_help.md) and the [quick report](#quick-reports).

## Removing a boat from the rota

Click on `Remove boat from rota` to remove a boat entirely.  

# Allocating volunteers 

## Allocating a volunteer to a boat

Select a volunteer from the dropdown menu, and then click `Save changes`. Volunteers are listed in order, with the ones most likely to be on a boat listed at the top. Note that those with PB2 qualifications are marked, and you can also see their current volunteer role if any in the dropdown. You can add several volunteers at a time, before clicking save. Once a volunteer is added to a boat on a given day, they can't be added to another boat.
If no volunteer dropdown is shown, it means all the available volunteers on a given day are already on boats.

![volunteers_added_to_boats.png](/static/volunteers_added_to_boats.png)

Once you have added one volunteer to a boat and pressed save, you have the option of adding more by selecting them from the dropdown on the boat, and then clicking save. The volunteers above all have existing roles in the volunteer rota, but it's also possible to add someone who doesn't, so let's do that:

![volunteer_added_to_boat_second.png](/static/volunteer_added_to_boat_second.png)

Note: Skipperman doesn't know about boat capacity, so it will allow you to add as many people to a boat as you like. 

## Changing roles of volunteers on boats

We can change the allocated role of a volunteer, or add a role to a volunteer who doesn't have one, by selecting the role from the dropdown and hitting save:

![boat_changed_role.png](/static/boat_changed_role.png)

Note that we can't change the group of a DI or coach who is on a boat, so it's best to use this function only for safety boat drivers and crew, and do all other role changes in the volunteer [volunteer rota page](volunteer_rota_help#changing-roles-and-groups). Remember by convention a 'helm' is just someone who has the relevant PB2 certificate so there can be more than one helm on a boat.
Note also that you can make someone a 'helm' even if they don't have a PB2 certificate -check the [warnings](#warnings) to see if you have done this.
Note that you could make someone a 'lake helm' on a river boat, and vice versa. Skipperman won't stop you, but it will look odd and mess up the rota so please check this.

## Removing a volunteer from a boat

To remove a volunteer from a boat, click on the &#174; symbol button. Note this won't remove from the volunter rota or change their role, just take them off the boat. To take someone off the rota entirely, you need to [rota page](volunteer_rota_help.md).


# Summary

Once you have some volunteers on boats, you can see a summary of how many people are on each boat by clicking ►Summary. This is a useful check to make sure you have the right number of helm/crew.

# Qualifications table

Click on ►Qualifications to see the editable qualifications table:

![boat_quali_table.png](/static/boat_quali_table.png)

For every person on a boat, that shows you whether they have PB2 or not. You can add or remove PB2 qualifications by changing the tickbox and pressing Save. Don't assume someone has PB2 - always check the official spreadsheet via the link.

# Warnings

## Active warnings

There are three types of checks that Skipperman will do, and you can see if there are any resulting warnings by clicking ►Warnings.

- Does every boat have a qualified driver on for every day?
- Is every volunteer qualified for their role?
- Is a volunteer allocated to a patrol boat and a club dinghy on the same day?

Warnings appear sorted by priority, and then by category.

You can eithier *clear* warnings, or click on them to be *ignored* (and then press `Save changes to warnings`). To clear warnings:

- Add a driver where one is missing
- Set a volunteer qualification in the [qualifications table](#qualifications-table)) or in the [volunteer rota](volunteer_rota_help.md), or [edit volunteer page](view_individual_volunteer_help.md).
- Remove the volunteer from eithier the [club sailing boat](#allocating-club-sailing-dinghies-to-instructors) or the [patrol boat](#allocating-a-volunteer-to-a-boat).

## Ignored warnings

Warnings that have been ignored appear here. You can 'unignore' them by clicking the checkbox and pressing `Save changes to warnings`.


# Copying

I'd advise you to read about copying in the [volunteer rota](volunteer_rota_help#copying) before looking at copying here - they work in exactly the same way, except that for patrol boats we can copy boats, roles, or both.

For a multi day event, people will often be on the same boat and/or doing the same role every day. As for volunteers, there are two types of copying you can do to copy roles and boats across all days and avoid tiresome re-entry.

- 'Copy and fill &#8646;' - this will copy from the relevant day where the button is located, and fill in any empty days with the same boat &#8646; B, role &#8646; R, or boat and role &#8646; BR.
- 'Copy and overwrite &#10234;' - this will copy from the relevant day where the button is located, and copy it to every single day irrespective of whether there is already a boat and / or role allocated; again we can do this for boats &#10234; B, roles &#10234; R and both &#10234; BR.

Note that the swap button moves roles 'up and down' between volunteers on the same day, whilst the copy button moves them 'left and right' across days for the same volunteer. The overwrite button is thicker, think of it as covering over the existing days.

As with the volunteer rota you can also copy, or copy and overwrite, across all volunteers using the buttons in the navigation bar for boats, and also for boats and roles.

# Swapping

I'd advise you to read about swapping in the [volunteer rota](volunteer_rota_help.md#swapping) before looking at swapping here, they work in exactly the same way except that you can swap boats, or boats and roles.

The swap button &#8693; allows you to swap round two volunteers. Note that a swap button moves roles 'up and down' between volunteers on the same day, whilst a copy moves them 'left and right' across days for the same volunteer. Just as for copying, we can swap boats using &#8693 B or boats and roles with &#8693 BR (we can't swap just roles - that can only be done on the [volunteer rota page](volunteer_rota_help.md#swaps)).  Swapping boats and roles is usually used for moving people between lake and river boats. Consider this starting point:

![boat_pre_swap.png](/static/boat_pre_swap.png)


## Swap boats

Initially let's just swap boats; if we click on Simon's Saturday  &#8693 B swap boat button we enter 'swap mode;:

![pressed_swap_boat_button.png](/static/pressed_swap_boat_button.png)

In 'Swap mode' we can only do one of two things, swap a volunteer with someone else, or cancel the swap. All the other buttons and functions are temporarily unavailable. Clicking on the button for the volunteer we wanted to swap (Simon) would obviously cancel the swap. Note we can't swap boats with Beth as we already on the same boat. If we click on Jake's 'Swap boats with me', we get:

![after_swapping_boats_button.png](/static/after_swapping_boats_button.png)

Jake and Simon now both have the wrong role; so this is most useful if you are moving within the river or lake safety fleet where the role doesn't change.

## Swap boats and roles

Instead of pressing swap boats, what would have happened if we had pressed Simon's Saturday  &#8693 BR swap boats and roles button?

![pressed_swap_boats_and_roles_button.png](/static/pressed_swap_boats_and_roles_button.png)

- Beth is on the same boat, if we press swap role then Simon will become the crew and Beth the helm.
- Richard is a coach, so we should avoid swapping roles and ought to only swap boats
- Jake is on a different boat, so we would swap both boats and roles.

Let's click on Jake as it's the most interesting:

![after_swapping_boats_and_roles.png](/static%2Fafter_swapping_boats_and_roles.png)

You can see how this is useful for moving safety crew between the lake and river.

Remember by convention a 'helm' is just someone who has the relevant PB2 certificate so there can be more than one helm on a boat.

## Moving boats without swapping

You can also move someone on to a different boat without selecting a volunteer they have to swap with. This is quicker than removing them from one boat and then selecting them on another.

# Allocating club sailing dinghies to instructors

You can also allocate club sailing dinghies to instructors and other helpers. These will appear on the volunteer rota report and the spotter sheet, but not the patrol boat rota report.

Click on  ►Club dinghies - allocate to instructors to start.

## To allocate a club dinghy to an instructor or helper

For the relevant club dinghy row, select the volunteers name on the appropriate day, then click 'Allocate dinghy'. Only volunteers available on that day who aren't already on a club dinghy are shown.

Note: it's possible to put someone on a patrol boat and a club dinghy - you won't be stopped. But it will appear as a [warning](#warnings) if you do so.

## To copy across allocations across days

To save time, if a volunteer is on a club dinghy for multiple days, then click on the &#10234; button next to a volunteer. This will copy the allocated dinghy to all the other days they are available. WARNING: this will overwrite any existing allocations.

## To remove an allocation on a given day

Just click on the 'Remove allocation' button. 

## Seeing a summary of club dinghies allocated

Click on  ►Club dinghies - summary. This will also include dinghies allocated to cadets in the [Sailors, groups and boats](group_allocation_help.md) page. You can change the number of boats available to hire at the event here.

# Quick reports

If you choose the 'quick report' option in the menu, you can run a [patrol boat rota report](patrol_boats_rota_report_help.md). This report will run with the default printing options, and it **will not be published to the public**. If you want to publish it, or change the report settings, go to the relevant part of the [reports menu.](reporting_help.md).