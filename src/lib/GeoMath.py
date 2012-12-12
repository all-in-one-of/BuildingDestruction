# -*- coding: utf-8 -*-
from destruction import Errors
from lib import HouInterface
from lib import TypeEnforcement
import hou  # @UnresolvedImport
import logging
import math
import random

epsilon = 0.1
# simple bulding, with 0.001 of epsilon 2, getSharedEdge fails in big prims,
# but with 0.1 getSharedEdges fails in get the REAL shared edges.
littleEpsilon = 0.002

class Matrix:
    '''
    Column major matrix, so we access first to columns an then to rows(like OpenGL)
    '''
    def __init__(self, cols=0, rows=0, item=None):
        self.M = []
        for _ in range(cols):
            fRow = []
            for _ in range(rows):
                fRow.append(item)
            self.M.append(list(fRow))
            if(not item):
                self.matrixIdentity()

    def addCol(self, col):
        self.M.append(list(col))

    def addRow(self, row):
        if(len(self.M) != 0):
            for index in range(len(self.M)):
                self.M[index].append(row[index])
        else:
            for index in range(len(row)):
                self.M.append([row[index]])

    def delCol(self, num):
        del self.M[num]

    def delRow(self, num):
        for col in self.M:
            del col[num]

    def delMatrix(self):
        self.M = []

    def copy(self, matrix):
        self.M = []
        for col in range(len(matrix.M)):
            self.M.append(list(matrix.M[col]))

    def getSize(self):
        return [len(self.M), len(self.M[0])]

    # Quadratic matrix
    def upgrade(self):
        if (len(self.M) == 0):
            col = [0]
        else:
            col = [0 for _ in range(len(self.M[0]))]
        self.addCol(col)
        if(len(self.M) != 1):
            row = [0 for _ in range(len(self.M))]
            self.addRow(row)

    def __getitem__(self, pos):
        if(type(pos) == int):
            return self.M[pos]
        return self.M[pos[0]][pos[1]]

    def __setitem__(self, pos, item):
        self.M[pos[0]][pos[1]] = item

    def matrix3FromMatrix4(self):
        matrix3 = Matrix(4, 4)
        matrix3.copy(self)
        matrix3.delRow(3)
        matrix3.delCol(3)
        return matrix3

    def matrix4FromMatrix3(self):
        matrix4 = Matrix(3, 3)
        matrix4.copy(self)
        matrix4.upgrade()
        return matrix4
    def printAttributes(self):
        numCol = len(self.M)
        for i in range(len(self.M[0])):
            print "[",
            for j in range(numCol):
                print self.M[j][i],
            print"]",
            if(i != len(self.M[0])):
                print "\n",
# Matrix operations

    def matrixIdentity(self):
        self.M = [[int(col == row) for row in range(len(self.M[0]))]for col in range(len(self.M))]

    def singleRotx(self, angle):
        angle = math.radians(angle)
        self.M[1][1] = math.cos(angle)
        self.M[2][1] = -math.sin(angle)
        self.M[1][2] = math.sin(angle)
        self.M[2][2] = math.cos(angle)

    def singleRoty(self, angle):
        angle = math.radians(angle)
        self.M[0][0] = math.cos(angle)
        self.M[2][0] = math.sin(angle)
        self.M[0][2] = -math.sin(angle)
        self.M[2][2] = math.cos(angle)

    def singleRotz(self, angle):
        angle = math.radians(angle)
        self.M[0][0] = math.cos(angle)
        self.M[1][0] = -math.sin(angle)
        self.M[0][1] = math.sin(angle)
        self.M[1][1] = math.cos(angle)

    def matrix4Trans(self, point):
        self.M[3][0] = point[0]
        self.M[3][1] = point[1]
        self.M[3][2] = point[2]
        self.M[3][3] = point[3]

    def matrixTranspose(self):
        self.M = map(lambda * row: list(row), *self.M)

    def adjugate(self):
        if(len(self.M) == 2):
            self.delMatrix()
            self.addCol([self.M[1][1], -self.M[0][1]])
            self.addCol([-self.M[1][0], self.M[0][0]])
        elif(len(self.M) == 3):
            '''
            A=(ek-fh)    D=(ch-bk)    G=(bf-ce)
            B=(fg-dk)    E=(ak-cg)    H=(cd-af)
            C=(dh-eg)    F=(gb-ah)    K=(ae-bd)
            '''
            A = self.M[1][1] * self.M[2][2] - self.M[2][1] * self.M[1][2]
            B = self.M[2][1] * self.M[0][2] - self.M[0][1] * self.M[2][2]
            C = self.M[0][1] * self.M[1][2] - self.M[1][1] * self.M[0][2]
            D = self.M[2][0] * self.M[1][2] - self.M[1][0] * self.M[2][2]
            E = self.M[0][0] * self.M[2][2] - self.M[2][0] * self.M[0][2]
            F = self.M[0][2] * self.M[1][0] - self.M[0][0] * self.M[1][2]
            G = self.M[1][0] * self.M[2][1] - self.M[2][0] * self.M[1][1]
            H = self.M[2][0] * self.M[0][1] - self.M[0][0] * self.M[2][1]
            K = self.M[0][0] * self.M[1][1] - self.M[1][0] * self.M[0][1]
            self.delMatrix()
            self.addRow([A, B, C])
            self.addRow([D, E, F])
            self.addRow([G, H, K])

    def matrix3Inverse(self):
        '''
        inverse= 1/determinant(M) *adjugate(M)^T
        '''
        det = self.determinant()
        self.adjugate()
        self.matrixTranspose()
        self.mulScalarToMatrix(1 / float(det))

    def matrix3InverseOrtogonal(self):
        self.matrixTranspose()

    def mulScalarToMatrix(self, value):
        for i in range(len(self.M)):
            for j in range(len(self.M[i])):
                self.M[i][j] = self.M[i][j] * value

    def matrix4Inverse(self):
        transpose = self.matrix3FromMatrix4()
        transpose.matrixTranspose()
        inverse = transpose.matrix4FromMatrix3()
        point = list(self.M[3])
        point = transpose.mulPoint3ToMatrix3(point)
        point.append(1)
        inverse.M[3][0] = -point[0]
        inverse.M[3][1] = -point[1]
        inverse.M[3][2] = -point[2]
        inverse.M[3][3] = point[3]
        self.M = inverse.M

    def mulMatrix4toMatrix4(self, matrix):
        result = Matrix(4, 4)
        for row in range(4):
            for col in range(4):
                result.M[col][row] = self.M[0][row] * matrix.M[col][0] + self.M[1][row] * matrix.M[col][1] + self.M[2][row] * matrix.M[col][2] + self.M[3][row] * matrix.M[col][3]
        self.M = result.M

    def mulPoint3ToMatrix3(self, point):
        result = []
        for row in range(3):
            result.append(self.M[0][row] * point[0] + self.M[1][row] * point[1] + self.M[2][row] * point[2])
        return result

    def mulPoint4ToMatrix4(self, point):
        result = []
        for row in range(4):
            result.append(self.M[0][row] * point[0] + self.M[1][row] * point[1] + self.M[2][row] * point[2] + self.M[3][row] * point[3])
        return result

    def determinant(self):
        if(len(self.M) == 2):
            return self.M[0][0] * self.M[1][1] - self.M[1][0] * self.M[0][1]
        elif(len(self.M) == 3):
            # Det=a(ek-fh)+b(fg-kd)+c(dh-eg)
            # fc=a(ek-fh)
            fc = self.M[0][0] * (self.M[1][1] * self.M[2][2] - self.M[2][1] * self.M[1][2])
            # sc=b(fg-kd)
            sc = self.M[1][0] * (self.M[2][1] * self.M[0][2] - self.M[2][2] * self.M[0][1])
            # tc=c(dh-eg)
            tc = self.M[2][0] * (self.M[0][1] * self.M[1][2] - self.M[1][1] * self.M[0][2])
            return fc + sc + tc


