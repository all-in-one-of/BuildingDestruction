# -*- coding: utf-8 -*-
import hou #@UnresolvedImport
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

def condition(referencedGeo, primReference):
    allPointsInside = False
    for position in [vertice.point().position() for vertice in primReference.vertices()]:
        counter = 0
        if hou.node(referencedGeo).geometry().boundingBox().contains(position):
            for prim in hou.node(referencedGeo).geometry().prims():
                if rayIntersect(position, prim):
                    counter += 1
        #si intersecta con un numero impar de poligonos significa que el centro
        #de la primitiva que evaluamos esta dentro del volumen('point in poligon' pero aplicado a 3D,
        #es decir, un "point in volume")
        allPointsInside = (counter % 2 != 0)
        if not allPointsInside: break
    return allPointsInside

def rayIntersect(pointIO, poly):
    listVert = []
    #Borramos componente que obviamos(la 'x') y proyectamos sobre el plano de las x
    #la primitiva de la geometria de referencia
    for vert in poly.vertices():
        listVert.append([vert.point().position()[1], vert.point().position()[2]])
    primNormal = poly.normal()
    if primNormal[0] == 0:
        #paralela o coincidente, ya que el vector normal(vector perpendicular al plano)
        #no contiene x, con lo cual significa que el rayo y el plano se estaran moviendo
        #paralelamente. Si la ecuacion da como resultado un numero==otronumero es porque siempre
        #hay punto en comun, por lo tanto, coincidente, si no, son paralelas ya que no hay ningun
        #punto en comun.
        return False
    somepoint = poly.vertices()[0].point().position()
    d = -primNormal[0] * somepoint[0] - primNormal[1] * somepoint[1] - primNormal[2] * somepoint[2]
    pointIntersect = [0, 0, 0]
    #solo tendra factor multiplicador 't' la componente x(ya que rayDirection=[1, 0, 0])
    #por tanto la aislamos 'x' para hayar el factor 't'.
    t = (primNormal[1] * pointIO[1] + primNormal[2] * pointIO[2] + d) / -primNormal[0] - pointIO[0]
    #con esto conseguimos simplemente rehusar cuando la interseccion esta detras del rayo.
    if t < 0:
        #Intersecta con el rayo contrario al que estamos evaluando(detras del rayo)
        return False
    #Una vez sabemos que intersecta con el rayo que toca solo tenemos en cuenta las componentes 'y' y 'z',
    #ya que proyectaremos(por ejemplo en x) sobre el plano de las x para poder evaluar
    #si el punto esta dentro del poligono. Proyectamos el punto del centro de la primitiva
    #de la geometria original
    pointIntersect[0] = pointIO[1]
    pointIntersect[1] = pointIO[2]
    numVert = len(listVert)
    counter = 0
    #Pasamos por todas las aristas de la primitiva de la geometria de referencia       
    for u in range(numVert):
        point1 = listVert[u % numVert]
        point2 = listVert[(u + 1) % numVert]
        if insideOutside(point1, point2, pointIntersect):
            counter += 1
    #si interseca un numero impar de veces, significa que el punto esta dentro
    #del poligono
    return counter % 2 != 0

def insideOutside(p1, p2, pIO):
    #Ahora el eje de las 'y' pasa a ser el de las 'x' y el eje 'z' el de las 'y'
    #"lanzamos" un rayo en el eje de las 'x'(que es el de las 'y' en realidad) y
    #miramos si el punto pIO esta entre p1 y p2 y si la interseccion se encuentra antes('y original' mas peque�a)
    #de pIO o no.
    if pIO[1] > min(p1[1], p2[1]) and pIO[1] <= max(p1[1], p2[1]):
        if pIO[0] <= max(p1[0], p2[0]) and p1[1] != p2[1]:
            interOfx = (pIO[1] - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]) + p1[0]
            return(p1[0] == p2[0] or pIO[0] <= interOfx)
