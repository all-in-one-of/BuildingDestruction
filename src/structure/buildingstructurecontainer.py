# -*- coding: utf-8 -*-

import buildingstructure
import buildingdestroyedstructure


class BuildingStructureContainer(object):

    def __init__(self):
        self.structures = {}
        self.current_displaying = None

    def add_default_structures(self, crack, path, inserts, geo,
                               user_restriction_parms):
        full_building_extra_structure = buildingstructure.BuildingStructure(
                                                crack, path, inserts,
                                                geo, user_restriction_parms)
        self.add_structure('Full building', full_building_extra_structure)

    def add_destroyed_structure(self):
        assert('Full building' in self.structures), (
                                        "No full building structure created")
        destroyed_building_extra_structure = (
                buildingdestroyedstructure.BuildingDestroyedStructure(
                                            self.structures['Full building']))
        destroyed_building_extra_structure.destroy_floors()
        self.add_structure('Destroyed building',
                            destroyed_building_extra_structure)

    def add_structure(self, structure_alias, structure):
        self.structures[structure_alias] = structure

    def display_structure(self, structure_alias):
        assert(structure_alias in self.structures), (
                        "Structure alias {} not valid".format(structure_alias))
        if(self.current_displaying):
            self.structures[self.current_displaying].display_off()
        self.current_displaying = None
        ok_displaying = self.structures[structure_alias].display_on()
        if(ok_displaying):
            self.current_displaying = structure_alias

        return ok_displaying