################______Vectors_______##############
'''
Texture coordinates in 2D, component 0 =Tangent component, component 1= bitangent component
Object coordinates in 3D
'''
def createTBNmatrix(oc1, oc2, oc3, tc1, tc2, tc3):
    '''
    T= 1/det(coefficient matrix) *(Δc3c1b * Δv2v1 - Δc2c1b * Δv3v1)
    B= 1/det(coefficient matrix) *(-Δc3c1t * Δv2v1 + Δc2c1t * Δv3v1)
    det(coefficient matrix)= Δc2c1t * Δc3c1b - Δc3c1t * Δc2c1b
    N=TxB
    '''
    den = (tc2[0] - tc1[0]) * (tc3[1] - tc1[1]) - (tc3[0] - tc1[0]) * (tc2[1] - tc1[1])
    T = vecScalarProduct(vecSub((vecScalarProduct(vecSub(oc2, oc1), (tc3[1] - tc1[1]))), (vecScalarProduct(vecSub(oc3, oc1), (tc2[1] - tc1[1])))), 1 / den)
    B = vecScalarProduct(vecPlus((vecScalarProduct(vecSub(oc2, oc1), -(tc3[0] - tc1[0]))), (vecScalarProduct(vecSub(oc3, oc1), (tc2[0] - tc1[0])))), 1 / den)
    N = vecCrossProduct(T, B)

    tbn = Matrix()
    tbn.addCol(T)
    tbn.addCol(B)
    tbn.addCol(N)

    return tbn

# Vectors functions
def angleBetweenVectors(vec1, vec2):
    return math.acos(vecDotProduct(vec1, vec2) / (vecModul(vec1) * vecModul(vec2)))

def vecNormalize(vec):
    modul = vecModul(vec)
    return [vec[0] / modul, vec[1] / modul, vec[2] / modul]

def vecModul(vec):
    return math.sqrt(vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2])

def vecDotProduct(vec1, vec2):
    return vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2]

def vecScalarProduct(vec1, sc):
    return [vec1[0] * sc, vec1[1] * sc, vec1[2] * sc]

def vecCrossProduct(vec1, vec2):
    # Determinant
    '''
    x = Ay * Bz - By * Az
    y = Az * Bx - Bz * Ax
    z = Ax * By - Bx * Ay
    '''
    crossx = vec1[1] * vec2[2] - vec2[1] * vec1[2]
    crossy = vec1[2] * vec2[0] - vec2[2] * vec1[0]
    crossz = vec1[0] * vec2[1] - vec2[0] * vec1[1]
    return [crossx, crossy, crossz]

# FIXME:When we get a item from a hou vector it's is very slow!!
def vecSub(vec1, vec2):
    return [vec1[0] - vec2[0], vec1[1] - vec2[1], vec1[2] - vec2[2]]

def vecPlus(vec1, vec2):
    return [vec1[0] + vec2[0], vec1[1] + vec2[1], vec1[2] + vec2[2]]

def rotateVecByVec(vector, normal, angle):
    # angleR = math.radians(angle)
    angleR = angle
    '''
    http://inside.mines.edu/~gmurray/ArbitraryAxisRotation/ArbitraryAxisRotation.html

    (1) translate space so that the rotation axis passes through the origin
    (2) rotate space about the  -axis so that the rotation axis lies in the  -plane
    (3) rotate space about the  -axis so that the rotation axis lies along the  -axis
    (4) perform the desired rotation by  about the  -axis
    (5) apply the inverse of step (3)
    (6) apply the inverse of step (2)
    (7) apply the inverse of step (1)
    '''
    # not (1), because we assume lastDir in origin(0,0,0) coordinate system
    if(not(normal[0] == 0 and normal[1] == 0)):
        '''
        Transformations for moving a vector to the z-axis
        '''
        # The matrix to rotate a vector about the  z-axis to the  xz-plane is
        Rxz = Matrix(4, 4)
        Rxz[0, 0] = normal[0] / math.sqrt(pow(normal[0], 2) + math.pow(normal[1], 2))
        Rxz[0, 1] = -normal[1] / math.sqrt(pow(normal[0], 2) + math.pow(normal[1], 2))
        Rxz[1, 0] = normal[1] / math.sqrt(pow(normal[0], 2) + math.pow(normal[1], 2))
        Rxz[1, 1] = normal[0] / math.sqrt(pow(normal[0], 2) + math.pow(normal[1], 2))
        # The matrix to rotate the vector in the xz-plane to the  z-axis is
        Rxz2z = Matrix(4, 4)
        Rxz2z[0, 0] = normal[2] / math.sqrt(math.pow(normal[0], 2) + math.pow(normal[1], 2) + math.pow(normal[2], 2))
        Rxz2z[0, 2] = math.sqrt(pow(normal[0], 2) + math.pow(normal[1], 2)) / math.sqrt(math.pow(normal[0], 2) + math.pow(normal[1], 2) + math.pow(normal[2], 2))
        Rxz2z[2, 0] = -math.sqrt(pow(normal[0], 2) + math.pow(normal[1], 2)) / math.sqrt(math.pow(normal[0], 2) + math.pow(normal[1], 2) + math.pow(normal[2], 2))
        Rxz2z[2, 2] = normal[2] / math.sqrt(math.pow(normal[0], 2) + math.pow(normal[1], 2) + math.pow(normal[2], 2))
        '''
        Rotations about the origin
        '''
        Rz = Matrix(4, 4)
        Rz.singleRotz(angleR)
        '''
        Inverses
        '''
        # Rxzi*Rxz2zi*Rz(Identity)Rxz2z*Rxz
        Rxzi = Matrix(4, 4)
        Rxz2zi = Matrix(4, 4)
        Rxzi.copy(Rxz)
        Rxzi.matrix4Inverse()
        Rxz2zi.copy(Rxz2z)
        Rxz2zi.matrix4Inverse()
        '''
        Get the final matrix
        '''
        # Rxzi*Rxz2zi*Rz(Identity)Rxz2z*Rxz
        Rxz2z.mulMatrix4toMatrix4(Rxz)
        Rz.mulMatrix4toMatrix4(Rxz2z)
        Rxz2zi.mulMatrix4toMatrix4(Rz)
        Rxzi.mulMatrix4toMatrix4(Rxz2zi)

        '''
        Get the vector rotated
        '''
        vectorRotated = list(vector)
        # with 0 in the last component, it will be a vector
        vectorRotated.append(0)
        vectorRotated = Rxzi.mulPoint4ToMatrix4(vectorRotated)
        # Del last component (0)
        vectorRotated.pop()
    else:

        '''
        Rotations about the origin
        '''
        Rz = Matrix(4, 4)
        Rz.singleRotz(angleR)
        '''
        Get the vector rotated
        '''
        vectorRotated = list(vector)
        # with 0 in the last component, it will be a vector
        vectorRotated.append(0)
        vectorRotated = Rz.mulPoint4ToMatrix4(vectorRotated)
        # Del last component (0)
        vectorRotated.pop()
    return vectorRotated

