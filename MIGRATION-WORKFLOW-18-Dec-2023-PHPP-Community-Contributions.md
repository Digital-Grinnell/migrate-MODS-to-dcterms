# Migration Workflow - 18-Dec-2023 - PHPP Community Contributions

This document includes the specifics of the `PHPP - Community Contributions` (grinnell:phpp-community) migration restarted on 18-Dec-2023.   See '`MIGRATION-WORKFLOW-12-Dec-2023-PHPP-Community-Contributions.md` for details that preceeded the restart.  

## Directory Changes in `export.sh`

Running the `export.sh` script for `phpp-community` previously saved MODS, OBJ, TN and other datastreams into network storage at `/mnt/libarchive/collection-MODS-export/phpp-community`, a process that took roughly 3 hours for a total of **5236** files.  While this is an acceptable elapsed time, the Python script responsible for reading the exported data, `main.py` in the `migrate-MODS-to-dcterms` project, was taking 10x to 20x longer than expected.  

### A New `exports` Directory

On December 18, 2023, changes were initiated in `export.sh` and `main.py` to save and subsequently read the exported datastreams from a `smb://storage/mediadb/DGingest/Migration-to-Alma/exports` root directory.  `export.sh` now deposits exported data into subdirectory of `//storage/mediadb/DGingest/Migration-to-Alma/exports` named for the collection being processed.  So, for example, the `phpp-community` collection exports are in the `//storage/mediadb/DGingest/Migration-to-Alma/exports/phpp-communuity` directory which has a `tree` output like:  

```
/Volumes/exports/phpp-community
├── OBJ
│   ├── grinnell_10147_OBJ.tiff
│   ├── grinnell_10147_TN.jpg
│   ├── grinnell_10148_OBJ.tiff
│   ├── grinnell_10148_TN.jpg
│   ├── ...
│   ├── grinnell_6517_TN.png
│   ├── grinnell_6522_OBJ.jpg
│   └── grinnell_6522_TN.jpg
├── grinnell_10147_MODS.xml
├── grinnell_10147_RELS-EXT.rdf
├── grinnell_10148_MODS.xml
├── grinnell_10148_RELS-EXT.rdf
├── ...
├── grinnell_6517_MODS.xml
├── grinnell_6517_RELS-EXT.rdf
├── grinnell_6522_MODS.xml
├── grinnell_6522_RELS-EXT.rdf
└── phpp-community.sparql

2 directories, 5339 files
```

It's worth noting that the `OBJ` subdirectory is important because having all of the "content" files, the OBJects and ThumbNails, in a single subdirectory makes uploading those files to AWS S3 storage much easier.  

### A New `outputs` Directory

Along with the network directory changes to `exports`, changes were made in `main.py` to save output to a new `smb://storage/mediadb/DGingest/Migration-to-Alma/outputs` root directory.  So, for the `phpp-community` collection the outputs, that's `.log` and `.remainder` files, will be saved to `//storage/mediadb/DGingest/Migration-to-Alma/outputs/phpp-communuity` directory which has a `tree` output, after script processing, like:  

```
/Volumes/outputs/phpp-community
├── collection.log
├── grinnell_10147_MODS.log
├── grinnell_10148_MODS.log
├── grinnell_10149_MODS.log
├── grinnell_10150_MODS.log
├── grinnell_10150_MODS.remainder
├── grinnell_10151_MODS.log
├── ...
├── grinnell_6522_MODS.log
├── grinnell_6522_MODS.remainder
└── mods.csv

1 directory, 2418 files
```

## DO NOT Copy Files to "Local" Storage

When this workflow was using the `/libarchivesmb/collection-MODS-export/` network storage for objects it was necessary to copy target files to local storage before running `main.py`.  **That is NO LONGER NECESSARY!**  The `main.py` script has been re-programmed to find exported files in `//storage/mediadb/DGingest/Migration-to-Alma/exports/<collection>` and route workflow output to `//storage/mediadb/DGingest/Migration-to-Alma/outputs/<collection>`.  

## OBJ Problems

Processing in `main.py` of the `phpp-community` collection produced a `mods.csv` file with zero OBJs found, the `.csv` and subsequent https://docs.google.com/spreadsheets/d/1JzW8TGU8qJlBAlyoMyDS1mkLTGoaLrsCzVtwQo-4JlU/edit#gid=57678785 sheet were full of **BOLD** RED `*** REPLACE ME! No corresponding OBJ file found! ***` messages!  The problem was found in `main.py` and corrected on 2-Jan-2023.  

## Provenance Problems

