from pyramid.view import view_config
import pyorient
import html
from .socialconfig import *
from pyramid.response import Response
from authomatic import Authomatic
from authomatic.adapters import WebObAdapter
from pyramid.httpexceptions import HTTPFound
from pyelasticsearch import ElasticSearch

# Connect to elasticsearch.
authomatic = Authomatic(config=CONFIG, secret='some random secret string')
es = ElasticSearch('http://localhost:9200/')


#--------------------------------- Very first route to be called.--------------------------------- #
@view_config(route_name='home', renderer='templates/login.jinja2')
def home(request):
    # Checks if user is already logged in then redirect to his/her profile page.
    session = request.session
    if 'session_profile_id' in session:
        profile_id = session["session_profile_id"]
        return HTTPFound(location="/profile/" + profile_id)
    # If user is not already logged in then show login page.
    return {'user': "NoData"}

#--------------------------  This route must be called for login procedure.------------------------ #
@view_config(route_name='login')
def login(request):
    session = request.session
    # We will need the response to pass it to the WebObAdapter.
    response = Response()
    # Get the internal provider name URL variable.
    provider_name = request.matchdict.get('provider_name')
    # Start the login procedure.
    result = authomatic.login(WebObAdapter(request, response), provider_name)

    # Do not write anything to the response if there is no result!
    if result:

        if result.error:
            # Login procedure finished with an error.
            response.write(u'<h2>Oops, It seems to have some problem while login. Please try Again: {0}</h2>'.format(result.error.message))

        elif result.user:

            if result.user.credentials:

                # We will access the user's basic info from r_basicprofile.
                url = 'https://api.linkedin.com/v1/people/~:(id,first-name,last-name,headline,location,industry,num-connections,summary,picture-url,positions,email-address)?format=json'
                # Access user's protected resource.
                access_response = result.provider.access(url)

                if access_response.status == 200:

                    # Once user logged in store profile id in session.
                    profile_id = access_response.data.get('id')
                    session['session_profile_id'] = profile_id

                    # Open db connection
                    client = pyorient.OrientDB("localhost", 2424)
                    session_id = client.connect("root", "root@123")
                    db_name = "LinkRygbee"
                    db_username = "root"
                    db_password = "root@123"

                    if client.db_exists(db_name, pyorient.STORAGE_TYPE_MEMORY):
                        client.db_open(db_name, db_username, db_password)
                        print(db_name + " opened successfully")
                    else:
                        print("database [" + db_name + "] does not exist! session ending...")

                    # Check whether user with retrieved profileId exist or not.
                    query = "select count(*) from users where providerId = '{}'"
                    users_result = client.command(query.format(profile_id))
                    user_record = users_result[0]

                    if (user_record.count > 0):
                        # If exist then redirect to profile page.
                        client.db_close()
                        return HTTPFound(location="/profile/" + profile_id)
                    else:
                        # If not then insert new user data into database.
                        emailAddress = access_response.data.get('emailAddress')
                        headline = access_response.data.get('headline')
                        summary = access_response.data.get('summary')
                        firstName = access_response.data.get('firstName')
                        lastName = access_response.data.get('lastName')
                        location = access_response.data.get('location').get('name')
                        industry = access_response.data.get('industry')
                        pictureUrl = access_response.data.get('pictureUrl')

                        # Insert user's details in in Class 'users' in Orientdb.
                        users_details = {'@users': {'providerId': profile_id, 'email': emailAddress, 'firstName': firstName,
                                          'lastName': lastName, 'headline': headline, 'industry': industry,
                                          'pictureUrl': pictureUrl, 'summary': summary, 'location': location}}
                        inserted_user = client.record_create(12, users_details)

                        # Insert user's details in Elasticsearch at users index.
                        es_created_user_detail = es.index('users',
                                                          'user',
                                                          {'providerId': profile_id, 'email': emailAddress,
                                                           'firstName': firstName, 'lastName': lastName,
                                                           'headline': headline, 'industry': industry,
                                                           'pictureUrl': pictureUrl, 'summary': summary,
                                                           'location': location},
                                                          )

                        # Insert user's Experience details in Class 'experience' in Orientdb.
                        positions = access_response.data.get('positions').get('values')
                        for position in positions:
                            month = position.get('startDate').get('month')
                            year = position.get('startDate').get('year')
                            date = str(month) + "/" + str(year)
                            location = position.get('location').get('name')
                            company = position.get('company').get('name')
                            # insert experience
                            users_experience_details = {'@experience': {'title': position.get('title'),
                                                   'summary': position.get('summary'),
                                                   'company': company,
                                                   'date': date,
                                                   'location': location}}
                            inserted_experience = client.record_create(13, users_experience_details)

                            # Create Edge from user to experience. So that we can come to know
                            # Which user has which experience.
                            has_edges = client.command(
                                "create edge has from" + inserted_user._rid + " to " + inserted_experience._rid
                            )

                        # Once all user related details are stored then redirect user to profile page.
                        client.db_close()
                        return HTTPFound(location="/profile/" + profile_id)
                else:
                    response.write('Oops, It seems to have some problem while fetching data. Please try Again<br />')
                    response.write(u'Status: {0} '.format(response.status))
    # It won't work if you don't return the response
    return response