def getVectorsArea(lenght, angle):
    # paralelepiped area between one vector in x, rotate around y an angle of "angle" with
    # lenght of vectors "lenght"
    # We have to do the cross product between the two vectors, one vector will be x=lenght and the
    # other is rotated in y an angle.
    # rotate around y: x=radi*cos(alfa), z=radi*sin(alfa)
    vector2 = []
    vector1 = [lenght, 0, 0]
    vector2.append(lenght * math.cos(angle))
    vector2.append(0)
    vector2.append(lenght * math.sin(angle))
    area = vecCrossProduct(vector1, vector2)
    return area

# End functions with vectors
def centerOfPoints(points):
    curSum = [0, 0, 0]
    for point in points:
        curSum = vecPlus(curSum, point)
    center = vecScalarProduct(curSum, 1.0 / len(points))
    return center

def pointEqualPoint(point1, point2):
    global littleEpsilon
    return vecModul(vecSub(point1, point2)) < littleEpsilon


def pointInSegmentDistance(p1, p2, pIO, epsilon=None):
    '''
    >>> p1 = [0,0,0]
    >>> p2 = [0,1,0]
    >>> p3 = [0, 0.5, 0]
    >>> pointInSegmentDistance (p1, p2, p3)
    True
    
    >>> p1 = [1,0,0]
    >>> p2 = [0,1,0]
    >>> p3 = [0.5, 0.5, 0]
    >>> pointInSegmentDistance (p1, p2, p3)
    True
    '''
    try:
        if(type(p1) != type(list()) or type(p2) != type(list()) or type(pIO) != type(list())):
            raise TypeError
    except:
        import sys
        import traceback
        logging.error("Exception ocurred, invalid type in: " + str(sys._getframe().f_code.co_name))
        traceback.print_stack()
        exit()
        return None
    global littleEpsilon
    if(not epsilon):
        epsilon = littleEpsilon

    vec12 = vecSub(p2, p1)
    vec1IO = vecSub(pIO, p1)
    vec21 = vecSub(p1, p2)
    vec2IO = vecSub(pIO, p2)

    dotProduct1 = vecDotProduct(vec12, vec1IO)
    dotProduct2 = vecDotProduct(vec21, vec2IO)
    if(vecModul(vec12) < epsilon):
        # Invalid edge
        return False
    proj1 = dotProduct1 / vecModul(vec12)
    proj2 = dotProduct2 / vecModul(vec12)
    if(proj1 < 0):
        # Extrem case
        if(vecModul(vec1IO) > epsilon):
            return False
    if(proj2 < 0):
        # Extrem case
        if(vecModul(vec2IO) > epsilon):
            return False

    distance = vecModul(vecSub(pIO, vecPlus(p1, vecScalarProduct(vecNormalize(vec12), proj1))))
    if(distance > epsilon):
        return False
    return True

def pointInSegment(p1, p2, pIO):
    global littleEpsilon
    epsilon = littleEpsilon
    if(p1[0] <> p2[0] or p1[1] <> p2[1] or p1[2] <> p2[2]):
        if(vecModul(vecSub(pIO, p1)) < littleEpsilon or vecModul(vecSub(pIO, p2)) < littleEpsilon):
            return True

        #=======================================================================
        # http://stackoverflow.com/questions/328107/how-can-you-determine-a-point-is-between-two-other-points-on-a-line-segment
        # Check if the cross product of (b-a) and (c-a) is 0, as tells Darius Bacon, tells you if
        # the points a, b and c are aligned.
        # But, as you want to know if c is between a and b, you also have to check that the dot product of
        # (b-a) and (c-a) is positive and is less than the square of the distance between a and b.
        #=======================================================================
        vec12 = vecSub(p2, p1)
        vec1IO = vecSub(pIO, p1)

        crossProduct = vecCrossProduct(vec12, vec1IO)
        lengthCross = vecModul(crossProduct)

        if(lengthCross > epsilon):
            return False

        dotProduct = vecDotProduct(vec12, vec1IO)

        if(dotProduct < -epsilon):
            return False

        length = vecModul(vec12)
        squaredLength = length * length
        dotProductEp = abs(dotProduct) - squaredLength

        if(dotProductEp > epsilon):
            return False
        return True
    else:
        return False
def getEdgesFromPoints(points):
    allEdges = []
    numPoints = len(points)
    for u in range(numPoints):
        point1 = points[u % numPoints]
        point2 = points[(u + 1) % numPoints]
        allEdges.append([point1, point2])
    return allEdges

def getEdgesFromPrim(prim):
    listPoints = [list(p.point().position()) for p in prim.vertices()]
    allEdges = getEdgesFromPoints(listPoints)
    return allEdges

def getSharedPoints(list_points_1, list_points_2, max_num=None):
    global littleEpsilon
    shared_points = []
    count = 0
    for point_1 in list_points_1:
        for point_2 in list_points_2:
            if(vecModul(vecSub(point_1, point_2)) < littleEpsilon):
                shared_points.append(list(point_1))
                count += 1
            if(count and count >= max_num):
                break
        if(count and count >= max_num):
            break

    return shared_points

def getEdgeBetweenEdges(edge1, edge2):
    try:
        if(type(edge1) != type(list()) or type(edge2) != type(list())):
            raise TypeError
    except:
        import sys
        logging.error("Exception ocurred, invalid type in: " + str(sys._getframe().f_code.co_name))
        return None

    global littleEpsilon
    epsilon = littleEpsilon
    finalEdge = []
    count = 0
    if(pointInSegmentDistance(edge2[0], edge2[1], edge1[0])):
        finalEdge.append(list(edge1[0]))
        count += 1
    if(pointInSegmentDistance(edge2[0], edge2[1], edge1[1])):
        finalEdge.append(list(edge1[1]))
        count += 1
    if(pointInSegmentDistance(edge1[0], edge1[1], edge2[0]) and count < 2):
        # we have to ensure taht points are not the same that we already put
        if(not(count == 1 and (vecModul(vecSub(edge2[0], finalEdge[0])) < epsilon))):
            finalEdge.append(list(edge2[0]))
            count += 1
    if(pointInSegmentDistance(edge1[0], edge1[1], edge2[1]) and count < 2):
        # we have to ensure taht points are not the same that we already put
        if(not(count == 1 and (vecModul(vecSub(edge2[1], finalEdge[0])) < epsilon))):
            finalEdge.append(list(edge2[1]))
            count += 1
    if(len(finalEdge) != 2):
        finalEdge = None
    return finalEdge

def getEdgesBetweenEdges(edges1, edges2, numEdges=None):
    try:
        if(type(edges1) != type(list()) or type(edges2) != type(list())):
            raise TypeError
    except:
        import sys
        logging.error("Exception ocurred, invalid type in: " + str(sys._getframe().f_code.co_name))
        return None

    if(numEdges == None):
        numEdges = max(len(edges1), len(edges2))
    matchEdges = []
    for edge1 in edges1:
        for edge2 in edges2:
            edge = getEdgeBetweenEdges(edge1, edge2)
            if(edge):
                matchEdges.append(edge)
            if(len(matchEdges) >= numEdges): break
    return matchEdges

def getEdgesBetweenPoints(listPoints1, listPoints2, numEdges=None):
    numVert1 = len(listPoints1)
    numVert2 = len(listPoints2)
    if(numEdges == None):
        numEdges = numVert1 * numVert2
    matchEdges = []
    edge1 = [None, None]
    edge2 = [None, None]
    for u in range(numVert1):
        edge1[0] = listPoints1[u % numVert1]
        edge1[1] = listPoints1[(u + 1) % numVert1]
        for j in range(numVert2):
            edge2[0] = listPoints2[j % numVert2]
            edge2[1] = listPoints2[(j + 1) % numVert2]
            edge = getEdgeBetweenEdges(edge1, edge2)
            if(edge):
                matchEdges.extend(edge)
            if(len(matchEdges) >= numEdges): break
    return matchEdges
