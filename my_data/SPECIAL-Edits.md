# VSCode SPECIAL MODS.xml Edits

## postcards

### Change errant /mods/classification> tags to /mods/location

Note that the following `regex` has NOT been tested!

find: `^<classification authority=\"local\" (type=\"mixed\")?>(.+)</classification>`  
replace: `<location>\n  <shelfLocator>$1</shelfLocator>\n</location>`  

The following 5 find and replace sequences were successful.  

find: `classification authority="local" type="mixed"`  
replace: `location`  

find: `classification authority="local"`  
replace: `location`  

find: `/classification`  
replace: `/location`  

find: `<location>`  
replace:   
```
<location>
  <shelfLocator>
```

find: `</location>`  
replace:  
```
</shelfLocator>
</location>
```

### Remove errant /physicalDescription/extent@displayLabel='Digital Extent' tags

find: <extent displayLabel="Digital Extent".+<\/extent>
replace: NONE


