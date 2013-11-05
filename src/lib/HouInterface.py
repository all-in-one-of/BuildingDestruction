'''
Created on 12 Apr 2011

@author: carlos
'''
import hou #@UnresolvedImport
import logging

class HouInterface(object):
    def __init__(self, geo=None):
        self.geometry = geo
        self.curves = {}
        self.points = {}
        self.transforms = {}
        self.tubes = {}
        self.cubes = {}
        self.grids = {}
        
    def initGeo(self):
        isGeoCreated = True
        if(not self.geometry):
            obj = hou.node('/obj')
            geo = obj.createNode('geo')
            #erase file node
            geo.children()[0].destroy()
            isGeoCreated = True
        else:
            geo = self.geometry
            isGeoCreated = False
        return geo, isGeoCreated
    
    def createNode(self, nodeType, geo, name=''):
        if(name):
            node = geo.createNode(nodeType, name, True)
        else:
            node = geo.createNode(nodeType)
        return node
    
    #Normally, if we created a geo just only for this node, we want to display
    #it always. Else, we want to not take the control about the display flag,
    #and we put the template flag instead.
    def setFlags(self, node, isGeoCreated):
        if(isGeoCreated):
            node.setDisplayFlag(True)
        else:
            node.setTemplateFlag(True)
            
    def showPoint(self, point, name='', size=0.05, color=[1, 0, 0]):
        geo = self.initGeo()
        sphere = self.createNode('sphere', geo, name)
        sphere.parm('radx').set(size)
        sphere.parm('rady').set(size)
        sphere.parm('radz').set(size)

        sphere.parm('tx').set(str(point[0]))
        sphere.parm('ty').set(str(point[1]))
        sphere.parm('tz').set(str(point[2]))
        
        colorNode = self.createNode('color', geo, name)
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
        
        return name

    def deletePoints(self):
        for point in self.points.values():
            for node in point:
                node.destroy()
        self.points.clear()

    def showCurve(self, points, name='', close=False):
        if(not points):
            return
        geo, isGeoCreated = self.initGeo()
        curveNode = self.createNode('curve', geo, name)
        name = curveNode.name()
        
        pointsString = ""
        for point in points:
            pointsString = pointsString + str(point[0]) + "," + str(point[1]) + "," + str(point[2]) + " "
        curveNode.parm('coords').set(pointsString)
        if(close):
            curveNode.parm('close').set(True)
        curveNode.setTemplateFlag(True)
        curveNode.moveToGoodPosition()
        geo.moveToGoodPosition()
        self.curves[name] = [curveNode]
        
        return name

    def deleteCurves(self):
        for curve in self.curves.values():
            for node in curve:
                node.destroy()
        self.curves.clear()

    def deleteCurve(self, tag):
        if(self.curves.has_key(tag)):
            for node in self.curves[tag]:
                node.destroy()
            del self.curves[tag]
    
    def showTube(self, name = '', radius = 1, center = [0,0,0], height = 10, orientation = 'y'):
        geo, isGeoCreated = self.initGeo()
        tubeNode = self.createNode('tube', geo, name)  
        name = tubeNode.name()
        
        tubeNode.parm('tx').set(center[0])
        tubeNode.parm('ty').set(center[1])
        tubeNode.parm('tz').set(center[2])
        
        tubeNode.parm('rad1').set(radius)
        tubeNode.parm('rad2').set(radius)
        
        tubeNode.parm('height').set(height)
        
        tubeNode.parm('orient').set(orientation)
        
        #End caps
        tubeNode.parm('cap').set(True)
        
        self.tubes[name] = [tubeNode]
        tubeNode.moveToGoodPosition()
        geo.moveToGoodPosition()
        self.setFlags(tubeNode, isGeoCreated)
        
        return name
        
    def deleteTube(self, tag):
        if(self.tubes.has_key(tag)):
            for node in self.tubes[tag]:
                node.destroy()
            del self.tubes[tag]
            
    def deleteTubes(self):
        for tube in self.tube.values():
            for node in tube:
                node.destroy()
        self.curves.clear()
        
    def showCube(self, name = '', size = [1,1,1], center = [0,0,0]):
        geo, isGeoCreated = self.initGeo()
        cubeNode = self.createNode('box', geo, name)
        name = cubeNode.name()
        
        cubeNode.parm('tx').set(center[0])
        cubeNode.parm('ty').set(center[1])
        cubeNode.parm('tz').set(center[2])
        
        cubeNode.parm('sizex').set(size[0])
        cubeNode.parm('sizey').set(size[1])
        cubeNode.parm('sizez').set(size[2])
    
        self.setFlags(cubeNode, isGeoCreated)
        self.cubes[name] = [cubeNode]
        
        cubeNode.moveToGoodPosition()
        return name
    
    def deleteCube(self, tag):
        if(self.cubes.has_key(tag)):
            for node in self.cubes[tag]:
                node.destroy()
            del self.cubes[tag]
    
    def deleteCubes(self):
        for cube in self.cubes.values():
            for node in cube:
                node.destroy()
        self.cubes.clear()

    def showGrid(self, name='', center = [0,0,0], sizex = 1, sizey = 1, rows = 1, columns = 1, orient = 'zx'):
        geo, isGeoCreated = self.initGeo()
        gridNode = self.createNode('grid', geo, name)
        name = gridNode.name()

        gridNode.parm('tx').set(center[0])
        gridNode.parm('ty').set(center[1])
        gridNode.parm('tz').set(center[2])

        logging.debug("showgrid x" + str(sizex))
        logging.debug("showgrid y" + str(sizey))
        logging.debug("showgrid c" + str(center))
        logging.debug("showgrid cols" + str(rows))
        logging.debug("showgrid crows" + str(columns))

        gridNode.parm('sizex').set(sizex)
        gridNode.parm('sizey').set(sizey)

        gridNode.parm('orient').set(orient)

        gridNode.parm('rows').set(rows)
        gridNode.parm('cols').set(columns)

        self.setFlags(gridNode, isGeoCreated)
        self.grids[name] = [gridNode]

        gridNode.moveToGoodPosition()
        return name

    def deleteGrid(self, tag):
        if(self.grids.has_key(tag)):
            for node in self.grids[tag]:
                node.destroy()
            del self.grids[tag]
    
    def deleteGrids(self):
        for cube in self.grids.values():
            for node in grid:
                node.destroy()
        self.grids.clear()

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


