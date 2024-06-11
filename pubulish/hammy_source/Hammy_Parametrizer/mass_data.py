from .block import Block
from .face import Face
from .massing import Massing
from hammy.Hammy_Utils import util
from copy import deepcopy



class MassData:
 
  ref_lib = None
  con_lib = None
 
  def __init__(self, massing):
    """_summary_

    Args:
      massing (object): class Massing instance
      constr_info (list): [
        constr_category (int): [0] -> {0, 1, 2, 3} Wood / Concrete
        constr_quality (float): [1] -> {0.5 - 1.5, 0.01 step}
      ]
    """
   
    self.massing = massing
    self.constr_category = int(self.massing.geo.abs_info[20])
    self.constr_sys = MassData.con_lib["Presets"][self.constr_category]
   # self.constr_sys["ExWall"] = MassData.con_lib["FacadeSys"][self.constr_category]
   # self.constr_sys["InWall"] = MassData.con_lib["InWallSys"][self.constr_category]
   # self.constr_sys["Floor"] = MassData.con_lib["SlabSys"][self.constr_category]
   # print(self.constr_sys)
    self.constr_quality = self.massing.geo.abs_info[21]
    self.bldg_json, self.constr_dict, self.boq, self.volume, self.rm_area = self.output_bldg_json()
    self.daylight_space = self.daylight_geo_space()

 
  @staticmethod
  def make_bc(f):
    ref_bc = MassData.ref_lib["bc_lib"]
    if f.bc == 2:
      if f.face_part == "Floor" and f.flr_id == 0:
        bc = ref_bc[2]
      else:
        bc = ref_bc[1]
    else:
      bc = ref_bc[0]
      neigh_name = f.neighbour_face.face_name
      bc["boundary_condition_objects"] = [neigh_name, neigh_name.split("..")[0]]
    return bc
 
 
  @staticmethod
  def output_win_json(w):

    win_json = deepcopy(MassData.ref_lib["json_outputs"]["win_template"])
    win_json["display_name"] = win_json["identifier"] = w.face_name
    win_json["geometry"]["plane"]["o"] = w.origin
    win_json["geometry"]["plane"]["n"] = w.vector_n
    win_json["geometry"]["plane"]["x"] = w.vector_x
    win_json["geometry"]["boundary"] = w.face_pts
   
    return win_json
 
 
  @staticmethod
  def output_face_json(f):

    face_json = deepcopy(MassData.ref_lib["json_outputs"]["face_template"])
   
    face_json["display_name"] = face_json["identifier"] = f.face_name
    face_json["geometry"]["plane"]["o"] = f.origin
    face_json["geometry"]["plane"]["n"] = f.vector_n
    face_json["geometry"]["plane"]["x"] = f.vector_x
    face_json["geometry"]["boundary"] = f.face_pts
   
    if f.is_donut:
      face_json["geometry"]["holes"] = [f.hole_pts[::-1]]
      face_json["geometry"]["vertices"] = f.vert_pts
     
    face_json["boundary_condition"] = MassData.make_bc(f)
    face_json["face_type"] = f.face_type
   
   # if f.face_type != "AirBoundary":
   #   face_json["properties"]["energy"]["constructions"] = f.constr # can have no constr
   
    if f.win:
      f.win.face_name = "Aperture_" + str(f.face_name)
      face_json["apertures"] = [MassData.output_win_json(f.win)]
 
    return face_json

 
 
 
  @staticmethod
  def output_blk_json(blk):
    blk_json = deepcopy(MassData.ref_lib["json_outputs"]["blk_template"])
    blk_json["faces"] = []
    blk_json["display_name"] = blk_json["identifier"] = blk.make_blk_name()
    blk_json["story"] = "Floor" + str(blk.flr_id)
   
    blk.volume = blk.calc_volume()
    blk_json["volume"] = blk.volume
    blk_json["ceiling_height"] = blk.z_rf
   
   # make win
    for f in blk.ew:
      if blk.isBldg or (not blk.isBldg and blk.ctyd_form == 1):
        f.win = f.make_window(blk.win_ratios[f.face_ori[0]], blk.height)
       # f.win = f.make_window(blk.win_ratio[f.face_ori], blk.height)
      else:
        f.is_glas = True
        f.win = f.make_window(0.95, blk.height)
       
    for f in blk.erf:
      if not blk.isBldg and blk.ctyd_form != 1:
        f.is_glas = True
        f.win = f.make_window(0.95, blk.height)
   # for f in blk.ew:
   #   f.win = f.make_window(blk.win_ratios[f.face_ori[0]], blk.height)
      
    fs = blk.ew + blk.iw + blk.aw + blk.erf + blk.irf + blk.arf + blk.eflr + blk.iflr + blk.aflr     
     
    for f in fs:
      blk_json["faces"].append(deepcopy(MassData.output_face_json(f)))   
   
    return blk_json
 
 

 
  def make_constr_jsons(self):
    con_ref = MassData.con_lib["Construction"]
    mat_ref = MassData.con_lib["Material"]
    insu_ref = MassData.con_lib["InsulationExWalls"]
    cons = []
    mats = []
    configs = {}
    for p, cn in self.constr_sys.items():
      con = con_ref[cn]
      for mn in con["materials"]:
        mat = deepcopy(mat_ref[mn])
        if p == "ExWall" and mn in insu_ref:
          mat["thickness"] = mat["thickness"] * self.constr_quality
          configs["ExWall"] = mat["thickness"]
        if p == "RoofCeiling" and mn in insu_ref:
          mat["thickness"] = mat["thickness"] * self.constr_quality
          configs["RoofCeiling"] = mat["thickness"]
        mats.append(mat)
      cons.append(con)
    return cons, mats, configs
 
 
 
  def output_bldg_json(self):
    bldg_json = deepcopy(MassData.ref_lib["json_outputs"]["bldg_template"])
    bldg_json["rooms"] = []
    bldg_json["display_name"] = bldg_json["identifier"] = self.massing.bldg_name
   # bldg_json["properties"]["energy"]["schedules"] = self.schedule
   # bldg_json["properties"]["energy"]["program_types"] = self.program
   
    blks = []
    for i in self.massing.bldg_blocks:
      for b in i:
        blks.append(b)
    blks.extend(self.massing.ctyd_blocks)
    
    rf_area = 0
    flr_area = 0
    ew_area = 0
    iw_area = 0
    win_area = 0
    gw_area = 0
    grf_area = 0
    
   # construction quantity calculations
    for b in blks:
      if b:
        all_fs = b.ew + b.iw + b.aw + b.erf + b.irf + b.arf + b.eflr + b.iflr + b.aflr
        for i, f in enumerate(all_fs):
          f.flr_id = b.flr_id
          f.face_name = b.blk_name + "..Face" + str(i) + "_" + f.face_part
          if f.face_type != "AirBoundary":
            if f.face_type == "RoofCeiling":
              if f.bc == 2:
                  rf_area += f.calc_face_area()
                
               # f.constr = self.constr_sys["RoofCeiling"]
              # else:
              #   flr_area += f.face_area
               # f.constr = self.constr_sys["Floor"]
            elif f.face_type == "Floor":
              # if f.bc == 2:
              if f.bc != 0:  
                flr_area += f.calc_face_area()
                
             # f.constr = self.constr_sys["Floor"]
            elif f.face_type == "Wall":
              if f.bc == 2:
                ew_area += f.calc_face_area()
                
               # f.constr = self.constr_sys["ExWall"]
              else:
                iw_area += f.calc_face_area()
                
               # f.constr = self.constr_sys["InWall"]

    tot_volume = 0        
    for b in blks:
      if b:       
        bldg_json["rooms"].append(deepcopy(MassData.output_blk_json(b)))
        tot_volume += b.volume
        all_fs = b.ew + b.erf
       
       # calculate window areas and glass wall areas
        for f in all_fs:
          if f.win:
            if f.face_part == "Wall":
              if f.is_glas:
                gw_area += f.win.calc_face_area()
                
              else:
                win_area += f.win.calc_face_area()
                
            else:
              grf_area += f.win.calc_face_area()
                

    self.massing.all_blks = blks
         
    con_json, mat_json, configs = self.make_constr_jsons()
    bldg_json["properties"]["energy"]["constructions"] = con_json
    bldg_json["properties"]["energy"]["materials"] = mat_json
    bldg_json["properties"]["energy"]["construction_sets"] = [MassData.con_lib["ConstructionSet"][self.constr_category]]
   
   
    constr_quantity_dict = {
      "RoofCeiling": rf_area - grf_area,
      "Floor": flr_area,
      "ExWall": ew_area-win_area,
      "InWall": iw_area / 2,
      "Window": win_area, 
      "GlsRoof": grf_area,
      "GlsWall": gw_area
      }  
   
    tot_area = flr_area
    constr_dict = self.constr_sys
   
    boq = {}
    for con_part, con_name in constr_dict.items():
      area = constr_quantity_dict[con_part]
      if con_part == "ExWall":
        config_thickness = configs["ExWall"]
      elif con_part == "RoofCeiling":
        config_thickness = configs["RoofCeiling"]
      else:
        config_thickness = None
      boq[con_part] = [[con_name, area, config_thickness]]
   
    return bldg_json, constr_quantity_dict, boq, tot_volume, tot_area
 
 
 
 # @staticmethod
 # def calc_core_nr_flr(form, a, d, span):
 #   if form == "Linear":
 #     core_nr = a / 800 + 1 if span == 1 else (a / d - 40) / 45 + 1
 #   elif form == "T":
 #     core_nr = a / 800 + 0.5 if span == 1 else (a / d - 60) / 45 + 1
 #   elif form == "H":
 #     core_nr = a / 800 + 0.5 if span == 1 else (a / d - 80) / 45 + 2
 #   elif form == "O":
 #     core_nr = a / 800 + 1 if span == 1 else (a / d) / 45 + 1
 #   return core_nr
 
 
 # def calc_core(self):
 #   max_flr_nr = self.massing.max_flr_nr
   
 #   depth = sum(self.massing.depths) / 4
 #   span = 1 if depth <= 9 else 2
   
 #   bldg_area_flr = []
 #   for fps in self.massing.bldg_fps:
 #     a = 0
 #     for fp in fps:
 #       a += util.calc_fp_area(fp)
 #     bldg_area_flr.append(a)
 #   ctyd_area = util.calc_fp_area(self.massing.ctyd_fps)
   
 #   bldg_pattern = self.massing.bldg_pattern
 #   ctyd_pattern = [1 if i < max_flr_nr else 0 for i in range(max_flr_nr)]
 #   ctyd_form = self.massing.ctyd_form
   
 #   ref_pattern = MassData.ref_lib["bldg_form"]
   
 #   core_nrs = []
 #   for i in range(max_flr_nr):
 #     core_nr = 0
 #     if i < len(bldg_pattern):
 #       if bldg_pattern[i] in ref_pattern["Riegel"]:
 #         if ctyd_pattern[i] and ctyd_form == 2:
 #           form = "T"
 #         else:
 #           form = "Linear"
 #       elif bldg_pattern[i] in ref_pattern["L"]:
 #         form = "Linear"
 #         if ctyd_pattern[i] and ctyd_form == 2:
 #           core_nr += 1
 #       elif bldg_pattern[i] in ref_pattern["U"]:
 #         form = "Linear"
 #         if ctyd_pattern[i] and ctyd_form == 2:
 #           core_nr += 1
 #       elif bldg_pattern[i] in ref_pattern["II"]:
 #         if ctyd_pattern[i] and ctyd_form == 2:
 #           form = "H"
 #         else:
 #           form = "Linear"
 #       elif bldg_pattern[i] in ref_pattern["O"]:
 #         form = "O"
 #         if ctyd_pattern[i] and ctyd_form == 2:
 #           core_nr += 1
 #       core_nr += MassData.calc_core_nr_flr(form, bldg_area_flr[i], depth, span)
 #     else:
 #       core_nr += MassData.calc_core_nr_flr("Linear", ctyd_area, depth, 1)   
     
 #     core_nrs.append(core_nr)
  def daylight_geo_space(self):
    
    bldg_blocks = self.massing.bldg_blocks 
    ctyd_blocks = self.massing.ctyd_blocks
    
    all_blocks = []
    for bs_flr in bldg_blocks:
        if bs_flr:
            for b in bs_flr:
                all_blocks.append(b)
    
    # all_blocks.extend(ctyd_blocks)
    
    all_walls_pts = []
    all_wins_pts = []
    all_wins_hori_pts = []
    all_flrs_pts = []
    all_rfs_pts = []
    

    for b in all_blocks:
        if b:
            for ew in b.ew:
                if ew.win:
                    win_pts = ew.win.face_pts
                ew_pts = [[win_pts[1]] + ew.face_pts[1:3] + [win_pts[2]]]
                all_walls_pts.append(ew_pts)
                all_wins_pts.append([win_pts])

            
            roofs = b.erf + b.irf
            
            for rf in roofs:
                # print("rf.face_name",rf.face_name)
                if rf.is_donut:
                    rf_pts = [rf.face_pts, rf.hole_pts[::-1]]
                    print(rf_pts)
                    all_rfs_pts.append(rf_pts)
                elif rf.is_glas:
                    all_wins_hori_pts.append([rf.face_pts])
                else:
                    
                    all_rfs_pts.append([rf.face_pts])
  
            flrs = b.eflr + b.iflr
            for flr in flrs:
                if flr.is_donut:
                    flr_pts = [flr.face_pts, flr.hole_pts[::-1]]
                    all_flrs_pts.append(flr_pts)
                else:
                    all_flrs_pts.append([flr.face_pts])
    all_cty_win_pts = []  
    all_cty_wall_pts = []     
    for b in ctyd_blocks:
        if b:
            for ew in b.ew:
                if ew.win:
                    win_pts = ew.win.face_pts

                ew_pts = [[win_pts[1]] + ew.face_pts[1:3] + [win_pts[2]]]

                all_cty_wall_pts.append(ew_pts)
                all_wins_pts.append([win_pts])
                all_cty_win_pts.append([win_pts])

            
            roofs = b.erf + b.irf
            for rf in roofs:
                if rf.is_donut:
                    rf_pts = [rf.face_pts, rf.hole_pts[::-1]]
                    all_rfs_pts.append(rf_pts)
                elif rf.is_glas:
                    all_wins_hori_pts.append([rf.face_pts])
                else:
                    all_rfs_pts.append([rf.face_pts])
                    
            flrs = b.eflr + b.iflr
            for flr in flrs:
                if flr.is_donut:
                    flr_pts = [flr.face_pts, flr.hole_pts[::-1]]
                    all_flrs_pts.append(flr_pts)
                else:

                    all_flrs_pts.append([flr.face_pts])

    return  all_walls_pts, all_wins_pts, all_wins_hori_pts, all_flrs_pts, all_rfs_pts,all_cty_win_pts,all_cty_wall_pts


  def estimate_constr_quantity(self):
    pass
 
  def output_boq(self):
    pass
    
    
    
    # @staticmethod
    # def calc_core_nr_flr(form, a, d, span):
    #     if form == "Linear":
    #         core_nr = a / 800 + 1 if span == 1 else (a / d - 40) / 45 + 1
    #     elif form == "T":
    #         core_nr = a / 800 + 0.5 if span == 1 else (a / d - 60) / 45 + 1
    #     elif form == "H":
    #         core_nr = a / 800 + 0.5 if span == 1 else (a / d - 80) / 45 + 2
    #     elif form == "O":
    #         core_nr = a / 800 + 1 if span == 1 else (a / d) / 45 + 1
    #     return core_nr
    
    
    # def calc_core(self):
    #     max_flr_nr = self.massing.max_flr_nr
        
    #     depth = sum(self.massing.depths) / 4
    #     span = 1 if depth <= 9 else 2
        
    #     bldg_area_flr = []
    #     for fps in self.massing.bldg_fps:
    #         a = 0
    #         for fp in fps:
    #             a += util.calc_fp_area(fp)
    #         bldg_area_flr.append(a)
    #     ctyd_area = util.calc_fp_area(self.massing.ctyd_fps)
        
    #     bldg_pattern = self.massing.bldg_pattern
    #     ctyd_pattern = [1 if i < max_flr_nr else 0 for i in range(max_flr_nr)] 
    #     ctyd_form = self.massing.ctyd_form
        
    #     ref_pattern = MassData.ref_lib["bldg_form"]
        
    #     core_nrs = []
    #     for i in range(max_flr_nr):
    #         core_nr = 0
    #         if i < len(bldg_pattern):
    #             if bldg_pattern[i] in ref_pattern["Riegel"]:
    #                 if ctyd_pattern[i] and ctyd_form == 2:
    #                     form = "T"
    #                 else:
    #                     form = "Linear"
    #             elif bldg_pattern[i] in ref_pattern["L"]:
    #                 form = "Linear"
    #                 if ctyd_pattern[i] and ctyd_form == 2:
    #                     core_nr += 1
    #             elif bldg_pattern[i] in ref_pattern["U"]:
    #                 form = "Linear"
    #                 if ctyd_pattern[i] and ctyd_form == 2:
    #                     core_nr += 1
    #             elif bldg_pattern[i] in ref_pattern["II"]:
    #                 if ctyd_pattern[i] and ctyd_form == 2:
    #                     form = "H"
    #                 else:
    #                     form = "Linear"
    #             elif bldg_pattern[i] in ref_pattern["O"]:
    #                 form = "O"
    #                 if ctyd_pattern[i] and ctyd_form == 2:
    #                     core_nr += 1
    #             core_nr += MassData.calc_core_nr_flr(form, bldg_area_flr[i], depth, span)
    #         else:
    #             core_nr += MassData.calc_core_nr_flr("Linear", ctyd_area, depth, 1)       
            
    #         core_nrs.append(core_nr)
            
        

    def estimate_constr_quantity(self):
        pass
    
    def output_boq(self):
        pass
        
    