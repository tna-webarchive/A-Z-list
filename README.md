# Set-Up
* Clone repo
* Configure command line GitHub access
  * Instructions for that [here](https://ukgwa.atlassian.net/wiki/spaces/GUID/pages/1169620993/Creating+A-Z+list+HTML)

# Process
## Adding Sites
### Getting Harvesting Summary

* Open the GWDB Reporting Tool ‘Harvesting Summary’

* Open the ‘Status’ drop down menu. Unselect ‘Transferred’. Leave all the other options selected.

* In left hand ‘Date website added to GWDB Between’ field select the date after the date the previous update finished (e.g. if the previous update covered the period 01.10.2020 to 31.12.2020 the date in this field would be 01.01.2021).

* In the right hand ‘Date website added to added to GWDB Between’ field select the final date you wish to include. This work is usually done quarterly(??) so the end date for the update mentioned above would be 31.03.2021.

  * Do not change any other fields.

* Click the ‘View Report’ button in the top right hand corner.

* Export as a csv file and save it in the A-Z-list directory

* Ensure it is called 'Harvesting Summary.csv'

### Adding Sites to Full List
* With the Harvesting Summary saved in the A-Z list, open the folder in temrinal.

* Paste the following commands: (NOTE: Python3 is the newer version of python, you might have to swap ‘python3’ for ‘python’)

  `git pull
   python add_sites.py`
* A prompt will pop up:


`New URLs between`
* Enter the date range which will become the session’s folder name e.g. ‘URLs between 01012021- 01032021’

* An excel document called ‘Verification.xlsx’ will be created containing sites which are found to be active in the archive.

* Check the site names, edit them if necessary. 

* Add the site’s categories from the drop downs in the Category columns.


* Once done, save and close the file.

* Hit Enter in the Terminal

* At this point a file called ‘cataloguing.xlsx’ will have been created which can be sent to cataloguing

* At this point the Full List will be updated to include the new sites.

* **If you have other changes to make to the Full List, make them at this point.  (before committing to GitHub)**

* You will have a chance to undo this process. Undoing will rollback all changes to prior state, i.e. step 7.

* **WARNING: Undoing the process will mean losing the Site names and Categories you have added. To keep them but undo the Full List update, move the ‘Verified New Sites.xlsx’ file to another location.** 

* By typing ‘commit’ (or anything containing the word commit (case insensitive)), the Full List will be updated locally and the changes pushed to the master list on github.

* After committing, you will be asked whether you’d like to generate the HTML of the updated full list. 

* typing 'y' will generate the HTML 

* Anything else will exit the process here. You can always generate the HTML another time without adding new sites.

## Generating HTML
* To Generate the HTML outside of the ‘Add sites’ process:

* Open terminal in the A-Z list directory

* Determine where you’d like the HTML file to be located once it has been created. 

* Enter: `python3 generateHTML.py <path to destination`

* where <path to destination> is replaced by the path to the file you’d like to create. For example to create the HTML in downloads I would type:

`python3 generateHTML.py C:\Users\micha\Downloads\A-Z-HTML.html`

* To create it in the A-Z-list folder you can just type the name of the HTML file e.g.

`python3 generateHTML.py A-Z-HTML.html`

 
# A note on requirements.txt
`requirements.txt` is a file to help other developers know what dependencies your application has.

Basically it is a list of Python modules, one per line.  It is mostly for external modules (e.g. things you install with pip) so if you used `pip install flask` then you're `requirements.txt` should have `flask` on one line.

Collaborators can then run `pip install -r requirements.txt` and automatically have all the dependencies installed in their environment.
