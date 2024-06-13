# SKIPPERMAN - Blackwater Sailing Club Cadet Skipper Managemet System


SKIPPERMAN is a piece of software to ease the admin burden on the cadet skipper and their team, which is considerable and historically involves lots of manual hacking of spreadsheets. 



## Abbreviations

WA - Wild Apricot, the BSC club management system
CW - cadet week

## Where does the name come from

Since we have ‘Dutyman (BSC Duty Management system), I thought a good name for this would be ‘Skipperman (BSC Cadet Skipper Management System)’. Obviously a certain lycra orange bodysuit costume was also inspirational here.

## Overall requirements, architecture and design decisions


### Data storage
 This will be in .csv files. We do not require concurrent access or speed; and this will mean that the underlying data is both human readable, can be hacked in excel, or imported into a future replacement product. It also means that full or partial sets of data can easily be shared by sending files, without requiring a central server; there will be no need for users to eg launch a database server. We won't use eg sqllite to maintain data consistency, but will enforce the use of common keys across tables eg for Cadets.

Generally each .csv table will have a minimum amount of information in (eg we wouldn't have one giant cadet data table), but there would be the option to create consolidated .csv with information from several tables as a report.

### Language
The back-end, and as much as possible of the front-end, will be in Python. Partly this is because Python is a full stack capable language, but also because the principal developer has mostly forgotten the other 50 or so languages he used to know.

### Useability and interface

Skipperman needs to be useable by non-technical people. Hence, Skipperman will have a GUI for non technical users, but with a seperation of functions so the data can be directly used from a python command line if you know the right function calls. 

A key design decision is how the GUI is implemented and deployed; a web front end seems the most logical solution, but should this be local or cloud hosted?

Skipperman also needs to be flexible enough so that it can cope with eg changes in WA event fields without rewriting code.



## Features

### Done:

- maintain a master list of cadets and events
- import a list of entries for a specific event from WA
- allocate cadets to groups 
- print a report of which cadet is in which group
- view / delete cadets
- edit / delete events
- view / edit /add volunteers 
- allocate volunteers to a rota
- allocate safety boats
- copy roles between volunteers on volunteer rota
- allow list of boats/dinghies/etc to be reordered
- import a set of members from WA to populate a list of cadets
- report on a volunteer rota
- reports can now be sent to .xls/.csv files
- spotter sheets report
- report to public weblink is optional and puts report in different place
- filter volunteer sheets on qualification
- regular backups; include roll back function 
- record qualification data 
- record ticksheet data
- print roll call lists
- record ticksheet entries
- print ticksheets from menu
- ticksheet level security
- add health to ticksheets
- instructor login
- power boat only volunteer rota
- memorise group orders and arrangements for reports (can deal with different / missing groups)
- add contact details and health to roll call report
- phone friendly ticksheet
- allow multiple days / different allocations to boats, groups etc
- cadet location warning
- auto completes club boat
- cadet days warning
- with skipper access only - grant qualification from ticksheet screen and log date when awarded
- report of qualifications awarded by date
- list of non volunteers with cadets who are too young or first event
- maintain lists of past, present, potential and future cadet committee members (CW)
- copy all roles in cadet week rota
- store clothing choices for cadets and colour teams
- summary of colours and clothing sizes
- cadet committee polo spreadsheet
- create a report of t-shirts and sizes required
- create a colour teams report
- create a report of expected qualifications for event
- put shareable files up like instructors documents; manage shared files eg deleete, generate QR codes
- clear old reports for event (remove rednedant permalinks) and other temp directories UTILITIES MENU
- only do volunteer check on import if disagreement between days
- key report links for instructors on event landing page
- event report with literally everything on it
- summarise food numbers for cadets & volunteers
- downloadable food report with summaries, plus cadet&volunteer details
- copy across for all boats
- show history of group allocation for volunteers
- custom font size in reports
- read only mode?
- apply triangle to other notes from registration in rota
- click on 'previous role' to clone across all days in rota
- 'copy all' needs to have hard copy and soft copy
- 'copy first day' as a hard copy; 'copy blanks' as a soft copy


### Needed before CW2024

- hard/soft copies in patrol boats

### General required before handover to Jonny:

ADMIN:
- wipe all non essential information from stored data on past events

REPORTING:
- refactor reporting so uses common data model, and generally tidy up 
- create a list of key volunteers to invite to curry evening (REPORT on volunteers)
- anything that is displayed on screen can be exported to .csv eg reg details, volunteer rota (and imported...???)
- create a report of cadets
- reset various options to default values


BACKEND:
- update payment status from unpaid to paid
- total paid amounts for annual report / xfer
- refactor weird intermediate steps (allocation data object)
- ensure clean seperation backend/data, data and logic
- editable user sailing groups, volunteer roles, skills: but plain text file so can replace configuration
- backup still not ideal; introduce checks, file locking ...


INTERFACE:
- memorise whether summary buttons pressed
- template download for import of list of cadets
- instructions
- dropdown list of previous event names when creating event

UNCLASSIFIED:

- add new volunteer from volunteer rota page should include skills filter
- don't allow duplicate mapping templates and delete templates allowed
- merge cadet / merge volunteer
- edit event (warnings especially days!)
- kick off manual import of cadets and volunteers from WA mapped data (include option to just import file)


ADMIN AND DOCUMENTATION:

- move all dangerous deletes to special admin area: , delete event (should never have to do this: many warnings!), delete cadet, delete volunteer
- clear description of field names
- code documentation



### Possible future plans

- think carefully about how to handle events with no cadets, volunteers etc
- generic 'ticketed' event selling multiple kinds of ticket eg hoodies, wristbands etc
- create a food report with allergies and numbers for food only events; combine with 
- maintain and report on tickets for gala dinner, include additional gala dinner invites eg sponsors, plus ones (CW)
  (FOOD ONLY EVENT WITH NAME IMPORT FROM ANOTHER EVENT)    
- two types of food event: as part of training event, or social only seperate
- manage social event with food only (Social)
- two types of clothing event: as part of training event, or social only seperate
- manage orders for hoodies (CW)


## A few questions - Sam
### Q:How is data storage going to work? Are we going to do cloud storage? Otherwise we would have a different copy for each user that then would need merging.

A: Mostly this is single user, but the main exception would be the volunteer rotas where the skipper and deputy will work on these in colloboration so there might be a case for having a merge feature for this specific use case.

That does not preclude cloud storage, which may make sense depending on how the application is ultimatly deployed.

### I think we could probably find a good python library so we wouldn't need a web interface. Either that or there exist plenty of good libraries in other languages (I have experience with .NET MAUI for example, which is cross platform).

-Sam

