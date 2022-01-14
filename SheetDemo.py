import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")

from gi.repository import WebKit2, Gtk, Gdk, GLib
from gi.repository.WebKit2 import WebView, Settings
import sys
from urllib.parse import parse_qsl, urlparse, urlencode, urlunparse
import os
from os import path
import tempfile
import time

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client import GOOGLE_REVOKE_URI, GOOGLE_TOKEN_URI, client
import httplib2
import threading

token_path = 'token.json'
token_txt = tempfile.NamedTemporaryFile()

class MyApp:
    def __init__(self):
        mydir = path.abspath(path.dirname(__file__))
        sys.path.append(mydir)
        os.environ["PYTHONPATH"] = mydir

        ctx = WebKit2.WebContext.get_default()
        def web_extensions_init(ctx):
            mydir = path.abspath(path.dirname(__file__))
            print(f"Extension directory: {mydir}")
            ctx.set_web_extensions_directory(mydir)
            ctx.set_web_extensions_initialization_user_data(GLib.Variant.new_string(token_txt.name))

        ctx = WebKit2.WebContext.get_default()
        ctx.connect('initialize-web-extensions', web_extensions_init)

        self.credentials = None
        self.web = WebKit2.WebView.new_with_context(ctx)
        wnd = Gtk.Window()
        wnd.connect("destroy", Gtk.main_quit)
        wnd.add(self.web)
        wnd.set_default_size(800, 640)
        wnd.show_all()

    def UpdateToken(self, Url):
        SCOPES = [  
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        while True:
            #try:
                creds = None
                if os.path.exists(token_path):
                    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'credentials.json', SCOPES)
                        flow.redirect_uri = "http://localhost:8081/"
                        url = flow.authorization_url()
                        print(url)
                        self.SetURL(url[0])
                        print('starting server ...')
                        creds = flow.run_local_server(
                            open_browser=False, 
                            port=8081, 
                            state=url[1], 
                            success_message="The authentication flow has completed. Opening Page...")
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())

                CLIENT_ID = creds.client_id
                CLIENT_SECRET = creds.client_secret
                REFRESH_TOKEN = creds.refresh_token

                self.credentials = client.OAuth2Credentials(
                    access_token=None,  # set access_token to None since we use a refresh token
                    client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    refresh_token=REFRESH_TOKEN,
                    token_expiry=None,
                    token_uri=GOOGLE_TOKEN_URI,
                    user_agent=None,
                    revoke_uri=GOOGLE_REVOKE_URI)

                self.credentials.refresh(httplib2.Http())  # refresh the access token (optional)

                with open(token_txt.name, "w") as f:
                    f.write(self.credentials.access_token)

                if Url is not None:
                    self.SetURL(Url)
                
                #break
            #except Exception as ex:
            #    print(ex)
            #    time.sleep(10)

                time.sleep(self.credentials._expires_in()//2)

        #threading.Timer ( 
        #    self.credentials._expires_in()//2, 
        #    self.UpdateToken, () ).start()
        
    def SetURL(self, url : str):
        if self.credentials is not None:
            o = list(urlparse(url))
            qs = parse_qsl(o[4])
            qs.append(('access_token',self.credentials.access_token))
            o[4] = urlencode(qs)  
            url = urlunparse(o)
        GLib.idle_add(self.web.load_uri, url)
    
if __name__ == "__main__":

    print(f"Name of the script      : {sys.argv[0]}")
    print(f"Arguments of the script : {sys.argv[1:]}")

    if len(sys.argv) < 2:
        print("Must pass URI to Google Spreadsheet")
        exit()

    app : MyApp = MyApp()
    thread = threading.Thread(target=app.UpdateToken, args=(sys.argv[1],))
    thread.daemon = True
    thread.start()
    #GLib.idle_add(app.UpdateToken)
    #app.SetURL(sys.argv[1])
    Gtk.main()
