from BaseHTTPServer import BaseHTTPRequestHandler
import cgi
import json
import urllib
import urlparse
import requests
import SocketServer
import argparse
import sys


parser = argparse.ArgumentParser(description='OAuth2 authorisation with google')
parser.add_argument('id', type=str, help='client id like ***-***.apps.googleusercontent.com')
parser.add_argument('secret', type=str, help='client secret like *****')
parser.add_argument('redirect', type=str, help='redirect uri like http://localhost:50505')
args = parser.parse_args()


def get_auth_url():
    authorize_url_params = {"url": "https://accounts.google.com/o/oauth2/auth", "scope": "email+profile",
                            "redirect": args.redirect, "id": args.id}
    authorize_url = "{url}?scope={scope}&redirect_uri={redirect}&response_type=code&" \
                    "client_id={id}&access_type=offline".format(**authorize_url_params)
    return authorize_url


def get_token(code):
    token_url = "https://accounts.google.com/o/oauth2/token"
    body = {
        "redirect_uri": args.redirect,
        "client_id": args.id,
        "client_secret": args.secret,
        "code": code,
        "grant_type": "authorization_code"
    }
    token_request = requests.post(token_url, data=body)
    response_dict = json.loads(token_request.content)
    if 'access_token' in response_dict:
        return response_dict['access_token']


def get_user_data(token):
    headers = {'Authorization': 'Bearer ' + token}
    user_data_request = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', headers=headers)
    return user_data_request.content


class RequestHandler(BaseHTTPRequestHandler):
    def get_request_dict(self):
        path = cgi.escape(urllib.unquote(self.path))
        parsed_url = urlparse.urlparse(path)
        return urlparse.parse_qs(parsed_url.query)

    def do_GET(self):
        request_dict = self.get_request_dict()
        if 'code' in request_dict:
            token = get_token(request_dict['code'])
            if token:
                response = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
                data = get_user_data(token)
                response += "<html>\n{}\n</html>".format(data)
                self.send_data(data)
            else:
                redirect_url = get_auth_url()
                self.send_redirect(redirect_url)
        else:
            redirect_url = get_auth_url()
            self.send_redirect(redirect_url)

    def send_data(self, data):
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data)

    def send_redirect(self, url):
        self.send_response(301)
        self.send_header("Location", url)
        self.end_headers()


PORT = 50505
httpd = SocketServer.TCPServer(("", PORT), RequestHandler)
print("go to http://localhost:{}".format(PORT))
httpd.serve_forever()