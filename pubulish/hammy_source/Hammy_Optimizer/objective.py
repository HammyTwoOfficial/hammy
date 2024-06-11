from typing import Any
from hammy.Hammy_LCA import LCA
from hammy.Hammy_Utils import util, util3



class Objective:
    
    def __init__(self, mass_data):
        self.check_valid = True
        self.mass_data = mass_data
        
        self.bldg_json, self.constr_dict, self.boq, self.volume, self.rm_area = self.mass_data.output_bldg_json()
        self.bldg_id = self.mass_data.massing.bldg_id

        self.daylight_objs_arr = None
        self.daylight_objs_dict = None

        self.energy_objs_arr = None
        self.energy_carbon_dict =None
        self.energy_carbon_arr = None

        self.design_fact_dict = None
        self.design_fact_arr = None

        self.mat_fact_dict = None
        self.mat_fact_arr = None
        
        self.calc_design_factors()
        self.calc_material_factors()
    
    def calc_design_factors(self):
        
        mass = self.mass_data.massing
        seg_pattrns = mass.geo.seg_pattern
        bldg_flr_pattern = mass.geo.flr_patterns
        bldg_seg_flr_nr = mass.geo.max_seg_flo_num
        ctyd_fp = mass.ctyd_fp
        ctyd_form = mass.ctyd_form
        ctyd_pattern = mass.ctyd_pattern
        # height factor
        max_flr_nr = mass.max_flr_nr
        
        
        rf = self.constr_dict["RoofCeiling"]
        flr = self.constr_dict["Floor"]
        ew = self.constr_dict["ExWall"]
        win = self.constr_dict["Window"]
        grf = self.constr_dict["GlsRoof"]
        gw = self.constr_dict["GlsWall"]
        
        # wall to flr ratio
        wfr = (ew + gw) / flr

        # shape coefficient
        a = rf + grf + ew + gw
        shape_coef = a / self.volume
        
        # avg depth
        depths = mass.depths
        sum_depth = 0
        for i in range(4):
            sum_depth += depths[i] * seg_pattrns[i]
        if sum(seg_pattrns) != 0 :
            avg_depth = sum_depth / sum(seg_pattrns)
        else:
            avg_depth = 0
        
        # ctyd size
        dists_cpt = util.dist_to_poly_sides(ctyd_fp)
        ctyd_depth = dists_cpt[0] + dists_cpt[2]
        
        
        # window ratio south / north
        win_ratio_s, win_ratio_n = mass.win_ratios
        
        # avg window ratio / glass ratios
        avg_win_ratio = win / (ew + win)
        gls_wall_ratio = (win + gw) / (ew + gw)
        gls_env_ratio = (win + gw + grf) / a
        
        all_glas_s = 0
        for b in mass.all_blks:
            if b:
                for f in b.ew:
                    if f.face_ori[0] == 0:
                        all_glas_s += f.calc_face_area()
        gls_s_to_flr = all_glas_s / flr              
        
        # print(self.constr_dict, all_glas_s)
        
        wall_area_s = 0
        wall_area_we = 0
        for bs in mass.bldg_blocks:
            for b in bs:
                for ew in b.ew:
                    pt1, pt2 = ew.face_pts[1:3]
                    ew_x, ew_y = util.calc_dist_x_y([pt1, pt2])
                    ori = ew.get_orientation()[1][0]
                    if ori == 0:
                        wall_area_s += ew_x
                    wall_area_we += ew_y      
        
        # wall orientation factor: south / west
        if wall_area_we != 0:
            wall_s_to_w = wall_area_s / (wall_area_we / 2)
        else:
            wall_s_to_w = 0
        
        
        
        
        ctyd_factor = 0
        # courtyard factor in 
        # {0: no ctyd, 1: outside ctyd, 2: inside with airwall}
        if ctyd_pattern:
            if ctyd_form == 1:
                if bldg_seg_flr_nr <= ctyd_pattern:
                    ctyd_factor = 0
                else:
                    ctyd_factor = 1
            else:
                ctyd_factor = ctyd_form + 2
        else:
            if [1, 1, 1, 1] in bldg_flr_pattern:
                ctyd_factor = 1
            else:
                ctyd_factor = 0
        
        
        # building form factor: first floor form
        if bldg_flr_pattern != []:
            bldg_form = util3.get_bldg_form_flr(bldg_flr_pattern[0], bool(ctyd_pattern), ctyd_form)[1]
        else:
            bldg_form = 0

         
        oDict = {
            "Shape Factors": {
                "Max. Flr Nr": max_flr_nr,
                "Total Area [m]": flr,
                "Wall to Flr Ratio": wfr,
                "Shape Coefficient": shape_coef,
                "Avg. Building Depth": avg_depth,
                "Courtyard Depth": ctyd_depth
            },
            "Window / Glass Factors": {
                "Window Ratio Avg.": avg_win_ratio,
                "Window Ratio South": win_ratio_s,
                "Window Ratio North": win_ratio_n,
                "Facade Glass Ratio": gls_wall_ratio,
                "Envelop Glass Ratio": gls_env_ratio,
                "Glass to Floor Ratio South": gls_s_to_flr
            },
            "Orientation Factors": {
                "Facade South to West Ratio": wall_s_to_w
            },
            "Form Factors": {
                "Courtyard Form Factor": ctyd_factor,
                "Building Form Factor": bldg_form
            }
        }
        
        oArr = [
            max_flr_nr,              # -[0]
            flr,
            wfr,                     # -[1]
            shape_coef,              # -[2]
            avg_depth,
            ctyd_depth,
            avg_win_ratio,           # -[3]
            win_ratio_s,             # -[4]
            win_ratio_n,             # -[5]
            gls_wall_ratio,          # -[6]
            gls_env_ratio,
            gls_s_to_flr,             # -[7]
            wall_s_to_w,             # -[8]
            ctyd_factor,             # -[9]
            bldg_form                # -[10]
            ]
        self.design_fact_dict = oDict
        self.design_fact_arr = oArr
        # return oDict, oArr

    @staticmethod
    def calc_constr_uvalue(mats_data, Rsi=0.13, Rse=0.04):
        rt = Rsi + Rse
        for l in mats_data:
            if l["conductivity"] != 0 and l["conductivity"] is not None:
                rt += l["thickness"] / l["conductivity"]        
        return 1/rt
    
    
    def calc_material_factors(self):
        
        mass_data = self.mass_data
        # construction type
        constr_type = mass_data.constr_category
        
        # insulation thickness 
        wall_insu_thickness = self.boq["ExWall"][0][-1]
        rf_insu_thickness = self.boq["RoofCeiling"][0][-1]
        
        # u-value of exterior wall
        ew_con_name = mass_data.constr_sys["ExWall"]
        mat_names = mass_data.con_lib["Construction"][ew_con_name]["materials"]
        all_mats = self.bldg_json["properties"]["energy"]["materials"]
        mats = []
        for mn in mat_names:
            for m in all_mats:
                if mn == m["identifier"]:
                    mats.append(m)
                    break 
        ew_u_value = Objective.calc_constr_uvalue(mats)
        
        # u-value of roof
        rf_con_name = mass_data.constr_sys["RoofCeiling"]
        mat_names = mass_data.con_lib["Construction"][rf_con_name]["materials"]
        all_mats = self.bldg_json["properties"]["energy"]["materials"]
        mats = []
        for mn in mat_names:
            for m in all_mats:
                if mn == m["identifier"]:
                    mats.append(m)     
                    break    
        rf_u_value = Objective.calc_constr_uvalue(mats, 0.1, 0.04)
        
        oDict = {
            "Material Factors": {
                "Material System": constr_type,
                "Insulation Thickness ExWall": wall_insu_thickness,
                "Insulation Thickness RoofCeiling": rf_insu_thickness,
                "U-Value ExWall": ew_u_value,
                "U-Value RoofCeiling": rf_u_value
            }
        }
        
        oArr = [
            constr_type, 
            wall_insu_thickness,
            rf_insu_thickness, 
            ew_u_value,
            rf_u_value
            ]
        self.mat_fact_dict = oDict
        self.mat_fact_arr = oArr

        # return oDict, oArr
    
    