Gail astutely reported on 1-Jan-2024 that this workflow was incorrectly exporting a MODS `note` record like `<note type="provenance history">Richard Schmidt</note>` (an example from `grinnell:11414`) as a `dc:description` field.  Why?  Because the default rule for `mods:note` is to migrate to `dc:description` per [MODS to Dublin Core Metadata Element Set Mapping Version 3](https://www.loc.gov/standards/mods/mods-dcsimple.html).  

Our `main.py`script already contained logic like this:  

```
  if 'citation'.lower() in note['@type']:                #Map: if x[@type='citation']:
    return multi('dcterms:bibliographicCitation', note)  #Map:   x -> dcterms:bibliographicCitation 
```

That code basically says any `mods:note` element with a `type=` attribute where the word citation appears... should map to `dcterms:bibliographicCitation`.  Later in that `if` block there's a catch-all that maps any remaining `mods:note` terms to `dc:description`.  On 2-Jan-2024 I took steps to add a similar cluse for `mods:note` elements with a `type=` attribute containing the word `provenance`.  

The new logic (complete) looks like this:  

```
  elif '@type' in note:                                    #Map:   elif x[@type]:
    if 'provenance'.lower() in note['@type']:              #Map:     if x[@type='provenance']:
      return multi('dcterms:provenance', note)             #Map:       x -> dcterms:provenance 
    elif 'citation'.lower() in note['@type']:              #Map:     if x[@type='citation']:
      return multi('dcterms:bibliographicCitation', note)  #Map:       x -> dcterms:bibliographicCitation 
    else:                                                  #Map:     else:
      return multi('dc:description', note)                 #Map:       x -> dc:description
```

## New Collection IDs Mapping

Steps were also taken in the `main.py` script to eliminate the `--collection_id` parameter and corresponding numeric `Collection ID` references from the input and `mods.csv` output.  This is because knowing the correct numeric `Collection ID` to represent each objects' "parent" collection isn't always possible, and those values will be different in production than they are/were in the Sandbox.  Things get even more complex when considering compound objects where the parent `Collection ID` needs to reflect either a newly generated sub-collection, or the `mms_id` of a parent object.  

To deal with this change and the aforementioned complexity, our migration Google Sheet now has a new [](https://docs.google.com/spreadsheets/d/1JzW8TGU8qJlBAlyoMyDS1mkLTGoaLrsCzVtwQo-4JlU/edit#gid=778112888) `collection_IDs` worksheet that maps `.csv` `collection_name` values like `grinnell:phpp-community` to their corresponding `collection_id` value.  The value of this change will be fully demonstrated once our new compound parent/child migration feature is implemented.  

## Running `main.py` On 2-Jan-2023

To test all of the changes noted above I ran the `main.py`, `to-google-sheet.py` and `expand-csv.py` scripts found in this repo against the files previously saved in `//storage/mediadb/DGingest/Migration-to-Alma/exports/phpp-community`.  The first of the commands was this:  

```zsh
python3 main.py --collection_name phpp-community --overwrite
```

### Results of Running `main.py`

An abreviated sample of the output from `main.py` includes:  

```
-- Now working in collection directory: /Volumes/outputs/phpp-community
No DCMIType match found for 'photograph'
No DCMIType match found for 'letter'
No DCMIType match found for 'manuscript'
No DCMIType match found for 'postcard'
No DCMIType match found for 'portrait'
No DCMIType match found for 'blank form'
No Resource Type match found for 'blank form'
No DCMIType match found for 'clipping'
No DCMIType match found for 'book'
No DCMIType match found for 'advertisement'
No DCMIType match found for 'article'
No DCMIType match found for 'miscellaneous document'
No DCMIType match found for 'pamphlet'
No Resource Type match found for 'Physical Object'
No DCMIType match found for 'ephemera'
No Resource Type match found for 'ephemera'
No DCMIType match found for 'essay'
No Resource Type match found for 'essay'
No DCMIType match found for 'program'
No DCMIType match found for 'miscellaneous document'
No DCMIType match found for 'history'
No Resource Type match found for 'history'
No DCMIType match found for 'manuscript'
No DCMIType match found for 'yearbook'
No DCMIType match found for 'report'
No DCMIType match found for 'newspaper'
No DCMIType match found for 'miscellaneous document'
No DCMIType match found for 'minutes (records)'
No DCMIType match found for 'memoir'
No DCMIType match found for 'map'
```

## Missing `mods:genre` AND `mods:typeOfResource`

There are a number of `*** REPLACE ME ***` cells in Column 'U' of the latest `phpp-community` worksheet indicating that a number of objects in the colleciton have **NO mods:genre nor mods:typeOfResource** element.  Most, perhaps all, of these objects appear to have had valid `mods:genre` and/or `mods:typeOfResource` elements in previous versions of their MODS records.  

I'm going to try to restore those old values for objects that currently have neither element, and I'm going to do so with a new `iduFix` command of the form:  `iduF <PIDs> GetOldXPath`.  

### Restoring `mods:typeOfResource`

I used my new _drush_ command like so: `drush -u 1 iduF grinnell:50-50000 GetOldXPath --dsid=MODS --xpath='/mods:mods/mods:typeOfResource'`. Tthat command found **more than 4200 objects** with no current `mods:typeOfResource` AND an older MODS version that had a `mods:typeOfResource` value.  The command generated a `/var/www/html/sites/default/files/restore_missing_metadata.out` file full of commands like this one:  

```
#   Restore lost metadata...  [2024-01-03 14:06:19] 
drush -u 1 iduF grinnell:23256 AddXML --dsid=MODS --xpath='/mods:mods' --title='typeOfResource' --contents='still image'
```

Doing a `source restore_missing_metadata.out` command took care of introducing the missing `mods:typeOfResource` elements back into all of the listed objects but that had to be done in two runs because of a network disconnect halfway through the first process.  The two halves of the process were subsequently saved as `sites/default/files/restore_missing_metadata.out.original-from-3-Jan-2023` and `sites/default/files/restore_missing_metadata.abridged-from-3-Jan-2023`. 

### Restoring `mods:genre`

I repeated the above process but for `mods:genre` using: `drush -u 1 iduF grinnell:50-50000 GetOldXPath --dsid=MODS --xpath='/mods:mods/mods:genre'`.  That run produced a new `restore_missing_metadata-GENRE.out` file for 83 objects.  Running `source restore_missing_metadata-GENRE.out` corrected those in short order.  

## Exported from Islandora

In _VSCode_ I used the `Remote SSH: Connection to host...` command and selected `DGDocker1`.  The provided me with a new _VSCode_ workspace window in which I opened the remote `/home/islandora` directory.  Within that directory both the `export.sh` and `collections.list` files were visible and opened for editing.  

I added a comment to indicate what I'm up to then I opened a new terminal in _VSCode_ within the active workspace, this gives me a command line interface inside the `DGDocker1` host.  In that terminal space I entered these commands to ensure that copies of `collections.list`, `export.sh` and `ri-query.txt` are active inside the _Apache_ container.  

```
docker cp collections.list isle-apache-dg:/. 
docker cp export.sh isle-apache-dg:/. 
docker cp ri-query.txt isle-apache-dg:/.
```

Next I tried the commands required to run the `export.sh` script.  The commands and subsequent output included:  

```zsh
[islandora@dgdocker1 ~]$ cd ~
[islandora@dgdocker1 ~]$ docker exec -it isle-apache-dg bash
root@c7ffceef5d29:/# time source export.sh
Processing collection 'phpp-community'; Query is '/mnt/libarchive/collection-MODS-export/phpp-community/phpp-community.sparql'...
  Collecting RELS-EXT...
Processing results 1 to 10                                                      [ok]
Datastream exported succeeded for grinnell:6183.                           [success]
Datastream exported succeeded for grinnell:12522.                          [success]
Datastream exported succeeded for grinnell:5681.                           [success]
Datastream exported succeeded for grinnell:20424.                          [success]
Datastream exported succeeded for grinnell:5284.                           [success]
Datastream exported succeeded for grinnell:12071.                          [success]
Datastream exported succeeded for grinnell:27234.                          [success]
Datastream exported succeeded for grinnell:20618.                          [success]
Datastream exported succeeded for grinnell:30060.                          [success]
Datastream exported succeeded for grinnell:6201.                           [success]
Processing results 11 to 20                                                     [ok]
Datastream exported succeeded for grinnell:30047.                          [success]
Datastream exported succeeded for grinnell:11811.                          [success]
...

```

## Exported Files




<!-- Progress Marker !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! -->
<div style="border: 3px solid red; padding: 10px; margin: 10px; font-weight: bold; font-size: large;text-align: center;"><span>Progress STOPPED here!</span></div>
<!-- Progress Marker !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! -->

# CRITICAL Error!!!

There were several hundred "bad parents" in DG that needed to be resolved before moving forward.  A "bad parent" is a compound parent object that lives in a different collection (or NO collection) than one or more of its children.  

The "bad parents" mentioned above were resolved over the weekend of December 16-17, but other script changes related to compound parent/child export are urgently needed so I'm going to terminate this document, revise the scripts (and `MIGRATION-WORKFLOW.md`), and open a new `MIGRATION-WORKFLOW-18-Dec-2023-PHPP-Community-Contributions.md`.   

<!-- Progress Marker !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! -->
<div style="border: 3px solid red; padding: 10px; margin: 10px; font-weight: bold; font-size: large;text-align: center;"><span>This marks the end of progress from 12-Dec to 18-Dec.  What follows below may be obsolete.  Look to `MIGRATION-WORKFLOW-18-Dec-2023-PHPP-Community-Contributions.md` for additional changes.</span></div>
<!-- Progress Marker !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! -->

```zsh
python3 to-google-sheet.py --collection_path ./data/phpp-community
python3 expand-csv.py --collection_path ./data/phpp-community
```

Most notably, that process created a new `expanded.csv` file, and that is the file that we need to ingest into our Alma (sandbox) instance.  **Critical note: The name must be `expanded.csv` as that is the expected metadata file name in our The `main.py` script also created a new `OBJ` subdirectory where all of the OBJ (object) files are stored.  

## Alma Digital Uploader

So, we invoke the _Alma Digital Uploader_ via `Resources | Digital Uploader` menu selections in Alma.  Then `Add New Ingest` from the menu tab in the upper-right corner, and entered the `Ingest Details | Name` as `postcards-Oct-5a`.  In this case that selection generated an all-important `ID` value of **p31n8ka9ojzg5tk37bhda**.  That ID will be needed very soon, so I made a copy of it.

Next, I selected `Add Files` then navigated to the local directory containing our `postcards-expanded.csv` file and picked it.  Next I clicked on `Upload All` to send that CSV file off for later processing.  Then I clicked `OK` and was transported back to a _Digital Uploader_ page showing my ID with a status of `Upload Complete`.  

Now we need to turn to our `aws S3` command line tool.  

## Engaging Amazon `aws`

Following guidance provided in `AWS-S3-Storage-Info.md`...  

To list the contents of our `upload` directory...  
```zsh
aws s3 ls s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/ --recursive --human-readable --summarize
```

Like so...   

```zsh
(.venv) ╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main●› 
╰─$ aws s3 ls s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/ --recursive --human-readable --summarize
2023-07-13 16:17:27    0 Bytes 01GCL_INST/upload/5415182260004641/722cyb6kfcq5xs8z447qr6/.lock
2023-10-03 16:40:01  228.5 KiB 01GCL_INST/upload/5457644820004641/temp/test.jpg
2023-10-05 13:39:59    0 Bytes 01GCL_INST/upload/5776525300004641/qcvgzywoqkdpqx07pb6gb/.lock
2023-10-05 13:39:59   33.5 KiB 01GCL_INST/upload/5776525300004641/qcvgzywoqkdpqx07pb6gb/postcards-expanded.csv

Total Objects: 4
   Total Size: 261.9 KiB
```

Notice in the output above that our `postcards-expanded.csv` file appears and our all-important ID from above, **qcvgzywoqkdpqx07pb6gb**, is part of the file's path.  

The `file_name_1` field of the latest `postcards-expanded.csv` file contains the names of several `.jpg` image files to be associated with imported objects.  Next, try transferring those named files from local storage to our _Amazon S3_ storage as described in `AWS-S3-Storage-Info.md`.  Like so...  

```zsh
╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main●› 
╰─$ aws s3 cp ./data/postcards/OBJ/ s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/p31n8ka9ojzg5tk37bhda/ --recursive   
upload: data/postcards/OBJ/grinnell_13282_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/p31n8ka9ojzg5tk37bhda/grinnell_13282_OBJ.jpg
upload: data/postcards/OBJ/grinnell_13279_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/p31n8ka9ojzg5tk37bhda/grinnell_13279_OBJ.jpg
upload: data/postcards/OBJ/grinnell_13277_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/p31n8ka9ojzg5tk37bhda/grinnell_13277_OBJ.jpg
upload: data/postcards/OBJ/grinnell_13278_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/p31n8ka9ojzg5tk37bhda/grinnell_13278_OBJ.jpg
upload: data/postcards/OBJ/grinnell_13280_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/p31n8ka9ojzg5tk37bhda/grinnell_13280_OBJ.jpg
upload: data/postcards/OBJ/grinnell_13276_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/p31n8ka9ojzg5tk37bhda/grinnell_13276_OBJ.jpg
upload: data/postcards/OBJ/grinnell_13281_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/p31n8ka9ojzg5tk37bhda/grinnell_13281_OBJ.jpg
upload: data/postcards/OBJ/grinnell_13275_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/p31n8ka9ojzg5tk37bhda/grinnell_13275_OBJ.jpg

```

Listing the contents of our `upload` directory now shows...  

```zsh
(.venv) ╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main●› 
╰─$ aws s3 ls s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/ --recursive --human-readable --summarize

2023-07-13 16:17:27    0 Bytes 01GCL_INST/upload/5415182260004641/722cyb6kfcq5xs8z447qr6/.lock
2023-10-03 16:40:01  228.5 KiB 01GCL_INST/upload/5457644820004641/temp/test.jpg
2023-10-05 13:39:59    0 Bytes 01GCL_INST/upload/5776525300004641/qcvgzywoqkdpqx07pb6gb/.lock
2023-10-05 13:39:59   33.5 KiB 01GCL_INST/upload/5776525300004641/qcvgzywoqkdpqx07pb6gb/postcards-expanded.csv
2023-10-05 13:53:27    7.6 MiB 01GCL_INST/upload/qcvgzywoqkdpqx07pb6gb/grinnell_13275_OBJ.jpg
2023-10-05 13:53:27    2.0 MiB 01GCL_INST/upload/qcvgzywoqkdpqx07pb6gb/grinnell_13276_OBJ.jpg
2023-10-05 13:53:27  680.7 KiB 01GCL_INST/upload/qcvgzywoqkdpqx07pb6gb/grinnell_13277_OBJ.jpg
2023-10-05 13:53:27  999.0 KiB 01GCL_INST/upload/qcvgzywoqkdpqx07pb6gb/grinnell_13278_OBJ.jpg
2023-10-05 13:53:27  674.0 KiB 01GCL_INST/upload/qcvgzywoqkdpqx07pb6gb/grinnell_13279_OBJ.jpg
2023-10-05 13:53:27    1.1 MiB 01GCL_INST/upload/qcvgzywoqkdpqx07pb6gb/grinnell_13280_OBJ.jpg
2023-10-05 13:53:27    3.1 MiB 01GCL_INST/upload/qcvgzywoqkdpqx07pb6gb/grinnell_13281_OBJ.jpg
2023-10-05 13:53:27  591.6 KiB 01GCL_INST/upload/qcvgzywoqkdpqx07pb6gb/grinnell_13282_OBJ.jpg

Total Objects: 12
   Total Size: 16.9 MiB
```

Just as we hoped it would be.  

## Returning to the Digital Uploader

With a handful of the OBJ image files now residing in our S3 `upload` path, it's time to return to the Alma sandbox and continue with process.  In the _Digital Uploader_ screen I select my ingest, the one with an ID of `p31n8ka9ojzg5tk37bhda` and then click `Submit Selected`.  

## Outcome

Lots of validation errors...  So I fixed them by removing some columns from the `expanded.csv` and by adding missing column headings to our `DigitalGrinnell Qualified DC` profile to come up with this list:  

![Updated Profile](https://dgdocumentation.blob.core.windows.net/migration-documentation/dcFieldConfigurationList.png)  

The columns I had to remove from `expanded.csv` were: `import-index`, `link-to-DG`, and `log-file-link`.   I subsequently tried using local field `local_50` defined as `google_sheet_source` to carry what was our old `import-index` and more.  I also had to change the mapping of `dcterms:rights` back to `dc:rights`.  

### Dealing with "Sloppy" Software

Every time I open the `DigitalGrinnell Qualified DC` profile and click away from the “Profile Details” tab, the default ‘values.csv’ filename pops back into play wiping out the collection-specific filename I set earlier.   This apparently happens “in the background” so even if I never return to the “Profile Details” and click “Save”, the filename is changed without making me aware.  

Consequently, I am changing the name of our generated ingest CSV file from `expanded.csv` to `values.csv` so that it matches the "default" that Alma insists on using, even when told to do otherwise!   **Alma-sense: Frustrating as hell!**  

## Bulk Ingest Woes

Before departing on a much-needed vacation, I tried a number of strategies to bulk ingest objects and had limited success, but NONE of my efforts ever produced a visible image linked to a new object in our sandbox.  I'm taking steps now to clean ALL of the files out of our S3 bucket so that I can try a new "standard" one-at-a-time ingest with an image file uploaded alongside the `values.csv` file (not via the S3 command interface). 

### Exporting Collection Objects

I recently made sure that all of the objects in our test target, the `Historic Iowa Postcards` collection, have proper MODS title elements so it's time now to re-export all of those MODS records for testing.  Doing that now using the process outlined in [Exporting from Islandora](#exporting-from-islandora) above.  Done.

### Purging our AWS S3 Storage

I did this...  

```zsh
╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main●›
╰─$ aws s3 rm s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/ --recursive --exclude "*" --include "*.jpg"
delete: s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/2njo0fqogj2q7gti4kfepi/grinnell_13326_OBJ.jpg
delete: s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/2njo0fqogj2q7gti4kfepi/grinnell_13325_OBJ.jpg
delete: s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/2njo0fqogj2q7gti4kfepi/grinnell_13328_OBJ.jpg
delete: s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/2njo0fqogj2q7gti4kfepi/grinnell_13331_OBJ.jpg
...
```

And this...  

```zsh
╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main●›
╰─$ aws s3 ls s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/ --recursive --human-readable --summarize
2023-07-13 16:17:27    0 Bytes 01GCL_INST/upload/5415182260004641/722cyb6kfcq5xs8z447qr6/.lock
2023-10-09 11:53:42   56.1 KiB 01GCL_INST/upload/dided3gjriu74abw1a27qh/grinnell_103_OBJ.pdf

Total Objects: 2
   Total Size: 56.1 KiB
╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main●›
╰─$ aws s3 rm s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/ --recursive --exclude "*" --include "*.pdf"
delete: s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/dided3gjriu74abw1a27qh/grinnell_103_OBJ.pdf
╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main●›
╰─$ aws s3 rm s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/ --recursive --exclude "*" --include "*.lock"
delete: s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5415182260004641/722cyb6kfcq5xs8z447qr6/.lock
╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main●›
╰─$ aws s3 ls s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/ --recursive --human-readable --summarize

Total Objects: 0
   Total Size: 0 Bytes
```

So, we now have a clean slate.  

### Moving Files from `libarchive` to This Repo

I connected my VPN and subsequently opened a remote session on `MAD24W812UJ1G9`, the to-be-retired-long-ago iMac in my office, it's the only machine I have that can connect _Microsoft_Azure_Storage_Explorer_ to the `libarchivesmb` share (because a static IP is required).  From there I copied the following files to the `/MIGRATION/postcards` directory on my `OneDrive`:

```
grinnell_13314_OBJ.jpg
grinnell_13313_OBJ.jpg
grinnell_13312_OBJ.jpg
grinnell_13311_OBJ.jpg
grinnell_13310_OBJ.jpg
grinnell_13315_OBJ.jpg
grinnell_13316_OBJ.jpg
grinnell_13317_OBJ.jpg
grinnell_13318_OBJ.jpg
grinnell_13319_OBJ.jpg
grinnell_13310_MODS.xml
grinnell_13311_MODS.xml
grinnell_13312_MODS.xml
grinnell_13313_MODS.xml
grinnell_13314_MODS.xml
grinnell_13315_MODS.xml
grinnell_13316_MODS.xml
grinnell_13317_MODS.xml
grinnell_13318_MODS.xml
grinnell_13319_MODS.xml
```

Next, I copied opened `OneDrive` on my MacBook, made sure all 20 files were downloaded, and copied them all to this repo's `data/postcards` directory.  I then created a new `OBJ` sub-directory and moved the local copy of all `.jpg` files there.

### Running the Scripts

As prescribed earlier, I ran the `main.py`, `to-google-sheet.py` and `expand-csv.py` scripts found in this repo against the files that were just saved in `data/postcards`.  The commands looked something like this:  

```zsh
python3 main.py --collection_path ./data/postcards
python3 to-google-sheet.py --collection_path ./data/postcards
python3 expand-csv.py --collection_path ./data/postcards
```

This produced, among others, the `values.csv` file needed for ingest.  

### Preparing Alma for Upload

This attempt will NOT engage Amazon S3 storage via the _S3_ command line, it will instead attache the `*.jpg` files to the `values.csv` in a package using the Alma `Digital Uploader`.   Like so...  

1) Opened the Alma sandbox.
2) Clicked `Resources` and `Digital Uploader`
3) Selected `Insert into: Digital Grinnell (DigitalGrinnell Qualified DC profile)`.
4) Clicked `Add New Ingest` and named it `Oct-20`.  The ID returned was `wnf0a4w7dphv190q883hbm`.
5) Clicked `Add Files` and picked the `values.csv` file plus all 10 of the `.jpg` files held in the `OBJ` subdirectory. 
6) Once all were visible in the window and `Pending Upload` I clicked `Upload All`. 
7) When all uploads were complete I clicked `OK`.
8) Next I checked for the uploaded files using the _AWS S3_ command line, like so:  

