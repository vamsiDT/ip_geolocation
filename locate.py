#%%
import os
import requests
import pandas as pd
import numpy as np
from ip2geotools.databases.noncommercial import DbIpCity,MaxMindGeoLite2City
import json
from dns import resolver
from dns import reversename
import xmlrpc.client as xmlrpclib# For planetlab cental api

#%%
############ Planetlab
api_server = xmlrpclib.ServerProxy('https://www.planet-lab.eu/PLCAPI/', allow_none=True)
auth = {}
auth['AuthMethod'] = 'password'
auth['Username'] = 'f2013790@goa.bits-pilani.ac.in'
auth['AuthString'] = 'kira.1234'
authorized = api_server.AuthCheck(auth)
#%%
plslice=api_server.GetSlices(auth)[0]
slice_node_ids=plslice["node_ids"]
slice_nodes=api_server.GetNodes(auth,slice_node_ids)
#%%
    ################ GET ALL NODES OF THE SLICE #####################
boot_nodes=list()
i=0
for node in slice_nodes:
    if(node['boot_state']=="boot" and node['run_level']=="boot"):
        boot_nodes.append(node)
        i=i+1
#%%
        ################ LIST OF ONLY WORKING NODES #####################
nodes=list()
for node in boot_nodes:
    # print(node['hostname'])
    x=os.system('ssh -o "StrictHostKeyChecking no" -o "PasswordAuthentication no" -o "ConnectTimeout 4" -l upmc_netmet '+node['hostname']+" echo works")
    if(not x):
        nodes.append(node)
#%%
        ################ SANITY CHECK FOR NODE STATE #####################
file=open("/home/vamsi/src/master-3/netmet/ip_geolocation/working_nodes.dat", 'r+')
for node in nodes:
    print(node['hostname'])
    file.write(node['hostname']+"\n")
    # print(node['site_id'])
    # print((api_server.GetSites(auth,node['site_id']))[0]['latitude'])
sites=api_server.GetSites(auth,slice_node_ids)
#%%

node_df = pd.read_csv("loc",delimiter='\t',usecols=[1,3],names=['hostname','min_rtt'])


#%%
node_df=node_df.sort_values(by='min_rtt',ascending=True)
node_df=node_df.reset_index(drop=True)
l=node_df['min_rtt']

print(node_df['hostname'][0])
print(node_df['hostname'][1])
print(node_df['hostname'][2])
# node_df = pd.DataFrame(columns=['hostname','node_id','site_id','latitude','longitude'])
# for site in sites:
    # print(site['node_ids'])


#%%
# slide_node_hostnames= [node['hostname']] for node in slice_nodes
# all_node_hostnames = [node['hostname'] for node in api_server.GetNodes(auth, all_node_ids, ['hostname'])]

node_ids=list()
node_hostnames=list()
# os.popen('ssh -o "StrictHostKeyChecking no" -l upmc_netmet '+i+" ls").read()
for i in range(len(slice_nodes)):
    x=os.system('ssh -o "StrictHostKeyChecking no" -l upmc_netmet '+slice_nodes[i]['hostname']+" echo works")
    if(not x):
        node_hostnames.append(all_node_hostnames[i])
        node_ids.append(all_node_ids[i])
        

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
