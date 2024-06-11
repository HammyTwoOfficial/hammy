from .block import Block
from .face import Face
from hammy.Hammy_Utils import util
import numpy as np
# from src.Hammy_Generator import Building
TOL = 1e-6
class Massing:

    
    def __init__(self, iGeometry):
        """ 
        This method is to merge all massing blocks into a building massing.

        Args:
            iGeometry (obj): 
                bldg_id (int),
                height (float),  
                bldg_pattern (list(list)), -> counterclockwise, [S, E, N, W]
                bldg_fps (list), -> counterclockwise, list per floor
                ctyd_fp (list), -> counterclockwise, one floor
                max_flr_nr (int)
                
            iVar (list): [
                depths (list): [0], -> counterclockwise, (4,)
                ctyd_pattern (int): [1]
                ctyd_form (int): [2], -> {0, 1} (indoor interial wall / massive)
                win_ratio_s (float): [3],
                win_ratio_n (float): [4],
            ]
        """
        
        self.geo = iGeometry
        self.bldg_id = self.geo.bldg_id
        self.bldg_name = "Bldg_" + str(self.bldg_id)
        self.flr_height = self.geo.flr_height
        self.bldg_pattern = self.geo.flr_patterns
        self.bldg_fps, self.ctyd_fp = self.geo.bd_fp
        self.max_flr_nr = self.geo.max_flo_num

        self.depths = [self.geo.abs_info[8], self.geo.abs_info[9], self.geo.abs_info[10], self.geo.abs_info[11]]
        self.ctyd_pattern = self.geo.cty_pattern
        self.ctyd_form = self.geo.cty_form
        self.win_ratios = [self.geo.abs_info[18], self.geo.abs_info[19]]
  
        # print(self.ctyd_pattern)
        # print(self.ctyd_form)
        # for i in self.bldg_fps:
        #     print(i)
        
        # print(self.ctyd_fp)
        # print(self.bldg_pattern)
        self.bldg_blocks = self.build_bldg_blocks()
        self.ctyd_blocks = self.build_ctyd_blocks()
        self.make_bldg_constructions()
        self.all_blks = None
        


    def build_bldg_blocks(self):
        """ 
        This method is to make building block instances in the building, including:
            - get footprint points
            - get building, floor, room id
            - get z coordinate (height)

        Returns:
            list: nested list of building block instances, one list per floor
        """
        bldg_blocks = []
        
        for i, fps_flr in enumerate(self.bldg_fps):
            if fps_flr:
                bldg_blocks_flr = []

                for j, fp in enumerate(fps_flr):
                    if fp:
                        b = Block(fp)
                        b.bldg_id = self.bldg_id
                        b.flr_id = i
                        b.blk_id = j
                        b.blk_name = b.make_blk_name()
                        b.height = self.flr_height
                        b.z_flr = i * b.height
                        b.z_rf = (i+1) * b.height    
                        b.win_ratios = self.win_ratios
                        
                        # check if donut and record the hole pts
                        if self.bldg_pattern[i] == [1, 1, 1, 1]:
                            b.has_hole = True
                            b.hole_pts = self.ctyd_fp[::-1]
                            b.hole_segs = util.pts_to_segs(b.hole_pts)
                            
                    bldg_blocks_flr.append(b)
                bldg_blocks.append(bldg_blocks_flr)  
                
        for i in range(self.max_flr_nr - len(bldg_blocks)):
            bldg_blocks.append([])

        return bldg_blocks     
            
            
    def build_ctyd_blocks(self):
        
        ctyd_blocks = []
        print(self.ctyd_pattern)
        if self.ctyd_pattern:
            
            for i in range(self.ctyd_pattern):
                print(self.ctyd_pattern)
                if self.ctyd_fp:
                    c = Block(self.ctyd_fp, False) 
                    c.bldg_id = self.bldg_id
                    c.flr_id = i
                    c.blk_id = 0
                    c.blk_name = c.make_blk_name()
                    c.height = self.flr_height
                    c.z_flr = i * c.height
                    c.z_rf = (i+1) * c.height  
                    c.win_ratios = self.win_ratios
                    c.ctyd_form = self.ctyd_form
                    
                    ctyd_blocks.append(c)
                
        for i in range(self.max_flr_nr - self.ctyd_pattern):
            ctyd_blocks.append(None)
            
        return ctyd_blocks
        
            
            
    
    @staticmethod
    def make_walls(blk, fp_segs, bc):
        fs = []
        for s in fp_segs:
            wall_pts = util.make_wall_from_seg(s, blk.z_flr, blk.z_rf)
            f = Face(wall_pts, "Wall", bc)
            f.ref_seg = s
            fs.append(f)
        
        return fs
    

    @staticmethod
    def pair_neighbour(f_lst1, f_lst2, rev = True):
        if rev:
            f_lst2.reverse()
            
        for f1, f2 in zip(f_lst1, f_lst2):
            f1.neighbour_face = f2
            f2.neighbour_face = f1
            
        
    @staticmethod
    def make_iws(blk, fp1_segs, bc, rev = True):
        if rev:
            fp2_segs = util.fp_segs_reverse(fp1_segs)
        else:
            fp2_segs = fp1_segs

        iws1 = Massing.make_walls(blk, fp1_segs, bc)
        iws2 = Massing.make_walls(blk, fp2_segs, bc)
        Massing.pair_neighbour(iws1, iws2)
        
        return iws1, iws2
        
    
      
    @staticmethod
    def merge_horizontal(bs, c, c_form):
        
        if not bs:
            c.ew = Massing.make_walls(c, c.fp_segs, 2)   
                 
        elif not c:
            for b in bs:
                b.ew = Massing.make_walls(b, b.fp_segs, 2) 
                # check donut case
                if b.hole_segs:
                    b.ew.extend(Massing.make_walls(b, b.hole_segs, 2))  
                    
        else:
            rev_c_segs = util.fp_segs_reverse(c.fp_segs)
            
            for b in bs: 
                # check donut case
                if b.has_hole:
                    b.ew = Massing.make_walls(b, b.fp_segs, 2)
                    # if c_form == 1:
                    #     b.aw, c.aw = Massing.make_iws(b, b.hole_segs, 0)
                    # else:
                    #     b.iw, c.iw = Massing.make_iws(b, b.hole_segs, 1)
                    b.iw, c.iw = Massing.make_iws(b, b.hole_segs, 1)
                else:
                    
                    b_ref_segs = util.split_footprints(b.fp_segs, rev_c_segs)[0]
                    b_ew_segs, rev_c_segs, iw_segs = util.remove_same_rows(b_ref_segs, rev_c_segs)

                    b.ew = Massing.make_walls(b, b_ew_segs, 2)       
                                 
                    # if c_form == 1:
                    #     aw1, aw2 = Massing.make_iws(b, iw_segs, 0)
                    #     b.aw.extend(aw1)
                    #     c.aw.extend(aw2)
                    # else:
                    #     iw1, iw2 = Massing.make_iws(b, iw_segs, 1)
                    #     b.iw.extend(iw1)
                    #     c.iw.extend(iw2)
                    iw1, iw2 = Massing.make_iws(b, iw_segs, 1)
                    b.iw.extend(iw1)
                    c.iw.extend(iw2)
                    c.ew = Massing.make_walls(c, util.fp_segs_reverse(rev_c_segs), 2)           
                    

    
    
    @staticmethod
    def make_rfs(blk, fp, bc, is_donut = False, is_seg = True):
        """_summary_

        Args:
            blk (_type_): _description_
            fp (_type_): if donut, list of vert, if not donut, face_pt
            bc (_type_): _description_
            is_donut (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        fs = []
        if is_donut:
            rf_pts = util.add_z_coordinate_to_pts(blk.fp_pts, blk.z_rf)
            f = Face(rf_pts, "RoofCeiling", bc)
            f.is_donut = True
            f.hole_pts = util.add_z_coordinate_to_pts(blk.hole_pts, blk.z_rf)
            f.vert_pts = util.add_z_coordinate_to_pts(fp, blk.z_rf)
            fs.append(f)
        else:   
            if is_seg:  
                for s in fp:
                    p = util.segs_to_pts(s)
                    rf_pts = util.add_z_coordinate_to_pts(p, blk.z_rf)
                    f = Face(rf_pts, "RoofCeiling", bc)
                    fs.append(f) 
            else:
                rf_pts = util.add_z_coordinate_to_pts(fp, blk.z_rf)
                f = Face(rf_pts, "RoofCeiling", bc)
                fs.append(f) 
        return fs


    @staticmethod
    def make_flrs(blk, fp, bc, is_donut = False, is_seg = True):
        fs = []
        if is_donut:
            flr_pts = util.add_z_coordinate_to_pts(blk.fp_pts[::-1], blk.z_flr)
            f = Face(flr_pts, "Floor", bc)
            f.is_donut = True
            f.hole_pts = util.add_z_coordinate_to_pts(blk.hole_pts[::-1], blk.z_flr)
            f.vert_pts = util.add_z_coordinate_to_pts(fp[::-1], blk.z_flr)
            fs.append(f)

        else:      
            if is_seg:
                for s in fp:
                    p = util.segs_to_pts(s)
                    flr_pts = util.add_z_coordinate_to_pts(p[::-1], blk.z_flr)
                    f = Face(flr_pts, "Floor", bc)
                    fs.append(f)
            else:
                flr_pts = util.add_z_coordinate_to_pts(fp[::-1], blk.z_flr)
                f = Face(flr_pts, "Floor", bc)
                fs.append(f)
            
        return fs    
        # fs = []
        # if is_donut:
        #     flr_pts = util.add_z_coordinate_to_pts(blk.face_pts[::-1], blk.z_flr)
        #     f = Face(flr_pts, "Floor", bc)
        #     f.is_donut = True
        #     f.hole_pts = util.add_z_coordinate_to_pts(blk.hole_pts[::-1], blk.z_flr)
        #     f.vert_pts = util.add_z_coordinate_to_pts(fp[::-1], blk.z_flr)
        #     fs.append(f)

        # else:      
        #     if is_seg:
        #         for s in fp:
        #             p = util.segs_to_pts(s)
        #             flr_pts = util.add_z_coordinate_to_pts(p[::-1], blk.z_flr)
        #             f = Face(flr_pts[::-1], "Floor", bc)
        #             fs.append(f)
        #     else:
        #         flr_pts = util.add_z_coordinate_to_pts(fp[::-1], blk.z_flr)
        #         f = Face(flr_pts[::-1], "Floor", bc)
        #         fs.append(f)
            
        # return fs    

    @staticmethod
    def make_rf_flr_pairs(blk0, blk1, fp, bc, is_donut = False, is_seg=True):
        irf0 = Massing.make_rfs(blk0, fp, bc, is_donut, is_seg)
        iflr1 = Massing.make_flrs(blk1, fp, bc, is_donut, is_seg)
        Massing.pair_neighbour(irf0, iflr1, False)
        return irf0, iflr1
        
        
    @staticmethod
    def merge_vertical_bldg(bs0, bs1, max_flr):
        if bs0 and bs1:
            if len(bs0) == 2:
                for b0 in bs0:
                    # len(bs0) == 1, len(bs1) == 1 or 2
                    for b1 in bs1:
                        if util.check_has_intersect(b0.fp_pts, b1.fp_pts):
                            sub1, sub2, inter = util.boolean_intersection(b0.fp_segs, b1.fp_segs) 

                            if sub1:
                                b0.erf.extend(Massing.make_rfs(b0, sub1, 2))
                            if sub2:
                                b1.eflr.extend(Massing.make_flrs(b1, sub2, 2))

                            irf0, iflr1 = Massing.make_rf_flr_pairs(b0, b1, [inter], 1)
                            b0.irf.extend(irf0)
                            b1.iflr.extend(iflr1)
                            if b1.flr_id == max_flr - 1:
                                b1.erf.extend(Massing.make_rfs(b1, b1.fp_pts, 2, is_seg=False))
                            
                            break
                        
                        # if not b0.erf:
                        else:
                            if len(bs1) == 1:
                                b0.erf.extend(Massing.make_rfs(b0, b0.fp_pts, 2, is_seg=False))

                    if b0.flr_id == 0:
                        b0.eflr.extend(Massing.make_flrs(b0, b0.fp_pts, 2, is_seg=False))
                    
            else:
                # len(bs0) == 1, len(bs1) == 2
                if len(bs1) == 2:
                    sub1, sub2, inter = util.boolean_intersection(bs0[0].fp_segs, bs1[0].fp_segs) 
                    if sub2:
                        bs1[0].eflr.extend(Massing.make_flrs(bs1[0], sub2, 2))
                    irf0, iflr1 = Massing.make_rf_flr_pairs(bs0[0], bs1[0], [inter], 1)
                    
                    bs0[0].irf.extend(irf0)
                    bs1[0].iflr.extend(iflr1)

                    for s in sub1:

                        if not util.check_has_intersect(util.segs_to_pts(s), bs1[1].fp_pts):
                            bs0[0].erf.extend(Massing.make_rfs(bs0[0], [s], 2))
                        else:
                            sub11, sub12, inter1 = util.boolean_intersection(s, bs1[1].fp_segs)
                            if sub12:
                                bs1[1].eflr.extend(Massing.make_flrs(bs1[1], sub12, 2))
                            
                            irf01, iflr11 = Massing.make_rf_flr_pairs(bs0[0], bs1[1], [inter1], 1)
                            bs0[0].irf.extend(irf01)
                            bs1[1].iflr.extend(iflr11)
                            
                            if bs0[0].has_hole:
                                hole_segs = util.fp_segs_reverse(bs0[0].hole_segs)
                                sub11, _, _ = util.boolean_intersection(sub11[0], hole_segs)
                            bs0[0].erf.extend(Massing.make_rfs(bs0[0], sub11, 2)) 
                    
                # len(bs0) == 1, len(bs1) == 1
                else:
                    sub1, sub2, inter = util.boolean_intersection(bs0[0].fp_segs, bs1[0].fp_segs)
 
                    if sub2:
                        bs1[0].eflr.extend(Massing.make_flrs(bs1[0], sub2, 2))
                    
                    if bs0[0].has_hole and bs1[0].has_hole:
                        inter_pts = util.segs_to_pts(inter)
                        donut_pts = util.make_donut(inter_pts, bs0[0].hole_pts)
                        irf0, iflr1 = Massing.make_rf_flr_pairs(bs0[0], bs1[0], donut_pts, 1, True)
                        
                    elif bs0[0].has_hole:   
                        hole_segs = util.fp_segs_reverse(bs0[0].hole_segs)
                        sub11, _, _ = util.boolean_intersection(sub1[0], hole_segs)
                        bs0[0].erf.extend(Massing.make_rfs(bs0[0], sub11, 2))   
                        irf0, iflr1 = Massing.make_rf_flr_pairs(bs0[0], bs1[0], [inter], 1)
                        
                    else:
                        irf0, iflr1 = Massing.make_rf_flr_pairs(bs0[0], bs1[0], [inter], 1)
                        if sub1:
                            bs0[0].erf.extend(Massing.make_rfs(bs0[0], sub1, 2))
                        
                    bs0[0].irf.extend(irf0)
                    bs1[0].iflr.extend(iflr1)
                    
                    
            
                if bs0[0].flr_id == 0:
                    if bs0[0].has_hole:
                        donut_pts = util.make_donut(bs0[0].fp_pts, bs0[0].hole_pts)
                        bs0[0].eflr.extend(Massing.make_flrs(bs0[0], donut_pts, 2, True))
                    else:   
                        bs0[0].eflr.extend(Massing.make_flrs(bs0[0], bs0[0].fp_pts, 2, is_seg=False))   
                    
                if bs1[0].flr_id == max_flr - 1:
                    if bs1[0].has_hole:
                        donut_pts = util.make_donut(bs1[0].fp_pts, bs1[0].hole_pts)
                        bs1[0].erf.extend(Massing.make_rfs(bs1[0], donut_pts, 2, True))
                    else:
                        for b1 in bs1:
                            b1.erf.extend(Massing.make_rfs(b1, b1.fp_pts, 2, is_seg=False))
                        
                        
        elif bs0 and not bs1:
            
            for b0 in bs0:
                if b0.has_hole:
                    donut_pts = util.make_donut(b0.fp_pts, b0.hole_pts)
                    b0.erf.extend(Massing.make_rfs(b0, donut_pts, 2, True))
                else:
                    b0.erf.extend(Massing.make_rfs(b0, b0.fp_pts, 2, is_seg=False))
                
                if b0.flr_id == 0:
                        b0.eflr.extend(Massing.make_flrs(b0, b0.fp_pts, 2, is_seg=False))
            
        
    @staticmethod
    def merge_vertical_ctyd(c0, c1, c_form, max_flr):
        if c0 and c1:
            # indoor
            if c_form == 0:
                arf0, aflr1 = Massing.make_rf_flr_pairs(c0, c1, c0.fp_pts, 0, is_seg=False)
                c0.arf.extend(arf0)
                c1.aflr.extend(aflr1)
            # massive
            else:
                irf0, iflr1 = Massing.make_rf_flr_pairs(c0, c1, c0.fp_pts, 1, is_seg=False)
                c0.irf.extend(irf0)
                c1.iflr.extend(iflr1)
            
            if c0.flr_id == 0:
                c0.eflr.extend(Massing.make_flrs(c0, c0.fp_pts, 2, is_seg=False))
            if c1.flr_id == max_flr - 1:
                c1.erf.extend(Massing.make_rfs(c1, c1.fp_pts, 2, is_seg=False))

        elif c0 and not c1:
            c0.erf.extend(Massing.make_rfs(c0, c0.fp_pts, 2, is_seg=False))
            
            if c0.flr_id == 0:
                c0.eflr.extend(Massing.make_flrs(c0, c0.fp_pts, 2, is_seg=False))
        

        
    def make_bldg_constructions(self):
        # iterate through [i] and [i+1] floor
        if self.max_flr_nr == 1:
            bs = self.bldg_blocks[0]
            c = self.ctyd_blocks[0]
            Massing.merge_horizontal(bs, c, self.ctyd_form)
            Massing.merge_vertical_bldg(bs, None, self.max_flr_nr)
            Massing.merge_vertical_ctyd(c, None, self.ctyd_form, self.max_flr_nr)
            
            
        for i in range(self.max_flr_nr - 1):
            # print("------------------------", i, i+1,"-----------------------------")
            bs0, bs1 = self.bldg_blocks[i:i+2]
            c0, c1 = self.ctyd_blocks[i:i+2]
            
            Massing.merge_horizontal(bs0, c0, self.ctyd_form)
            Massing.merge_horizontal(bs1, c1, self.ctyd_form)
            
            Massing.merge_vertical_bldg(bs0, bs1, self.max_flr_nr)
            Massing.merge_vertical_ctyd(c0, c1, self.ctyd_form, self.max_flr_nr)


                        
    
