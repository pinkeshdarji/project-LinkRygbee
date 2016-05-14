# config.py
from authomatic.providers import oauth2

CONFIG = {


    'lin': {

        'class_': oauth2.LinkedIn,

        
        'consumer_key': 'some_consumer_key',
        'consumer_secret': 'some_consumer_secret',

        # But it is also an OAuth 2.0 provider and it needs scope.
        'scope': ['r_basicprofile','r_emailaddress','rw_company_admin','w_share'],
    },


}
