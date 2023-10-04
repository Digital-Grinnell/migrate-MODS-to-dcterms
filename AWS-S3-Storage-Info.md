# AWS S3 Info

New `AWS Access Key ID` and `AWS Secret Access Key` were generated and shared by Kayla on 7-July-2023.  The key and secret are saved in Mark's KeePass vault.    

  AWS Region: `us-east-1`  
  Prod: `na-st01.ext.exlibrisgroup.com`  
  PSB: `na-test-st01.ext.exlibrisgroup.com`  

  Our `upload` directory is identifed as: `s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/`  
  
## AWS S3 Command Line

The _AWS S3 CLI_ (command line interface) was successfully installed on MacBook Pro _MA10713_ in July 2023.  Installation guidance was provided by [awscli](https://formulae.brew.sh/formula/awscli), the Homebrew formulae for MacBook installation.  The [AWS CLI Command Reference](https://docs.aws.amazon.com/cli/latest/reference/s3/) provides a complete list and explanation of available commands.  With the _AWS S3 CLI_ installed and configured we can list the contents of our upload directory like so:  

```
╭─mcfatem@MAC02FK0XXQ05Q ~/MIGRATION/preliminary-testing 
╰─$ aws s3 ls s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/ --recursive --human-readable --summarize      
2023-07-05 15:11:45    0 Bytes 01GCL_INST/upload/5457616230004641/eghxpgf4afoqo2s6b4aiy/.lock
2023-07-05 15:11:45  228.5 KiB 01GCL_INST/upload/5457616230004641/eghxpgf4afoqo2s6b4aiy/grinnell_16934_OBJ.jpg
2023-07-05 15:11:45    6.6 KiB 01GCL_INST/upload/5457616230004641/eghxpgf4afoqo2s6b4aiy/grinnell_16934_OBJ.jpg.clientThumb
2023-07-05 15:11:45    2.3 KiB 01GCL_INST/upload/5457616230004641/eghxpgf4afoqo2s6b4aiy/migration-test-MODS-to-DC---Alma--2023-07-05a.csv
2023-07-05 15:20:32    0 Bytes 01GCL_INST/upload/5457616230004641/jr4w1f8qx4i17cm5vui4pa/.lock
2023-07-05 15:20:33  228.5 KiB 01GCL_INST/upload/5457616230004641/jr4w1f8qx4i17cm5vui4pa/grinnell_16934_OBJ.jpg
2023-07-05 15:20:33    6.6 KiB 01GCL_INST/upload/5457616230004641/jr4w1f8qx4i17cm5vui4pa/grinnell_16934_OBJ.jpg.clientThumb
2023-07-05 15:20:32    2.3 KiB 01GCL_INST/upload/5457616230004641/jr4w1f8qx4i17cm5vui4pa/migration-test-MODS-to-DC---Alma--2023-07-05a.csv
2023-07-07 13:24:28    2.3 KiB 01GCL_INST/upload/5457616410004641/3m5zwz3119le574zmi2oh/migration-test-MODS-to-DC---Alma--2023-07-05a.csv
2023-07-07 14:41:08    1.2 MiB 01GCL_INST/upload/5457628040004641/test/grinnell_23345_OBJ.pdf
2023-07-07 14:46:07    3.1 KiB 01GCL_INST/upload/5457628040004641/test/migration-test-MODS-to-DC---2023-07-07-Testing.csv

Total Objects: 11
   Total Size: 1.6 MiB
```

Everything listed above is from previous use of the Alma Digital Uploader and all were deleted using single-file `rm` _AWS S3 CLI_ commands on 10-July-2023.  For example: 

```
╭─mcfatem@MAC02FK0XXQ05Q ~/MIGRATION/preliminary-testing 
╰─$ aws s3 rm s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5457616230004641/eghxpgf4afoqo2s6b4aiy/.lock            
delete: s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5457616230004641/eghxpgf4afoqo2s6b4aiy/.lock
╭─mcfatem@MAC02FK0XXQ05Q ~/MIGRATION/preliminary-testing 
╰─$ aws s3 rm s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5457616230004641/eghxpgf4afoqo2s6b4aiy/grinnell_16934_OBJ.jpg
delete: s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5457616230004641/eghxpgf4afoqo2s6b4aiy/grinnell_16934_OBJ.jpg
╭─mcfatem@MAC02FK0XXQ05Q ~/MIGRATION/preliminary-testing 
╰─$ aws s3 rm s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5457616230004641/eghxpgf4afoqo2s6b4aiy/grinnell_16934_OBJ.jpg.c
lientThumb
delete: s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5457616230004641/eghxpgf4afoqo2s6b4aiy/grinnell_16934_OBJ.jpg.clientThumb
```

After removing all the existing files...  

```
╭─mcfatem@MAC02FK0XXQ05Q ~/MIGRATION/preliminary-testing 
╰─$ aws s3 ls s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/ --recursive --human-readable --summarize                                

Total Objects: 0
   Total Size: 0 Bytes
```

## Recursive AWS S3 Operations

The most useful _AWS S3 CLI_ commands like `cp`, `mv`, and `rm` are single-file operations, they operate on only one file at a time.  However, these can be combined with the `--recursive` option to effect changes in bulk.  For example...  

```
╭─mcfatem@MAC02FK0XXQ05Q ~/MIGRATION/preliminary-testing 
╰─$ aws s3 rm s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/preliminary-testing/ --recursive         
delete: s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/preliminary-testing/d.csv
delete: s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/preliminary-testing/test.jpg
delete: s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/preliminary-testing/test.pdf
```

## Mounting the Upload Folder to a Mac

Let's try [goofyfs](https://github.com/kahing/goofys) as documented in [Mounting an S3 bucket as a folder on Mac OS X](https://gist.github.com/tomsing1/8ea0169f7a47224accc3ae18ca14e951) to access the _AWS S3_ bucket and `upload`` directory provided with Alma.  **Nope, that failed on MA10713.**  

The installation also failed on my personal Mac Mini, and installation of any alternatives for mounting an _S3_ directory look equally bleak.  So, let's scrap this notion and just use the _AWS S3 CLI_ instead.

# Typical Upload and Bulk Ingest via CSV

In the Alma GUI it goes something like this:

1) Create new, or modify an existing, _Import Profile - Digital_,
2) Use the _Digital Uploader_ (_DU_) to associate that profile with a process which creates and reports an upload <sup>*</sup>directory name,
3) Upload all files (including the .csv) to the new directory either in _DU_ or some other client like the _AWS S3 CLI_,
4) Submit the associated profile and process (job) for completion, and
5) Finally, _run_ the process that was just submitted.

