##Trajectory generalization=group
##input=vector
##max_radius=number 0.01000 
##grouped_points=output vector
##group_centroids=output vector

import processing 
from processing.tools.vector import VectorWriter
from qgis.core import *
from PyQt4.QtCore import *

import math
from PyQt4.QtCore import QVariant 

class Group():
    def __init__(self,pt):
        self.points = [pt]
        self.centroid = pt 
    
    def add_point(self,pt):
        self.points.append(pt)
        
    def delete_points(self):
        self.points = []
    
    def recompute_centroid(self):
        x = [pt.x() for pt in self.points]
        y = [pt.y() for pt in self.points]
        self.centroid = QgsPoint( sum(x)/len(x) , sum(y)/len(y) )
    
class Grid():
    def __init__(self,bbox, cell_size):
        w = bbox.width()
        h = bbox.height()
        self.x_min = bbox.xMinimum()
        self.y_min = bbox.yMinimum()
        self.cell_size = cell_size
        self.cells = []
        self.n_rows = int(math.ceil(h/self.cell_size))
        self.n_cols = int(math.ceil(w/self.cell_size))
        self.d = QgsDistanceArea()
        for i in range(0,self.n_cols):
            self.cells.append([])
            for j in range(0,self.n_rows):
                x = self.x_min + (i+0.5)*self.cell_size 
                y = self.y_min + (j+0.5)*self.cell_size 
                self.cells[i].append(None)#QgsPoint(x,y))
        self.resulting_groups = []
    
    def insert_points(self,points):
        for pt in points:
            c = self.get_closest_centroid(pt,self.cell_size)
            if not c:
                #print("New group")
                g = Group(pt) 
                self.resulting_groups.append(g)
                (i,j) = self.get_grid_position(g.centroid)
                self.cells[i][j] = g
            else:
                #print("Existing group")
                (i,j) = c
                #c = self.cells[i][j]
                #g = self.get_group(c)
                g = self.cells[i][j]
                if g:
                    g.add_point(pt)
                    g.recompute_centroid()
                else:
                    print("Error: no group in cell {0},{1}".format(i,j))
                    print(pt)
            #(i,j) = self.get_grid_position(g.centroid)
            #self.cells[i][j] = g#.centroid
            
    def get_group(self,centroid):
        """ returns the group with the provided centroid """
        for g in self.resulting_groups:
            if g.centroid.compare(centroid):
                return g 
            
    def get_closest_centroid(self,pt,max_dist=100000000):
        (i,j) = self.get_grid_position(pt)
        shortest_dist = self.cell_size * 100
        nearest_centroid = None
        for k in range(max(i-1,0),min(i+2,self.n_cols)):
            for m in range(max(j-1,0),min(j+2,self.n_rows)):
                if not self.cells[k][m]: # no centroid in this cell yet
                    continue 
                dist = self.d.measureLine(pt,self.cells[k][m].centroid)
                if dist <= max_dist and dist < shortest_dist:
                    nearest_centroid = (k,m)
                    shortest_dist = dist
        return nearest_centroid
        
    def get_grid_position(self,pt):
        i = int(math.floor((pt.x() - self.x_min) / self.cell_size))
        j = int(math.floor((pt.y() - self.y_min) / self.cell_size))
        return (i,j)
        
    def redistribute_points(self,points):
        for g in self.resulting_groups:
            g.delete_points()
        for pt in points:
            (i,j) = self.get_closest_centroid(pt,self.cell_size * 20)
            if i != None and j != None:
                g = self.cells[i][j]
                g.add_point(pt)
            else:
                print("Discarding {}".format(pt))

l = processing.getObject(input)

#l = iface.activeLayer()
geoms = [QgsGeometry(f.geometry()) for f in l.getFeatures()] # copying geometries is necessary to avoid segfaults!
if geoms[0].asMultiPoint() == []: # if geoms are Points, asMultiPoint() returns empty lists
    points = [f.geometry().asPoint() for f in l.getFeatures()]
else:
    points = []
    for g in geoms:
        for pt in g.asMultiPoint():
            points.append(pt)

bbox = l.extent()
grid = Grid(bbox,max_radius)
print("Inserting {} points ...".format(len(points)))
grid.insert_points(points)
print("Redistributing {} points ...".format(len(points)))
grid.redistribute_points(points)

fields = [QgsField('GROUP', QVariant.Int)]
geom_type = 1 # point 
writer_pts = VectorWriter(grouped_points, None, fields, geom_type, l.crs() )
writer_centroids = VectorWriter(group_centroids, None, fields, geom_type, l.crs() )

print("Writing {} groups ...".format(len(grid.resulting_groups)))

for id,g in enumerate(grid.resulting_groups):
    fet2 = QgsFeature()
    fet2.setGeometry(QgsGeometry.fromPoint(g.centroid))
    fet2.setAttributes([id])
    writer_centroids.addFeature(fet2)
    for pt in g.points:
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromPoint(pt))
        fet.setAttributes([id])
        writer_pts.addFeature(fet)
    
    
    
del writer_pts
del writer_centroids


