# VSCode SPECIAL MODS.xml Edits

## postcards

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