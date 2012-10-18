'''
Created on Oct 17, 2011

@author: carlos
'''
import CreateTBN
import Errors
from ExternalClasses import GeoMath
from ExternalClasses import HouInterface
import logging
littleEpsilon = 0.002
class BoundingBox(object):
    def __init__(self, points):
        pass
    '''
    def contain_point_2D(self, point):
        pass
    
    def contain_bounding_box_2D(self, bounding_box):
        pass
    '''
class BoundingBox2D(BoundingBox):
    '''
        #=======================================================================
        # Simple containing 2D
        #=======================================================================
        >>> points1=[[0,0,0],[1,0,0],[1,1,0],[0,1,0]]
        >>> points2=[[0.1,0.1,0],[0.9,0.1,0],[0.9,0.9,0],[0.1,0.9,0]]
        >>> b1=BoundingBox2D(points1)
        >>> b2=BoundingBox2D(points2)
        
        >>> b1.contain_bounding_box_2D(b2)
        True
        
        >>> b2.contain_bounding_box_2D(b1)
        False
        
        #=======================================================================
        # Complex containing 2D
        #=======================================================================
        >>> points1=[[0,0,0],[1,0,0],[1,1,0],[0,1,0]]
        >>> points2=[[-0.1,-0.1,0],[-0.9,-0.1,0],[-0.9,-0.9,0],[-0.1,-0.9,0]]
        >>> b1=BoundingBox2D(points1)
        >>> b2=BoundingBox2D(points2)
        
        >>> b1.contain_bounding_box_2D(b2)
        False
        
        >>> b2.contain_bounding_box_2D(b1)
        False
        
        >>> points1=[[0,0,0],[1,0,0],[1,1,0],[0,1,0]]
        >>> points2=[[0.1,0.1,0],[0.9,0.1,0],[-0.9,-0.9,0],[-0.1,-0.9,0]]
        >>> b1=BoundingBox2D(points1)
        >>> b2=BoundingBox2D(points2)
        
        >>> b1.contain_bounding_box_2D(b2)
        False
        
        >>> b2.contain_bounding_box_2D(b1)
        False
        
        #=======================================================================
        # Complex intersection 2D
        #=======================================================================
        >>> points1=[[0,0,0],[1,0,0],[1,1,0],[0,1,0]]
        >>> points2=[[0.1,0.1,0],[0.9,0.1,0],[0.9,0.9,0],[0.1,0.9,0]]
        >>> b1=BoundingBox2D(points1)
        >>> b2=BoundingBox2D(points2)
        
        >>> b1.intersect_bounding_box_2D(b2)
        False
        
        >>> b2.intersect_bounding_box_2D(b1)
        False
        
        >>> points1=[[0,0,0],[1,0,0],[1,1,0],[0,1,0]]
        >>> points2=[[-0.1,-0.1,0],[-0.9,-0.1,0],[-0.9,-0.9,0],[-0.1,-0.9,0]]
        >>> b1=BoundingBox2D(points1)
        >>> b2=BoundingBox2D(points2)
        
        >>> b1.intersect_bounding_box_2D(b2)
        False
        
        >>> b2.intersect_bounding_box_2D(b1)
        False
        
        >>> points1=[[0,0,0],[1,0,0],[1,1,0],[0,1,0]]
        >>> points2=[[0.1,0.1,0],[-0.9,-0.1,0],[-0.9,-0.9,0],[-0.1,-0.9,0]]
        >>> b1=BoundingBox2D(points1)
        >>> b2=BoundingBox2D(points2)
        
        >>> b1.intersect_bounding_box_2D(b2)
        True
        
        >>> b2.intersect_bounding_box_2D(b1)
        True
        
        #=======================================================================
        # Simple containing 3D
        #=======================================================================
        #=======================================================================
        # >>> points1=[[0,0,0],[1,0,0],[1,1,0],[0,1,0]]
        # >>> points2=[[0.1,0.1,0],[0.9,0.1,0],[0.9,0.9,0],[0.1,0.9,0]]
        # >>> b1=BoundingBox2D(points1)
        # >>> b2=BoundingBox2D(points2)
        # 
        # >>> b1.contain_bounding_box_3D(b2)
        # True
        # 
        # >>> b2.contain_bounding_box_3D(b1)
        # False
        # 
        # >>> points1=[[1,1,0],[1,1,1],[1,2,1],[1,2,0]]
        # >>> points2=[[1.1,1.1,0],[1.1,1.1,0.9],[1.1,1.9,0.9],[1,1.9,0]]
        # >>> b1=BoundingBox2D(points1)
        # >>> b2=BoundingBox2D(points2)
        # 
        # >>> b1.contain_bounding_box_3D(b2)
        # True
        # 
        # >>> b2.contain_bounding_box_3D(b1)
        # False
        #=======================================================================
    '''
    
    def __init__(self, points, prim=None, dict_of_min_max={}):
        reload (GeoMath)
        reload (CreateTBN)
        self.points_object_space = points
        self.points_tangent_space = []
        self.rectangle_tangent_space = []
        self.rectangle_object_space = []
        self.edges_object_space = []
        self.edges_tangent_space = []
        if('x_min' in dict_of_min_max):
            self.x_min = dict_of_min_max['x_min']
            self.x_max = dict_of_min_max['x_max']
            self.y_min = dict_of_min_max['y_min']
            self.y_max = dict_of_min_max['y_max']
            
        if('x_min_tangent' in dict_of_min_max):
            self.x_min_tangent = dict_of_min_max['x_min_tangent']
            self.x_max_tangent = dict_of_min_max['x_max_tangent']
            self.y_min_tangent = dict_of_min_max['y_min_tangent']
            self.y_max_tangent = dict_of_min_max['y_max_tangent']
            
        self.prim = prim
        self.tbn_class = None
        self.to_display_intersections = []
        self.vector_size_object_space = []
        self.vector_size_tangent_space = []
        self.create_3D_to_2D_rectangle(prim)

    def get_vector_size_object_space(self):
        return self.__vector_size_object_space


    def set_vector_size_object_space(self, value):
        self.__vector_size_object_space = value


    def del_vector_size_object_space(self):
        del self.__vector_size_object_space


    def get_vector_size_tangent_space(self):
        return self.__vector_size_tangent_space


    def set_vector_size_tangent_space(self, value):
        self.__vector_size_tangent_space = value


    def del_vector_size_tangent_space(self):
        del self.__vector_size_tangent_space

    def get_edges_object_space(self):
        return self.__edges_object_space


    def get_edges_tangent_space(self):
        return self.__edges_tangent_space


    def set_edges_object_space(self, value):
        self.__edges_object_space = value


    def set_edges_tangent_space(self, value):
        self.__edges_tangent_space = value


    def del_edges_object_space(self):
        del self.__edges_object_space


    def del_edges_tangent_space(self):
        del self.__edges_tangent_space


    def get_rectangle_tangent_space(self):
        return self.__rectangle_tangent_space


    def get_rectangle_object_space(self):
        return self.__rectangle_object_space


    def set_rectangle_tangent_space(self, value):
        self.__rectangle_tangent_space = value


    def set_rectangle_object_space(self, value):
        self.__rectangle_object_space = value


    def del_rectangle_tangent_space(self):
        del self.__rectangle_tangent_space


    def del_rectangle_object_space(self):
        del self.__rectangle_object_space


    def get_x_min_tangent(self):
        return self.__x_min_tangent


    def get_x_max_tangent(self):
        return self.__x_max_tangent


    def get_y_min_tangent(self):
        return self.__y_min_tangent


    def get_y_max_tangent(self):
        return self.__y_max_tangent


    def set_x_min_tangent(self, value):
        self.__x_min_tangent = value


    def set_x_max_tangent(self, value):
        self.__x_max_tangent = value


    def set_y_min_tangent(self, value):
        self.__y_min_tangent = value


    def set_y_max_tangent(self, value):
        self.__y_max_tangent = value


    def del_x_min_tangent(self):
        del self.__x_min_tangent


    def del_x_max_tangent(self):
        del self.__x_max_tangent


    def del_y_min_tangent(self):
        del self.__y_min_tangent


    def del_y_max_tangent(self):
        del self.__y_max_tangent


    def get_display_intersections(self):
        return self.__display_intersections


    def set_display_intersections(self, value):
        self.__display_intersections = value


    def del_display_intersections(self):
        del self.__display_intersections


    def get_tbn_class(self):
        return self.__tbn_class


    def set_tbn_class(self, value):
        self.__tbn_class = value


    def del_tbn_class(self):
        del self.__tbn_class


    def get_points_tangent_space(self):
        return self.__points_tangent_space


    def set_points_tangent_space(self, value):
        self.__points_tangent_space = value


    def del_points_tangent_space(self):
        del self.__points_tangent_space


    def get_prim(self):
        return self.__prim


    def set_prim(self, value):
        self.__prim = value


    def del_prim(self):
        del self.__prim
        
    def get_x_min(self):
        return self.__x_min


    def get_x_max(self):
        return self.__x_max


    def get_y_min(self):
        return self.__y_min


    def get_y_max(self):
        return self.__y_max


    def get_points_object_space(self):
        return self.__points_object_space


    def set_x_min(self, value):
        self.__x_min = value


    def set_x_max(self, value):
        self.__x_max = value


    def set_y_min(self, value):
        self.__y_min = value


    def set_y_max(self, value):
        self.__y_max = value


    def set_points_object_space(self, value):
        self.__points_object_space = value


    def del_x_min(self):
        del self.__x_min


    def del_x_max(self):
        del self.__x_max


    def del_y_min(self):
        del self.__y_min


    def del_y_max(self):
        del self.__y_max


    def del_points_object_space(self):
        del self.__points_object_space

        
    def create_rectangle(self, type_points):
        
        if(type_points == 'tangent'):
            return [[self.get_x_min_tangent(), self.get_y_min_tangent(), 0],
                     [self.get_x_max_tangent(), self.get_y_min_tangent(), 0],
                      [self.get_x_max_tangent(), self.get_y_max_tangent(), 0],
                       [self.get_x_min_tangent(), self.get_y_max_tangent(), 0]]
        
        if(type_points == 'object'):
            return [[self.get_x_min(), self.get_y_min(), 0],
                     [self.get_x_max(), self.get_y_min(), 0],
                      [self.get_x_max(), self.get_y_max(), 0],
                       [self.get_x_min(), self.get_y_max(), 0]]


    def calculate_bounding_box_tangent_space(self):
        #Calculate bounding box in tangent space
        points_tangent_space = self.get_points_tangent_space()
        self.x_min_tangent = points_tangent_space[0][0]
        self.x_max_tangent = points_tangent_space[0][0]
        self.y_min_tangent = points_tangent_space[0][1]
        self.y_max_tangent = points_tangent_space[0][1]
        try:
            if(not(self.x_max_tangent > 0 and self.y_max_tangent > 0 and
                self.x_min_tangent > 0 and self.y_min_tangent > 0)):
                raise Errors.NegativeValueError(
                                            'Size cant be negtive',
                                             'We need a positive size to do a ' 
                                             'correct management of the size '
                                             'after in other functions')
        except Errors.NegativeValueError as e:
            Errors.Error.display_exception(e)
            #MAYFIX:Non negative values?
            #exit()
        for point in points_tangent_space:
            self.x_min_tangent = min(self.x_min_tangent, point[0])
            self.y_min_tangent = min(self.y_min_tangent, point[1])
            self.x_max_tangent = max(self.x_max_tangent, point[0])
            self.y_max_tangent = max(self.y_max_tangent, point[1])
            
        bounding_box_space_tangent_size = GeoMath.vecSub(
                        [self.x_max_tangent, self.y_max_tangent, 0],
                        [self.x_min_tangent, self.y_min_tangent, 0])
        
        self.set_vector_size_tangent_space(bounding_box_space_tangent_size)

    def create_3D_to_2D_rectangle(self, prim):
        try:
            if(not prim):
                raise Errors.CantBeNoneError('Prim cant be none', 'We need a prim to calculate tbn some steps after')
        except Errors.CantBeNoneError as e:
            Errors.Error.display_exception(e)
            exit()
        tbn_class = CreateTBN.CreateTBN(prim)
        tbn_class.do(scale=True)
        tbn_matrix = tbn_class.get_tbn()
        tbn_inverse_matrix = tbn_class.get_tbn_inverse()
        temporary_list = []
        for point in self.get_points_object_space():
            point_relative = GeoMath.vecSub(point, tbn_class.get_point_which_is_relative())
            point_tangent_space = tbn_inverse_matrix.mulPoint3ToMatrix3(point_relative)
            temporary_list.append(point_tangent_space)
            
        self.set_points_tangent_space(temporary_list)
        self.calculate_bounding_box_tangent_space()
        #=======================================================================
        # Tranform to object space
        #=======================================================================
        rectangle_tangent_space = self.create_rectangle('tangent')
        rectangle_object_space = []
        for point_tangent_space in rectangle_tangent_space:
            point_object_space_relative = tbn_matrix.mulPoint3ToMatrix3(point_tangent_space)
            point_object_space = GeoMath.vecPlus(point_object_space_relative, tbn_class.get_point_which_is_relative())
            rectangle_object_space.append(point_object_space)
            
        self.set_rectangle_object_space(rectangle_object_space)
        bounding_box_object_space_size = GeoMath.vecSub(rectangle_object_space[2],
                                                       rectangle_object_space[0])
        self.set_vector_size_object_space(bounding_box_object_space_size)
        self.set_rectangle_tangent_space(rectangle_tangent_space)
        self.set_edges_object_space(GeoMath.getEdgesFromPoints(rectangle_object_space))
        self.set_edges_tangent_space(GeoMath.getEdgesFromPoints(rectangle_tangent_space))
        self.tbn_class = tbn_class
            
    def contain_point_2D(self, point):
        return GeoMath.pointInPoints(point, self.get_points_object_space())
        
    def intersect_edge_2D(self, edge):
        intersection = GeoMath.getIntersectionsBetweenEdges2D(self.get_edges_object_space(), [edge], 1)
        return intersection
    
    def contain_bounding_box_2D(self, bounding_box):
        '''
        Eficient method, use this.
        @param bounding_box:
        @type bounding_box:
        '''
        contain_all_points = True
        for point_param_box in bounding_box.get_points_object_space():
            contain_all_points = self.contain_point_2D(point_param_box)
            if(not contain_all_points):
                break
        return contain_all_points
    
    def intersect_bounding_box_2D(self, bounding_box, DISPLAY=False):
        intersection = GeoMath.getIntersectionsBetweenEdges2D(self.get_edges_object_space(), bounding_box.get_edges_object_edges(), 1)
        if(DISPLAY):
            self.to_display_intersections.append(intersection)
        return intersection != []
    
    def intersect_bounding_box_without_limits_2D(self, bounding_box, DISPLAY=False):
        intersection = GeoMath.getIntersectionBetweenEdgesWithoutLimits2D(self.get_edges_object_space(), bounding_box.get_edges_object_edges(), 1)
        if(DISPLAY):
            self.to_display_intersections.append(intersection)
        return intersection
    
    def intersect_bounding_box_with_limits_2D(self, bounding_box, DISPLAY=False):
        intersection = GeoMath.getIntersectionBetweenEdgesWithoutLimits2D(self.get_edges_object_space(), bounding_box.get_edges_object_edges(), 1)
        intersection_bool = intersection or GeoMath.getEdgesBetweenEdges(self.get_points_object_space(), bounding_box.get_points_object_space(), 1)
        if(DISPLAY):
            self.to_display_intersections.append(intersection)
        return intersection_bool
    
    def contain_point_3D(self, point):
        inside = None
        if(not self.get_points_tangent_space()):
            self.create_3D_to_2D_rectangle(self.get_prim())
            inside = GeoMath.pointInPoints(point, self.get_points_tangent_space())
        return inside
        
    def intersect_edge_3D(self, edge):
        intersection = GeoMath.getFalseIntersectionsBetweenEdges3D(self.get_edges_tangent_space(), edge, self.get_prim(), 1)
        return intersection
    
    def contain_bounding_box_3D(self, bounding_box):
        try:
            if(not self.get_prim()):
                raise Errors.CantBeNoneError('Prim cant be none', 'We need a prim to calculate tbn some steps after')
        except Errors.CantBeNoneError as e:
            Errors.Error.display_exception(e)
            exit()
        
        inside = True
        if(not self.get_rectangle_tangent_space()):
            self.convert_3D_to_2D(self.get_prim())
        this_point_relative = self.get_tbn_class().get_point_which_is_relative()
        this_tbn_inverse_matrix = self.get_tbn_class().get_tbn_inverse()
        param_bounding_box_points_in_this_tangent_space = []
        for point in bounding_box.get_points_object_space():
            point_relative = GeoMath.vecSub(point, this_point_relative)
            point_tangent_space = this_tbn_inverse_matrix.mulPoint3ToMatrix3(point_relative)
            param_bounding_box_points_in_this_tangent_space.append(list(point_tangent_space))
            
        for point in param_bounding_box_points_in_this_tangent_space:
            logging.debug("Rectangle tangent space" + str(self.get_rectangle_tangent_space()))
            inside = GeoMath.pointInPoints(point, self.get_rectangle_tangent_space())
            if(not inside):
                break
        return inside
        
    def intersect_bounding_box_3D(self, bounding_box, DISPLAY=False):
        try:
            if(not self.get_prim()):
                raise Errors.CantBeNoneError('Prim cant be none', 'We need a prim to calculate tbn some steps after')
        except Errors.CantBeNoneError as e:
            Errors.Error.display_exception(e)
            exit()
        
        if(not self.get_points_tangent_space()):
            self.create_3D_to_2D_rectangle(self.get_prim())
        this_point_relative = self.get_tbn_class().get_point_which_is_relative()
        this_tbn_inverse_matrix = self.get_tbn_class().get_tbn_inverse()
        param_bounding_box_points_in_this_tangent_space = []
        for point in bounding_box.get_rectangle_object_space():
            point_relative = GeoMath.vecSub(point, this_point_relative)
            this_tbn_inverse_matrix.printAttributes()
            point_tangent_space = this_tbn_inverse_matrix.mulPoint3ToMatrix3(point_relative)
            param_bounding_box_points_in_this_tangent_space.append(point_tangent_space)
        intersections = GeoMath.getIntersectionsBetweenEdges2D(GeoMath.getEdgesFromPoints(self.get_rectangle_tangent_space()), GeoMath.getEdgesFromPoints(param_bounding_box_points_in_this_tangent_space))
        if(DISPLAY):
            for intersection in intersections:
                this_tbn_matrix = self.get_tbn_class().get_tbn()
                point_object_space = this_tbn_matrix.mulPoint3ToMatrix3(intersection)
                point_absolute = GeoMath.vecPlus(point_object_space, this_point_relative)
                self.to_display_intersections.append(point_absolute)
            self.display_intersections()
        return intersections

    def intersect_bounding_box_without_limits_3D(self, bounding_box, DISPLAY=False):
        global littleEpsilon
        try:
            if(not self.get_prim()):
                raise Errors.CantBeNoneError('Prim cant be none', 'We need a prim to calculate tbn some steps after')
        except Errors.CantBeNoneError as e:
            Errors.Error.display_exception(e)
            exit()
        
        if(not self.get_points_tangent_space()):
            self.convert_3D_to_2D(self.get_prim())
        this_point_relative = self.get_tbn_class().get_point_which_is_relative()
        this_tbn_inverse_matrix = self.get_tbn_class().get_tbn_inverse()
        param_bounding_box_points_in_this_tangent_space = []
        for point in bounding_box.get_rectangle_object_space():
            point_relative = GeoMath.vecSub(point, this_point_relative)
            point_tangent_space = this_tbn_inverse_matrix.mulPoint3ToMatrix3(point_relative)
            param_bounding_box_points_in_this_tangent_space.append(point_tangent_space)
        intersections = GeoMath.getIntersectionsBetweenEdges2D(self.get_edges_tangent_space(), \
                       GeoMath.getEdgesFromPoints(param_bounding_box_points_in_this_tangent_space))
        if (intersections):
            #===============================================================
            # Check if the limits are touching and if it are touching it, 
            # check if the intersection is in there. If it is in there,
            # the intersection lie in the limit, so we dont consider an
            # intersection
            #===============================================================
            edges_shared_between_bounding_boxes = \
            GeoMath.getEdgesBetweenEdges(self.get_edges_tangent_space(), \
            GeoMath.getEdgesFromPoints(param_bounding_box_points_in_this_tangent_space))
            inside = False
            print "Edges shared between"
            print edges_shared_between_bounding_boxes
            for intersection in intersections:
                inside = GeoMath.pointInEdges(intersection, edges_shared_between_bounding_boxes)
                if(not inside):
                    break
            #===============================================================
            # If all intersections lie in the edges shared between bounding
            # boxes we discart its
            #===============================================================
            if(inside):
                intersections = []
            else:
                #check if intersections are in the corner, because we consider corner as limit
                shared_points_between_bounding_boxes = GeoMath.getSharedPoints(self.get_rectangle_tangent_space(), param_bounding_box_points_in_this_tangent_space)                              
                #If all intersections lie in the corner we doen't consider intersections as intersections
                true_intersections = list(intersections)
                for intersection in intersections:
                    for corner in shared_points_between_bounding_boxes:
                        if(GeoMath.vecModul(GeoMath.vecSub(corner, intersection)) <= littleEpsilon):
                            true_intersections.remove(intersection)
                            break
                intersections = true_intersections
                
        if(DISPLAY):
            for intersection in intersections:
                this_tbn_matrix = self.get_tbn_class().get_tbn()
                point_object_space = this_tbn_matrix.mulPoint3ToMatrix3(intersection)
                point_absolute = GeoMath.vecPlus(point_object_space, this_point_relative)
                self.to_display_intersections.append(point_absolute)
            self.display_intersections()
        return intersections
        
    def intersect_bounding_box_with_limits_3D(self, bounding_box, DISPLAY=False):
        try:
            if(not self.get_prim()):
                raise Errors.CantBeNoneError('Prim cant be none', 'We need a prim to calculate tbn some steps after')
        except Errors.CantBeNoneError as e:
            Errors.Error.display_exception(e)
            exit()
        
        if(not self.get_points_tangent_space()):
            self.convert_3D_to_2D(self.get_prim())
        this_point_relative = self.get_tbn_class().get_point_which_is_relative()
        this_tbn_inverse_matrix = self.get_tbn_class().get_tbn_inverse()
        param_bounding_box_points_in_this_tangent_space = []
        for point in bounding_box.get_rectangle_object_space():
            point_relative = GeoMath.vecSub(point, this_point_relative)
            point_tangent_space = this_tbn_inverse_matrix.mulPoint3ToMatrix3(point_relative)
            param_bounding_box_points_in_this_tangent_space.append(point_tangent_space)
        intersections = GeoMath.getIntersectionsBetweenEdges2D(self.get_edges_tangent_space(), \
                       GeoMath.getEdgesFromPoints(param_bounding_box_points_in_this_tangent_space))
        
        #=======================================================================
        # work in object space because we only has to know if the bounding boxes
        # share some edge between
        #=======================================================================
        edges_shared_between_bounding_boxes = \
        GeoMath.getEdgesBetweenEdges(self.get_edges_tangent_space(), \
        GeoMath.getEdgesFromPoints(param_bounding_box_points_in_this_tangent_space))
            
        if(DISPLAY):
            for intersection in intersections:
                this_tbn_matrix = self.get_tbn_class().get_tbn()
                point_object_space = this_tbn_matrix.mulPoint3ToMatrix3(intersection)
                point_absolute = GeoMath.vecPlus(point_object_space, this_point_relative)
                self.to_display_intersections.append(point_absolute)
            self.display_intersections()
        return intersections, edges_shared_between_bounding_boxes

    #===========================================================================
    # Display some help to the user    
    #===========================================================================
    def display_bounding_box_object_space(self):
        hi = HouInterface.HouInterface()
        hi.showCurve(self.get_rectangle_object_space(), "bounding_box", True)
        
    def display_bounding_box_tangent_space(self):
        hi = HouInterface.HouInterface()
        hi.showCurve(self.get_rectangle_tangent_space(), "bounding_box", True)
        
    def display_intersections(self):
        hi = HouInterface.HouInterface()
        for intersection in self.get_display_intersections():
            hi.showPoint(point=intersection, name="intersection")
            
    if __name__ == "__main__":
        import doctest
        doctest.testmod()
    
    x_min = property(get_x_min, set_x_min, del_x_min, "x_min's docstring")
    x_max = property(get_x_max, set_x_max, del_x_max, "x_max's docstring")
    y_min = property(get_y_min, set_y_min, del_y_min, "y_min's docstring")
    y_max = property(get_y_max, set_y_max, del_y_max, "y_max's docstring")
    points_object_space = property(get_points_object_space, set_points_object_space, del_points_object_space, "points's docstring")
    prim = property(get_prim, set_prim, del_prim, "prim's docstring")
    points_tangent_space = property(get_points_tangent_space, set_points_tangent_space, del_points_tangent_space, "points_tangent_space's docstring")
    tbn_class = property(get_tbn_class, set_tbn_class, del_tbn_class, "tbn_class's docstring")
    to_display_intersections = property(get_display_intersections, set_display_intersections, del_display_intersections, "to_display_intersections's docstring")
    x_min_tangent = property(get_x_min_tangent, set_x_min_tangent, del_x_min_tangent, "x_min_tangent's docstring")
    x_max_tangent = property(get_x_max_tangent, set_x_max_tangent, del_x_max_tangent, "x_max_tangent's docstring")
    y_min_tangent = property(get_y_min_tangent, set_y_min_tangent, del_y_min_tangent, "y_min_tangent's docstring")
    y_max_tangent = property(get_y_max_tangent, set_y_max_tangent, del_y_max_tangent, "y_max_tangent's docstring")
    rectangle_tangent_space = property(get_rectangle_tangent_space, set_rectangle_tangent_space, del_rectangle_tangent_space, "rectangle_tangent_space's docstring")
    rectangle_object_space = property(get_rectangle_object_space, set_rectangle_object_space, del_rectangle_object_space, "rectangle_object_space's docstring")
    edges_object_space = property(get_edges_object_space, set_edges_object_space, del_edges_object_space, "edges_object_space's docstring")
    edges_tangent_space = property(get_edges_tangent_space, set_edges_tangent_space, del_edges_tangent_space, "edges_tangent_space's docstring")
    vector_size_tangent_space = property(get_vector_size_tangent_space, set_vector_size_tangent_space, del_vector_size_tangent_space, "vector_size_tangent_space's docstring")
    vector_size_object_space = property(get_vector_size_object_space, set_vector_size_object_space, del_vector_size_object_space, "vector_size_object_space's docstring")

def test():
    import doctest
    doctest.testmod(verbose=True)
