To produce a configurable report, from the **main menu**, select **Reports**, the report you require, and click on the relevant event.
---

The configurable event reports in Skipperman allow you to produce nicely formatted .pdf and useful spreadsheet files, which are essential in managing an event.

[TOC]

More report specific information is here:

- [Group allocation for an event](group_allocation_report_help.md) 
- [Volunteer rota for an event](volunteer_rota_report_help.md) 
- [Spotter sheet for an event](spotter_sheet_report.md) 
- [Roll call / health / contacts](roll_call_help.md) 


# The reporting option page

Once you have selected a report and an event, you will see the main reporting option page. This shows the three groups of configurable parameters:

- [report specific](#report-specific-parameters)
- [printing options](#print-options)
- [group layout and arrangement](#arrangement-options)

Under each heading the configuration is summarised. Pressing on the modify button in each heading will allow you to change the parameters.

You can also [create a report](#creating-a-report) from here, or [reset all the configuration to it's default setting](#resetting-options).

# Making the .pdf report look nice

It can take a little bit of effort to make a crowded .pdf report look right with all the information fitting in, especially if you have a lot of sailors or volunteers to fit in. However the advantage of Skipperman over a spreadsheet is that once you have got the layout right, the same report can be produced after making any required changes. Skipperman does it level best to arrange the report as efficiently as possible, but a little human fine tuning doesn't go amiss.

First set your [report specific parameters](#report-specific-parameters), and then go into the [printing options](#print-options). Choose your paper size and orientation (landscape works best for busy reports), and any other options you like; but for now leave the font size as default (zero); and equalise column widths.

Now go into [the arrangement options](#arrangement-options), and reset them to ensure you have all the groups in. The configurable reports all have groups in them. For the volunteer rota a group is a team of volunteers. For the other reports, a group is a sailing group.  If there are groups you want to leave out for some reason, delete them (you can easily put them back). Click on 'arrange in most efficient rectangle', and then click on 'create report'. You are checking to see if the space has been used efficiently, and if everything has fitted on the page.

(Note that it's possible the groups might be slightly different on each day so you might need to check all the pages in the report).

If everything isn't fitting on, try moving some groups around in the layout. If one column is bigger than the others, move a group out of it. Try and keep a logical layout (eg all lake sailing groups near each other, or all topper groups together).

If you have one column with a big gap to the next, try going to [printing options](#print-options) and setting equalise column widths to False. If the report is still slightly too big for the page, try reducing the font size. Start with size 10. You can also try increasing the font size if you have too much space. But watch out for 'overlay' effects, where letters get overprinted.

# Report specific parameters

Reports have parameters that are specific to the type of report. 

- [Group allocation for an event](group_allocation_report_help.md#report-specific-parameters) 
- [Volunteer rota for an event](volunteer_rota_report_help.md#report-specific-parameters) 
- [Spotter sheet for an event](spotter_sheet_report.md#report-specific-parameters) 
- [Roll call / health / contacts](roll_call_help.md#report-specific-parameters) 

Click back if you don't want to change parameters, and reset if you want to [return them to their default values](#resetting-options).

Once you have selected the specific parameters you want, click save to return to the main [reporting option page](#the-reporting-option-page), or [create a report with these options](#creating-a-report).

# Print options

The print options affect how the report looks and how it can be shared.

- Is the report a document .pdf or a spreadsheet .csv? Pdfs are multi-colum (like a newspaper), with seperate pages. Spreadsheets have seperate tabs, with the information in a single run.
- Should it be made publically available with a shareable web link? Ensure there is no personal information! Generally only rota and group allocations should be shared.

For pdf reports:

- Landscape or portrait?
- Font size. If this is zero, Skipperman will try and guess the right scale. It isn't always right!
- Font. Note that courier is the 'typewriter' font which can sometimes make layout easier as it is fixed width.
- Equalise column widths. Without this the columns in the report can be different widths. Equalising makes things look nicer, but is less efficient for space.
- What is the report title? This will appear on each page
- Highlight first value in group. This is useful for highlighting team leaders in the volunteer rota report.

For all reports:

- What is the filename? This doesn't really matter unless the file is publicly shared.
- Do you want the group name as a header?
- Do you want the number of sailors / volunteers in the group in the header?
- Do you want the group name to be inserted in front of every item? 
- Do you want a row number to be put at the start of the line?
- Do you want the group to be dropped from the main part of the data (fine if it's there as a header as well)

Click back if you don't want to change parameters, and reset if you want to [return them to their default values](#resetting-options).

Once you have selected the specific parameters you want, click save to return to the main [reporting option page](#the-reporting-option-page), or [create a report with these options](#creating-a-report).


# Arrangement options

The configurable reports all have groups in them. For the volunteer rota a group is a team of volunteers. For the other reports, a group is a sailing group.

For the volunteer rota, and group allocation reports, it can be difficult to fit everyone on one page. To help with this, the arragement page allows you to move the various groups around.

The arrangement options are split into:

- [The arragement order](#the-arrangement-order)
- [The arrangement layout](#the-arrangement-layout)

Note there is no save option on the form; all changes are saved immediately. Pressing back will return you to the [main reporting options page](#the-reporting-option-page).

## The arrangement order

We can arrange the groups at the event in order by using the up and down buttons. You can also delete groups from a report. This will show a warning, and you can add the missing group(s) back by clicking the 'Add' button that appears.

## The arrangement layout

Layout isn't used by .csv spreadsheet reports which have a single column of lines, one for each sailor or volunteer (of course there will still be multiple spreadsheet columns). Layout is used by .pdf reports which have multiple columns.

Once the groups are in order, if you click 'Arrange in the most efficient rectangle' then the groups will be laid out in that order across an appropriate number of columns. You can change this layout by clicking the arrow buttons.

The numbers in brackets show the size of each group.


## Creating a report

If you click on [create report](#creating-a-report), then the appropriately arranged report will be downloaded. It can take a little trial in error in moving the groups around to get the best fit.


## Reset the options

Clicking 'reset' will reset the arrangement options. All the groups in the data will be included in the report, in the default order (which can be set in the configuration pages for [sailing groups](configuration_help.md#sailing-groups) and [volunteer teams](configuration_help.md#volunteer-teams)).


# Creating a report

You can create a report from the [main reporting option page](#the-reporting-option-page), or from any configuration page. This will download the report to your computer, and if relevant create or update a [shared version](#sharing-a-report-). 

# Sharing a report  

If you have set the output to public option in [the print options](#print-options), then the report can also be accessed once created from the web link shown on the [main reporting options page](#the-reporting-option-page). The web link will always end with the filename you are using.

Report links can also be shared via QR codes, which can be created from the [utilities / file management page](file_management_help.md).

You can also delete your report after the event from the [utilities / file management page](file_management_help.md).


# Resetting options

If you make a lot of changes to the print options, and you have lost track, then you should return them to their default values by resetting them. You can eithier reset all the options on the [main reporting option page](#the-reporting-option-page), or you can separately reset each of the report specific, print options, and group layout on the relevant page.

If you would like to change the default options, please contact a Skipperman admin.