# class PerformanceObjective:

    # def __init__(self,mass_data,energy_objs_arr,daylight_objs_arr):
        
    #     self.mass_data = mass_data
        
    #     self.daylight_objs_arr = daylight_objs_arr
    #     self.daylight_objs_dict = self.daylight_dict()

    #     self.energy_objs_arr = energy_objs_arr
    #     self.energy_carbon_dict, self.energy_carbon_arr = self.calc_energy_carbon()
    
    
    """
    energy_objs_arr = [ heating, cooling ,total]
    daylight_objs_arr = [sDA, ASE]
    
    """

    def daylight_dict(self, daylight_objs_arr):
        self.daylight_objs_arr = daylight_objs_arr
        oDict = {
            "Daylight Performance": {
                "sDA": self.daylight_objs_arr[0],
                "ASE": self.daylight_objs_arr[1]
            }
        }
        self.daylight_objs_dict = oDict
        # return oDict



    def calc_energy_carbon(self,energy_objs_arr):
        self.energy_objs_arr = energy_objs_arr
        # energy demands: heating, cooling, total
        q_ht, q_cl, q_tot= self.energy_objs_arr
        # q_tot = q_ht + q_cl

        lca = LCA(self.mass_data,self.energy_objs_arr) 
         
        # carbon footprints: Module A, B, C, D
        ec_modules = lca.ec_modules
        ec_mod_prop = lca.ec_mod_prop
        # embedded carbon
        ec_sum = lca.ec_sum

        # operational carbon
        oc_sum = lca.oc_sum
        
        # total carbon footprint
        c_tot = ec_sum + oc_sum
        
        oDict = {
            "Energy Demands": {
                "Energy Demand Heating [MJ/m2]": q_ht,
                "Energy Demand Cooling [MJ/m2]": q_cl,
                "Total Energy Demand [MJ/m2]": q_tot
            },
            "Carbon Footprints": {
                "GWP in Moduels [CO2 eq.kg/m2/a]": ec_modules,
                "GWP Embedded [CO2 eq.kg/m2/a]": ec_sum,
                "GWP Operational [CO2 eq.kg/m2/a]": oc_sum,
                "GWP Total [CO2 eq.kg/m2/a]": c_tot
            }
        }
        
        oArr = [
            q_ht,
            q_cl,
            q_tot,
            ec_modules[0],
            ec_modules[1],
            ec_modules[2],
            ec_modules[3],
            ec_sum,
            oc_sum,
            c_tot
        ]
        self.energy_carbon_dict = oDict
        self.energy_carbon_arr  = oArr
        # return oDict, oArr
