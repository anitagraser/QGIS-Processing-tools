##Trajectory generalization=group
##input=vector
##min_angle=number 45.0
##min_stop_duration=number 120.0
##min_distance=number 100.0
##max_distance=number 1000.0
##characteristic_points=output vector

import processing 
from processing.tools.vector import VectorWriter
from qgis.core import *
from PyQt4.QtCore import *

class Analyzer:
    def __init__(self,traj, max_distance, min_distance, min_stop_duration, min_angle = 45):
        self.i = 0
        self.j = 1
        self.k = 2
        self.traj = traj
        self.n = self.traj.numPoints()
        self.max_distance = max_distance
        self.min_distance = min_distance
        self.min_stop_duration = min_stop_duration
        self.min_angle = min_angle
        self.significant_points = [self.traj.startPoint(),self.traj.endPoint()]
        self.d = QgsDistanceArea()
        self.d.setEllipsoid('WGS84')
        self.d.setEllipsoidalMode(True)
        
    def find_significant_points(self):
        
        while self.j < self.n-1:
            
            #print(self.j)
            
            if self.is_representative_max_distance():
                #print("representative max distance at {0}".format(self.j))
                self.significant_points.append(self.traj.pointN(self.j))
                self.i = self.j
                self.j = self.i + 1
                continue
                
            elif self.more_points_further_than_min_distance():
                if self.k > self.j + 1:
                    d_time = self.traj.pointN(self.k-1).m() - self.traj.pointN(self.j).m()
                    if d_time >= self.min_stop_duration:
                        #print("significant stop ({1}) at {0}".format(self.j,d_time))
                        self.significant_points.append(self.traj.pointN(self.j))
                        self.i = self.j
                        self.j = self.k
                        continue 
                    else:
                        # compute the average spatial position to represent the similar points
                        m = self.j + (self.k-1-self.j)/2
                        self.j = m
                
                a_turn = self.compute_angle_between_vectors()
                #print("{0}: {1}".format(self.j,a_turn))
                if a_turn >= self.min_angle and a_turn <= (360-self.min_angle):
                    #print("significant angle ({0}) at {1}".format(a_turn,self.j))
                    self.significant_points.append(self.traj.pointN(self.j))
                    self.i = self.j
                    self.j = self.k
                else:
                    self.j += 1
                        
            else:
                return self.significant_points
        
        return self.significant_points
   
    def compute_angle_between_vectors(self):
        p_i = self.traj.pointN(self.i)
        p_j = self.traj.pointN(self.j)
        p_k = self.traj.pointN(self.k)
        azimuth_ij = QgsPoint(p_i.x(),p_i.y()).azimuth(QgsPoint(p_j.x(),p_j.y()))
        azimuth_jk = QgsPoint(p_j.x(),p_j.y()).azimuth(QgsPoint(p_k.x(),p_k.y()))
        #print("{0} - {1}".format(azimuth_ij,azimuth_jk))
        return abs(azimuth_ij - azimuth_jk) 
    
    def more_points_further_than_min_distance(self):
        for self.k in range(self.j+1,self.n):
            p_j = self.traj.pointN(self.j)
            p_k = self.traj.pointN(self.k)
            d_space_j_k = self.d.measureLine(QgsPoint(p_j.x(),p_j.y()),QgsPoint(p_k.x(),p_k.y()))
            if d_space_j_k >= self.min_distance:
                return True
        return False
        
    def is_representative_max_distance(self):
        p_i = self.traj.pointN(self.i)
        p_j = self.traj.pointN(self.j)
        d_space = self.d.measureLine(QgsPoint(p_i.x(),p_i.y()),QgsPoint(p_j.x(),p_j.y()))
        
        if d_space >= self.max_distance:
            self.significant_points.append(p_i)
            return True
        else:
            return False
        

l = processing.getObject(input)

significant_points = []

for f in l.getFeatures():
    line = f.geometry().geometry()
    n = line.numPoints()
    #print("Line with {0} points".format(n))
    #max_distance = 1000 # meters 
    #min_distance = 100 # meters
    #min_stop_duration = 120 # seconds 
    a = Analyzer(line, max_distance, min_distance, min_stop_duration)
    significant_points = significant_points + a.find_significant_points()

print("Number of significant points: {0}".format(len(significant_points)))

fields = []
geom_type = 1 # point 
writer = VectorWriter(characteristic_points, None, fields, geom_type, l.crs() )

for pt in significant_points:
    feat = QgsFeature()
    feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(pt.x(),pt.y())))
    writer.addFeature(feat)
    
del writer 
