from .LandmarkTarget import *
from .shapes import *
from .methods import *


class ipGeolocator:
    def __init__(self, solver='netmet', detail=False):
        self.solver = solver
        self.detail = detail
        self.LandmarkDict = {}
        self.TargetDict = {}
        self.nt = 0

    def set_solver(self, sol):
        self.solver = sol

    def add_landmark(self, ID, lat,lon):
        try:
            self.LandmarkDict[ID]
            print(str(ID) + ':Landmark with same ID already exists')
            return
        except KeyError:
            lm = Landmark(ID, geoPoint(lat,lon))
            self.LandmarkDict[ID] = lm
        return lm

    def add_target(self, ID=None):
        try:
            self.TargetDict[ID]
            print('Target with same ID already exists')
            return
        except:
            self.nt = self.nt + 1
            if ID:
                pass
            else:
                ID = 't' + str(self.nt)
            t = Target(ID)
            self.TargetDict[ID] = t
        return (t, ID)

    def locate(self, **kwargs):
        for tID in self.TargetDict.keys():
            tar = self.TargetDict[tID]
            cA = []
            for tup in tar.measures:
                landmark = tup[0]
                c = self.LandmarkDict[landmark].loc
                d = tup[1]
                ######### CHECK THIS #####################
                cartesian=geo_to_cartesian(c)
                cartesian=cartesianPoint(cartesian.x,cartesian.y,cartesian.z)
                circ=cartesian_circ(cartesian,d)
                cA.append(circ)
                
                # cA.append(circle(cartesian, d))
            if self.solver == 'target_matrixLse':
                # print("solver")
                ans=target_matrixLse(cA)
                gp = cartesian_to_geo(ans)
                gp=geoPoint(gp.lat,gp.lon)
                tar.loc = gp
            if self.solver == 'target_svd':
                # print("solver")
                ans=target_svd(cA)
                gp = cartesian_to_geo(ans)
                gp=geoPoint(gp.lat,gp.lon)
                tar.loc = gp
            if self.solver == 'target_lse':
                # print("target_lse")
                ans=target_lse(cA)
                gp = cartesian_to_geo(ans)
                gp=geoPoint(gp.lat,gp.lon)
                tar.loc = gp
                
