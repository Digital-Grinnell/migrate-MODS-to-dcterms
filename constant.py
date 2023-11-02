DONE = ' ==> '
HREF = 'https://digital.grinnell.edu/islandora/object/'
DEBUG = False
LINK = '/Volumes/LIBRARY/ALLSTAFF/DG-Metadata-Review-2020-r1/'

# COLLECTIONS_PATH = '/Volumes/LIBRARY/ALLSTAFF/DG-Metadata-Review-2020-r1/*'
# COLLECTIONS_PATH = '/Volumes/DGIngest/Metadata-Review-2020/xml-working-copy/*'
# COLLECTIONS_PATH = '/Volumes/DGIngest/Metadata-Review-2020/test/*'
# COLLECTIONS_PATH = '/Users/markmcfate/GitHub/Map-MODS-to-MASTER/my_data/test/*'
# COLLECTIONS_PATH = '/Users/markmcfate/GitHub/Map-MODS-to-MASTER/my_data/xml/*'
# COLLECTIONS_PATH = '/Volumes/March2020/exported-MODS/*'

NEEDLES = ['Remaining elements are:', 'xmlns', 'xsi', '==>']

CREATORS = ['creator','author','artist','composer']

DCMITypes = ['Collection','Dataset','Event','Image','Interactive Resource','Moving Image','Physical Object','Service','Software','Sound','Still Image','Text']

# The following RESOURCETypes dict must match Alma's `Configuration` | `Discovery` | 
#   `Loading External Data Sources` | `Dublin Core type to Discovery Type mapping`
#

RESOURCETypes = {  
 'proceedings': 'conference_proceedings',
 'proceeding': 'conference_proceedings',
 'photograph': 'images',
 'poster': 'images',
 'report': 'technical_reports',
 'journal': 'journals',
 'map': 'maps',
 'manuscript': 'manuscripts',
 'book': 'books',
 'article': 'articles',
 'book chapter': 'book_chapters',
 'book review': 'reviews',
 'dataset': 'research_datasets',
 'dissertation': 'dissertations',
 'document': 'text_resources',
 'image': 'images',
 'website': 'websites',
 'video': 'videos',
 'government document': 'government_documents',
 'score': 'scores',   # This is the end of the pre-defined set of keys.  Everything below is a "custom" mapping.
 'postcard': 'images' }

TARGET_LEVEHSHTEIN_RATIO = 90

GOOGLE_SHEET = 'https://docs.google.com/spreadsheets/d/1JzW8TGU8qJlBAlyoMyDS1mkLTGoaLrsCzVtwQo-4JlU/edit?usp=sharing'

ALMA_API_KEY = 'l8xx7a591a1ba5224ef29fd78a99db986ea9'

NO_FILE_ERROR = "*** REPLACE ME! No corresponding OBJ file found! ***"
REPLACE_ME = "*** REPLACE ME! ***"

TEMP_CSV = "temporary.csv"

ALTERNATING_COLORS = { 'yellow': [ {'backgroundColor': {'red': 1, 'green': 0.984, 'blue': 0 }}, 
                                   {'backgroundColor': {'red': 0.871, 'green': 0.863, 'blue': 0.337 }} ],
                       'green':  [ {'backgroundColor': {'red': 0.137, 'green': 0.922, 'blue': 0.165 }}, 
                                   {'backgroundColor': {'red': 0.443, 'green': 0.969, 'blue': 0.463 }} ] }
                                     

