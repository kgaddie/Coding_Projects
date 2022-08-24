#Readme
## Project: Whisky Data

### Description
This project involves Web Scraping and use of Geolocation Data to gather a list of all Whisky Distilleries in the world, searching and assigning geolocation coordinates (latitude/longitude by address or country), and compiling into a base dataset for ingestion into a Tableau Dashboard

### Files Included

##### whisky_distillery_database.ipynb
Whisky Distillery Database Notebook is a Jupyter Notebook consisting of the Python script using BeautifulSoup to web scrape the WhiskyBase.com Distillery listing page in order to create a base dataframe of distillery names and countries of origin. Using Geocoders from Geopy, a function is outlined searching for an address based on distillery name, verified against the country identified, and if matched returned a lat/long set of coordinates. If a match is not returned, the simple lat/long combination for the country of designation is used instead.

##### sample_distillery_database.csv
A sample dataset of the generated whisky distilleries and geolocation data from the whisky_distillery_database.ipynb is provided for viewing and reference.

##### whisky_ratings_database.ipynb
Whisky Ratings Database Notebook references a Google Forms survey allowing users to input whisky tasting notes into an aggregated spreadsheet for compilation of tasting notes by distillery and bottling. This data is then merged with the whiskey distillery database to include location data for the distilleries for presentation into a Tableau Public Dashboard

##### sample_whisky_ratings_data.csv
A sample dataset of the compiled whisky ratings dataframe with geolocation data by distillery is provided for viewing and reference.