<sup>*</sup>Grinnell's sandbox Alma upload directory path will be of the form  
`s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/<profile ID>/<process ID>/`. 

# Modified Upload and Bulk Ingest via CSV

Instead of the above process I'm going to try this: 

1) Use the _AWS S3 CLI_ to create `s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5457644820004641/temp/` and upload object files to that folder,
  - Example: `aws s3 cp test.jpg s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5457644820004641/temp/`
2) Create new, or modify an existing, _Import Profile - Digital_,
3) Use the _Digital Uploader_ (_DU_) to associate that profile with a process which creates and reports an upload <sup>*</sup>directory name, 
4) Copy (`cp`) or move (`mv`) the object files from `s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5457644820004641/temp/` to the new <sup>*</sup>upload directory,
  - Example: `aws s3 cp s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5457644820004641/temp/ s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5457644820004641/m0m3jd053ao1m1f86v44/ --recursive`
5) Add the `.csv` file to the process using the _Digital Uploader_,
6) Submit the associated profile and process (job) for completion, and
7) Finally, _run_ the process that was just submitted.

---

## Additional Guidance

The email from Laura regarding AWS S3 access...  

Subject: GCL - Access Amazon bucket directly for Alma-D loading  
 
Hello-  
To upload pdf files to Amazon:  
1. Install aws2 CLI on the file ‘source’ server (from):  
https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html  
2. How to use the client interface:  
https://awscli.amazonaws.com/v2/documentation/api/latest/reference/s3/index.html  
3. aws configuration should be performed  
>> aws (or aws2.7) configure (e.g.):  
AWS Access Key ID [****************(key_currently_configured)]:   
AWS Secret Access Key (secret) [****************(secret_currently_configured)]:   
Default region name [us-east-1]:eu-central-1   
Default output format [table]:table (or text)  
4. Upload files from the source server’s local directory to ExL aws bucket:   
aws s3 cp <local folder> s://eu-st01.ext.exlibrisgroup.com/27UOJ_INST/upload/alma/files –recursive  

-For Alma-D it would be the import profile ID (code)  
-RE: Default region name [us-east-1]:eu-central-1  
 
Resources:  

Bulk file upload for ingest (directly to Amazon ‘upload’ folder in your bucket)  
Access Amazon bucket directly  

In each AWS region, a “bucket”, or S3 storage location, is defined; here’s yours:  
  AWS Region: `us-east-1`  
  Prod: `na-st01.ext.exlibrisgroup.com`  
  PSB: `na-test-st01.ext.exlibrisgroup.com`  

