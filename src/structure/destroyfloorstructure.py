# -*- coding: utf-8 -*-
from destruction import crackbuilder_beziersmooth
from destruction import crack
from lib import GeoMath
from lib import HouInterface
import floordestroyed
import logging
from destruction import InfoPathPrim

FLOOR_SIZE = 1

def destroy_floor(floor, building_crack, building_crack_path_ordered):

    # Get the intersections of the floor with the building crack to create the
    # start point and the final point of the floor crack
    intersections = floor.intersections_with_crack(building_crack.patternCrack,
                                                   building_crack_path_ordered)
    logging.debug("intersections " + str(intersections))
    # FIXME: Assume we have only two intersections, namely, the crack passes twice
    # across the floor in 'y'
    if(len(intersections) > 1):
        start_point = intersections[0]
        final_point = intersections[1]

        gridName = create_grid(floor)
        infoPath = find_path(gridName, start_point, final_point)

        crack_ = crack.CrackFloor(start_point, final_point, infoPath)
        final_floor = floordestroyed.FloorDestroyed(floor.get_floor_params(),
                                                    floor.get_absolute_points,
                                                    [start_point, final_point],
                                                    crack)
        destroyed = True
    else:
        # Floor not destroyed
        destroyed = False
        final_floor = floor

    return final_floor, destroyed


def destroy_floors(floors_structure):
    destroyed_floors = {}
    floors = floors_structure.get_floors()
    building_crack = floors_structure.get_crack()
    building_crack_path_ordered = floors_structure.get_path()
    for floor in floors:
        floor_computed, destroyed = destroy_floor(floor, building_crack,
                                                  building_crack_path_ordered)
        if(destroyed):
            # Only push destroyed floors
            destroyed_floors[floor] = floor_computed

    return destroyed_floors

def create_grid(floor):
    global FLOOR_SIZE
    reload(HouInterface)
    hou = HouInterface.HouInterface()

    points = floor.get_absolute_points()
    center = GeoMath.centerOfPoints(points)

    vec1 = GeoMath.vecSub(points[0], points[1])
    vec2 = GeoMath.vecSub(points[2], points[1])

    if (vec1[0] != 0):
        vecx = GeoMath.vecModul(vec1)
        vecz = GeoMath.vecModul(vec2)
    else:
        vecx = GeoMath.vecModul(vec2)
        vecz = GeoMath.vecModul(vec1)

    gridName = hou.showGrid('floor', center, vecx, vecz, FLOOR_SIZE, FLOOR_SIZE)

    return gridName


def find_path(gridName, startPoint, finalPoint):
    path = []
    infoPath = InfoPathPrim.convertListFromInfoPrimToPrim(path)