# at least one shared edge, if not, return empty edge
def getEdgesBetweenPrims(prim1, prim2, numEdges=None):
    curNumEdges = 0
    finalEdges = []
    edges1 = getSharedEdgesPrims(prim1, prim2)
    edges2 = getSharedEdgesPrims(prim2, prim1)

    if(numEdges == None):
        numEdges = max(len(edges1), len(edges2))

    for edge1 in edges1:
        for edge2 in edges2:
            toValidateEdge = getEdgeBetweenEdges(edge1, edge2)
            if(toValidateEdge):
                finalEdges.append(toValidateEdge)
                curNumEdges += 1
                # go to the next edge
                break
        if(curNumEdges >= numEdges):
            # stop the for statement
            break

    return finalEdges
getEdgesBetweenPrims = TypeEnforcement.memoized(getEdgesBetweenPrims)

def getCenterEdge(edge):
    center = []
    plus = vecPlus(edge[0], edge[1])
    center.append(plus[0] / 2)
    center.append(plus[1] / 2)
    center.append(plus[2] / 2)
    return center

def getRandomPointInEdge(edge, range):
    vec = vecSub(edge[0], edge[1])
    numRand = random.random() * vecModul(vec)
    vecNor = vecNormalize(vec)
    if(numRand - range < 0):
        numRand = range
    elif((vecModul(vec) - numRand) < range):
        numRand = vecModul(vec) - range
    point = vecPlus(edge[1], vecScalarProduct(vecNor, numRand))
    return point

def getEdgeWithPointInPrim(prim, point):
    listVertex = prim.vertices()
    numVert = len(listVertex)
    for u in range(numVert):
        point1 = list(listVertex[u % numVert].point().position())
        point2 = list(listVertex[(u + 1) % numVert].point().position())
        if(pointInSegmentDistance(point1, point2, point)):
            return [point1, point2]
    return None

def getEdgeWithPoint(edges, point):
    for u in range(len(edges)):
        point1 = edges[u][0]
        point2 = edges[u][1]
        if(pointInSegmentDistance(point1, point2, point)):
            return [point1, point2]

def bolzanoIntersectionPoint2_5D(point1, point2, reference_point, axis):
    if(axis == 'x'): axis = 0
    if(axis == 'y'): axis = 1
    if(axis == 'z'): axis = 2
    try:
        if(type(axis) != type(int())):
            raise TypeError
    except TypeError:
        print "Expected integer"

    if(point1[axis] < reference_point[axis] and point2[axis] > reference_point[axis]):
        return True
    if(point1[axis] > reference_point[axis] and point2[axis] < reference_point[axis]):
        return True

    return False
# Intersect the bounding box of the edge, not the edge.
def bolzanoIntersectionEdges2_5D(edges1, edges2):
    edge_1_inter = None
    edge_2_inter = None
    for edge1 in edges1:
        for edge2 in edges2:
            inter = bolzanoIntersectionPoint2_5D(edge1[0], edge1[1], edge2[0], 'y')
            if(not inter):
                inter = bolzanoIntersectionPoint2_5D(edge1[0], edge1[1], edge2[1], 'y')
            if(inter):
                edge_2_inter = edge2
                break
        if(inter):
            edge_1_inter = edge1
            break

    return inter, edge_1_inter, edge_2_inter

def getFalseIntersectionBetweenTwoEdges3D(edge1, edge2, prim):
    vertices = [list(p.point().position()) for p in prim.vertices()]
    tbn = createTBNmatrix(vertices[0], vertices[1], vertices[2], [0, 1], [0, 0], [1, 0])
    tbnInverse = Matrix(3, 3)
    tbnInverse.copy(tbn)
    tbnInverse.matrix3Inverse()
    pointWhichIsRelative = vertices[1]

    # Relative the points of edges to the point in prim which is relative in tbn matrix
    edge10relative = vecSub(edge1[0], pointWhichIsRelative)
    edge11relative = vecSub(edge1[1], pointWhichIsRelative)
    edge20relative = vecSub(edge2[0], pointWhichIsRelative)
    edge21relative = vecSub(edge2[1], pointWhichIsRelative)

    # Tranform to tangent space
    edge10tbn = tbn.mulPoint3ToMatrix3(edge10relative)
    edge11tbn = tbn.mulPoint3ToMatrix3(edge11relative)
    edge20tbn = tbn.mulPoint3ToMatrix3(edge20relative)
    edge21tbn = tbn.mulPoint3ToMatrix3(edge21relative)


    # Make the edges in tangent space
    edge1tbn = [edge10tbn, edge11tbn]
    edge2tbn = [edge20tbn, edge21tbn]


    # Find intersections in 2D
    pointIntersectiontbn = getIntersectionBetweenTwoEdges2D(edge1tbn, edge2tbn)
    # Transform to object coordinates
    if(pointIntersectiontbn.__class__ == type(list())):
        # If exists inersection
        pointIntersection = tbnInverse.mulPoint3ToMatrix3(pointIntersectiontbn)
        pointIntersection = vecPlus(pointWhichIsRelative, pointIntersection)
    else:
        pointIntersection = None
    return pointIntersection

# FIXME: when lines lies in diferntes planes, it is not work. So it is called "false" intersection
def getFalseIntersectionsBetweenEdges3D(list_edges1, list_edges2, prim, num_max_edges):
    count = 0
    edgesIntersection = []
    for edge1 in list_edges1:
        for edge2 in list_edges2:
            intersection = getFalseIntersectionBetweenTwoEdges3D(edge1, edge2, prim)
            if(intersection.__class__ == type(list())):
                edgesIntersection.append(intersection)
                count += 1
                if(num_max_edges and count >= num_max_edges):
                    break
        if(num_max_edges and count >= num_max_edges):
                    break

    return edgesIntersection
def getIntersectionsBetweenEdges2D(edges1, edges2, maxEdges=None, epsilon=None):
    count = 0
    edgesIntersection = []

    for edge1 in edges1:
        for edge2 in edges2:
            intersection = getIntersectionBetweenTwoEdges2D(edge1, edge2 , epsilon)
            if(intersection.__class__ == type(list())):
                edgesIntersection.append(intersection)
                count += 1
                if(maxEdges and count >= maxEdges):
                    break
        if(maxEdges and count >= maxEdges):
                    break

    return edgesIntersection

def getIntersectionBetweenEdgesWithoutLimits2D(edges1, edges2, maxEdges=None):
    count = 0
    edgesIntersection = []
    for edge1 in edges1:
        for edge2 in edges2:
            intersection = getIntersectionBetweenTwoEdges2D(edge1, edge2)
            if(intersection.__class__ == type(list())):
                dist10 = vecModul(vecSub(intersection, edge1[0]))
                dist11 = vecModul(vecSub(intersection, edge1[1]))
                dist20 = vecModul(vecSub(intersection, edge2[0]))
                dist21 = vecModul(vecSub(intersection, edge2[1]))
                if(dist10 > epsilon and dist11 > epsilon and dist20 > epsilon and dist21 > epsilon):
                    edgesIntersection.append(intersection)
                    count += 1
                    if(maxEdges and count >= maxEdges):
                        break
        if(maxEdges and count >= maxEdges):
                    break

    return edgesIntersection

