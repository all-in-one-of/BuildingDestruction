import productTree
import parseparameters

DEFAULT_LABELS =  {
    'floors': '',
    'floor': '',
    'windows': '',
    'window': '',
    'doors': '',
    'door': ''    
}

class BuildingParts(object):
    '''
    Give context to the building, identifying its parts, like floors, windows, etc.
    '''
    def __init__(self, top_node, label_dictionary = DEFAULT_LABELS):
        '''
        @param top_node the top node of the building. We are using the product 
        tree library to navigate over the tree, so we don't depend on a specific
        tool that creates the nodes.
        
        @param label_dictionary cotains the labels to identify the parts of the
        building. For example, you can call the floors "plants", so you have to
        make a dictionary like {floors: "plants"}
        The dictionary has to be like:
        floors: label
        floor: label
        windows: label
        window: label
        doors: label
        door: label
        '''
        self.__top_node = top_node
        self.__original_label_dicionary = label_dictionary
        self.__label_dictionary = parseparameters.parse_parameters(label_dictionary, DEFAULT_LABELS)
        '''
        building_parts will be a structure contaning all parts of the building.
        It is a dictionary with the given structure:
        {
            'Base_*':{
                        'Roof_*': [roof_parent_node, group_name]
                        'Side_*': [side_node, group_name]
                        'Tier_*': [name, level]
                        'Floor_*': [floor_node, [tier_associated_*, *], [side_associated_*, *]]
                        'Window_*': [window_parent_node, window_name, [tier_associated_*, *], [side_associated_*, *]]
                        'Door_*': [door_parent_node, door_name, [tier_associated_*, *], [side_associated_*, *]]
                    }
        }
        '''
        self.__building_parts = {}
        
    def identify_parts(self):
        '''
        @return building_parts it is the main dictionary of parts. It is
        something like:
        {
        floors: 
        '''

    
    def _ensure_existing_parts(self):
        
        #Manage errors maybe due to user interaction in the GUI while the program run
        assert (not len(self.__original_label_dicionary.keys()) > 
               len(self.__label_dictionary.keys())), (
               "Some part of the building were not recognizable")
        
    
    def _identify_floors(self):
        pass
    
    def _identify_floor(self):
        pass
    
    def _identify_windows(self):
        pass
    
    def _identify_window(self):
        pass
    
    def _identify_doors(self):
        pass
    
    def _identify_door(self):
        pass
        
