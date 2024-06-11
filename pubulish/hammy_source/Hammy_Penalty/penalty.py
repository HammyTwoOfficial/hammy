from hammy.Hammy_Utils import util, util3
import numpy as np
import math
TOL = 1e-6
     
class Penalty:
    
    def __init__(self, 
                 detection, 
                 objectives,
                 assumptions = [
                    12,     # min_size
                    80,     # min_angle
                    250,    # max_ctyd_area_0
                    250,    # max_ctyd_area_1 
                    3,      # mat_type  
                    0.75,   # t_sda
                    0.4,    # t_ase 
                    0.05    # calibration value of daylight factor   
                            ]
                 ):
        
        self.site_fp = detection.site_data
        self.area_req = detection.area_req
        self.objectives = objectives
        self.mass_data = self.objectives.mass_data
        self.boq = self.mass_data.boq
        self.mass = self.mass_data.massing
        
        self.geometry = self.mass.geo
        self.sample = self.geometry.abs_info

        self.assumptions = assumptions

        # self.objs = objs
        
        self.bldg_fps, self.ctyd_fp = self.geometry.bd_fp
        self.flr_patterns = self.geometry.flr_patterns
        self.ctyd_pattern = self.geometry.cty_pattern
        self.ctyd_form = self.geometry.cty_form
        self.seg_pattern = self.geometry.seg_pattern
        self.max_seg_nr = self.geometry.max_seg_flo_num
        # self.gwp_embed = self.objs[27]
        self.flr_forms = self.calc_flr_forms()
        
        self.calc_penalty_items()
        
        
    def calc_area(self):
        area = 0
        for flr_fps in self.bldg_fps:
            if flr_fps:
                for fp in flr_fps:
                    area += util.calc_fp_area(fp)
                    
        if self.ctyd_pattern:
            ctyd_area = util.calc_fp_area(self.ctyd_fp)
            if self.ctyd_form == 0:
                area += ctyd_area
            else:
                area += ctyd_area * (self.ctyd_pattern + 1)
    
        return area
    
    
    def calc_ctyd_size(self):
        dists_cpt = util.dist_to_poly_sides(self.ctyd_fp)
        dists = [2*d for d in dists_cpt]
        lengths = util.calc_poly_side_lengths(self.ctyd_fp)
        return min(dists + lengths)
    
    
    def calc_ctyd_area(self):
        ctyd_area = util.calc_fp_area(self.ctyd_fp)
        return ctyd_area
    
    
    def calc_flr_forms(self):
        flr_forms = []
        for i, bldg_flr_p in enumerate(self.flr_patterns):
            if self.ctyd_pattern >= i:
                ctyd_flr_p = 1
            else:
                ctyd_flr_p = 0
            flr_form = util3.get_bldg_form_flr(bldg_flr_p, ctyd_flr_p, self.ctyd_form)[0]
            flr_forms.append(flr_form)
        return flr_forms
    
    
    def calc_seg_dist(self):
        for i, f in enumerate(self.flr_forms):
            if f and f in ["H", "T", "II", "U", "U+"]:
                fps = self.bldg_fps[i]
                pts = []
                for fp in fps:
                    pts.extend(fp)
                min_dist = util.calc_min_dists(pts)
                return min_dist

        return np.inf
    
    
    def calc_site_dist(self):
        flr_fps_0 = self.bldg_fps[0]
        is_out = False
        for fp in flr_fps_0:
            segs = util.pts_to_segs(fp)
            for seg in segs:
                if not util.is_line_in_poly(seg, self.site_fp):
                    is_out = True
                    break
            if is_out:
                break
        
        if is_out:
            exceed_dist = []
            for fp in flr_fps_0:
                for pt in fp:
                    dists = util.dist_to_poly_sides(self.site_fp, pt)
                    exceed_dist.append(min(dists))
            return max(exceed_dist)
        
        return 0
    
    
    def calc_min_angle(self):
        flr_fps_0 = self.bldg_fps[0]
        angles = []
        
        for fp in flr_fps_0:
            a_seg = util.calc_poly_angles(fp)
            angles.extend(a_seg)
        
        if self.ctyd_pattern:
            a_ctyd = util.calc_poly_angles(self.ctyd_fp)
            angles.extend(a_ctyd)
        angles = [a for a in angles if not math.isnan(a)]    
        return min(angles)

    def calc_min_seg_pattern(self):
        if max(self.seg_pattern) == 0:
            return 0
        else:
            pa_list = []
            for pa in self.seg_pattern:
                if pa != 0:
                    pa_list.append(pa)
            return min(pa_list)
                    

    @staticmethod
    def p_func(loss, func_type):
        """
        This method provide different types of penalty functions

        Args:
            loss (float): _description_
            constraint (float): _description_
            func_type (str):
                - log -> log(1+x)
                - exp -> e^x
                - sinh -> sinh(x)
                - quad -> x^2 s
                - sqrt -> sqrt(x)
                - linear -> x
        """
        if func_type == "quad":
            fitness = loss ** 2
        elif func_type == "sqrt":
            fitness = np.sqrt(loss)
        elif func_type == "exp":
            fitness = np.exp(loss) - 1
        elif func_type == "log":
            fitness = -np.log(-loss) 
        elif func_type == "sinh":
            fitness = np.sinh(loss)
        else:
            fitness = loss
        return fitness    
            
    
    def calc_design_items(self):
        try:
            self.tot_area = self.calc_area()
        except:
            self.tot_area = self.area_req * 0.9
            
        try:
            self.min_ctyd_size = self.calc_ctyd_size()
        except:
            self.min_ctyd_size = 6
            
        try:
            self.ctyd_area = self.calc_ctyd_area()
        except:
            self.ctyd_area = 150
            
        try:
            self.min_seg_dist = self.calc_seg_dist()
        except:
            self.min_seg_dist = 6
            
        try:
            self.exceed_site_dist = self.calc_site_dist()
        except:
            self.exceed_site_dist = 0
            
        try:
            self.min_angle = self.calc_min_angle()
            if math.isnan(self.min_angle):
                self.min_angle = 60
        except:
            self.min_angle = 60
        
        try:
            self.min_seg_pa = self.calc_min_seg_pattern()
        except:
            self.min_seg_pa = 0
    
    


    def calc_penalty_items(self):
        min_size = self.assumptions[0]
        min_angle = self.assumptions[1]
        max_ctyd_area_0 = self.assumptions[2]
        max_ctyd_area_1 = self.assumptions[3]
        min_mat_type = self.assumptions[4]
        min_sDA = self.assumptions[5]
        max_ASE = self.assumptions[6]
        
        # shape validation 
        if self.objectives.check_valid is False:
            print("None")
            p_shape = 0
            try:
                self.min_angle = self.calc_min_angle()
            except:
                self.min_angle = 30
                
            p_shape = (90 - self.min_angle) / 60
            if math.isnan(p_shape):
                p_shape = 1

            if abs(p_shape) < 0.5:
                p_shape = 0.5 
                
            p_min_area = 0
            p_max_area = 0
            p_site = 0
            p_seg_size = 0
            p_seg_height = 0
            p_angle = 0
            p_ct_size = 0
            p_ct_area = 0
            p_ct_height = 0
            p_ct_form = 0
            p_mat = 0
            
        else:
            self.calc_design_items()
            p_shape = 0


            # area requirement
            if self.tot_area < self.area_req:
                p_min_area = (self.area_req - self.tot_area) / self.area_req
            else:
                p_min_area = 0
            
            if self.tot_area > self.area_req * 1.2:
                p_max_area = (self.tot_area - self.area_req * 1.2) / (self.area_req * 0.4)
            else:
                p_max_area = 0
            
            
             
             
            # exceeding site
            if self.exceed_site_dist > 0:
                p_site = self.exceed_site_dist / 15
            else:
                p_site = 0
            

            
            
            # sharp angle
            if self.min_angle < min_angle:
                p_angle = (min_angle - self.min_angle) / min_angle
            else:
                p_angle = 0
            
            
            
            # seg pattern
            p_seg_height = 0
            for sp in self.seg_pattern:
                if sp and sp < 3:
                    p_seg_height += (3-sp) / 3
                    
            if self.flr_patterns == []:
                p_seg_height = 0
            else:
                p_seg_height /= sum(self.flr_patterns[0])
                
                
                
            
            p_seg_size = 0
            # segment distance
            if self.flr_forms != [] and self.flr_forms[0] == "O":
                if min(self.min_ctyd_size, self.min_seg_dist) < min_size * 0.9:
                    p_seg_size = (min_size * 0.9 - min(self.min_ctyd_size, self.min_seg_dist)) / min_size
            else:
                if self.min_seg_dist < min_size:
                    p_seg_size = (min_size - self.min_seg_dist) / min_size
                else:
                    p_seg_size = 0
                
                
                    
            p_ct_size = 0
            p_ct_area = 0
            p_ct_form = 0
            p_ct_height = 0     
            
            # ctyd factors
            if self.ctyd_pattern:
                
                # ctyd size
                if self.min_ctyd_size < min_size * 0.9:
                    if self.min_seg_pa:
                        p_ct_size = (min_size* 0.9 - self.min_ctyd_size) / min_size* 0.9 * self.min_seg_pa / 4
                    else:
                        p_ct_size = (min_size* 0.9 - self.min_ctyd_size) / min_size* 0.9
                
                
                # just have ctyd, no height or area limit for massive ctyd
                if self.flr_forms == []:
                    if self.ctyd_form == 0:
                        p_ct_height = self.ctyd_pattern / 7
                        p_ct_area = self.ctyd_area / (1200 - max_ctyd_area_0)
                
                    else:
                        p_ct_height = 0
                
                else:
                    # ctyd height should no more than segment height
                    if self.ctyd_pattern > self.max_seg_nr:
                        p_ct_height = (self.ctyd_pattern - self.max_seg_nr) / 5
                    
                    # glass ctyd       
                    if self.ctyd_form == 0:
                        if self.flr_forms[0] in ["I", "L"]:
                            p_ct_form = self.ctyd_area / (1200 - max_ctyd_area_0) * self.min_ctyd_size / (min_size + 3)
                        
                        if self.ctyd_area > max_ctyd_area_0:
                            p_ct_area = (self.ctyd_area - max_ctyd_area_0) / (1200 - max_ctyd_area_0) * self.min_ctyd_size / (min_size + 3) * self.ctyd_pattern / 7
                    
                    
                    # massive ctyd
                    else:
                        if "T" == self.flr_forms[0]:
                            max_ct_height = len(self.flr_forms) - 1 - self.flr_forms[::-1].index("T")
                        elif "H" == self.flr_forms[0]:
                            max_ct_height = len(self.flr_forms) - 1 - self.flr_forms[::-1].index("H")   
                        else:
                            max_ct_height = 3
                        if self.ctyd_pattern > max_ct_height:
                            p_ct_form = (self.ctyd_pattern - max_ct_height) / 4 * self.min_ctyd_size / (min_size + 3)

                        # ctyd area
                        if self.ctyd_area > max_ctyd_area_1:
                            if "T" == self.flr_forms[0] or "H" == self.flr_forms[0]:
                                p_ct_area = 0
                            else:
                                p_ct_area = (self.ctyd_area - max_ctyd_area_1) / (1200 - max_ctyd_area_1) * self.min_ctyd_size / (min_size + 3) * self.ctyd_pattern / 3
            else:
                if self.flr_forms != []:
                    if self.flr_forms[0] in ["O", "U"] and self.ctyd_area > max_ctyd_area_0*5:
                        p_ct_area = (self.ctyd_area - max_ctyd_area_0*5) / max_ctyd_area_0*5
            
            

            # material
            mat_type = self.sample[20]

            flr_q = self.boq["Floor"][0][1]
            ew_q = self.boq["ExWall"][0][1]
            iw_q = self.boq["InWall"][0][1]
            rf_q = self.boq["RoofCeiling"][0][1]
            opak_q = flr_q + ew_q + iw_q + rf_q

            if abs(mat_type - 0) < TOL:
                quantity = flr_q + ew_q + iw_q
            elif abs(mat_type - 1) < TOL:
                quantity = ew_q + iw_q
            elif abs(mat_type - 2) < TOL:
                quantity = iw_q/2

            if mat_type < min_mat_type:
                
                p_mat = (min_mat_type - mat_type) / 3 * quantity / opak_q
            else:
                p_mat = 0

        
        
        
        # daylight penalty
        sda, ase = self.objectives.daylight_objs_arr
        
        if self.ctyd_form == 0 and self.ctyd_pattern:
            daylight_calibr = self.assumptions[-1]
        else:
            daylight_calibr = 0
        
        sda -= daylight_calibr
        ase -= daylight_calibr
        
        if sda < min_sDA:
            p_sda = min_sDA - sda
        else:
            p_sda = 0
        if ase > max_ASE:
            p_ase = ase - max_ASE
        else:
            p_ase = 0
         
        

        # set properties
        self.p_shape = p_shape
        
        # self.p_area = p_area
        self.p_min_area = p_min_area
        self.p_max_area = p_max_area
        
        self.p_site = p_site
        
        # self.p_size = p_size
        self.p_seg_size = p_seg_size
        self.p_ct_size = p_ct_size
        
        self.p_angle = p_angle
        
        # self.p_visual = p_visual
        self.p_sda = p_sda
        self.p_ase = p_ase
        
        self.p_mat = p_mat
        
        self.p_seg_height = p_seg_height
        # self.p_ct = p_ct
        self.p_ct_height = p_ct_height
        self.p_ct_form = p_ct_form
        
        self.p_ct_area = p_ct_area

        self.p_items = [
            self.p_shape,           # [0]
            self.p_min_area,        # [1]
            self.p_max_area,        # [2]
            self.p_site,            # [3]
            self.p_seg_size,        # [4]
            self.p_ct_size,         # [5]
            self.p_angle,           # [6]
            self.p_sda,             # [7]
            self.p_ase,             # [8]
            self.p_mat,             # [9]
            self.p_seg_height,      # [10]
            self.p_ct_height,       # [11]
            self.p_ct_form,         # [12]
            self.p_ct_area          # [13]
        ]
        
        keys = [
            "p_shape",           # [0]
            "p_min_area",        # [1]
            "p_max_area",        # [2]
            "p_site",            # [3]
            "p_seg_size",        # [4]
            "p_ct_size",         # [5]
            "p_angle",           # [6]
            "p_sda",             # [7]
            "p_ase",             # [8]
            "p_mat",             # [9]
            "p_seg_height",      # [10]
            "p_ct_height",       # [11]
            "p_ct_form",         # [12]
            "p_ct_area"          # [13]
        ]
        print("\033[32mPENALTY\033[0m")
        for i,p in zip(keys, self.p_items):
            print(i, p)       

