#--------------------------  This route to be called for showing user dashboard.------------------------ #
@view_config(route_name='userdashboard', renderer='templates/profile.jinja2')
def showUserDashboard(request):
    # Get profileID from session to query user related data.
    session = request.session
    if 'session_profile_id' in session:
        profile_id = request.matchdict['profile_id']

        #NOTE: Result from ES if we want to fetch result from ES rather than Orientdb in any case.
        # es_user = es.search('providerId:' + id + '', index='users')
        # user = es_user["hits"]["hits"][0]["_source"]
        # print(user)

        # Connect to db
        client = pyorient.OrientDB("localhost", 2424)
        session_id = client.connect("root", "root@123")
        db_name = "LinkRygbee"
        db_username = "root"
        db_password = "root@123"

        if client.db_exists(db_name, pyorient.STORAGE_TYPE_MEMORY):
            client.db_open(db_name, db_username, db_password)
            print(db_name + " opened successfully")
        else:
            print("database [" + db_name + "] does not exist! session ending...")

        # Result from Orientdb. We also have option to fetch result from ES.
        query = "select * from users where providerId = '{}'"
        users_records = client.command(query.format(html.escape(profile_id)))
        show_user = users_records[0]
        #print(record)

        # Store result in user dictionary.
        user = dict(firstName=show_user.firstName,
                    lastName=show_user.lastName,
                    headline=show_user.headline,
                    location=show_user.location,
                    industry=show_user.industry,
                    pictureUrl=show_user.pictureUrl,
                    email=show_user.email,
                    summary=show_user.summary
                    )

        # We can also store result retrieved from ES in user dictionary.
        # user = dict(firstName=user["firstName"],
        #             lastName=user["lastName"],
        #             headline=user["headline"],
        #             location=user["location"],
        #             industry=user["industry"],
        #             pictureUrl=user["pictureUrl"],
        #             email=user["email"],
        #             summary=user["summary"]
        #             )


        # Fetch user's experience details.
        query = "select expand( out( has )) from users where providerId = '{}'"
        user_has_experience = client.command(query.format(profile_id))

        # For loop to store multiple experience of single user.
        user_experience_dict = [dict(company=user_experience.company,
                              location=user_experience.location,
                              date=user_experience.date,
                              summary=user_experience.summary,
                              title=user_experience.title) for user_experience in user_has_experience]
        #print(user_exp_dict)
    else:
        return HTTPFound(location="/")

    return {'user': user, 'users_experience': user_experience_dict}

#--------------------------  This route to be called for user logout.------------------------ #
@view_config(route_name='logout')
def logoutUser(request):
    # Invalidate session on logout.
    session = request.session
    session.invalidate()
    # And redirect to login page.
    return HTTPFound(location="/")

#--------------------------  This route to be called to search for users.------------------------ #
@view_config(route_name='searchuser', renderer='json')
def searchuser(request):
    # Get search query from URL
    search_query = request.matchdict['search_query']

    # Query to return search result based on "summary", "industry", "headline", "firstName", "lastName", "location"
    query = {
        "query": {
            "query_string": {
                "query": search_query,
                "fields": ["summary", "industry", "headline", "firstName", "lastName", "location"]
            }
        }
    }

    # Store result
    searchresult = es.search(query, index='users')

    # And return it to ajax request.
    return searchresult
