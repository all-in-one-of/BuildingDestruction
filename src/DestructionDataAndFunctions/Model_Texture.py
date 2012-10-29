# -*- coding: utf-8 -*-
'''
Created on Sep 20, 2011

@author: carlos
'''
from ExternalClasses import XMLParser
from ExternalClasses import HouInterface
import Data
import Texture
import TextureForPrim
import logging
class Model_Texture(object):
    '''
    classdocs
    '''


    def __init__(self, nodeWithPrims=None, listOfInserts=None):
        reload (Data)
        reload (Texture)
        reload (TextureForPrim)
        reload (XMLParser)
        self.nodeWithPrims = nodeWithPrims
        logging.debug('INSERTS MODEL' + str(listOfInserts))
        self.listOfInserts = listOfInserts
        self.defaultTexture = None
        self.defaultTextureXML = None
        #FIXME: hardcoded path
        self.pathToDefinitionFile = '/home/carlos/Work/University/Git_laptop/BuildingDestruction/resources/modelTexture.xml'
        #Initialize XML parsers
        self.XMLTextures = XMLParser.XMLParserTextures(self.pathToDefinitionFile)
        self.XMLMaterials = XMLParser.XMLParserMaterials(self.pathToDefinitionFile)
        self.assignedPrimOBJ = {}
        self.assignedPrimTexture = {}
        self.listOfTextures = []
        self.HI = None
        self.materials = []

    def doMaterialsTexture(self):
        #Our single material class is the material there
        for complexMaterial in self.XMLMaterials.getAllComplexMaterials():
            dictCompMaterial = {}
            compMatName = self.XMLMaterials.getComplexMaterialName(complexMaterial)
            for material in self.XMLMaterials.getMaterialsFromComplexMaterial(complexMaterial):
                dictAtomsMaterial = {}
                matName = self.XMLMaterials.getMaterialName(material)
                matWavelentgh = int(self.XMLMaterials.getMaterialWavelenght(material))
                for atomMaterial in self.XMLMaterials.getAtomMaterialsFromMaterial(material):
                    atomMatName = self.XMLMaterials.getAtomMaterialName(atomMaterial) #@UnusedVariable
                    atomMatClass = self.XMLMaterials.getAtomMaterialClass(atomMaterial)
                    atomMatPercent = int(self.XMLMaterials.getAtomMaterialPercent(atomMaterial))
                    #Create single material if the class of material defined in the XML exists
                    if(atomMatClass in Data.__dict__): #@UndefinedVariable
                        singleMatClassObject = Data.__dict__[atomMatClass]() #@UndefinedVariable
                        logging.debug('singleMatClasObject ' + str(singleMatClassObject))
                        dictAtomsMaterial[singleMatClassObject] = atomMatPercent
                    else:
                        logging.error('Method doMaterialsTexture, No class from material found:' + str(atomMatClass))
                    materialObject = Data.SingleMaterial(dictAtomsMaterial, matName)
                dictCompMaterial[matWavelentgh] = materialObject
            self.materials.append(Data.ComplexMaterial(dictCompMaterial, compMatName))

    def doClassTexture(self, texture, prim=None, defaultTex=False):
        if(not self.materials):
            self.doMaterialsTexture()
        logging.debug('OBJ: ' + str(self.XMLTextures.getOBJ(texture)))
        if (prim):
            logging.debug('Material for prim: ' + str(prim.number()) + ' ' + self.XMLTextures.getMaterial(texture))
        complexMat = None
        compMatName = self.XMLTextures.getMaterial(texture)
        for compMat in self.materials:
            if(compMat.get_name() == compMatName):
                complexMat = compMat
        if(complexMat):
            '''
            if(self.materials.has_key(self.XMLTextures.getMaterial(texture))):
                dict = {Data.SetPatternWall(): 50, Data.SetPatternWallBroken():50}
                material = Data.SingleMaterial(dict, "Brick")
                complexMat = Data.ComplexMaterial({0: material}, "Wall")
                delimitedProportions=self.XMLTextures.getPoints(texture)
            if(self.XMLTextures.getMaterial(texture)=='window'):
                dict = {Data.SetPatternGlass(): 100}
                material = Data.SingleMaterial(dict, "Glass")
                complexMat = Data.ComplexMaterial({0: material}, "Window")
            '''
            delimitedProportions = self.XMLTextures.getPoints(texture)
            if(delimitedProportions):
                t = Texture.Texture(complexMat, delimitedProportions=delimitedProportions, isDefault=defaultTex)
            else:
                if(not prim):
                    #All area of prim
                    t = Texture.Texture(complexMat, delimitedProportions=[[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], isDefault=defaultTex)
                else:
                    t = Texture.Texture(complexMat, absolutePointsNotErasable=[list(p.point().position()) for p in prim.vertices()], isDefault=defaultTex)

            if(prim):
                t.mappingToPrimitive(prim)
        else:
            print "ERROR NOT FOUND MATERIAL!"
            logging.error('Method doClassTexture, material defined in XML doesnt exists')
            t = None
        return t


    def getTextureFromOBJ(self, OBJ):
        texture = None
        if(OBJ):
            texture = self.XMLTextures.getTextureFromOBJ(OBJ)
        return texture

    def assignTextureForPrim(self):
        groupsWithOBJ = self.assignInsertsToOBJ()
        prims = list(self.nodeWithPrims.geometry().prims())
        groupsOfNode = [gr for gr in self.nodeWithPrims.geometry().primGroups()]
        namedGroups = [g.name() for g in groupsOfNode]
        #For each group in inserts
        for group in groupsWithOBJ.keys():
            #See in the node of all groups the index of one group of inserts
            #If the group exists in the groups of prims...
            if(namedGroups.count(group) > 0):
                index = namedGroups.index(group)
                #Get the prims for this group of prims from inserts with OBJ
                primsInGroupOfNode = groupsOfNode[index].prims()
                for prim in primsInGroupOfNode:
                    #For each prim in the group, add with its OBJ
                    self.assignedPrimOBJ[prim] = groupsWithOBJ[group]
                    #Delete from the original copy group, because it has texture
                    if(prim in prims):
                        prims.remove(prim)

        for prim in prims:
            self.assignedPrimOBJ[prim] = None

        #Now we have to connect the file of description of textures with the prims
        for prim in self.assignedPrimOBJ.keys():
            textureXML = self.getTextureFromOBJ(self.assignedPrimOBJ[prim])
            if(textureXML):
                tex = self.doClassTexture(textureXML, prim)
                #FIXME: Now only one!!! We can have more than ona texture for prim, add a "for" statement
                if(tex):
                    self.assignedPrimTexture[prim] = TextureForPrim.TextureForPrim([tex], prim, self.getDefaultTexture(prim))
            else:
                self.assignedPrimTexture[prim] = TextureForPrim.TextureForPrim([], prim, self.getDefaultTexture(prim))
        logging.debug('prim with objs ' + str(self.assignedPrimOBJ))

    def assignInsertsToOBJ(self):
        dic = {}
        for insert in self.listOfInserts:
            obj = insert.parm('asset').evalAsString()
            obj = obj.split('/').pop()
            obj = obj.split('.')[0]
            for group in insert.parm('filter').evalAsString().split():
                #for each group in filter assign the .OBJ
                dic[group] = obj
        return dic

    def showTextures(self, geo):
        if(not self.HI):
            self.HI = HouInterface.HouInterface(geo)
        for texForPrim in self.assignedPrimTexture.values():
            for singleTex in texForPrim.getLayers():
                singleTex.showTexture(self.HI)

    def deleteShowTextureNodes(self):
        if(self.HI):
            self.HI.deleteCurves()

    def getDefaultTexture(self, prim):
        if(not self.defaultTexture):
            tex = self.XMLTextures.getDefaultTexture()
            tex = self.doClassTexture(tex, prim=prim, defaultTex=True)
            self.defaultTexture = tex
        return self.defaultTexture

    def getDefaultTextureXML(self):
        if(not self.defaultTextureXML):
            tex = self.XMLTextures.getDefaultTexture()
            self.defaultTextureXML = tex
        return self.defaultTextureXML
