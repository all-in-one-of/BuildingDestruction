'''
Created on 12 Apr 2011

@author: carlos
'''
import hou #@UnresolvedImport

class HouInterface(object):
    def __init__(self, geo=None):
        self.geometry = geo
        self.curves = {}
        self.points = {}
        self.transforms = {}
        
    def showPoint(self, point, name='', size=0.05, color=[1, 0, 0]):
        if(not self.geometry):
            obj = hou.node('/obj')
            geo = obj.createNode('geo')
            #erase file node
            geo.children()[0].destroy()
        else:
            geo = self.geometry
        sphere = geo.createNode('sphere')
        sphere.parm('radx').set(size)
        sphere.parm('rady').set(size)
        sphere.parm('radz').set(size)
        
        sphere.parm('tx').set(str(point[0]))
        sphere.parm('ty').set(str(point[1]))
        sphere.parm('tz').set(str(point[2]))
        if(name):
            colorNode = geo.createNode('color', name)
            name = colorNode.name()
        else:
            colorNode = geo.createNode('color')
            name = colorNode.name()
        colorNode.parm('colorr').set(str(color[0]))
        colorNode.parm('colorg').set(str(color[1]))
        colorNode.parm('colorb').set(str(color[2]))
        colorNode.setNextInput(sphere)
        colorNode.setTemplateFlag(True)
        colorNode.setDisplayFlag(True)
        sphere.moveToGoodPosition()
        colorNode.moveToGoodPosition()
        geo.moveToGoodPosition()
        self.points[name] = [sphere, colorNode]
        
    def deletePoints(self):
        "POINTS!!!!!!!!!!"
        print self.points
        for point in self.points.values():
            for node in point:
                node.destroy()
        self.points.clear()
        
    def showCurve(self, points, name='', close=False):
        if(not points):
            return
        if(not self.geometry):
            obj = hou.node('obj')
            if(name != ''):
                geo = obj.createNode('geo', name)
            else:
                geo = obj.createNode('geo')
            #erase file node
            geo.children()[0].destroy()
        else:
            geo = self.geometry
            
        pointsString = ""
        if(name != ''):
            curveNode = geo.createNode('curve', name, True)
            name = curveNode.name()
        else:
            curveNode = geo.createNode('curve')
            name = curveNode.name()
        for point in points:
            pointsString = pointsString + str(point[0]) + "," + str(point[1]) + "," + str(point[2]) + " "
        curveNode.parm('coords').set(pointsString)
        if(close):
            curveNode.parm('close').set(True)
        curveNode.setTemplateFlag(True)
        curveNode.moveToGoodPosition()
        geo.moveToGoodPosition()
        self.curves[name] = [curveNode]
        
    def deleteCurves(self):
        "Cruves!!!!!!!!!!"
        print self.curves
        for curve in self.curves.values():
            for node in curve:
                node.destroy()
        self.curves.clear()
        
    def deleteCurve(self, tag):
        if(self.curves.has_key(tag)):
            for node in self.curves[tag]:
                node.destroy()
            del self.curves[tag]
            
    def transform(self, volume, translate=[0, 0, 0], scale=[0, 0, 0], rotate=[0, 0, 0]):
        node = volume.parent().createNode('xtrans')
        node.parm('tx').set(translate[0])
        node.parm('ty').set(translate[1])
        node.parm('tz').set(translate[2])
        
        node.parm('sx').set(scale[0])
        node.parm('sy').set(scale[1])
        node.parm('sz').set(scale[2])
        
        node.parm('rx').set(rotate[0])
        node.parm('ry').set(rotate[1])
        node.parm('rz').set(rotate[2])
        
        return node
        
        
