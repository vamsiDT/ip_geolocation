#%%
import requests
import pandas as pd
from ip2geotools.databases.noncommercial import DbIpCity,MaxMindGeoLite2City
import json
from dns import resolver
from dns import reversename

#%%
############ TESTING PURPOSES



#%%

headers = {
'accept': 'application/json',
'Content-Type': 'application/json',
}

IpGeoloc=pd.read_csv("ips.txt",usecols=[0],names=['ip'])

lati=list()
longi=list()
sc=list()


for ip in IpGeoloc["ip"]:

    ############ GEO LOCATE ####################
    dat={}
    response = DbIpCity.get(ip, api_key='free')
    latitude =  response.latitude
    longitude = response.longitude
    lati.append(latitude)
    longi.append(longitude)
    
    
    ################# FINALLY CHECK THE SCORE OF OBTAINED GEO LOCATION FROM MATTHIEU'S API ###########3
# data = '{"' + str(ip) + '":[' + str(latitude) + "," + str(longitude) + ']}'
    dat[str(ip)]=[latitude,longitude]
    data=json.dumps(dat)
    scoreReq = requests.post('http://ares.planet-lab.eu:8000/', headers=headers, data=data)
    scoreResp = scoreReq.content.decode('utf-8')
    score=json.loads(scoreResp)
    sc.append(score["score"])



IpGeoloc["latitude"]=latitude
IpGeoloc["longitude"]=longitude
IpGeoloc["score"]=sc
