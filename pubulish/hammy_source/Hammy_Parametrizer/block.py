from .face import Face
import numpy as np
from hammy.Hammy_Utils import util



class Block:
    def __init__(self, fp_pts, isBldg = True):
        self.fp_pts = fp_pts
        self.fp_segs = util.pts_to_segs(fp_pts)
        self.isBldg = isBldg
        
        self.bldg_id = None
        self.flr_id = None
        self.blk_id = None
        self.blk_name = None
        self.height = None
        self.z_flr = None
        self.z_rf = None  
        self.win_ratios = None 
        self.ctyd_form = None
        
        self.volume = None
        
        self.has_hole = False
        self.hole_pts = None
        self.hole_segs = None
        
        self.ew = []
        self.iw = []
        self.aw = []
        
        self.erf = []
        self.irf = []
        self.arf = []
        
        self.eflr = []
        self.iflr = []
        self.aflr = []
        

    def make_blk_name(self):
        blk_type = "BldgBlk" if self.isBldg else "CtydBlk"
        blk_name = blk_type + "_" + str(self.flr_id) + str(self.blk_id)
        return blk_name
    
    
    def calc_volume(self):
        area = 0
        for f in self.eflr + self.iflr + self.aflr:
            area += f.calc_face_area()
        volume = area * self.height
        return volume