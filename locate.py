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
from geopy.distance import geodesic
import math
import matplotlib.pyplot as plt
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
hostnames=list()
site_id=list()
latitude=list()
longitude=list()
for node in nodes:
    hostnames.append(node['hostname'])
    site_id.append(node['site_id'])
    latitude.append((api_server.GetSites(auth,node['site_id']))[0]['latitude'])
    longitude.append((api_server.GetSites(auth,node['site_id']))[0]['longitude'])
dataframe=pd.DataFrame(data=None,columns=['hostnames','site_id','latitude','longitude'])
dataframe['hostnames']=hostnames
dataframe['site_id']=site_id
dataframe['latitude']=latitude
dataframe['longitude']=longitude
#%%
        ################ SANITY CHECK FOR NODE STATE #####################
file=open("/home/vamsi/src/master-3/netmet/ip_geolocation/working_nodes.dat", 'w+')
for hostname in dataframe['hostnames']:
    print(hostname)
    file.write(hostname + "\n")

#%%
os.system("/home/vamsi/src/master-3/netmet/ip_geolocation/loc.sh > /home/vamsi/src/master-3/netmet/ip_geolocation/loc.dat")
node_df = pd.read_csv("loc.dat",delimiter=',',usecols=[1,3],names=['hostname','min_rtt'])
#%%
node_df=node_df.sort_values(by='min_rtt',ascending=True)
node_df=node_df.reset_index(drop=True)

site_id=list()
latitude=list()
longitude=list()
for i in node_df['hostname']:
    ind=list(dataframe['hostnames']).index(str(i))
    site_id.append(dataframe['site_id'][ind])
    latitude.append(dataframe['latitude'][ind])
    longitude.append(dataframe['longitude'][ind])
node_df['site_id']=site_id
node_df['latitude']=latitude
node_df['longitude']=longitude
#############################
nsite_used=3
#############################
n_lochosts=list()
n_locsites=list()
n_loclat=list()
n_loclon=list()
# n_lochosts.append(dataframe['hostnames'][ind])
# i=1;

for i in node_df['hostname']:
    ind=list(dataframe['hostnames']).index(str(i))
    if(dataframe['site_id'][ind] not in n_locsites):
        n_locsites.append(dataframe['site_id'][ind])
        n_lochosts.append(dataframe['hostnames'][ind])
        n_loclat.append(dataframe['latitude'][ind])
        n_loclon.append(dataframe['longitude'][ind])
print(node_df['hostname'][0])
print(node_df['hostname'][1])
print(node_df['hostname'][2])
print("##########")
print(n_lochosts[0])
print(n_lochosts[1])
print(n_lochosts[2])
# node_df = pd.DataFrame(columns=['hostname','node_id','site_id','latitude','longitude'])
# for site in sites:
    # print(site['node_ids'])
#%%
os.system("/home/vamsi/src/master-3/netmet/ip_geolocation/rtt_dist.sh > /home/vamsi/src/master-3/netmet/ip_geolocation/rtt_dist.dat")
#%%
nodes_dist = pd.read_csv("rtt_dist.dat",delimiter=',',usecols=[1,3,5],names=['src_hostname','dst_hostname','min_rtt'])
s_lat=list()
s_lon=list()
d_lat=list()
d_lon=list()
dist=list()

for index, row in nodes_dist.iterrows():
# for i in nodes_dist['src_hostname']:
    
    src_node=row['src_hostname']
    dst_node=row['dst_hostname']
    # print(src_node,"",dst_node)
    ind=list(dataframe['hostnames']).index((src_node))
    src_lat=list(dataframe['latitude'])[ind]
    src_lon=list(dataframe['longitude'])[ind]
    # print(ind)
    ind=list(dataframe['hostnames']).index((dst_node))
    dst_lat=list(dataframe['latitude'])[ind]
    dst_lon=list(dataframe['longitude'])[ind]
    print(ind,"",dst_lat,"",dst_lon)
    
    distance=geodesic([src_lat,src_lon],[dst_lat,dst_lon]).kilometers
    
    s_lat.append(src_lat)
    s_lon.append(src_lon)
    d_lat.append(dst_lat)
    d_lon.append(dst_lon)
    
    dist.append(distance)
   
nodes_dist['src_lat'] = s_lat
nodes_dist['src_lon'] = s_lon
nodes_dist['dst_lat'] = d_lat
nodes_dist['dst_lon'] = d_lon
nodes_dist['distance']=dist
#%%
from sklearn import datasets, linear_model
regr = linear_model.LinearRegression()
x=list()
y=list()
for index,row in nodes_dist.iterrows():
    if(row['min_rtt']>0):
        x.append(row['distance'])
        y.append(row['min_rtt'])

x_sc = np.array(x)[:,np.newaxis]
regr.fit(x_sc,y)
y_pred = regr.predict(x_sc)

fig,ax=plt.subplots(1,1)
ax.set_xlabel("distance (Kilometers)")
ax.set_ylabel("rtt (ms)")
ax.set_title("rtt and distance relation between planetlab landmarks \n(upmc_netmet slice nodes only)")
ax.scatter(x,y,s=1)
ax.plot(x,y_pred)


regr1 = linear_model.LinearRegression()
x1=list()
y1=list()
for index,row in nodes_dist.iterrows():
    if(row['min_rtt']>0):
        y1.append(row['distance'])
        x1.append(row['min_rtt'])

x1_sc = np.array(x1)[:,np.newaxis]
regr1.fit(x1_sc,y1)
y1_pred = regr1.predict(x1_sc)

fig1,ax1=plt.subplots(1,1)
ax1.set_ylabel("distance (Kilometers)")
ax1.set_xlabel("rtt (ms)")
ax1.set_title("rtt and distance relation between planetlab landmarks \n(upmc_netmet slice nodes only)")
ax1.scatter(x1,y1,s=1)
ax1.plot(x1,y1_pred)

#%%
    

import localization as lx

P=lx.Project(mode='Earth1',solver='LSE')


P.add_anchor('anchore_A',(n_loclat[0],n_loclon[0]))
P.add_anchor('anchore_B',(n_loclat[1],n_loclon[1]))
P.add_anchor('anchore_C',(n_loclat[2],n_loclon[2]))

t,label=P.add_target()

t.add_measure('anchore_A',620)
t.add_measure('anchore_B',900)
t.add_measure('anchore_C',800)

P.solve()

# Then the target location is:

print(t.loc)




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