def getIntersectionBetweenTwoEdges2D(edge1, edge2, epsilon=None):
    global littleEpsilon
    if(not epsilon):
        epsilon = littleEpsilon
    # First line
    p = edge1[0]
    v = vecSub(edge1[1], edge1[0])
    # Second line
    o = edge2[0]
    k = vecSub(edge2[1], edge2[0])

    # Omega= (OyVx - PyVx - VyOx + VyPx) / (VyKx + VxKy)
    divider = (v[1] * k[0] - v[0] * k[1])

    if(divider > (epsilon / 100) or divider < -(epsilon / 100)):
        # If divider==0 the lines are parallel, no solution possible
        omega = float((o[1] * v[0] - p[1] * v[0] - v[1] * o[0] + v[1] * p[0])) / float(divider)
    else:
        return None

    # Lambda = (Oy + omega*Ky - Py) / Vy
    # lam = (o[1] + omega * k[1] - p[1]) / v[1]
    pointIntersection = [o[0] + omega * k[0], o[1] + omega * k[1], 0]
    # Check if the point lies in edges
    if (pointInSegmentDistance(edge1[0], edge1[1], pointIntersection) and pointInSegmentDistance(edge2[0], edge2[1], pointIntersection)):
        return pointIntersection
    else:
        # RETURN NONE
        return None

def clipPoints(points, pointToClipWith, firstPoint):
    pointAchieved = False
    nextEnd = False
    pointsClipped = [list(firstPoint)]
    if(vecModul(vecSub(points[0], firstPoint)) < littleEpsilon):
        normalTrack = True
        curIndex = 0
        nextIndex = 1
    else:
        curIndex = len(points) - 1
        nextIndex = len(points) - 2
        normalTrack = False

    while(not pointAchieved and not nextEnd):
        if(pointInSegmentDistance(points[curIndex], points[nextIndex], pointToClipWith)):
            pointAchieved = True
            pointsClipped.append(pointToClipWith)
        else:
            pointsClipped.append(points[nextIndex])
            curIndex = nextIndex
            if(normalTrack):
                nextIndex = (nextIndex + 1) % len(points)
                if(nextIndex == 0):
                    nextEnd = True
            else:
                nextIndex = (nextIndex - 1)
                if(nextIndex < 0):
                    nextIndex = len(points) - 1
                    nextEnd = True
    return pointsClipped, pointAchieved
'''
Function to measure the distance in a track of edges to a point
'''
def takeDistanceInTrackToPoint(points, pointToIntersect, firstPoint):
    global littleEpsilon
    distance = 0
    pointAchieved = False
    nextEnd = False
    if(vecModul(vecSub(points[0], firstPoint)) < littleEpsilon):
        normalTrack = True
        curIndex = 0
        nextIndex = 1
    else:
        curIndex = len(points) - 1
        nextIndex = len(points) - 2
        normalTrack = False

    while(not pointAchieved and not nextEnd):
        if(pointInSegmentDistance(points[curIndex], points[nextIndex], pointToIntersect)):
            distance += vecModul(vecSub(points[curIndex], pointToIntersect))
            pointAchieved = True
        else:
            distance += vecModul(vecSub(points[curIndex], points[nextIndex]))
            curIndex = nextIndex
            if(normalTrack):
                nextIndex = (nextIndex + 1) % len(points)
                if(nextIndex == 0):
                    nextEnd = True
            else:
                nextIndex = (nextIndex - 1)
                if(nextIndex < 0):
                    nextIndex = len(points) - 1
                    nextEnd = True
    return distance, pointAchieved
'''
Function to track edges.
When I tell track edges I mean find a path (edgement hablando) between one edge and another.
Normally, this edges are closed, so we have two paths between first edge and last egde, so
this functions will return two sets of edges.
'''

def trackEdges(firstEdge, setOfEdgesToTrack, lastEdge, exceptions):
    global littleEpsilon
    curPoint = firstEdge[0]
    setOfEdgesTracking = list(setOfEdgesToTrack)
    # print "All edges"
    # print setOfEdgesToTrack
    for edge in setOfEdgesTracking:
        if(sameEdge(firstEdge, edge)):
            setOfEdgesTracking.remove(edge)
            break
    setOfEdgesTracked1 = []
    count = 0
    # print "First and last edge"
    # print firstEdge, lastEdge
    # One direction of tracking
    while(not pointInSegmentDistance(lastEdge[0], lastEdge[1], curPoint) and count < len(setOfEdgesToTrack)):
        trackEdge = getEdgeWithPoint(setOfEdgesTracking, curPoint)
        # print "SetOfEdgesTracking1"
        # print setOfEdgesTracking
        # Next point to evaluate
        # print "curPoint"
        # print curPoint
        # print "Track edge1: "+str(trackEdge)
        if(trackEdge not in exceptions):
            setOfEdgesTracked1.append(list(trackEdge))

        if(trackEdge[0] == curPoint):
            curPoint = trackEdge[1]
        else:
            curPoint = trackEdge[0]

        # Edge already tracted
        setOfEdgesTracking.remove(trackEdge)

        # Pay atention with possible errors
        count += 1

    # The other direction of tracking edges
    curPoint = firstEdge[1]
    setOfEdgesTracked2 = []
    count = 0
    while(not pointInSegmentDistance(lastEdge[0], lastEdge[1], curPoint) and count < len(setOfEdgesToTrack)):
        # print "SetOfEdgesTracking2"
        # print setOfEdgesTracking
        # Next point to evaluate
        # print "curPoint"
        # print curPoint
        trackEdge = getEdgeWithPoint(setOfEdgesTracking, curPoint)
        # print "Track edge2: "+str(trackEdge)
        if(trackEdge not in exceptions):
            setOfEdgesTracked2.append(list(trackEdge))

        # Next point to evaluate
        if(trackEdge[0] == curPoint):
            curPoint = trackEdge[1]
        else:
            curPoint = trackEdge[0]

        # Edge already tracted
        setOfEdgesTracking.remove(trackEdge)

        # Pay atention with possible errors
        count += 1

    return setOfEdgesTracked1, setOfEdgesTracked2

# Origin in prim.center, vec1[0] and vec2[0] equal to prim.center()
def angleBetweenPointsByPrim(point1, point2, prim):
    '''
    http://www.gamedev.net/community/forums/topic.asp?topic_id=503639
    '''
    onePoint = primBoundingBox(prim).center()  # [0.5, 0.5, 0]
    normal = prim.normal()  # [0.5, 0.5, 0]
    dist1 = ((point1[0] - onePoint[0]) * normal[0] + (point1[1] - onePoint[1]) * normal[1] + (point1[2] - onePoint[2]) * normal[2])
    projectionPoint1 = [point1[0] - dist1 * normal[0], point1[1] - dist1 * normal[1], point1[2] - dist1 * normal[2]]
    dist2 = ((point2[0] - onePoint[0]) * normal[0] + (point2[1] - onePoint[1]) * normal[1] + (point2[2] - onePoint[2]) * normal[2])
    projectionPoint2 = [point2[0] - dist2 * normal[0], point2[1] - dist2 * normal[1], point2[2] - dist2 * normal[2]]

    vec1 = vecSub(projectionPoint1, onePoint)
    vec2 = vecSub(projectionPoint2, onePoint)

    cross = vecCrossProduct(vec1, vec2)
    angle = math.atan2(vecModul(cross), vecDotProduct(vec1, vec2))
    if (vecDotProduct(cross, normal) < 0):
        angle = -angle
    return angle

