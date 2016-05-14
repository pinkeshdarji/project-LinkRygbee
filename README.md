# project-LinkRygbee
This project enables users to create accounts (and login) using their LinkedIn profile.Once the profile is created all sectional information (eg: Summary, industry, location , Experience, etc.) is pulled up in a nice dashboard (and stored in OrientDB). Whatever gets stored in OrientDB is synced into Elasticsearch.There is a search mechanism in the frontend to look up for registered people having similar interests.

![alt tag](https://github.com/pinkeshdarji/project-LinkRygbee/blob/master/Images/profile-page-overview.png)
##Setup:
1. Copy LinkRygbee folder which is inside code folder and paste it to location where your pyramid porjects are configured to run.
2. Create Database with name as 'LinkRygbee' in orientdb.
3. Copy paste LinkRygbee.gz file from database folder and import it in 'LinkRygbee' database.
4. Create Application at (https://www.linkedin.com/developer/apps) and obtain consumer_key(Client ID) and consumer_secret(Client Secret).
5. After creating application check all default application permission(r_basicprofile,r_emailaddress,rw_company_admin,w_share) and set Authorized Redirect URLs as http://localhost:6543/login/lin

##Configuration:
1. Edit socialconfig.py file inside project.Change consumer_key and consumer_secret obtained from linkedIn.


##How to run:
1. Start orientdb running at localhost:2480
2. Start elasticsearch running at localhost:9000
3. Run Linkrygbee project which you have pasted earlier as usual.

##Dependency: 
#### *For running this project you need 3 libraries to be installed.*
1. Authomatic:- pip install authomatic (http://peterhudec.github.io/authomatic/)
2. pyorient:- pip install pyorient
(https://github.com/orientechnologies/pyorient)
3. pyelasticsearch:- pip install pyelasticsearch
(http://pyelasticsearch.readthedocs.io/en/latest/)
:+1:



