from hammy.Hammy_Utils import util
import numpy as np


class Face:
    
    def __init__(self, face_pts, face_part, bc):
        self.face_pts = face_pts
        self.face_part = face_part
        self.bc = bc
        
        self.is_donut = False
        self.hole_pts = None
        self.vert_pts = None
        
        self.face_type = self.make_face_type()
        self.origin, self.vector_n, self.vector_x = self.make_plane() 
        self.face_ori = self.get_orientation() 
        
        self.neighbour_face = None
          
        self.face_area = None
        self.flr_id = None
        self.face_name = None

        self.is_glas = False
        self.win = None
        
        self.constr = None

    def make_face_type(self):
        face_type = "AirBoundary" if self.bc == 0 else self.face_part
        return face_type

    
    def make_plane(self):
        """
            - origin
            - n
            - x
        """
        if self.face_part == "Wall":
            n, x = util.make_face_vectors(self.face_pts)
            origin = self.face_pts[1]
        elif self.face_part == "RoofCeiling":
            n = [0.0, 0.0, 1.0]
            x = [1.0, 0.0, 0.0]
            origin = self.face_pts[1]
        else:
            n = [0.0, 0.0, -1.0]
            x = [1.0, 0.0, 0.0]
            origin = self.face_pts[2]
            
        return origin, n, x
    
    def calc_face_area(self):
        if self.face_part == "Wall":
            p1 = np.asarray(self.face_pts[1])
            p2 = np.asarray(self.face_pts[2])
            l = np.linalg.norm(p2 - p1)
            h = self.face_pts[0][2] - self.face_pts[1][2]
            area = l * h
        else:
            if self.hole_pts:
                area = util.calc_fp_area(self.face_pts) - util.calc_fp_area(self.hole_pts)
            else:
                area = util.calc_fp_area(self.face_pts)
        return area
            
    
    def get_orientation(self):
        """
        Return:
            0: South
            1: North 
            2: West/ East 
        """
        if self.vector_n[1] < 0:
            sn = 0
            win_ori = 0
            
        elif self.vector_n[1] == 0:
            sn = 1
            win_ori = 0
        else:
            sn = 1
            win_ori = 1
            
        if self.vector_n[0] < 0:
            ew = 0
        else:
            ew = 1
            
        return win_ori, [sn, ew]

    
    
    def make_window(self, win_ratio, height):
        
        if self.face_part == "Wall" and self.bc == 2:
            a = self.face_pts[0]
            d = self.face_pts[-1]
            dz = win_ratio * height
            z = a[2] - dz
            zl = a[2] - dz * 0.95
            zu = a[2] - dz * 0.05
            b = a[:2] + [z]
            c = d[:2] + [z]          
            # b = a[:2] + [zl]
            # c = d[:2] + [zl]
            # a = a[:2] + [zu]
            # d = d[:2] + [zu]
            
            win_pts = [a, b, c, d]
            win = Face(win_pts, self.face_part, 2)
            return win
        
        elif self.face_part == "RoofCeiling" and self.bc == 2:
            win_pts = util.scale_polygon(self.face_pts, win_ratio)
            win = Face(win_pts, self.face_part, 2)
            return win
        
        else:
            return None   
    
    