def angleBetweenPointsByVec(point1, point2, vec):
    '''
    http://www.gamedev.net/community/forums/topic.asp?topic_id=503639
    '''
    onePoint = [0, 0, 0]  # [0.5, 0.5, 0]
    normal = vec  # [0.5, 0.5, 0]
    dist1 = ((point1[0] - onePoint[0]) * normal[0] + (point1[1] - onePoint[1]) * normal[1] + (point1[2] - onePoint[2]) * normal[2])
    projectionPoint1 = [point1[0] - dist1 * normal[0], point1[1] - dist1 * normal[1], point1[2] - dist1 * normal[2]]
    dist2 = ((point2[0] - onePoint[0]) * normal[0] + (point2[1] - onePoint[1]) * normal[1] + (point2[2] - onePoint[2]) * normal[2])
    projectionPoint2 = [point2[0] - dist2 * normal[0], point2[1] - dist2 * normal[1], point2[2] - dist2 * normal[2]]

    vec1 = vecSub(projectionPoint1, onePoint)
    vec2 = vecSub(projectionPoint2, onePoint)

    cross = vecCrossProduct(vec1, vec2)
    angle = math.atan2(vecModul(cross), vecDotProduct(vec1, vec2))
    if (vecDotProduct(cross, normal) < 0):
        angle = -angle
    return angle

def getMinMaxAngleBetweenPointsInPrim(prim1, prim2, refPrim):
    # points1=[po.point().position() for po in prim1.vertices()]
    points1 = [list(primBoundingBox(prim1).center())]
    points2 = [po.point().position() for po in prim2.vertices()]
    minAngle = maxAngle = angleBetweenPointsByPrim(points1[0], points2[0], refPrim)

    for point1 in points1:
        for point2 in points2:
            curAngle = angleBetweenPointsByPrim(point1, point2, refPrim)
            if(curAngle < minAngle):
                minAngle = curAngle
            if(curAngle > maxAngle):
                maxAngle = curAngle
    return minAngle, maxAngle


def sameEdge(edge1, edge2):
    return ((edge1[0] == edge2[0] or edge1[0] == edge2[1]) and (edge1[1] == edge2[0] or edge1[1] == edge2[1]))

def edgeInEdge(edge1, edge2):
    return (pointInSegmentDistance(edge1[0], edge1[1], edge2[0]) and pointInSegmentDistance(edge1[0], edge1[1], edge2[1]))

def determineDirEdge(edge, prim, clockwise):
    points = [list(p.point().position()) for p in prim.vertices()]
    if(clockwise):
        index = 0
        nextIndex = 1
        while(not (pointInSegmentDistance(points[index], points[nextIndex], edge[0]) and  pointInSegmentDistance(points[index], points[nextIndex], edge[1])) and nextIndex != 0):
            # Module
            index = (index + 1) % len(points)
            nextIndex = (index + 1) % len(points)
            # The sum of the diferences between nearly points has to be smallest than the distance of the big edge
        if((pointInSegmentDistance(points[index], points[nextIndex], edge[0]) and pointInSegmentDistance(points[index], points[nextIndex], edge[1]))):
            sum = vecModul(vecSub(edge[0], points[index])) + vecModul(vecSub(edge[1], points[nextIndex]))
            return sum < vecModul(vecSub(points[index], points[nextIndex]))
        else:
            return False
    else:
        index = 0
        nextIndex = len(points) - 1
        while(not (pointInSegmentDistance(points[index], points[nextIndex], edge[0]) and pointInSegmentDistance(points[index], points[nextIndex], edge[1])) and nextIndex != 0):
            index -= 1
            # Module
            if(index < 0):
                index = len(points) - 1
            nextIndex = index - 1
            if(nextIndex < 0):
                nextIndex = len(points) - 1
        # Last comprovation
        if((pointInSegmentDistance(points[index], points[nextIndex], edge[0]) and pointInSegmentDistance(points[index], points[nextIndex], edge[1]))):
            sum = vecModul(vecSub(edge[0], points[index])) + vecModul(vecSub(edge[1], points[nextIndex]))
            return sum < vecModul(vecSub(points[index], points[nextIndex]))
        else:
            return False


################______PRIMITIVES_______##################

# Functions to work with primitives

# Return the edges conected between lists, None if no edge connected#
'''
>>> if(True):
...     listPoints1=[[3.1875,18.75,25.0], [3.125,18.75,25.0]]
...     listPoints2=[[3.255,18.75,25.0], [3.125,18.75,25.0]]  
...     len(getSharedEdges(listPoints1, listPoints2, 1))
1
'''
# return the edges coencted from the two lists
def getSharedEdges(listPoints1, listPoints2, numEdges):
    numVert1 = len(listPoints1)
    numVert2 = len(listPoints2)
    matchEdges = []
    for u in range(numVert1):
        pointPr11 = listPoints1[u % numVert1]
        pointPr12 = listPoints1[(u + 1) % numVert1]
        if(pointPr11[0] <> pointPr12[0] or pointPr11[1] <> pointPr12[1] or pointPr11[2] <> pointPr12[2]):
            for j in range(numVert2):
                pointPr21 = listPoints2[j % numVert2]
                pointPr22 = listPoints2[(j + 1) % numVert2]
                if(pointPr21[0] <> pointPr22[0] or pointPr21[1] <> pointPr22[1] or pointPr21[2] <> pointPr22[2]):
                    if((pointInSegmentDistance(pointPr21, pointPr22, pointPr11) and pointInSegmentDistance(pointPr21, pointPr22, pointPr12)) or(pointInSegmentDistance(pointPr11, pointPr12, pointPr21) and  pointInSegmentDistance(pointPr11, pointPr12, pointPr22))):
                        curMatchEdge = [pointPr11, pointPr12]
                        curMatchEdge2 = [pointPr21, pointPr22]
                        matchEdges.append(curMatchEdge)
                        matchEdges.append(curMatchEdge2)
                        break
            if(len(matchEdges) >= numEdges): break
    return matchEdges

# Return the edges conected between primitives from the first prim, None if no edge connected, return edge from first prim#
# TEMP: Remove memoize
def getSharedEdgesPrims(prim1, prim2, numEdges=None):
    if(not numEdges):
        numEdges = max(len(prim1.vertices()), len(prim2.vertices()))
    listVertex1 = list(prim1.vertices())
    listVertex2 = list(prim2.vertices())
    numVert1 = len(listVertex1)
    numVert2 = len(listVertex2)
    matchEdges = []
    for u in range(numVert1):
        pointPr11 = list(listVertex1[u % numVert1].point().position())
        pointPr12 = list(listVertex1[(u + 1) % numVert1].point().position())
        for j in range(numVert2):
            pointPr21 = list(listVertex2[j % numVert2].point().position())
            pointPr22 = list(listVertex2[(j + 1) % numVert2].point().position())
            if((pointInSegmentDistance(pointPr21, pointPr22, pointPr11) and
               pointInSegmentDistance(pointPr21, pointPr22, pointPr12))
               or(pointInSegmentDistance(pointPr11, pointPr12, pointPr21) and
               pointInSegmentDistance(pointPr11, pointPr12, pointPr22))):
                curMatchEdge = [list(pointPr11), list(pointPr12)]
                matchEdges.append(curMatchEdge)
                break

        if(len(matchEdges) >= numEdges): break

    return matchEdges
getSharedEdgesPrims = TypeEnforcement.memoized(getSharedEdgesPrims)

def getConnectedPrims(prim, setOfPrims, num=None):
    if(not num): num = len(setOfPrims)
    connectedList = []
    count = 0
    numConected = 0
    while(numConected < num and count < len(setOfPrims)):
        tempPrim = setOfPrims[count]
        if(tempPrim != prim):
            if (len(getEdgesBetweenPrims(prim, tempPrim, 1)) >= 1):
                connectedList.append(tempPrim)
                numConected += 1
        count += 1
    return  connectedList
