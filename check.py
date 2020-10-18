import requests
import os.path
import tweepy

with open("twitterkeys.txt") as f:
    lines = f.readlines()
    CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET = [l.strip() for l in lines]
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

with open("adskey.txt") as f:
    token = f.read().strip()
headers = {"Authorization": "Bearer "+token}
params = {"q":"citations(bibcode:2012A&A...537A.128R)", "rows":"2000","fl":"bibcode,pub,title"}
url = "https://api.adsabs.harvard.edu/v1/search/bigquery"
r = requests.get(url, headers=headers, params=params)
response = r.json()["response"]

oldcf = "oldcitations.txt"
firstrun = not os.path.isfile(oldcf)
if not firstrun:
    with open(oldcf,"r") as f:
        oldc = f.readlines()
else:
    oldc = []
oldc = [l.strip() for l in oldc]

debug = False # "2020arXiv201006614G"

for p in response["docs"]:
    bibcode = p["bibcode"]
    if bibcode not in oldc or bibcode == debug:
        if not firstrun:
            debug = False
            pub = p["pub"]
            title = p["title"][0]
            maxlength = 280 - 25
            text = "A new paper has cited REBOUND:\n"+title
            if len(text)>maxlength:
                text = text[:maxlength-2] + '..' 
            url = "https://ui.adsabs.harvard.edu/abs/"+bibcode+"/abstract"
            text += " "+ url
            api.update_status(text)
    if bibcode not in oldc:
        with open(oldcf,"a") as f:
            print(bibcode,file=f)



