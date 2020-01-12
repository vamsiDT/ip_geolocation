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
# import localization as lx
from sklearn import datasets, linear_model
# from .ipGeolocator import ipGeolocator as lx
import netmetGeolocator as lx

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

############## UNCOMMENT TO CREATE NEW RTT DISTANCE FILE ############

# os.system("/home/vamsi/src/master-3/netmet/ip_geolocation/rtt_dist.sh > /home/vamsi/src/master-3/netmet/ip_geolocation/rtt_dist.dat")


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
    # print(ind,"",dst_lat,"",dst_lon)
    
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
#    #%%
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
def geolocateIP (ip,sol):
    os.system("/home/vamsi/src/master-3/netmet/ip_geolocation/loc.sh "+ip+" > /home/vamsi/src/master-3/netmet/ip_geolocation/loc.dat")
    node_df = pd.read_csv("loc.dat",delimiter=',',usecols=[1,3],names=['hostname','min_rtt'])
#    #%%
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
    n_locrtt_target=list()
    # n_lochosts.append(dataframe['hostnames'][ind])
    # i=1;
    
    for i in node_df['hostname']:
        ind=list(dataframe['hostnames']).index(str(i))
        if(dataframe['site_id'][ind] not in n_locsites):
            n_locsites.append(dataframe['site_id'][ind])
            n_lochosts.append(dataframe['hostnames'][ind])
            n_loclat.append(dataframe['latitude'][ind])
            n_loclon.append(dataframe['longitude'][ind])
            inde=list(node_df['hostname']).index(dataframe['hostnames'][ind])
            n_locrtt_target.append(node_df['min_rtt'][inde])
    # print(node_df['hostname'][0])
    # print(node_df['hostname'][1])
    # print(node_df['hostname'][2])
    # print("##########")
    # print(n_lochosts[0])
    # print(n_lochosts[1])
    # print(n_lochosts[2])
    # node_df = pd.DataFrame(columns=['hostname','node_id','site_id','latitude','longitude'])
    # for site in sites:
        # print(site['node_ids'])
#    #%%
    
#    #%%

    
    
#    #%%
    # trilands={}
    # for index,row in nodes_dist.iterrows():
    #     if (row['src_hostname']==n_lochosts[0] and row['dst_hostname']==n_lochosts[1]):
    #         trilands["ab"]=row
    #     if (row['src_hostname']==n_lochosts[1] and row['dst_hostname']==n_lochosts[2]):
    #         trilands["bc"]=row
    #     if (row['src_hostname']==n_lochosts[0] and row['dst_hostname']==n_lochosts[2]):
    #         trilands["ca"]=row
    
    # for i in trilands.keys():
        # print(trilands[i]['min_rtt'],trilands[i]['distance'])
#    #%%
        
    
    ######################
    # regression predict function gives distance from given rtt
    # these distances are radius of circles from 3 landmarks chosen above
    # finally we need to find a best point where the target is located
    ######################
    
    # The code block below gives the target location, given 3 landmark locations 
    # and target distances from the 3 landmarks
    
    # Any new method to find the optimize target location should be added here.
    ###########################################################################
    try:
        locator=lx.ipGeolocator(solver=sol)
        target,target_id=locator.add_target()
        
        it=0
        for i in range(len(n_lochosts)):
            
            if(it>=3):
                break
            # print(n_locrtt_target[i])
            if(n_locrtt_target[i]==n_locrtt_target[i]):
                it=it+1
                locator.add_landmark(n_lochosts[i],n_loclat[i],n_loclon[i])
                # print(n_lochosts[i],n_loclat[i],n_loclon[i])
                target.add_measure(n_lochosts[i],regr1.predict(np.array([n_locrtt_target[i]])[:,np.newaxis])[0])
                # print(n_lochosts[i],regr1.predict(np.array([n_locrtt_target[i]])[:,np.newaxis])[0])
        # locator.add_landmark('anchore_A',n_loclat[0],n_loclon[0])
        # locator.add_landmark('anchore_B',n_loclat[1],n_loclon[1])
        # locator.add_landmark('anchore_C',n_loclat[2],n_loclon[2])
        
        
        
        # target.add_measure('anchore_A',regr1.predict(np.array([n_locrtt_target[0]])[:,np.newaxis])[0])
        # target.add_measure('anchore_B',regr1.predict(np.array([n_locrtt_target[1]])[:,np.newaxis])[0])
        # target.add_measure('anchore_C',regr1.predict(np.array([n_locrtt_target[2]])[:,np.newaxis])[0])
        # print("no")
        locator.locate()
        # print("hi")
        return (list([target.loc.lat,target.loc.lon]))
    except:

        return(list([0,0]))
        
    ###########################################################################
       


#%%

headers = {
'accept': 'application/json',
'Content-Type': 'application/json',
}

IpGeoloc=pd.read_csv("ips2.txt",usecols=[0],names=['ip'])
solver=list(["target_matrixLse","target_lse","target_svd"])
for sol in solver:
    lati=list()
    longi=list()
    sc=list()
    os.system("rm /home/vamsi/src/master-3/netmet/ip_geolocation/scores_"+str(sol)+".dat")
    file=open("/home/vamsi/src/master-3/netmet/ip_geolocation/scores_"+str(sol)+".dat", 'w+')
    file.close()
    for ip in IpGeoloc["ip"]:
    
        ############ GEO LOCATE ####################
        
        file=open("/home/vamsi/src/master-3/netmet/ip_geolocation/scores_"+str(sol)+".dat", 'a+')
        location = geolocateIP(str(ip),sol)
        latitude=location[0]
        longitude=location[1]
        dat={}
        
        try:
            response = DbIpCity.get(ip, api_key='free')
            latitu =  response.latitude
            longitu = response.longitude
        except:
            latitu = 90
            longitu = 90
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
        # file.write(hostname + "\n")
        file.write("ip," + str(ip) + ",latitude," + str(latitude) + ",longitude," + str(longitude) + ",score," + str(score["score"]) + ",distance_error," + str(geodesic([latitude,longitude],[latitu,longitu]).kilometers) + "\n")
        file.close()
    IpGeoloc["latitude"]=latitude
    IpGeoloc["longitude"]=longitude
    IpGeoloc["score"]=sc


    scores_dict = pd.read_csv("/home/vamsi/src/master-3/netmet/ip_geolocation/scores_"+str(sol)+".dat",delimiter=',',usecols=[1,3,5,7,9],names=['ip','latitude','longitude','score','distancce_error_solvsdb'])
    scores_dict.to_json(r"/home/vamsi/src/master-3/netmet/ip_geolocation/scores_"+str(sol)+".json",orient='records')
    # with open('scores_ipup.json') as json_file:
    #     scores_ipup = json.load(json_file)
