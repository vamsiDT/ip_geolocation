import numpy as np
import math
##################################################################################################
class geoPoint:
    def __init__(self,lat,lon):
        self.lat = lat
        self.lon = lon

class cartesianPoint:
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
    def xyz(self):
        return [self.x, self.y, self.z]
    def __str__(self):
        return 'p(' + str(self.x) + ',' + str(self.y) + ',' + str(self.z) + ')'

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __sub__(self, other):
        if isinstance(other, cartesianPoint):
            tx = self.x - other.x
            ty = self.y - other.y
            tz = self.z - other.z
        else:
            tx = self.x - other.dx
            ty = self.y - other.dy
            tz = self.z - other.dz
        return cartesianPoint(tx, ty, tz)

    def __add__(self, other):
        if isinstance(other, cartesianPoint):
            tx = self.x + other.x
            ty = self.y + other.y
            tz = self.z + other.z
        else:
            tx = self.x + other.dx
            ty = self.y + other.dy
            tz = self.z + other.dz
        return cartesianPoint(tx, ty, tz)

    def __mul__(self, other):
        return cartesianPoint(other * self.x, other * self.y, other * self.z)

    def __rmul__(self, other):
        return cartesianPoint(other * self.x, other * self.y, other * self.z)

    def __div__(self, other):
        return cartesianPoint(self.x / other, self.y / other, self.z / other)

    def __neg__(self):
        x = -self.x
        y = -self.y
        z = -self.z
        return cartesianPoint(x, y, z)

    def area(self):
        return 0.0

    def dist(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2) ** 0.5

    def std(self):
        if self.dim == 2:
            return [self.x, self.y]
        return [self.x, self.y, self.z]

    def c2s(self):
        R = self.dist(cartesianPoint(0, 0, 0))
        lg = math.atan(self.y / self.x)
        lat = math.acos(self.z / R)
        return (lg, lat, R)

    # ~ def transform(self,p1,p2):
    # ~ if isinstance(p2,point):
    # ~ v=vec(p1,p2)
    # ~ rot=v.angle()
    # ~ return self.transform(p1,rot)
    # ~ else:
    # ~ temp=self-p1
    # ~ rot=p2
    # ~ px=math.cos(rot)*temp.x+math.sin(rot)*temp.y
    # ~ py=-math.sin(rot)*temp.x+math.cos(rot)*temp.y
    # ~ return point(px,py)
    def transform(self, p, rot):
        px = math.cos(rot) * self.x + math.sin(rot) * self.y
        py = -math.sin(rot) * self.x + math.cos(rot) * self.y
        p_t = cartesianPoint(px, py)
        return p_t - p

    def rot(self, a):
        px = math.cos(a) * self.x - math.sin(a) * self.y
        py = math.sin(a) * self.x + math.cos(a) * self.y
        return cartesianPoint(px, py)

    # def angle(self, p):
    #     v = vec(self, p)
    #     return v.angle()



#### ALL IN UNITS OF EARTH RADIUS.
class geo_to_cartesian:
    def __init__(self,p):
        R=6371
        
        self.x = R*np.cos(np.deg2rad(p.lon))*np.cos(np.deg2rad(p.lat))
        self.y = R*np.sin(np.deg2rad(p.lon))*np.cos(np.deg2rad(p.lat))
        self.z = R*np.sin(np.deg2rad(p.lat))
        # print("x= "+str(self.x)+" y= "+str(self.y)+" z= "+str(self.z))
    # def get_cartesian(self):

class cartesian_to_geo:
    def __init__(self,car):
        R=6371
        try:
            if(car.z>R):
                self.lat=0
            else:
                self.lat = np.rad2deg(np.arcsin(car.z/R))
            self.lon = np.rad2deg(np.arctan2(car.y,car.x))
        except:
            self.lat = 0
            self.lon = 0
        
        # print("lat= "+str(self.lat)+" lon= "+str(self.lon))

class cartesian_circ:
    def __init__(self,car,d):
        self.c= car
        self.r = float(d)
        # self.x = car.x
        # self.y = car.y
        # self.z = car.z
        # self.d = d
###################################################################################################
