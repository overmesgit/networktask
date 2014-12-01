import json
import urlparse
import requests

import argparse

parser = argparse.ArgumentParser(description='OAuth2 authorisation with google')
parser.add_argument('id', type=str, help='client id')
parser.add_argument('secret', type=str, help='client secret')
parser.add_argument('redirect', type=str, help='redirect uri')
args = parser.parse_args()


authorize_url_params = {"url": "https://accounts.google.com/o/oauth2/auth", "scope": "email+profile",
                        "redirect": args.redirect, "id": args.id}
authorize_url = "{url}?scope={scope}&redirect_uri={redirect}&response_type=code&" \
                "client_id={id}&access_type=offline".format(**authorize_url_params)
print "Please go here and authorize: ", authorize_url


redirect_response = raw_input('Paste the full redirect URL here: ')
parsed_url = urlparse.urlparse(redirect_response)

token_url = "https://accounts.google.com/o/oauth2/token"
body = {
    "redirect_uri": args.redirect,
    "client_id": args.id,
    "client_secret": args.secret,
    "code": urlparse.parse_qs(parsed_url.query)['code'],
    "grant_type": "authorization_code"
}
token_request = requests.post(token_url, data=body)
response_dict = json.loads(token_request.content)


headers = {'Authorization': 'Bearer ' + response_dict['access_token']}
user_data_request = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', headers=headers)
print user_data_request.content
