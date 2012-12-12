# -*- coding: utf-8 -*-
'''
Created on Jul 22, 2011

@author: carlos
'''
from lib import GeoMath
import logging
DEBUG = False

class TextureForPrim(object):
    '''
    classdocs
    '''

    def __init__(self, textures, prim, defaultTexture=None):
        '''
        Constructor
        '''
        self.prim = prim
        self.textures = list(textures)
        self.defaultTexture = defaultTexture
        self.orderedListOfTextures = None
        self.reverseListOfTextures = None

    def findIntersectionWithNearestTexture(self, points):
        global DEBUG
        nearestPointIntersect = []
        tex = None
        if(DEBUG):
            debugPoints = []
        # Initialize with a random texture
        minDistance = 999999
        for texture in self.textures:
            distance, pointIntersect, allIntersections = texture.checkIntersectionWithTexture(points, self.prim)
            # DEBUG ONLY
            if (DEBUG and pointIntersect):
                debugPoints.extend(allIntersections)

            if(((not nearestPointIntersect) or (distance < minDistance)) and pointIntersect):
                minDistance = distance
                nearestPointIntersect = pointIntersect
                tex = texture

        return tex, nearestPointIntersect, minDistance

    # This method return the upper texture containing a point. Be careful! to correct use of methos
    # the point MUST NOT LIE in a edge of some texture
    def findUpperTextureContainingPoint(self, point):

        if(not self.reverseListOfTextures):
            # Get ordered layers
            layers = list(self.getLayers())
            # We want to start from the upper texture, so we inverse the list
            layers.reverse()
            self.reverseListOfTextures = layers

        layerInPoint = None
        for layer in self.reverseListOfTextures:
            if(layer.pointInTexture(point)):
                if(GeoMath.pointInEdges(point, GeoMath.getEdgesFromPoints(layer.get_absolute_points()))):
                    # Warning!!! point are in the edge of a texture, so if you call this method to know
                    # the next texture be careful, it will be error
                    logging.warning('Method findUpperTextureContainingPoint, Point lie in a edge of texture')
                layerInPoint = layer
                break
        if(not layerInPoint):
            layerInPoint = self.getDefaultTexture()
        return layerInPoint

    def getLayers(self):
        if(not self.orderedListOfTextures):
            # Insertion algorithm to do a layered order of textures O(n²)
            self.orderedListOfTextures = []
            for texture in self.textures:
                texOutside = False
                n = 0
                while(not texOutside and n < len(self.orderedListOfTextures)):
                    if(not GeoMath.polygonInPolygon(texture.get_absolute_points(), self.orderedListOfTextures[n].get_absolute_points())):
                        texOutside = True
                    else:
                        n += 1
                self.orderedListOfTextures.insert(n, texture)
        # Insert default texture as the upper texture
            self.orderedListOfTextures.insert(0, self.getDefaultTexture())
        return self.orderedListOfTextures

    def get_upper_texture(self, texture):
        layers = self.getLayers()
        if(texture in layers):
            index = layers.index(texture)
        if(index == len(layers) - 1):
            layer = None
        else:
            layer = layers[index + 1]
        return layer

    def get_lower_texture(self, texture):
        layers = self.getLayers()
        if(texture in layers):
            index = layers.index(texture)
        if(index == 0):
            layer = None
        else:
            layer = layers[index - 1]
        return layer

    def getDefaultTexture(self):
        return self.defaultTexture

    def getFirstLayer(self, pointIni):
        first = self.getLayers()[0]
        texEdges = []
        texPoints = first.get_absolute_points()
        for n in range(len(texPoints) - 1):
            texEdges.append([texPoints[n], texPoints[n + 1]])
        if(GeoMath.pointInEdges(pointIni, texEdges)):
            firstLayer = first
        else:
            firstLayer = self.defaultTexture
        return firstLayer


