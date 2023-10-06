# VSCode SPECIAL MODS.xml Edits

## postcards

### Change errant /mods/classification> tags to /mods/location

find: `<classification authority="local"( type="mixed")?>(.+)<\/classification>`
replace: `<location>\n  <shelfLocator>$2</shelfLocator>\n</location>`  

### Remove errant /physicalDescription/extent@displayLabel='Digital Extent' tags

find: <extent displayLabel="Digital Extent".+<\/extent>
replace: NONE

### Remove any "empty" MODS tags

find: <location>\n.+<shelfLocator></shelfLocator>\n.+<\/location>
replace: NONE

