# -*- coding: utf-8 -*-
import buildingstructure
import destroyfloorstructure


class BuildingDestroyedStructure():
    '''
    This class is a wrapper of buildingstructure.BuildingStructure to add more
    functionality and some custom functions to destroy the structure.

    Ideally this class has to be a subclass of a general building structure
    class, but given that building structure class is already created at the
    moment of the creation of this class and we need this class to create all
    the extra structure we make a wrapper and modify only the part we need to
    destroy the structure of the original building.
    We don't need the creating part, only the structure created. So a wrapper
    now is the best solution.
    '''
    def __init__(self, full_building_structure):
        self.full_building_structure = full_building_structure
        self.floors_structure = None
        self.metallic_structure = None

    def destroy_floors(self, crack_type='Bezier smooth'):
        '''
        We only save the destroyed floors, not the full ones.
        when we display_on the floors we will
        '''
        full_floors_structure = (
                        self.full_building_structure.get_floor_structure())
        destroyed_floors = destroyfloorstructure.destroy_floors(
                                                        full_floors_structure,
                                                        crack_type)
        self.floors = destroyed_floors

    def display_on(self):
        '''
        We have to show the full floors when no floor destroyed is found
        '''
        # Display floors
        for floor in self.floors_structure.get_floors():
            if(floor not in self.floors):
                # Floor not destroyed
                floor.display_on()
            else:
                # Floor destroyed
                self.floors[floor].display_on()

    def display_off(self):
        '''
        We have to delete the floors from normal structure and for the
        destroyed one
        '''
        # Getting off the floors
        for floor in self.floors_structure.get_floors():
            if(floor not in self.floors):
                # Floor not destroyed
                floor.display_off()
            else:
                # Floor destroyed
                self.floors[floor].display_off()