To directly access files in S3, an access key and secret are needed.   

Access keys are managed in Alma from Configuration: Resource Management > Resource Configuration > Digital Storage.   
 
You can create up to two access key and secret pairs.   
Once issued, the secret can’t be recovered, so be sure to keep it safe.   
If needed, an access key can be revoked and a new one issued.  
The access key and secret are used for direct access to the S3 storage area using one of the following 3rd party tools to communicate directly with the S3 service:  

  [AWS command line interface](http://aws.amazon.com/cli/)  
  [Alma Digital Uploader](https://urldefense.proofpoint.com/v2/url?u=https-3A__jweisman.github.io_Alma-2DDigital-2DUploader_&d=DwMFAg&c=HUrdOLg_tCr0UMeDjWLBOM9lLDRpsndbROGxEKQRFzk&r=nH2hMpTvSjRhUuvRH71mY5LhDqSZ1TYK6GsIHqRQC1c&m=-JuEOZM0gpMhZXxMr49M_ZXWoieQMYliMJ7dnaICruddgAelUnJ61JLyMI0xGqHg&s=Dva9a1tSUSJFLANgehujABaEYysojFBBDqj98osIfyI&e=) (external app)  
  ~~CloudBerry Explorer Freeware for Windows - MSP360~~  
  S3 Browser or ~~MSP360™ Explorer~~  
  3rd-party FTP-like interfaces  

Access keys are per institution; credentials generated via the sandbox environment are valid for the production environment (and vice versa).  

Additional Documentation:  
[Amazon S3 Regions and Buckets](https://urldefense.proofpoint.com/v2/url?u=https-3A__developers.exlibrisgroup.com_alma_integrations_digital_almadigital_&d=DwMFAg&c=HUrdOLg_tCr0UMeDjWLBOM9lLDRpsndbROGxEKQRFzk&r=nH2hMpTvSjRhUuvRH71mY5LhDqSZ1TYK6GsIHqRQC1c&m=-JuEOZM0gpMhZXxMr49M_ZXWoieQMYliMJ7dnaICruddgAelUnJ61JLyMI0xGqHg&s=x8gx1JfQywiG93p4MBxdckIc5fzfaDMoXuUFHaWVflU&e=)  
[Alma Digital APIs](https://urldefense.proofpoint.com/v2/url?u=https-3A__developers.exlibrisgroup.com_alma_integrations_digital_almadigital_&d=DwMFAg&c=HUrdOLg_tCr0UMeDjWLBOM9lLDRpsndbROGxEKQRFzk&r=nH2hMpTvSjRhUuvRH71mY5LhDqSZ1TYK6GsIHqRQC1c&m=-JuEOZM0gpMhZXxMr49M_ZXWoieQMYliMJ7dnaICruddgAelUnJ61JLyMI0xGqHg&s=x8gx1JfQywiG93p4MBxdckIc5fzfaDMoXuUFHaWVflU&e=)  
[Alma Digital storage limits](https://urldefense.proofpoint.com/v2/url?u=https-3A__knowledge.exlibrisgroup.com_Alma_Knowledge-5FArticles_Alma-5FDigital-5Fstorage-5Flimits&d=DwMFAg&c=HUrdOLg_tCr0UMeDjWLBOM9lLDRpsndbROGxEKQRFzk&r=nH2hMpTvSjRhUuvRH71mY5LhDqSZ1TYK6GsIHqRQC1c&m=-JuEOZM0gpMhZXxMr49M_ZXWoieQMYliMJ7dnaICruddgAelUnJ61JLyMI0xGqHg&s=CKtod-00dmoNotkdk564t38i1lxVZV7jJCKdVuHWBRs&e=)  
[Configuring Digital Storage](https://urldefense.proofpoint.com/v2/url?u=https-3A__knowledge.exlibrisgroup.com_Alma_Product-5FDocumentation_010Alma-5FOnline-5FHelp-5F-28English-29_Digital-5FResource-5FManagement_020Configuring-5FDigital-5FResource-5FManagement_020Configuring-5FDigital-5FStorage&d=DwMFAg&c=HUrdOLg_tCr0UMeDjWLBOM9lLDRpsndbROGxEKQRFzk&r=nH2hMpTvSjRhUuvRH71mY5LhDqSZ1TYK6GsIHqRQC1c&m=-JuEOZM0gpMhZXxMr49M_ZXWoieQMYliMJ7dnaICruddgAelUnJ61JLyMI0xGqHg&s=VEa9pa1OrTc0fAzKAAkFYaJM2LRMcBb6E4_OsdqP7AQ&e=)  





