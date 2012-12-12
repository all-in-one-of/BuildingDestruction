# -*- coding: utf-8 -*-
from destruction import crackbuilder_beziersmooth
from destruction import crack
import floordestroyed
CRACK_BUILDER_TYPES = {'Bezier smooth': crackbuilder_beziersmooth.CrackBuilderBezierSmooth()}

def destroy_floor(floor, building_crack, building_crack_path_ordered, crack_type):
    global CRACK_BUILDER_TYPES
    assert(crack_type in CRACK_BUILDER_TYPES), (
     "Crack type {} not valid for floor destruction".format(str(crack_type)))
    builder = CRACK_BUILDER_TYPES[crack_type]
    # Get the intersections of the floor with the building crack to create the
    # start point and the final point of the floor crack
    intersections = floor.intersections_with_crack(building_crack, building_crack_path_ordered)
    # Assume we have only two intersections, namely, the crack passes twice
    # across the floor in 'y'
    if(intersections):
        start_point = intersections[0]
        final_point = intersections[1]
        crack = crack.Crack(start_point, final_point, builder)
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

def destroy_floors(floors_structure, crack_type):
    destroyed_floors = {}
    for floor in floors:
        floor_computed, destroyed = destroyfloor.destroy_floor(floor, building_crack,
                                                         building_crack_path_ordered,
                                                         crack_type)
        if(destroyed):
            # Only push destroyed floors
            destroyed_floors[floor] = floor_computed

    return destroyed_floors
