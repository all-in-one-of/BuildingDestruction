from MainFunctions import DefDestroy
from MainFunctions import InitDestroyedBuilding
import logging
import os
class destructionSession(object):
    
    PROJECT_DIR = os.path.dirname(__file__)
    PARENT_DIR = os.path.dirname(PROJECT_DIR)
    filename_dir = os.path.join(PARENT_DIR, 'destruction.log')
    #L: %(levelname)-2s 
    logging.basicConfig(filename=filename_dir, format='T: %(asctime)-4s M:%(message)s ', datefmt='%d %M:%S', filemode='w', level=logging.DEBUG)

    buildingInitializedClass = None
    destroyClass = None
    
    def build_new_logging_file(self):
        filename = self.filename
        file_log = open(filename)
        file_log.truncate()
        file_log.close()
        logging.basicConfig(filename=filename, format='L: %(levelname)-2s T: %(asctime)-4s M:%(message)s ', datefmt='%d/%m/%y %H:%M:%S', filemode='w', level=logging.DEBUG)

    def initBuilding(self, geo):
        self.__class__.buildingInitializedClass = InitDestroyedBuilding.InitDestroyedBuilding()
        self.__class__.buildingInitializedClass.twoSpeheresDestruction(geo)
        
    def searchPath(self):
        self.__class__.destroyClass = DefDestroy.DefDestroy()
        self.__class__.destroyClass.initPattern(self.__class__.buildingInitializedClass)
        
    def doCrack(self):
        self.__class__.destroyClass.patternControl.doCrack()
    
    def doBoleanIntersection(self):
        self.__class__.destroyClass.patternControl.doBooleanIntersection(self.__class__.buildingInitializedClass)
        
    def showCrack(self):
        self.__class__.destroyClass.patternControl.showCrack()
           
    def dontShowCrack(self):
        self.__class__.destroyClass.patternControl.deleteShowCrackNodes()
            
    def showTextures(self):
        self.__class__.destroyClass.patternControl.showTextures()   
        
    def dontShowTextures(self):
        self.__class__.destroyClass.patternControl.deleteShowTextureNodes()
        
    def showIntersectionTexture(self):
        self.__class__.destroyClass.patternControl.showIntersectionTexture()   
        
    def dontShowIntersectionTexture(self):
        self.__class__.destroyClass.patternControl.deleteShowIntersectionTexture()

    def resetBooleanIntersection(self):
        self.__class__.destroyClass.patternControl.deleteBooleanIntersectionNodes()
        self.doBoleanIntersection()
        
    def resetCrack(self):
        self.__class__.destroyClass.patternControl.doCrack()
           
    def resetPath(self):
        self.__class__.destroyClass.deleteNodes()
        self.searchPath()
        
    def goToTheStart(self):
        self.__class__.destroyClass.patternControl.deleteBooleanIntersectionNodes()
        self.dontShowCrack()
        self.dontShowIntersectionTexture()
        self.dontShowTextures()
        self.__class__.destroyClass.deleteNodes()
        
    def add_noise_to_crack(self, heigth, frequency, for_edge, wavelength):
        self.dontShowCrack()
        self.__class__.destroyClass.patternControl.add_noise_to_crack(heigth, frequency, for_edge, wavelength)
    
    def createStructure(self):
        logging.debug("createStructure!!")
        self.__class__.destroyClass.createStructure(self.__class__.buildingInitializedClass)