getConnectedPrims = TypeEnforcement.memoized(getConnectedPrims)

def getConnectedPrimsOneForEachEdge(prim, setOfPrims, numPrims=None):
    if(not numPrims):
        numPrims = len(setOfPrims)
    listVertex1 = list(prim.vertices())
    numVert1 = len(listVertex1)
    matchPrims = []
    for u in range(numVert1):
        pointPr11 = listVertex1[u % numVert1].point().position()
        pointPr12 = listVertex1[(u + 1) % numVert1].point().position()
        for prim2 in setOfPrims:
            if(prim2 != prim):
                matchEdge = False
                listVertex2 = list(prim2.vertices())
                numVert2 = len(listVertex2)
                for j in range(numVert2):
                    pointPr21 = listVertex2[j % numVert2].point().position()
                    pointPr22 = listVertex2[(j + 1) % numVert2].point().position()
                    if((pointInSegmentDistance(pointPr21, pointPr22, pointPr11) and
                       pointInSegmentDistance(pointPr21, pointPr22, pointPr12))
                       or(pointInSegmentDistance(pointPr11, pointPr12, pointPr21) and
                       pointInSegmentDistance(pointPr11, pointPr12, pointPr22))):
                        matchEdge = True
                        break
                if(matchEdge):
                    matchPrims.append(prim2)
                    break
        if(len(matchPrims) >= numPrims): break
    return matchPrims

def getConnectedInfoPrims(prim, setOfPrims, num=None):
    if(not num): num = len(setOfPrims)
    connectedList = []
    count = 0
    numConected = 0
    while(numConected < num and count < len(setOfPrims)):
        tempPrim = setOfPrims[count]
        if(tempPrim != prim):
            if (len(getSharedEdgesPrims(prim.prim, tempPrim.prim, 1)) == 1):
                connectedList.append(tempPrim)
                numConected += 1
        count += 1
    return  connectedList
getConnectedInfoPrims = TypeEnforcement.memoized(getConnectedInfoPrims)

def getAnglePrims(curPrim, nextPrim, refPrim):
    vecFromRefCur = vecSub(primBoundingBox(curPrim.prim).center(), primBoundingBox(refPrim.prim).center())
    vecInterPrim = vecSub(primBoundingBox(nextPrim.prim).center(), primBoundingBox(curPrim.prim).center())
    vecFromRefNext = vecSub(primBoundingBox(nextPrim.prim).center(), primBoundingBox(refPrim.prim).center())
    vfrc = vecModul(vecFromRefCur)
    vip = vecModul(vecInterPrim)
    vfrn = vecModul(vecFromRefNext)
    # Propiety of coseno
    angleToSum = math.acos((vip * vip - vfrn * vfrn - vfrc * vfrc) / (-2 * vfrc * vfrn))
    return angleToSum

def primBoundingBox(prim):
    tempListMin = prim.vertices()[0].point().position()
    tempListMax = prim.vertices()[0].point().position()
    for index in prim.vertices():
        position = index.point().position()
        tempListMin[0] = min(tempListMin[0], position[0])
        tempListMin[1] = min(tempListMin[1], position[1])
        tempListMin[2] = min(tempListMin[2], position[2])
        tempListMax[0] = max(tempListMax[0], position[0])
        tempListMax[1] = max(tempListMax[1], position[1])
        tempListMax[2] = max(tempListMax[2], position[2])
    boundingBox = hou.BoundingBox(tempListMin[0], tempListMin[1], tempListMin[2], tempListMax[0], tempListMax[1], tempListMax[2])
    return boundingBox

def pointInPolygon(pointIO, poly):
    global littleEpsilon
    reload (HouInterface)
    listVert = []
    # Borramos componente que obviamos(la 'x') y proyectamos sobre el plano de las x
    # la primitiva de la geometria de referencia

    '''
    Start Modification 8/6/2011
    Adaptly it to the tangent space knowledge to do a properly point in polygon
    '''
    # Convert to the tangent space of x
    goodPoints = []
    for vertex in poly.vertices():
        curPoint = vertex.point().position()
        if(curPoint not in goodPoints):
            goodPoints.append(curPoint)

    tbn = createTBNmatrix(goodPoints[1], goodPoints[0], goodPoints[2], [0, 0], [1, 0], [0, 1])
    tbn.matrix3Inverse()
    # Relative to point in [0,0] in texture coordinate
    pointRelative = vecSub(pointIO, list(poly.vertices()[1].point().position()))
    pointIOtangentSpace = tbn.mulPoint3ToMatrix3(pointRelative)
    for vert in poly.vertices():
        pointRelative = vecSub(list(vert.point().position()), list(poly.vertices()[1].point().position()))
        pointRelativetbn = tbn.mulPoint3ToMatrix3(pointRelative)
        pointRelativetbn[2] = 0
        listVert.append(tbn.mulPoint3ToMatrix3(pointRelative))

    '''
    OLD CODE:
    
    primNormal=[0, 0, 1]
    if primNormal[0]==0:
        #paralela o coincidente, ya que el vector normal(vector perpendicular al plano)
        #no contiene x, con lo cual significa que el rayo y el plano se estaran moviendo
        #paralelamente. Si la ecuacion da como resultado un numero==otronumero es porque siempre
        #hay punto en comun, por lo tanto, coincidente, si no, son paralelas ya que no hay ningun
        #punto en comun.
        return False

    This is part of point in volume!!!! we project the iopoint into primitive        
    
    somepoint=listVert[0]
    d=-primNormal[0]*somepoint[0]-primNormal[1]*somepoint[1]-primNormal[2]*somepoint[2]
    pointIntersect=[0, 0, 0]
    #solo tendra factor multiplicador 't' la componente x(ya que rayDirection=[1, 0, 0])
    #por tanto la aislamos 'x' para hayar el factor 't'.
    t=(primNormal[1]*pointIO[1]+primNormal[2]*pointIO[2]+d)/-primNormal[0]-pointIO[0]
    #con esto conseguimos simplemente rehusar cuando la interseccion esta detras del rayo.
    if t<0:
        #Intersecta con el rayo contrario al que estamos evaluando(detras del rayo)
        return False
    '''

    '''
    new code
    '''
    pointIntersect = []
    pointIntersect.append(pointIOtangentSpace[0])
    pointIntersect.append(pointIOtangentSpace[1])
    pointIntersect.append(0)
    numVert = len(listVert)
    counter = 0
    # Una vez sabemos que intersecta con el rayo que toca solo tenemos en cuenta las componentes 'y' y 'z',
    # ya que proyectaremos(por ejemplo en x) sobre el plano de las x para poder evaluar
    # si el punto esta dentro del poligono. Proyectamos el punto del centro de la primitiva
    # de la geometria original


    # Pasamos por todas las aristas de la primitiva de la geometria de referencia
    for u in range(numVert):
        point1 = listVert[u % numVert]
        point2 = listVert[(u + 1) % numVert]
        if intersect(point1, point2, pointIntersect):
            counter += 1
    # si interseca un numero impar de veces, significa que el punto esta dentro
    # del poligono
    return counter % 2 != 0