```zsh
╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main●›
╰─$ aws s3 ls s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/ --recursive --human-readable --summarize
2023-10-20 23:44:37    0 Bytes 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/.lock
2023-10-20 23:44:52    3.0 MiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13310_OBJ.jpg
2023-10-20 23:45:04    6.6 KiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13310_OBJ.jpg.clientThumb
2023-10-20 23:44:49  605.7 KiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13311_OBJ.jpg
2023-10-20 23:44:52    7.4 KiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13311_OBJ.jpg.clientThumb
2023-10-20 23:45:23    1.0 MiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13312_OBJ.jpg
2023-10-20 23:45:27    7.4 KiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13312_OBJ.jpg.clientThumb
2023-10-20 23:45:04    4.4 MiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13313_OBJ.jpg
2023-10-20 23:45:23    7.0 KiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13313_OBJ.jpg.clientThumb
2023-10-20 23:45:27    5.6 MiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13314_OBJ.jpg
2023-10-20 23:45:50    7.0 KiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13314_OBJ.jpg.clientThumb
2023-10-20 23:44:46  586.7 KiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13315_OBJ.jpg
2023-10-20 23:44:49    6.9 KiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13315_OBJ.jpg.clientThumb
2023-10-20 23:44:41    1.1 MiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13317_OBJ.jpg
2023-10-20 23:44:46    6.9 KiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13317_OBJ.jpg.clientThumb
2023-10-20 23:44:38  525.2 KiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13318_OBJ.jpg
2023-10-20 23:44:41    6.3 KiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13318_OBJ.jpg.clientThumb
2023-10-20 23:45:50    4.9 MiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13319_OBJ.jpg
2023-10-20 23:46:08    6.7 KiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/grinnell_13319_OBJ.jpg.clientThumb
2023-10-20 23:44:38   15.1 KiB 01GCL_INST/upload/5776525300004641/wnf0a4w7dphv190q883hbm/values.csv

Total Objects: 20
   Total Size: 21.8 MiB
```

