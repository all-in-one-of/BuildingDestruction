# -*- coding: utf-8 -*-
import hou  # @UnresolvedImport

from destruction import crack
from lib import GeoMath
from lib import HouInterface
import floordestroyed
import logging
import floor
from destruction import InfoPathPrim

TILE_SIZE = 0.50
# FIXME: we assume floors reside in the xz plane

class DestroyFloorStructure(object):

    def __init__(self, floors_structure):
        self.floors_structure = floors_structure
        self.hout = HouInterface.HouInterface()
        geo, isCreated = self.hout.initGeo()
        self.hout.geometry = geo
        self.destroyed_floors = {}
        
    def do(self):
        self.destroyed_floors = self.destroy_floors(self.floors_structure)
        
    def destroy_floor(self, floor_, building_crack, building_crack_path_ordered):
        reload(HouInterface)
        reload(floor)
        # Get the intersections of the floor with the building crack to create the
        # start point and the final point of the floor crack
        intersections = floor_.intersections_with_crack(
            building_crack.patternCrack,
            building_crack_path_ordered)
        logging.debug("intersections " + str(intersections))
        if(len(intersections) > 0):
            gridName = self.create_grid(floor_)
            for inter in intersections:
                start_point = inter[0]
                final_point = inter[1]

                self.hout.showPoint(start_point)
                self.hout.showPoint(final_point)
                infoPath = self.find_path(gridName, start_point, final_point)

                crack_ = crack.CrackFloor(infoPath)
            final_floor = floordestroyed.FloorDestroyed(floor_.get_floor_params(),
                                                        floor_.get_absolute_points,
                                                        [start_point, final_point],
                                                        crack)
            destroyed = True
        else:
            # Floor not destroyed
            destroyed = False
            final_floor = floor_

        return final_floor, destroyed


    def destroy_floors(self, floors_structure):
        destroyed_floors = {}
        floors = floors_structure.get_floors()
        building_crack = floors_structure.get_crack()
        building_crack_path_ordered = floors_structure.get_path()
        count = 0
        for floor_ in floors:
            logging.debug("Floor number " + str(count))
            count = count + 1
            floor_computed, destroyed = self.destroy_floor(
                floor_, building_crack, building_crack_path_ordered)
            if(destroyed):
                # Only push destroyed floors
                destroyed_floors[floor_] = floor_computed

        return destroyed_floors


    def create_grid(self, floor_):
        global FLOOR_SIZE
        reload(HouInterface)

        points = floor_.get_absolute_points()
        center = GeoMath.centerOfPoints(points)

        vec1 = GeoMath.vecSub(points[0], points[1])
        vec2 = GeoMath.vecSub(points[2], points[1])

        if (vec1[0] != 0):
            vecx = GeoMath.vecModul(vec1)
            vecz = GeoMath.vecModul(vec2)
        else:
            vecx = GeoMath.vecModul(vec2)
            vecz = GeoMath.vecModul(vec1)
        columns = vecx / TILE_SIZE
        rows = vecz / TILE_SIZE
        gridName = self.hout.showGrid('floor', center, vecx, vecz, rows, columns)

        return gridName

    def findExtremePrims(self, startPoint, finalPoint, prims):
        startPrim = finalPrim = None
        for prim in prims:
                edge = GeoMath.getEdgeWithPointInPrim(prim, startPoint)
                if(edge):
                    startPrim = prim
                    logging.debug("prims start floor " + str(startPrim.number()))
                    break

        for prim in prims:
            edge = GeoMath.getEdgeWithPointInPrim(prim, finalPoint)
            if(edge):
                finalPrim = prim
                logging.debug("prims final floor " + str(finalPrim.number()))
                break
                    
        return startPrim, finalPrim
                
    def find_path(self, gridName, startPoint, finalPoint):
        reload(GeoMath)
        path = []
        grid = self.hout.grids[gridName][0]
        logging.debug('grid name ' + str(grid))
        prims = grid.geometry().prims()
        startPrim, finalPrim = self.findExtremePrims(startPoint, finalPoint, prims)
        if (startPrim == None or finalPrim == None):
            logging.debug("Start and final prims can't be ensured since the intersections_with_crack with the crack are a little misplaced, and that cause pointInEdge to fail when trying to know which primitive is the start and the final")
        # Unique prim
        if (finalPrim.number() == startPrim.number()):
            uniquePrim = InfoPathPrim.InfoPathPrim(startPrim)
            uniquePrim.setiPoint(startPoint)
            uniquePrim.setfPoint(finalPoint)
            return [uniquePrim]
            
        logging.debug("prims with floor " + str(
            [startPrim.number(), finalPrim.number()]))
        navigationLine = GeoMath.vecSub(finalPoint, startPoint)

        mappedStartPoint = [startPoint[0], startPoint[2], 0]
        mappedFinalPoint = [finalPoint[0], finalPoint[2], 0]

        primsInPath = []
        for prim in prims:
            if (prim.number() == startPrim.number() or prim.number() == finalPrim.number()):
                continue
            edges = GeoMath.getEdgesFromPrim(prim)
            mappedEdges = [[[edge[0][0], edge[0][2], 0], [edge[1][0], edge[1][2], 0]]
                           for edge in edges]
            logging.debug("prim number " + str(prim.number()))
            inters = GeoMath.getIntersectionsBetweenEdges2D(
                mappedEdges, [[mappedStartPoint, mappedFinalPoint]])

            if (inters):
                logging.debug("Inter in path " + str(inters))
                # Demap again to original 'y' component, which both start point or
                # final point have
                demappedInters = [[inter[0], startPoint[1], inter[1]]
                                for inter in inters]
                distPoint0 = GeoMath.vecModul(
                    GeoMath.vecSub(demappedInters[0], startPoint))
                distPoint1 = GeoMath.vecModul(
                    GeoMath.vecSub(demappedInters[1], startPoint))
                if (distPoint0 < distPoint1):
                    startPrimPoint = demappedInters[0]
                    finalPrimPoint = demappedInters[1]
                else:
                    startPrimPoint = demappedInters[1]
                    finalPrimPoint = demappedInters[0]
                infoPrim = InfoPathPrim.InfoPathPrim(prim)
                infoPrim.setiPoint(startPrimPoint)
                infoPrim.setfPoint(finalPrimPoint)
                primsInPath.append(infoPrim)
                logging.debug("Prim intersects " + str(prim.number()) + " " + str(startPrimPoint) + " " + str(finalPrimPoint)) 

        sorted(primsInPath, key=lambda infoPrim:
               GeoMath.vecModul(GeoMath.vecSub(infoPrim.iPoint, startPoint)))
        logging.debug("Testing??")
        if (not primsInPath):
            logging.debug("No intersections " + str(primsInPath))
            return
            
        startInfoPrim = InfoPathPrim.InfoPathPrim(startPrim)
        finalInfoPrim = InfoPathPrim. InfoPathPrim(finalPrim)
        
        startInfoPrim.setiPoint(startPoint)
        startInfoPrim.setfPoint(primsInPath[0].iPoint)
        finalInfoPrim.setiPoint(primsInPath[len(primsInPath) - 1].fPoint)
        finalInfoPrim.setfPoint(finalPoint)
        
        primsInPath.append(finalInfoPrim)
        primsInPath.insert(0, startInfoPrim)
        
        logging.debug([prim.prim.number() for prim in primsInPath])
        
        #DEBUG:
        logging.debug("Before showing path")
        self.showPath(gridName, InfoPathPrim.convertListFromInfoPrimToPrim(primsInPath))
        
        return primsInPath

    def showPath(self, gridName, orderedPrims):
        groupPath = self.hout.geometry.createNode('group', 'groupPath')
        groupPath.parm('crname').set("path")
        string = ""
        for prim in orderedPrims:
            string = string + str(prim.number()) + " "
        groupPath.parm('pattern').set(string)
        node = self.hout.grids[gridName][0]
        logging.debug("Showing path " + str(groupPath))
        groupPath.setNextInput(node)
        groupPath.moveToGoodPosition()
