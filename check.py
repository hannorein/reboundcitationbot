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
bibcodestocheck = ["2015MNRAS.446.1424R", "2012A&A...537A.128R", "2015MNRAS.452..376R", "2018MNRAS.473.3351R", "2019MNRAS.485.5490R", "2011MNRAS.415.3168R", "2011ascl.soft10016R", "2020MNRAS.491.2885T"]
q = "citations(bibcode:"+(") or citations(bibcode:".join(bibcodestocheck))+")"
params = {"q":q, "rows":"2000","fl":"bibcode,pub,title"}
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



