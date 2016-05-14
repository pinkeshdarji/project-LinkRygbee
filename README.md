# project-LinkRygbee
This project enables users to create accounts (and login) using their LinkedIn profile.Once the profile is created all sectional information (eg: Summary, industry, location , Experience, etc.) is pulled up in a nice dashboard (and stored in OrientDB). Whatever gets stored in OrientDB is synced into Elasticsearch.There is a search mechanism in the frontend to look up for registered people having similar interests.

Setup:
1. Copy LinkRygbee folder inside code folder and paste it to location where your pyramid porjects are configured to run.
2. Create Database with name as 'LinkRygbee' in orientdb.
2. Import LinkRygbee.gz file in 'LinkRygbee' database.
3. 

Before running make sure you have started 
1. Orientdb running at localhost:2480
2. elasticsearch running at localhost:9000

