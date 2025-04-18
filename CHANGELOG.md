
# to do next

Before Cadet week
- merge cadet, merge volunteer #15
- delete empty event, empty cadet, empty volunteer #26
- edit event name #16 and days (document what happens if days are edited)
- replace key data with parquet
- clean up html component mapping
- food add non registered #28
- food documentation and checks #49
- clothing documentation and checks #49
- add food / clothing to giant data dump #54
- add missing stuff to data dumps #55

# Version 2.3
- instructors can do attendance online
- fix a few odd bugs, clean up where cache flushing used
- more elegant handling of manual registration converting to WA
- massive warning if unique key creators missing from field mappings
- produce QR code from report page itself
- better doc on what happens if skipperman fields updated or added
- cleaned up repo to reduce disk usage on server
- speed up display of large tables by not flushing cache
- allow swapping on to empty boat
- clean up button mapping to make consistent
- can add a partner as new registration even if registration data missing
- clicking on volunteer does not show availability checkboxes; add remove role across days button
- configure visible events in group allocation 
- club boat limits general configuration 
- sort order refresh without clicking triangle
- fixed sticky problem with session state by adding redirect 

# Version 2.2
- documentation for reporting 
- click on volunteer name reveals history and availability checkboxes
- improved volunteer data dump so skills seperate, ideal for filtering
- WA qualication import
- added guess boat button 
- removed club boat automapping
- keep double handers aligned; Remove double handed button
- dont show similar cadets/volunteers if there are none. Default to similar names.
- report reset print options to defaults, different defaults for report types 
- add delete from event button to volunteers in rota page 
- on input show progress 
- training group preallocation spreadsheet 
- improve handling of import club membership list so that new adults / juniors are ignored, but existing ex cadets are included.
- Connected cadets shown in volunteer rota are all cadets, not just ones at event
- better handling of discrepancies in membership list upload
- made it easier to find cadets/volunteers when looking at all of them by adding sort order (also refactored code) 

# Version 2.1

- fixed summary by role/group not accurate in rota by adding no group
- registration editing help
- group allocation help
- option to add registration manually, with help, on both registration and group allocation 
- Helpful error mesage if adding a two handed partner who is already registered
- Adding cancel button when adding sailor
- Fixed a number of minor bugs
- Don't print cadets date of birth if default. Don't match default date cadets to others on similar.
- Modify mapping in table on screen
- Much documentation
- Read only flag on all pages
- Only skipper / admin can make backups

 
# Version 2.0

- full code refactoring and many improvements (sorry not been keeping a record)

# Version 1.0

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
- read only mode
- apply triangle to other notes from registration in rota
- hard/soft copies in patrol boats and volunteers
- improve UI of copy/swap in patrol boats and volunteers
- proper help pages
- addditional warnings for patrol boats and volunteers