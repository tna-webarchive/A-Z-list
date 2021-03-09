# A-Z List
Add the harvesting summary to the folder and run the process.py script

## A note on requirements.txt
`requirements.txt` is a file to help other developers know what dependencies your application has.

Basically it is a list of Python modules, one per line.  It is mostly for external modules (e.g. things you install with pip) so if you used `pip install flask` then you're `requirements.txt` should have `flask` on one line.

Collaborators can then run `pip install -r requirements.txt` and automatically have all the dependencies installed in their environment.