9) Back in Alma, I selected the `wnf0a4w7dphv190q883hbm` job named `Oct-20`, then clicked `Submit Selected` and finally `Run MD Import`. 
10) Then `Resources` and `Monitor and View Imports`.  The job status was `In Process` for some time.

_Almost midnight, time to try and get some sleep... _

### Completed Successfully

_6 AM and I don't have any plans until roughly 8:30 AM, so I'm back at it..._

I started by checking the status of last evening's Alma import via `Resources` and `Monitor and View Imports`.  The job status there changed to `Completed Successfully`.  Clicking the `...` menu and `Report` on that job showed the following abridged summary:  

| Counters |  |  
| --- | --- |  
| Total records processed | 10 | 
| Total records imported | 10 |
| Total records deleted | 0 | 
| Total records not imported/deleted | 0 | 
| Total electronic portfolios activated | 0 |  
| Total Bibliographic records created linked to the CZ | 0 |  
| Total digital items processed | 10 |   
| Total digital items imported | 10 |   

| Bibliographic Record Matches |  | |
| 1	| Matches found	| 6	|
| 2	| Single-matches found | 6 |
| 3 | Multi-matches found	| 0	|
| 4	| Multi-matches resolved automatically	| 0	|
| 5	| Multi-matches resolved automatically, Disregard CZ records| 0	|
| 6	| Multi-matches resolved automatically, Disregard invalid/canceled system	| 0	|
| 7	| Multi-matches resolved automatically, Prefer record with the same inventory type | 0 |
| 8	| Multi-matches resolved automatically, Prefer record with the same title type | 0 |	
| 9	| Multi-matches resolved automatically, Use latest created record | 0	|
| 10 | Multi-matches skipped | 0 |	
| 11 | Multi-matches, too many results were found	| 0 |

