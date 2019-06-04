#
# readme.txt
#

# HOOPS TO JUMP THROUGH FOR INSTALLATION

# you might need to install python-dev and python-tk
# if error on python-tk, try: pip install python-tk after virtualenv step below
sudo apt-get install python-dev python-tk

# clone the repo
cd ~/
git clone keybase://team/full_crocodile/guacamole

# change into guacamole folder
cd ~/guacamole/

# create a virtual python environment and activate it
virtualenv python; . ./python/bin/activate

# you need matplotlib
pip install matplotlib

# download and uncompress the database
gunzip db_lbc.dpkl.gz


# HOOPS TO JUMP THROUGH EVERYTIME
cd ~/guacamole/
git fetch
. python/bin/activate
python -i console.py	# <del> or <ctrl>-C to interrupt, <ctrl>-D to quit


# HOOPS TO KEEP DATABASE UPDATED
python lbdb.py	# and let it run forever, 
		# it will connect regularly to localbitcoins.com for data!!!


# WHAT ARE THESE FILES ABOUT?
location_idslugs.txt	# list of locations we track, DON'T CHANGE IT FOR NOW!
db_lbc.shelf	# the ginormous raw localbitcoins ads per snap for all locations
db_lbc.dpkl	# the smaller database that we track and use
colors.py	# new/unstable functions for selecting colors to make charts
stats.py	# new/unstable functions for gathering statistics on data sets
library.py	# somewhat stable functions for re-use by other files
lbdb.py		# creates/updates both databases, defines shelf/dpkl data types
recipes.py	# new/unstable canned recipes for creating reports and charts
upgrade.py	# code for the latest database upgrade, if conversion needed.
console.py	# to be run interactively, sets up for access to all above
