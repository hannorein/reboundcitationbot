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
params = {"q":q, "rows":"2000","fl":"bibcode,pub,title,author"}
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
            pub = p["pub"]
            title = p["title"][0]
            authors = p["author"]
            authortxt = authors[0].split(",")[0]
            if len(authors)==2:
                authortxt += " & "+authors[1].split(",")[0]
            if len(authors)>2:
                authortxt += " et al."
            maxlength = 280 - 25
            text = "A new paper by "+authortxt+" has cited REBOUND:\n"+title
            text = text.replace("&amp;","&")
            if len(text)>maxlength:
                text = text[:maxlength-2] + '..' 
            url = "https://ui.adsabs.harvard.edu/abs/"+bibcode+"/abstract"
            text += " "+ url
            api.update_status(text)
            if bibcode not in oldc:
                with open(oldcf,"a") as f:
                    print(bibcode,file=f)
                break



