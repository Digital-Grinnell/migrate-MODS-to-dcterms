# Migration Workflow - Start to Finish

This document is intended to be a comprehensive resource for understanding and managing the Grinnell College Libraries migration of Digital.Grinnell's Islandora framework to an Alma-Digital (Alma-D) instance.  

# Exporting from Islandora

Exports from DG/Islandora include MODS metadata files named `grinnell_<pid number>_MODS.xml` and OBJ (the object content) files named similarly in the form `grinnell_<pid number>_OBJ.<extension>`.  Two [blog](https://static.grinnell.edu/dlad-blog) posts address details surrounding the export of these datastreams from some of my earlier work:  

  - [Export Rootstalk OBJs from Digital.Grinnell](https://static.grinnell.edu/dlad-blog/posts/117-export-rootstalk-objs-from-dg/)
  - [Exporting, Editing & Replacing MODS Datastreams: Updated Technical Details](https://static.grinnell.edu/dlad-blog/posts/115-exporting-editing-replacing-mods-datastreams-updated-technical-details/)

The principles and commands mentioned in those posts have been encapsulated into a bash script named `export.sh` on node `DGDocker1`, the host server for our Islandora instance, in `/home/islandora`.  

## export.sh

As of this writing, the `export.sh` script reads like this:  

```sh
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
    echo Processing collection '${collection}'; Query is '${q}'...
    cd /var/www/html/sites/default
    drush -u 1 islandora_datastream_export --export_target=${Target}/${collection} --query=${q} --query_type=islandora_datastream_exporter_ri_query  --dsid=MODS
    drush -u 1 islandora_datastream_export --export_target=${Target}/${collection} --query=${q} --query_type=islandora_datastream_exporter_ri_query  --dsid=OBJ
    cd ~
done < collections.list
```

As you can see above, `export.sh` reads a list of collections to be exported from the `collections.list` text file held in the same directory.  That file at the time of this writing simply contains:  

```
postcards
social-justice
```

Ultimately the `export.sh` script and `collections.list` need to reside inside the `Apache` container in our Islandora/ISLE instance.  Note that the `Apache` container has NO editor installed so it's best to edit both files using `nano` from the `/home/islandora` directory of DGDocker1.  Those commands might look like this:  

```zsh
cd /home/islandora
nano collections.list
nano export.sh
```

The following commands issued from `DGDocker1` can then be used to place them where they need to be:  

```zsh
docker cp collections.list isle-apache-dg:/. 
docker cp export.sh isle-apache-dg:/. 
```

To run the `export.sh` script one must simply shell into the `isle-apache-dg` container and source the `export.sh` script like so:  

```zsh
[islandora@dgdocker1 ~]$ cd ~
[islandora@dgdocker1 ~]$ docker exec -it isle-apache-dg bash
root@be75c79ac587:/# source export.sh
```

Output from the above command sequence currently looks like this:  

```zsh
[islandora@dgdocker1 ~]$ cd ~
[islandora@dgdocker1 ~]$ docker exec -it isle-apache-dg bash
root@be75c79ac587:/# source export.sh
mkdir: cannot create directory ‘/mnt/libarchive/collection-MODS-export/postcards’: File exists
Processing collection ${collection}
bash: Query: command not found
Processing results 1 to 10                                                        [ok]
Datastream exported succeeded for grinnell:13669.                                                              [success]
Datastream exported succeeded for grinnell:13545.                                                              [success]
Datastream exported succeeded for grinnell:13544.                                                              [success]
Datastream exported succeeded for grinnell:16335.                                                              [success]
Datastream exported succeeded for grinnell:16324.                                                              [success]
Datastream exported succeeded for grinnell:13583.                                                              [success]
...
```

## Exported Files

`export.sh` currently specifies the destination for exported MODS and OBJ files as `/mnt/libarchive/collection-MODS-export` in a subdirectory with the same name as the named collection from `collections.list`.  `/mnt/libarchive/` is Azure network storage shared as `libarchive`.  That storage is most easily accessible using the _Microsoft Azure Storage Explorer_ (MASE) application as illustrated below.  

![Microsoft Azure Storage Explorer](https://dgdocumentation.blob.core.windows.net/migration-documentation/MASE-showing-libarchive.png)  

## Copy Files to Local Storage

This is, for now, a necessary evil... we need to copy all the `.xml` MODS and corresponding OBJ files to local storage.  In this instance I copied those files using _Microsoft Azure Storage Explorer_ into this project repo and a directory named `data/postcards`.

## Run Scripts Against Files in Local Storage

Next step, running the `main.py`, `to-google-sheet.py` and `expand-csv.py` scripts found in this repo against the files that were just saved in `data/postcards`.  The commands looked something like this:  

```zsh
python3 main.py --collection_path ./data/postcards
python3 to-google-sheet.py --collection_path ./data/postcards
python3 expand-csv.py --collection_path ./data/postcards
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

I connected my VPN and subsequently opened a remote session on `MAD24W812UJ1G9`, the presumably repossessed iMac in my office, it's the only machine I have that can connect _Microsoft_Azure_Storage_Explorer_ to the `libarchivesmb` share (because a static IP is required).  From there I copied the following files to the `/MIGRATION/postcards` directory on my `OneDrive`:

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













This document needs the following...

  - ~~Document the setup and execution of the `drush -u 1 iduF islandora_datastream_export...` command.~~  
    - ~~Include destination paths and other details.~~  
  - Document best means of moving files into place for subsequent steps, presumably `aws S3` commands.
  - Document the use of this project repo to generate a `.csv`.
  - Document the Alma portion of the import process in detail.