def pointInPoints(pointIO, poly):
    global littleEpsilon
    reload (HouInterface)
    listVert = []
    # Borramos componente que obviamos(la 'x') y proyectamos sobre el plano de las x
    # la primitiva de la geometria de referencia

    '''
    Start Modification 8/6/2011
    Adaptly it to the tangent space knowledge to do a properly point in polygon
    '''
    # Convert to the tangent space of x
    logging.debug("points in point in points" + str(poly))
    logging.debug("pointIO in point in points" + str(pointIO))
    goodPoints = []
    for vertex in poly:
        curPoint = vertex
        if(curPoint not in goodPoints):
            goodPoints.append(curPoint)
    logging.debug("goodPoints in point in points" + str(goodPoints))
    tbn = createTBNmatrix(goodPoints[1], goodPoints[0], goodPoints[2], [0, 0], [1, 0], [0, 1])
    tbn.matrix3Inverse()
    # Relative to point in [0,0] in texture coordinate
    pointRelative = vecSub(pointIO, list(poly[1]))
    pointIOtangentSpace = tbn.mulPoint3ToMatrix3(pointRelative)
    for vert in poly:
        pointRelative = vecSub(list(vert), list(poly[1]))
        pointRelativetbn = tbn.mulPoint3ToMatrix3(pointRelative)
        pointRelativetbn[2] = 0
        listVert.append(tbn.mulPoint3ToMatrix3(pointRelative))

    '''
    OLD CODE:
    
    primNormal=[0, 0, 1]
    if primNormal[0]==0:
        #paralela o coincidente, ya que el vector normal(vector perpendicular al plano)
        #no contiene x, con lo cual significa que el rayo y el plano se estaran moviendo
        #paralelamente. Si la ecuacion da como resultado un numero==otronumero es porque siempre
        #hay punto en comun, por lo tanto, coincidente, si no, son paralelas ya que no hay ningun
        #punto en comun.
        return False

    This is part of point in volume!!!! we project the iopoint into primitive        
    
    somepoint=listVert[0]
    d=-primNormal[0]*somepoint[0]-primNormal[1]*somepoint[1]-primNormal[2]*somepoint[2]
    pointIntersect=[0, 0, 0]
    #solo tendra factor multiplicador 't' la componente x(ya que rayDirection=[1, 0, 0])
    #por tanto la aislamos 'x' para hayar el factor 't'.
    t=(primNormal[1]*pointIO[1]+primNormal[2]*pointIO[2]+d)/-primNormal[0]-pointIO[0]
    #con esto conseguimos simplemente rehusar cuando la interseccion esta detras del rayo.
    if t<0:
        #Intersecta con el rayo contrario al que estamos evaluando(detras del rayo)
        return False
    '''

    '''
    new code
    '''
    pointIntersect = []
    pointIntersect.append(pointIOtangentSpace[0])
    pointIntersect.append(pointIOtangentSpace[1])
    pointIntersect.append(0)
    numVert = len(listVert)
    counter = 0
    # Una vez sabemos que intersecta con el rayo que toca solo tenemos en cuenta las componentes 'y' y 'z',
    # ya que proyectaremos(por ejemplo en x) sobre el plano de las x para poder evaluar
    # si el punto esta dentro del poligono. Proyectamos el punto del centro de la primitiva
    # de la geometria original


    # Pasamos por todas las aristas de la primitiva de la geometria de referencia
    for u in range(numVert):
        point1 = listVert[u % numVert]
        point2 = listVert[(u + 1) % numVert]
        if intersect(point1, point2, pointIntersect):
            counter += 1
    # si interseca un numero impar de veces, significa que el punto esta dentro
    # del poligono
    return counter % 2 != 0

def pointsInPoints(pointsInOut, pointsContainer):
    for pointIO in pointsInOut:
        inPoly = pointInPoints(pointIO, pointsContainer)
        if(not inPoly):
            break
    return inPoly

def pointInEdges(point, edges):
    pointIn = False
    try:
        if(not edges or not point):
            raise Errors.CantBeNoneError('Edges cant be none', 'Function pre-condition')
    except Errors.CantBeNoneError as e:
        print 'Exception ocurred:', e.expr
        return None

    for edge in edges:

        pointIn = pointInSegmentDistance(edge[0], edge[1], point)
        if(pointIn):
            break
    return pointIn

def polygonInPolygon(poly, polyInsideOutside):
    pointOutside = False
    n = 0
    while(not pointOutside and n < len(polyInsideOutside)):
        pointOutside = pointInPoints(polyInsideOutside[n], poly)
        n += 1
    return not pointOutside

def intersect(p1, p2, pIO):
    if pIO[1] > min(p1[1], p2[1]) and pIO[1] <= max(p1[1], p2[1]):
        if pIO[0] <= max(p1[0], p2[0]) and p1[1] != p2[1]:
            interOfx = (pIO[1] - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]) + p1[0]
            return(p1[0] == p2[0] or pIO[0] <= interOfx)
# End functions to work with primitives

# Fucntions to work with volumes
def pointInVolume(referencedGeo, pointIO):
    counter = 0
    global littleEpsilon
    reload (HouInterface)
    if referencedGeo.geometry().boundingBox().contains(pointIO):
        for prim in referencedGeo.geometry().prims():
            intersect = True
            goodRayIntersection = True
            primNormal = list(prim.normal())
            if primNormal[0] == 0:
                # paralela o coincidente, ya que el vector normal(vector perpendicular al plano)
                # no contiene x, con lo cual significa que el rayo y el plano se estaran moviendo
                # paralelamente. Si la ecuacion da como resultado un numero==otronumero es porque siempre
                # hay punto en comun, por lo tanto, coincidente, si no, son paralelas ya que no hay ningun
                # punto en comun.
                intersect = False

            somepoint = prim.vertices()[0].point().position()
            d = -primNormal[0] * somepoint[0] - primNormal[1] * somepoint[1] - primNormal[2] * somepoint[2]

            # solo tendra factor multiplicador 't' la componente x(ya que rayDirection=[1, 0, 0])
            # por tanto la aislamos 'x' para hayar el factor 't'.
            rayVector = [1, 0, 0]
            if(intersect):
                t = (primNormal[0] * pointIO[0] + primNormal[1] * pointIO[1] + primNormal[2] * pointIO[2] + d) / -(primNormal[0] * rayVector[0] + primNormal[1] * rayVector[1] + primNormal[2] * rayVector[2])
                # con esto conseguimos simplemente rehusar cuando la interseccion esta detras del rayo.
                if t < 0:
                    # Intersecta con el rayo contrario al que estamos evaluando(detras del rayo)
                    goodRayIntersection = False

            if(intersect and goodRayIntersection):
                projectedPoint = [pointIO[0] + rayVector[0] * t, pointIO[1] + rayVector[1] * t, pointIO[2] + rayVector[2] * t]
                if pointInPolygon(projectedPoint, prim):
                    counter += 1
    # si intersecta con un numero impar de poligonos significa que el centro
    # de la primitiva que evaluamos esta dentro del volumen('point in poligon' pero aplicado a 3D,
    # es decir, un "point in volume")
    return counter % 2 != 0

def boundingBox(points):
    tempListMin = list(points[0])
    tempListMax = list(points[0])
    for position in points:
        tempListMin[0] = min(tempListMin[0], position[0])
        tempListMin[1] = min(tempListMin[1], position[1])
        tempListMin[2] = min(tempListMin[2], position[2])
        tempListMax[0] = max(tempListMax[0], position[0])
        tempListMax[1] = max(tempListMax[1], position[1])
        tempListMax[2] = max(tempListMax[2], position[2])
    boundingBox = hou.BoundingBox(tempListMin[0], tempListMin[1], tempListMin[2], tempListMax[0], tempListMax[1], tempListMax[2])
    return boundingBox

def test():
    import doctest
    from ExternalClasses import GeoMath
    doctest.testmod(GeoMath, verbose=True)

if __name__ == "__main__":
    test()
