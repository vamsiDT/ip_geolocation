#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 11:48:24 2020

@author: vamsi
"""


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
# from sklearn import datasets, linear_model
# from .ipGeolocator import ipGeolocator as lx
import netmetGeolocator as lx

from sklearn.model_selection import train_test_split, cross_validate
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, r2_score


with open('scores_ipup.json') as json_file:
        scores_ipup = json.load(json_file)

sol_1 = pd.DataFrame(data=None)
lat1=list()
lon1=list()
for each in scores_ipup:
    lat1.append(each['latitude'])
    lon1.append(each['longitude'])
with open('netmet_geo.json') as json_file:
        netmet_geo = json.load(json_file)
sol_2 = pd.DataFrame(data=None)
lat2=list()
lon2=list()
for each in scores_ipup:
    lat2.append(netmet_geo[each['ip']][0])
    lon2.append(netmet_geo[each['ip']][1])
    
error=list()
for i in range(len(lat1)):
    error.append(geodesic([lat1[i],lon1[i]],[lat2[i],lon2[i]]).kilometers)

num_bins = 1000
counts, bin_edges = np.histogram (error, bins=num_bins, normed=True)
cdf = np.cumsum (counts)
fig,ax = plt.subplots(1,1)
ax.set_xlabel("distance")
ax.set_ylabel("cdf")
ax.set_xscale("log",basex=10)
plt.plot (bin_edges[1:], cdf/cdf[-1])
