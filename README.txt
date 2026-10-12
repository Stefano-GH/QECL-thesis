##############################
# ----- Virtual environment
# Windows
Create venv: python -m venv <name_of_virtual_environment (typically env)>
Run venv: env/Scripts/activate
Deactivate venv: deactivate

# MAC / Linux
Create venv: python3 -m venv <name_of_virtual_environment (typically env)>
Run venv: env/bin/activate
Deactivate venv: deactivate



# ----- Packages inside venv
See all the packages: pip list
Install new package: pip install <package_name>



# ----- Save venv for remote repository
Export dependencies on an external file: pip freeze --all > requirements.txt



# ----- Import dependencies on a venv
pip install -r requirements.txt

