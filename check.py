# REBOUND Citation Bot
# Hanno Rein 2024
import requests
import os.path
from mastodon import Mastodon
from atproto import Client, client_utils
from bs4 import BeautifulSoup

# Read secrets
with open("mastodonkeys.txt") as f:
    lines = f.readlines()
    MASTODON_ACCESS_TOKEN, = [l.strip() for l in lines]

with open("bluesky.txt") as f:
    blueskykey = f.read().strip()

with open("adskey.txt") as f:
    token = f.read().strip()

# Query ADS
headers = {"Authorization": "Bearer "+token}
bibcodestocheck = ["2015MNRAS.446.1424R", "2012A&A...537A.128R", "2015MNRAS.452..376R", "2018MNRAS.473.3351R", "2019MNRAS.485.5490R", "2011MNRAS.415.3168R", "2011ascl.soft10016R", "2019MNRAS.489.4632R", "2020MNRAS.491.2885T", "2023arXiv230705683J"]
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
            soup = BeautifulSoup(title,features="html.parser")
            title = soup.get_text()
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
            
            try:
                mastodon = Mastodon(
                        access_token = MASTODON_ACCESS_TOKEN,
                        api_base_url = "https://mastodon.social/",
                        )
                mastodon.status_post(text+" "+url+ " #nbody #astrodon")
            except:
                print("Error posting to mastodon.")

            try:
                client = Client()
                client.login('reboundbot.bsky.social', blueskykey)
                text_builder = client_utils.TextBuilder()
                text_builder.text(text+"\n\nFind the paper on ")
                text_builder.link("NASA ADS", url)
                client.send_post(text_builder)
            except:
                print("Error posting to bluesky.")

            if bibcode not in oldc:
                with open(oldcf,"a") as f:
                    print(bibcode,file=f)
                break