| Bibliographic Records Imported                 |    |
|------------------------------------------------|----|
| Total records imported                         | 10 |
| Bibliographic records created linked to the CZ | 0  |
| Imported records upon no match                 | 4  |
| Unlinked from CZ                               | 0  |
| Merged records                                 | 0  |
| Merged records (manually)                      | 0  |
| Overlaid records (manually)                    | 0  |
| Overlaid records                               | 6  |
| Newly added records                            | 0  |
| Newly added records (manually)                 | 0  |
| Record redirections                            | 0  |
| Headings calculated                            | 0  |

| Digital                                               |    |
|-------------------------------------------------------|----|
| Total digital items imported                          | 10 |
| Records assigned to collection                        | 10 |
| Imported digital items when skipped record processing | 0  |
| Digital items added                                   | 10 |
| Records requiring attention                           | 0  |


### Results in Primo

Odd, to say the least.  This is what I see in the `Digital Grinnell` collection...  

![Digital Grinnell Collection](https://dgdocumentation.blob.core.windows.net/migration-documentation/Primo-Digital-Grinnell-Screen-%20Shot-2023-10-21-at-7.14.29-AM.png)  

![Historic Iowa Postcards Collection](https://dgdocumentation.blob.core.windows.net/migration-documentation/Primo-HIPC-Screen%20Shot-2023-10-21-at-7.18.16-AM.png)  

![Sample Object Detail](https://dgdocumentation.blob.core.windows.net/migration-documentation/Primo-postcard-detail-Screen-Shot-2023-10-21-at-7.26.59-AM.png)  


#### Conclusions

  - Clearly, the pre-existence of "deleted", but still present, "matching" bib records from previous imports is still having a tremendous impact on the organization of these objects.  
  - Some of the objects display a thumbnail which was apparently generated by the `Digital Uploader`.  The same cannot be said for the process when `aws s3` is used to upload objects/images.  
    - **Attention!  The `aws S3` solution to this dilema is to harvest not only the object metadata and OBJ datastream from `Digital.Grinnell`, the `TN` datastream also needs to be harvested and uploaded to `s3`.**
  - None of the object details are showing the imported images, and all of them prominently display `View Full Text` and a warning that `Additional services may be available if you sign in`.  So we either have an image permissions issue, or we are not engaging the correct "viewer"?
  - In at least some instances clicking on the "open" icon (a box with an arrow point up to the right) beneath `View Full Text` and `Digital Version(s)` will open the image in a viewer.  Is this acceptable?  
    - **Attention!  Kayla suggested the absence of the image in the detailed record is due to unresolved login issues.  If we were able to login to Primo as a known user the images would appear.  ITS is working on resolution.**  

# Applying Lessons Learned to the `Social Justice` Collection

My notes regarding the creation of a new sandbox `Social Justice` collection follow...  

- Need to create a new sub-collection of `Digital Grinnell` in the sandbox...  
  - In our Alma sandbox... `Resources` then `Manage Collections`.  Select the `Digital Grinnell` top-level collection then `Add Sub-collection`.

  ![Creating the `Social Justice` Collection](https://dgdocumentation.blob.core.windows.net/migration-documentation/Creating-the-Social-Justice-Collection.png)

    - Collection ID is `81294733160004641` and MMS ID is `991011403611304641`.
    - Note that the original thumbnail (shown above) was too large to upload so its size was reduced to one half of the original.

- Based on conclusions drawn above, the `export.sh` process needs to be tweaked so that `TN` datastreams are gathered in addition to the `MODS` and `OBJ` datastreams. Making those changes now...  

```zsh
[islandora@dgdocker1 ~]$ docker cp export.sh isle-apache-dg:/export.sh
[islandora@dgdocker1 ~]$ docker cp collections.list isle-apache-dg:/collections.list
[islandora@dgdocker1 ~]$ docker exec -it isle-apache-dg bash
root@be75c79ac587:/# cat export.sh
Target=/mnt/libarchive/collection-MODS-export
# wget https://gist.github.com/McFateM/5bd7e5b0fa5d2928b2799d039a4c0fab/raw/collections.list
while read collection
do
    cp -f ri-query.txt query.sparql
    sed -i 's|COLLECTION|'${collection}'|g' query.sparql
    mkdir ${Target}/${collection}
    cp -f query.sparql ${Target}/${collection}/${collection}.sparql
    rm -f query.sparql
    q=${Target}/${collection}/${collection}.sparql
    echo "Processing collection '${collection}'; Query is '${q}'..."
    cd /var/www/html/sites/default
    drush -u 1 islandora_datastream_export --export_target=${Target}/${collection} --query=${q} --query_type=islandora_datastream_exporter_ri_query  --dsid=MODS
    drush -u 1 islandora_datastream_export --export_target=${Target}/${collection} --query=${q} --query_type=islandora_datastream_exporter_ri_query  --dsid=OBJ
    drush -u 1 islandora_datastream_export --export_target=${Target}/${collection} --query=${q} --query_type=islandora_datastream_exporter_ri_query  --dsid=TN
    cd ~
done < collections.list

root@be75c79ac587:/# source export.sh
mkdir: cannot create directory ‘/mnt/libarchive/collection-MODS-export/social-justice’: File exists
Processing collection 'social-justice'; Query is '/mnt/libarchive/collection-MODS-export/social-justice/social-justice.sparql'...
Processing results 1 to 10                                   [ok]
Datastream exported succeeded for grinnell:10377.       [success]
Datastream exported succeeded for grinnell:184.         [success]
Datastream exported succeeded for grinnell:109.         [success]
...
```

The files produced by `export.sh` have all been saved, temporarily, in this repo and a new directory at `./data/social-justice`.  

Based on `aws s3 ls...` results above I assume that thumbnail images need to be named to match their corresponding object.  For instance, an object with a filename of `grinnell_10383_OBJ.jpg` needs to have a thumbnail file named `grinnell_10383_OBJ.jpg.clientThumb`, but that thumbnail extracted from _Digital.Grinnell_ has a filename of `grinnell_10383_TN.jpg`.  

`main.py` should be modified to take care of renaming `TN` exports in the future.  For now, I've manually renamed a number of the `TN` files found in `./data/social-justice/OBJ`, and I moved objects not-to-be-considered in this first test to a new `./data/social-justice/witheld` directory.  

## Running the Scripts

```zsh
python3 main.py --collection_path ./data/social-justice --collection_id 81294733160004641
python3 to-google-sheet.py --collection_path ./data/social-justice
python3 expand-csv.py --collection_path ./data/social-justice
```

All of this, after a little wrangling, produced what looks like a viable `values.csv`.  Let's try to ingest all of this...  

So, we invoke the _Alma Digital Uploader_ via `Resources | Digital Uploader` menu selections in Alma.  Then `Add New Ingest` from the menu tab in the upper-right corner, and entered the `Ingest Details | Name` as `social-justice-Oct-23`.  In this case that selection generated an all-important `ID` value of **1wfpbky9juyzriocfgsv0i**.  That ID will be needed very soon, so I made a copy of it.

Next, I selected `Add Files` then navigated to the local directory containing our `./data/social-justice/values.csv` file and picked it.  Next I clicked on `Upload All` to send that CSV file off for later processing.  Then I clicked `OK` and was transported back to a _Digital Uploader_ page showing my ID with a status of `Upload Complete`.  

Now we need to turn to our `aws S3` command line tool.  

## Engaging Amazon `aws`

Following guidance provided in `AWS-S3-Storage-Info.md`...  

To list the contents of our `upload` directory...  
```zsh
aws s3 ls s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/ --recursive --human-readable --summarize
```

Like so...   

```zsh
(.venv) ╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main●› 
╰─$ aws s3 ls s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/ --recursive --human-readable --summarize
2023-10-23 11:27:47    0 Bytes 01GCL_INST/upload/5776525300004641/1wfpbky9juyzriocfgsv0i/.lock
2023-10-23 11:27:47   17.5 KiB 01GCL_INST/upload/5776525300004641/1wfpbky9juyzriocfgsv0i/values.csv

Total Objects: 2
   Total Size: 17.5 KiB
```

Notice in the output above that our `values.csv` file appears and our all-important ID from above, **1wfpbky9juyzriocfgsv0i**, is part of the file's path.  

The `file_name_1` field of the latest `values.csv` file contains the names of several `.jpg` image files, and a couple `.pdf` files, to be associated with imported objects.  Next, try transferring those named files from local storage to our _Amazon S3_ storage as described in `AWS-S3-Storage-Info.md`.  Like so...  

```zsh
(.venv) ╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main●› 
╰─$ aws s3 cp ./data/social-justice/OBJ/ s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/ --recursive   
upload: data/social-justice/OBJ/grinnell_10361_OBJ.pdf.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10361_OBJ.pdf.clientThumb
upload: data/social-justice/OBJ/grinnell_10362_OBJ.pdf.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10362_OBJ.pdf.clientThumb
upload: data/social-justice/OBJ/grinnell_102_OBJ.pdf.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_102_OBJ.pdf.clientThumb
upload: data/social-justice/OBJ/grinnell_10366_OBJ.jpg.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10366_OBJ.jpg.clientThumb
upload: data/social-justice/OBJ/grinnell_10367_OBJ.jpg.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10367_OBJ.jpg.clientThumb
upload: data/social-justice/OBJ/grinnell_10365_OBJ.jpg.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10365_OBJ.jpg.clientThumb
upload: data/social-justice/OBJ/grinnell_102_OBJ.pdf to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_102_OBJ.pdf
upload: data/social-justice/OBJ/grinnell_10368_OBJ.jpg.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10368_OBJ.jpg.clientThumb
upload: data/social-justice/OBJ/grinnell_10369_OBJ.jpg.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10369_OBJ.jpg.clientThumb
upload: data/social-justice/OBJ/grinnell_10361_OBJ.pdf to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10361_OBJ.pdf
upload: data/social-justice/OBJ/grinnell_10370_OBJ.jpg.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10370_OBJ.jpg.clientThumb
upload: data/social-justice/OBJ/grinnell_10371_OBJ.jpg.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10371_OBJ.jpg.clientThumb
upload: data/social-justice/OBJ/grinnell_10372_OBJ.jpg.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10372_OBJ.jpg.clientThumb
upload: data/social-justice/OBJ/grinnell_10373.OBJ.jpg.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10373.OBJ.jpg.clientThumb
upload: data/social-justice/OBJ/grinnell_10367_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10367_OBJ.jpg
upload: data/social-justice/OBJ/grinnell_10366_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10366_OBJ.jpg
upload: data/social-justice/OBJ/grinnell_10374_OBJ.jpg.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10374_OBJ.jpg.clientThumb
upload: data/social-justice/OBJ/grinnell_10369_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10369_OBJ.jpg
upload: data/social-justice/OBJ/grinnell_10368_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10368_OBJ.jpg
upload: data/social-justice/OBJ/grinnell_10365_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10365_OBJ.jpg
upload: data/social-justice/OBJ/grinnell_10370_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10370_OBJ.jpg
upload: data/social-justice/OBJ/grinnell_103_OBJ.pdf to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_103_OBJ.pdf
upload: data/social-justice/OBJ/grinnell_10375_OBJ.jpg.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10375_OBJ.jpg.clientThumb
upload: data/social-justice/OBJ/grinnell_103_OBJ.pdf.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_103_OBJ.pdf.clientThumb
upload: data/social-justice/OBJ/grinnell_10371_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10371_OBJ.jpg
upload: data/social-justice/OBJ/grinnell_184_OBJ.jpg.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_184_OBJ.jpg.clientThumb
upload: data/social-justice/OBJ/grinnell_10373_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10373_OBJ.jpg
upload: data/social-justice/OBJ/grinnell_10372_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10372_OBJ.jpg
upload: data/social-justice/OBJ/grinnell_185_OBJ.jpg.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_185_OBJ.jpg.clientThumb
upload: data/social-justice/OBJ/grinnell_186_OBJ.jpg.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_186_OBJ.jpg.clientThumb
upload: data/social-justice/OBJ/grinnell_10374_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10374_OBJ.jpg
upload: data/social-justice/OBJ/grinnell_187_OBJ.jpg.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_187_OBJ.jpg.clientThumb
upload: data/social-justice/OBJ/grinnell_10362_OBJ.pdf to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10362_OBJ.pdf
upload: data/social-justice/OBJ/social-justice.sparql to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/social-justice.sparql
upload: data/social-justice/OBJ/grinnell_184_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_184_OBJ.jpg
upload: data/social-justice/OBJ/grinnell_10375_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10375_OBJ.jpg
upload: data/social-justice/OBJ/grinnell_185_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_185_OBJ.jpg
upload: data/social-justice/OBJ/grinnell_187_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_187_OBJ.jpg
upload: data/social-justice/OBJ/grinnell_186_OBJ.jpg to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_186_OBJ.jpg
```

Listing the contents of our `upload` directory now shows...  

```zsh
(.venv) ╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main●› 
╰─$ aws s3 ls s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/ --recursive --human-readable --summarize
2023-10-23 11:30:37   32.2 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_102_OBJ.pdf
2023-10-23 11:30:37    8.0 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_102_OBJ.pdf.clientThumb
2023-10-23 11:30:37  191.4 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10361_OBJ.pdf
2023-10-23 11:30:37    2.9 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10361_OBJ.pdf.clientThumb
2023-10-23 11:30:37    5.5 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10362_OBJ.pdf
2023-10-23 11:30:37    8.6 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10362_OBJ.pdf.clientThumb
2023-10-23 11:30:37    2.8 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10365_OBJ.jpg
2023-10-23 11:30:37   39.0 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10365_OBJ.jpg.clientThumb
2023-10-23 11:30:37    2.2 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10366_OBJ.jpg
2023-10-23 11:30:37   33.6 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10366_OBJ.jpg.clientThumb
2023-10-23 11:30:37    1.5 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10367_OBJ.jpg
2023-10-23 11:30:37   31.7 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10367_OBJ.jpg.clientThumb
2023-10-23 11:30:37    2.2 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10368_OBJ.jpg
2023-10-23 11:30:37   38.0 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10368_OBJ.jpg.clientThumb
2023-10-23 11:30:37    1.9 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10369_OBJ.jpg
2023-10-23 11:30:37   32.9 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10369_OBJ.jpg.clientThumb
2023-10-23 11:30:37    2.3 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10370_OBJ.jpg
2023-10-23 11:30:37   34.1 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10370_OBJ.jpg.clientThumb
2023-10-23 11:30:37    2.3 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10371_OBJ.jpg
2023-10-23 11:30:37   33.4 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10371_OBJ.jpg.clientThumb
2023-10-23 11:30:37    2.5 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10372_OBJ.jpg
2023-10-23 11:30:38   34.0 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10372_OBJ.jpg.clientThumb
2023-10-23 11:30:38   31.8 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10373.OBJ.jpg.clientThumb
2023-10-23 11:30:38    2.2 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10373_OBJ.jpg
2023-10-23 11:30:39    2.0 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10374_OBJ.jpg
2023-10-23 11:30:39   33.6 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10374_OBJ.jpg.clientThumb
2023-10-23 11:30:39    1.9 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10375_OBJ.jpg
2023-10-23 11:30:39   38.2 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_10375_OBJ.jpg.clientThumb
2023-10-23 11:30:39   56.1 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_103_OBJ.pdf
2023-10-23 11:30:39    9.9 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_103_OBJ.pdf.clientThumb
2023-10-23 11:30:39    1.2 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_184_OBJ.jpg
2023-10-23 11:30:39   12.1 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_184_OBJ.jpg.clientThumb
2023-10-23 11:30:39    1.9 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_185_OBJ.jpg
2023-10-23 11:30:39   31.1 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_185_OBJ.jpg.clientThumb
2023-10-23 11:30:39   18.2 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_186_OBJ.jpg
2023-10-23 11:30:39   24.0 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_186_OBJ.jpg.clientThumb
2023-10-23 11:30:40    6.8 MiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_187_OBJ.jpg
2023-10-23 11:30:40    8.7 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_187_OBJ.jpg.clientThumb
2023-10-23 11:30:40  134 Bytes 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/social-justice.sparql
2023-10-23 11:27:47    0 Bytes 01GCL_INST/upload/5776525300004641/1wfpbky9juyzriocfgsv0i/.lock
2023-10-23 11:27:47   17.5 KiB 01GCL_INST/upload/5776525300004641/1wfpbky9juyzriocfgsv0i/values.csv

Total Objects: 41
   Total Size: 58.1 MiB
```

Looking good!  Just as we hoped it would be.  

## Returning to the Digital Uploader

With a handful of the OBJ files and `.clientThumb` files now residing in our S3 `upload` path, it's time to return to the Alma sandbox and continue with process.  In the _Digital Uploader_ screen I select my ingest, the one with an ID of `1wfpbky9juyzriocfgsv0i` and then click `Submit Selected`, then once enabled, `Run MD Import`.  

## Outcome

I got the dreaded status of `Manual Handling Required`.  8^(  The records returned state:  

| Error Message                         | Number of Records |
|---------------------------------------|-------------------|
| Field dcterms:dateAccepted is invalid | 15                |
| Field dcterms:temporal is invalid     | 18                |

Returing to the `Manual Handling Required` option I choose to `Reject File`, and investigate the nature of these validation errors.  Rejecting the file appears to have removed ONLY the `values.csv` file from S3 storage, so for now I've added the missing columns to the `DigitalGrinnell Qualified DC` profile so that I can try again.  Unfortunately, that will mean a new ingest job and ID.  This system sucks!  

The new ingest is `social-justice-Oct-23-fix` with a new ID of `s54yeugkjpq5j28f58z4ui`.   

Making sure the site ID of `5776525300004641` is accounted for...   

```zsh
╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main●›
╰─$ aws s3 cp ./data/social-justice/OBJ/ s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/ --recursive
upload: data/social-justice/OBJ/grinnell_10361_OBJ.pdf.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10361_OBJ.pdf.clientThumb
upload: data/social-justice/OBJ/grinnell_102_OBJ.pdf.clientThumb to s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_102_OBJ.pdf.clientThumb
...
```

And now...  

```zsh
╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main●›
╰─$ aws s3 ls s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/ --recursive --human-readable --summarize
2023-10-23 11:30:37   32.2 KiB 01GCL_INST/upload/1wfpbky9juyzriocfgsv0i/grinnell_102_OBJ.pdf
... Files in the above directory are invalid, the site ID was not included!
2023-10-23 12:35:48    0 Bytes 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/.lock
2023-10-23 12:41:18   32.2 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_102_OBJ.pdf
2023-10-23 12:41:18    8.0 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_102_OBJ.pdf.clientThumb
2023-10-23 12:41:18  191.4 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10361_OBJ.pdf
2023-10-23 12:41:18    2.9 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10361_OBJ.pdf.clientThumb
2023-10-23 12:41:18    5.5 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10362_OBJ.pdf
2023-10-23 12:41:18    8.6 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10362_OBJ.pdf.clientThumb
2023-10-23 12:41:18    2.8 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10365_OBJ.jpg
2023-10-23 12:41:18   39.0 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10365_OBJ.jpg.clientThumb
2023-10-23 12:41:18    2.2 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10366_OBJ.jpg
2023-10-23 12:41:18   33.6 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10366_OBJ.jpg.clientThumb
2023-10-23 12:41:18    1.5 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10367_OBJ.jpg
2023-10-23 12:41:18   31.7 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10367_OBJ.jpg.clientThumb
2023-10-23 12:41:18    2.2 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10368_OBJ.jpg
2023-10-23 12:41:18   38.0 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10368_OBJ.jpg.clientThumb
2023-10-23 12:41:18    1.9 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10369_OBJ.jpg
2023-10-23 12:41:18   32.9 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10369_OBJ.jpg.clientThumb
2023-10-23 12:41:18    2.3 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10370_OBJ.jpg
2023-10-23 12:41:18   34.1 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10370_OBJ.jpg.clientThumb
2023-10-23 12:41:18    2.3 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10371_OBJ.jpg
2023-10-23 12:41:19   33.4 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10371_OBJ.jpg.clientThumb
2023-10-23 12:41:19    2.5 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10372_OBJ.jpg
2023-10-23 12:41:19   34.0 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10372_OBJ.jpg.clientThumb
2023-10-23 12:41:19   31.8 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10373.OBJ.jpg.clientThumb
2023-10-23 12:41:19    2.2 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10373_OBJ.jpg
2023-10-23 12:41:20    2.0 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10374_OBJ.jpg
2023-10-23 12:41:20   33.6 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10374_OBJ.jpg.clientThumb
2023-10-23 12:41:20    1.9 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10375_OBJ.jpg
2023-10-23 12:41:20   38.2 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_10375_OBJ.jpg.clientThumb
2023-10-23 12:41:20   56.1 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_103_OBJ.pdf
2023-10-23 12:41:20    9.9 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_103_OBJ.pdf.clientThumb
2023-10-23 12:41:20    1.2 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_184_OBJ.jpg
2023-10-23 12:41:20   12.1 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_184_OBJ.jpg.clientThumb
2023-10-23 12:41:20    1.9 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_185_OBJ.jpg
2023-10-23 12:41:20   31.1 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_185_OBJ.jpg.clientThumb
2023-10-23 12:41:20   18.2 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_186_OBJ.jpg
2023-10-23 12:41:21   24.0 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_186_OBJ.jpg.clientThumb
2023-10-23 12:41:21    6.8 MiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_187_OBJ.jpg
2023-10-23 12:41:21    8.7 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/grinnell_187_OBJ.jpg.clientThumb
2023-10-23 12:41:21  134 Bytes 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/social-justice.sparql
2023-10-23 12:35:48   17.5 KiB 01GCL_INST/upload/5776525300004641/s54yeugkjpq5j28f58z4ui/values.csv

Total Objects: 80
   Total Size: 116.2 MiB
```

So, I uploaded files, OBJs and properly renamed TNs, to the "new" subdirectory and IT JUST WORKED.  19 new objects, no apparent errors.  One thing to note, the old PIDs of the objects appear twice in the metadata as `dc:identifier`.  It appears that this is due to that value appearing as both a `dc:identifier` field AND in the `originating_system_id` field in the `values.csv` file.  **I'm taking steps now to suppress the translation of those PIDs into the `dc:identifier` column of the CSV so that duplication no longer takes place.**  

## Compound Objects

On October 27, 2023, I was able to successfully perform our first bulk ingest of a compound parent object and some of its children.  The result can currently be seen in Primo at https://grinnell-psb.primo.exlibrisgroup.com/discovery/fulldisplay?docid=alma991011403607404641&context=L&vid=01GCL_INST:GCL&lang=en&adaptor=Local%20Search%20Engine.  Note that this was largely a "manual" test, the `values.csv` was generated by the `main.py` script from this repo, but some information had to be added before ingest in order to make this work.  

I'm taking steps now to automate those previously "manual" steps so that future `values.csv` files will automatically reflect compound parents and children.  

### RELS-EXT Needed

Identifying a compound and it's parent cannot be reliably done using just a `MODS.xml` record, doing this will most likely require a `RELS-EXT` record so I'm taking steps to modify the `export.sh` script and subsequently `main.py` to introduce the necessary data and logic.  

# New Compound Behavior

After meeting on the morning of October 31, 2023, we've decided to look at automated generation of new collections to represent compound objects, rather than using differnt "reps" of a bib record to represent the children.  In this scheme each compound parent should create a new collection using the parent title as the collection name, and all children of that compound then become individual objects within.  Before embarking on this change some cleanup of `main.py` was in order.  

