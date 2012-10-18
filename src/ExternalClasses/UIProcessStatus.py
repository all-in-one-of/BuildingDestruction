'''
Created on Oct 27, 2011

@author: carlos
'''
import logging
class UIProcessStatus(object):
    '''
    classdocs
    '''


    def __init__(self, name, max_distance_to_complete):
        '''
        Constructor
        '''
        self.name = name
        self.max_distance_to_complete = max_distance_to_complete
        self.status_number = 0
        
    def print_status(self, status=None):
        if(not status):
            status = self.status_number
        self.status_number = status
        print "Proces status" + str(status)
        logging.info("Process " + str(self.name) + " status: " + str(status))
        
    def calculate_status(self, distance, inverse=False):
        if(not inverse):
            self.status_number = (distance / self.max_distance_to_complete) * 100
        else:
            self.status_number = (
                                 ((self.max_distance_to_complete - distance)
                                  / self.max_distance_to_complete) * 100)
