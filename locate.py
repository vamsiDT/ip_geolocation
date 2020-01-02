import requests
import pandas as pd
from ip2geotools.databases.noncommercial import DbIpCity


import json

headers = {
'accept': 'application/json',
'Content-Type': 'application/json',
}

IpGeoloc=pd.read_csv("ips.txt",usecols=[0],names=['ip'])

lati=list()
longi=list()
sc=list()

for ip in IpGeoloc["ip"]:
    response = DbIpCity.get(ip, api_key='free')
    latitude =  response.latitude
    longitude = response.longitude
    data = '{"' + str(ip) + '":[' + str(latitude) + "," + str(longitude) + ']}'
    score = requests.post('http://ares.planet-lab.eu:8000/', headers=headers, data=data)
    content = score.content.decode('utf-8')
    x=json.loads(content)
    sc.append(x["score"])
    lati.append(latitude)
    longi.append(longitude)
    
IpGeoloc["latitude"]=latitude
IpGeoloc["longitude"]=longitude
IpGeoloc["score"]=sc