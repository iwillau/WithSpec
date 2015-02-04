Siren Client for Python
=======================

Fury Badge Here.


A generic client for consuming an Hypermedia API utilising Siren. 

The client consumes the Siren and creates objects which represent the various 
Siren Objects. This library does not provide a transport mechanism to access the
API but is designed to work with a 
(requests)[http://docs.python-requests.org/en/latest/] session.

Authentication is provided by the session manager provided to the the Siren
client. Usage patterns below.


## Config

1. rel_base If set to a value, and this value is at the start of any rel
            that rel will have that value removed:
            
            Example:
               rel_base = 'http://my.company/schema/'
               
               rel from the API: 'http://my.company/schema/links'
               
               The resultant rel will be: 'links'
               

## Api Setup

1. Imply Using request.Session

import siren_client
siren_object = siren_client.get('http://my.siren.api/')


2. Pass your own Session (or equivalent)
from siren_client import SirenClient

my_custom_session = MyCustomSession()
siren_object = SirenClient(
                    session=my_custom_session,
                    data=my_custom_session.get('http://my.siren.api/'),
                    )


3. Config is passed around as a dictionary

my_config = {
    'rel_base': 'http://my.company/schema/',
    }
    
my_custom_session = MyCustomSession()
siren_object = SirenClient(
                    session=my_custom_session,
                    data=my_custom_session.get('http://my.siren.api/'),
                    config=my_config,
                    )
                    
assert siren_object.config['rel_base'] == 'http://my.siren.api/'


