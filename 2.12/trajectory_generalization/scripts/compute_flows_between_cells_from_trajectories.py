##Trajectory generalization=group
##input_trajectories=vector
##weight_field=field input_trajectories
##use_weight_field=boolean
##input_cell_centers=vector
##flow_lines=output vector
##cell_counts=output vector 

import processing 
from processing.tools.vector import VectorWriter
from qgis.core import *
from PyQt4.QtCore import *
from datetime import datetime, timedelta 

import processing 

class SequenceGenerator():
    def __init__(self,centroid_layer,trajectory_layer,weight_field=None):
        centroids = [f for f in centroid_layer.getFeatures()]
        self.cell_index = QgsSpatialIndex()
        for f in centroids:
            self.cell_index.insertFeature(f)
        self.id_to_centroid = {f.id(): [f,[0,0,0,0,0]] for (f) in centroids}
        self.weight_field = weight_field
        if weight_field is not None:
            self.weightIdx = trajectory_layer.fieldNameIndex(weight_field)
        else:
            self.weightIdx = None
        self.sequences = {}
        
        nTraj = float(trajectory_layer.featureCount())
        for i,traj in enumerate(trajectory_layer.getFeatures()):
            self.evaluate_trajectory(traj)
            progress.setPercentage(i/nTraj*100)
            
    def evaluate_trajectory(self,trajectory):
        points = trajectory.geometry().asPolyline()
        this_sequence = []
        for i, pt in enumerate(points):
            id = self.cell_index.nearestNeighbor(pt,1)[0]
            nearest_cell = self.id_to_centroid[id][0]
            nearest_cell_id = nearest_cell.id()
            prev_cell_id = None
            if len(this_sequence) > 1:
                prev_cell_id = this_sequence[-1]
                if self.weight_field is not None:
                    weight = trajectory.attributes()[self.weightIdx]
                else:
                    weight = 1
                if self.sequences.has_key((prev_cell_id,nearest_cell_id)):
                    self.sequences[(prev_cell_id,nearest_cell_id)] += weight
                else:
                    self.sequences[(prev_cell_id,nearest_cell_id)] = weight
            if nearest_cell_id != prev_cell_id: 
                # we have changed to a new cell --> up the counter 
                m = trajectory.geometry().geometry().pointN(i).m()
                t = datetime(1970,1,1) + timedelta(seconds=m) + timedelta(hours=8) # Beijing GMT+8
                h = t.hour 
                self.id_to_centroid[id][1][0] = self.id_to_centroid[id][1][0] + 1
                self.id_to_centroid[id][1][h/6+1] = self.id_to_centroid[id][1][h/6+1] + 1
                this_sequence.append(nearest_cell_id)
    
    def create_flow_lines(self):
        lines = []
        for key,value in self.sequences.iteritems(): 
            p1 = self.id_to_centroid[key[0]][0].geometry().asPoint()
            p2 = self.id_to_centroid[key[1]][0].geometry().asPoint()
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPolyline([p1,p2]))
            feat.setAttributes([key[0],key[1],value])
            lines.append(feat)
        return lines

centroid_layer = processing.getObject(input_cell_centers)
trajectory_layer = processing.getObject(input_trajectories)
sg = SequenceGenerator(centroid_layer,trajectory_layer, weight_field if use_weight_field else None)

fields = [QgsField('FROM', QVariant.Int),
              QgsField('TO', QVariant.Int),
              QgsField('COUNT', QVariant.Int)]
geom_type = 2
writer = VectorWriter(flow_lines, None, fields, geom_type, centroid_layer.crs() )
for f in sg.create_flow_lines():
    writer.addFeature(f)
del writer 

fields = centroid_layer.fields()
fields.append( QgsField('COUNT',QVariant.Int))
fields.append( QgsField('COUNT_Q1',QVariant.Int))
fields.append( QgsField('COUNT_Q2',QVariant.Int))
fields.append( QgsField('COUNT_Q3',QVariant.Int))
fields.append( QgsField('COUNT_Q4',QVariant.Int))
writer = VectorWriter(cell_counts, None, fields, 1, centroid_layer.crs() )
for key, value in sg.id_to_centroid.iteritems():
    (in_feature, n) = value
    out_feature = QgsFeature()
    out_feature.setGeometry(in_feature.geometry())
    attributes = in_feature.attributes()
    attributes.append(n[0])
    attributes.append(n[1])
    attributes.append(n[2])
    attributes.append(n[3])
    attributes.append(n[4])
    out_feature.setAttributes(attributes)
    writer.addFeature(out_feature)
del writer 


