# config.py
from authomatic.providers import oauth2

CONFIG = {


    'lin': {

        'class_': oauth2.LinkedIn,

        # Facebook is an AuthorizationProvider too.
        'consumer_key': '758smstgs08hyg',
        'consumer_secret': 'sIOvYg3d0Yf21NAt',

        # But it is also an OAuth 2.0 provider and it needs scope.
        'scope': ['r_basicprofile','r_emailaddress','rw_company_admin','w_share'],
    },


}
