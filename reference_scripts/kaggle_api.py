## Kaggle API Script Reference
### Description: Python Code which highlights various ways to interact via the Kaggle API with data posted in competitions and in their database of available datasets
### Date Last Updated: 23 August 2022

###############################
## Connect to Kaggle via API ##
###############################

from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi()
api.authenticate()

###################################
## Interacting with Competitions ##
###################################

# Get an list of active competitions by Cateogry Type
## Example Categories: ‘all’, ‘featured’, ‘research’, ‘recruitment’, ‘gettingStarted’, ‘masters’, ‘playground’
api.competitions_list(category='gettingStarted')

# Select specific competition or topic
api.competitions_list(search='titanic')
api.competitions_list(search='nlp')

# Saving returned search as list 
nlp_list=api.competitions_list(search='nlp')

#Selecting specific competition from returned list
nlp_list[1]

# Pulling Data in from Selected Competition
## Example Comeptition is the Titanic Classification Competition
## Output is a list of three files: [train.csv, test.csv, gender_submission.csv]

api.competition_list_files('titanic') # Code to see Listed Files
api.competition_download_files('titanic') # Code to Download Files

## For Zipped results, use the following script to unzip the file
### NOTE: Require ZipFile Package Installation

from zipfile import ZipFile
zf = ZipFile('titanic.zip')
zf.extractall("/data") #save files in selected data folder
zf.close()

## Submitting your completed file to Competition
api.competition_submit(#name of saved results
'gender_submission.csv','API Submission',#name of competition
'titanic')

###############################
## Interacting with Datasets ##
###############################

# To download all files under a specific dataset profile
## Example dataset: COVID-19 data
## NOTE: Path format is (of_person_who_published_dataset)/name (of_the_Kaggle_dataset)

api.dataset_download_files('imdevskp/corona-virus-report')

# To Specify which file you want to download
api.dataset_download_file('imdevskp/corona-virus-report','covid_19_clean_complete.csv')

# Unzip files (to notebook/code location versus a network location)
zf = ZipFile('covid_19_clean_complete.csv.zip')
zf.extractall() 
zf.close()

