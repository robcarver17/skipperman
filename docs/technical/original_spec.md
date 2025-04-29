# SKIPPERMAN - Blackwater Sailing Club Cadet Skipper Managemet System: Original spec

This was the original spec document written in late summer 2023.

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

## A few questions - Sam G.

### Q:How is data storage going to work? Are we going to do cloud storage? Otherwise we would have a different copy for each user that then would need merging.

A: Mostly this is single user, but the main exception would be the volunteer rotas where the skipper and deputy will work on these in colloboration so there might be a case for having a merge feature for this specific use case.

That does not preclude cloud storage, which may make sense depending on how the application is ultimatly deployed.

### I think we could probably find a good python library so we wouldn't need a web interface. Either that or there exist plenty of good libraries in other languages (I have experience with .NET MAUI for example, which is cross platform).


