# ////////////////////////////////////////////
# Product Tree loader routines
#
# ////////////////////////////////////////////

from xml.dom import minidom
from xml.dom import  Node

# ////////////////////////////////////////////
# productTreeXMLFileReader:
#     This class will read and XML file
#     with all the primitives in the model.
#     (with the respective Insert nodes)
#
#    Call as:
#        import productTreeXMLFileReader
#        productTreeXMLFileReader.productTreeXMLFileReader(fileToRead, container, baseAssetPath, level, loadAssets)
#            fileToRead: the path to the productTree file to read
#            container: the goemetry container (geo) that will hold the building
#            baseAssetPath: the path from where to access the assets. This is equivalent to $HIP
#            level: the number of levels to load. Only makes sense for tree-based models. For
#                    terminal prims models, use any number or leave the default value (0).
#                    Must be a positive integer value.
#            LoadAssets: wether load the assets for terminal prims or not. If False, it won't
#                    load the assets. If True, it will
#
# Sample usage:
#
#   For CornerBuilding:
#      productTreeXMLFileReader.productTreeXMLFileReader('/Users/dagush/skylineEngine/Demos/UrbanSprawl/City/CornerBuilding.productTree', hou.node('/obj/geo1'), "/Users/dagush/skylineEngine/Demos/UrbanSprawl")
#
# //////////////////////////////////////////

class XMLParser:
    def __init__(self, path):
        openedFile = open(path).read()
        self.pT_File = self.clean(openedFile)
        self.pT_File = minidom.parseString(self.pT_File)

    def read(self, tag):
        list = self.pT_File.getElementsByTagName(tag)
        nodes = self.keepNodesOnly(list)
        return nodes

    def clean(self, fileToClean):
        foo = fileToClean
        without_n = foo.replace('\n', '')
        without_t = without_n.replace('\t', '')
        return without_t

    def getNextNode(self, sibling, tagName):
        childNode = sibling
        # print "      START", tagName, childNode
        while childNode != None:
            if childNode.nodeType == Node.ELEMENT_NODE and childNode.nodeName == tagName:
                # print "      FOUND", tagName, childNode
                return childNode
            # print "      =>", tagName, childNode
            childNode = childNode.nextSibling
        # print "      FINAL", tagName, childNode
        return childNode

    def keepNodesOnly(self, nodes):
        for n in nodes:
            if n.nodeType == Node.TEXT_NODE:
                nodes.remove(n)
        return nodes

    def getAttrib(self, node, attrib):
        return (node.attributes.getNamedItem(attrib).nodeValue).encode('latin')

class XMLParserTextures(XMLParser):

    def getAllTextures(self):
        return self.read('texture')

    def getDefaultTexture(self):
        objs = self.read('obj')
        defTex = None
        for obj in objs:
            if(obj.childNodes[0].nodeValue.encode('latin') == 'default'):
                defTex = obj.parentNode
                break
        return defTex
    def getTextureFromOBJ(self, OBJ):
        matchedTexture = None
        for texture in self.getAllTextures():
            if(self.getOBJ(texture) == OBJ):
                matchedTexture = texture
                break
        return matchedTexture
    def getOBJ(self, texture):
        obj = texture.getElementsByTagName('obj')[0]
        value = obj.childNodes[0].nodeValue.encode('latin')
        return value

    def getMaterial(self, texture):
        mat = texture.getElementsByTagName('mat')[0]
        value = mat.childNodes[0].nodeValue.encode('latin')
        return value

    def getPoints(self, texture):
        points = texture.getElementsByTagName('points')
        points = self.keepNodesOnly(points)[0]
        parsedPoints = []
        points = self.keepNodesOnly(points.childNodes)
        for p in points:
            x = float(self.getAttrib(p, 'x'))
            y = float(self.getAttrib(p, 'y'))
            z = float(self.getAttrib(p, 'z'))
            parsedPoints.append([x, y, z])
        return parsedPoints

class XMLParserMaterials(XMLParser):

    def getAllComplexMaterials(self):
        return self.read('complexMaterial')

    def getMaterialsFromComplexMaterial(self, compMat):
        return compMat.getElementsByTagName('material')

    def getAtomMaterialsFromMaterial(self, mat):
        return mat.getElementsByTagName('atomMaterial')

    def getComplexMaterialName(self, comMat):
        name = comMat.getElementsByTagName('comMatName')
        name = self.keepNodesOnly(name)[0]
        name = name.childNodes[0].nodeValue.encode('latin')
        return name

    def getMaterialWavelenght(self, mat):
        wave = mat.getElementsByTagName('wavelength')
        wave = self.keepNodesOnly(wave)[0]
        wave = wave.childNodes[0].nodeValue.encode('latin')
        return wave
    def getMaterialName(self, mat):
        name = mat.getElementsByTagName('matName')
        name = self.keepNodesOnly(name)[0]
        name = name.childNodes[0].nodeValue.encode('latin')
        return name
    def getAtomMaterialName(self, atomMat):
        atomMatName = atomMat.getElementsByTagName('atomMatName')
        atomMatName = self.keepNodesOnly(atomMatName)[0]
        atomMatName = atomMatName.childNodes[0].nodeValue.encode('latin')
        return atomMatName

    def getAtomMaterialClass(self, atomMat):
        atomMatClass = atomMat.getElementsByTagName('atomMatClass')
        atomMatClass = self.keepNodesOnly(atomMatClass)[0]
        atomMatClass = atomMatClass.childNodes[0].nodeValue.encode('latin')
        return atomMatClass

    def getAtomMaterialPercent(self, atomMat):
        atomMatPercent = atomMat.getElementsByTagName('atomMatPercent')
        atomMatPercent = self.keepNodesOnly(atomMatPercent)[0]
        atomMatPercent = atomMatPercent.childNodes[0].nodeValue.encode('latin')
        return atomMatPercent


