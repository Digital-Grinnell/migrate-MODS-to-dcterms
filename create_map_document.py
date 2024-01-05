# This script will sacn the project's Python scripts and extract all comments...

# import community packages
import os, argparse
from comment_parser import comment_parser

# import my packages
import my_data, my_colorama, constant

## === MAIN ======================================================================================

# Get the runtime args...
parser = argparse.ArgumentParser( )
parser.add_argument('--no_args_yet', '-no', nargs=1,
  help="Just a placeholder for now.", required=False, default="Nothing")
args = parser.parse_args( )

msg = "-- Now working in project directory: %s" % os.getcwd( )
my_colorama.blue(msg)

comments = []

# Go

for file in constant.CODE_FILES:
  code = comment_parser.extract_comments(file)
  for index, c in enumerate(code):
    text = f"{c}"
    if constant.MAP_MARKER in text:
      comments.append(text[5:])

# Save the logic in c.METADATA_LOGIC_FILE
with open(constant.METADATA_LOGIC_FILE, 'w') as logic:
  for line in comments:
    print(line)
    if line.startswith('  '):
      text = f"{line}\n"
    else:
      text = f"\n{line}\n"  
    logic.write(text)
    




