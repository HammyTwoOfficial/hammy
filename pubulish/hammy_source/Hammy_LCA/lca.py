from .material import Material
from .construction import Construction
import numpy as np



class LCA():
    
    b6_factors = [
        0.2606, # gas
        0.623,  # Electricity mix
    ]
    
    def __init__(self, mass_data, sim_res, iRSP = 50):#       iBOQ, iSimRes, iRmArea, iRSP = 50):
        """ 
        This class calculate all EE related 

        Args:
            iBOQ (dict(list)): Budget of quantities
            {
                "RoofCeiling": [
                    ["ConstrName1", SrfArea1, config_thickness],
                ],
                "Floor": [],
                "ExWall": [
                    ["ConstrName1", SrfArea1, config_thickness]
                    ],
                "Window": [],
            },
            iSimRes (list): [
                heating_e [0],
                cooling_e [1],
                tot_e [2]
            ]
            iRmArea (float): total room area of the massing group
            iRSP (int): Remaining Service Period = 50
        """
        self.mass_data = mass_data
        self.boq = self.mass_data.boq 
        self.sim_res = sim_res
        self.rm_area = self.mass_data.rm_area
        self.rsp = iRSP

        self.ec_modules, self.ec_mod_prop, self.ec_parts, self.ec_sum = self.calc_ec()
        self.oc_heating, self.oc_cooling, self.oc_sum = self.calc_oc()
        
        self.gwp = self.ec_sum + self.oc_sum
        
    def calc_ec(self):

        gwp_e = []
        for con_part, con_boqs in self.boq.items():
            if con_boqs:
                gwp_e_part = np.zeros((4,))
                for con_boq in con_boqs:
                    con_name, srf_area, insu_thick = con_boq
                    con = Construction(con_part, con_name, srf_area, insu_thick)
                    # print(con.__dict__)
                    gwp_e_part += con.gwp_e
                gwp_e.append(gwp_e_part)
            else:
                gwp_e.append(np.zeros(4,))
         
        gwp_e_modules = np.sum(gwp_e, axis=0) / self.rm_area / self.rsp    
        gwp_e_parts = np.sum(gwp_e, axis=1) / self.rm_area / self.rsp        
        gwp_e_sum = np.sum(gwp_e) / self.rm_area / self.rsp       

        gwp_e_modules_prop = gwp_e_modules / gwp_e_sum
        return gwp_e_modules.tolist(), gwp_e_modules_prop.tolist(), gwp_e_parts.tolist(), gwp_e_sum
       
       
    def calc_oc(self, b6_f_i = 1):
        b6_f = LCA.b6_factors[b6_f_i]
        gwp_o = np.asarray(self.sim_res) * b6_f / 3.6    # MJ to kwh 
        return gwp_o.tolist()
        

        
        
        
        
# def calc_LCA(oeDict, eeDict, b6_f = [10.26, 8.77, 0.623]):
#     """_summary_

#     Args:
#         oeDict (_type_): _description_
#         eeDict (_type_): _description_
#         b6_f (list, optional): [pet, penrt, gwp]. Defaults to [10.26, 8.77, 0.623].

#     Returns:
#         dict: name: [values]
#     """
    
#     df_rows = {}
#     for grp_name, grp_info in eeDict.items():
#         # print(grp_name)
#         rmArea = oeDict[grp_name][0]
#         oe = oeDict[grp_name][1]
#         b6_Matrix = np.round(np.array(b6_f) * oe, 3)
#         conset = ConstructionSet(grp_info, rmArea)
#         byModu = np.column_stack((conset.mod_matrix, b6_Matrix))
#         byConPart = conset.conPart_matrix
#         bySum = conset.sum_matrix + b6_Matrix
        
#         building_id = grp_name.split("_")[0]
#         scale = grp_name.split("_")[1]
#         location = grp_name.split("_")[2]
#         testMode = grp_name.split("_")[3]
#         if "Beton" in grp_name:
#             material_system = "Beton"
#         elif "Holz" in grp_name:
#             material_system = "Holz"
#         else:
#             material_system = None
#         if "Default" in grp_name and material_system is None:
#             material_system = "Beton"
            
            
#         basic_info = [building_id, scale, location, testMode, material_system]
        
#         srf_areas = conset.srf_areas
#         tot_srf_area = sum(srf_areas)
#         external_areas_f = round((srf_areas[0]+srf_areas[2])/ tot_srf_area, 3)
#         wall_areas_f = round((srf_areas[2]+srf_areas[3])/ rmArea, 3)
#         srf_area_per_m2 = tot_srf_area / rmArea
        
#         geo_info = [rmArea, srf_area_per_m2, external_areas_f, wall_areas_f]
        
        
        
#         df_row = [grp_name] + basic_info + geo_info + list(np.round(np.concatenate((bySum.flatten(), byConPart.flatten(), byModu.flatten())) ,3))
#         df_rows[grp_name] = df_row
        
#     return df_rows



# def merge_results(keylist):
    
#     folder_oe_path = path + r"\outputs\for_sim_result"
#     folder_ee_path = path + r"\outputs\for_lca_calc"    
    
#     df_dict = {}
#     for filenameOE in os.listdir(folder_oe_path):
#         if fnmatch(filenameOE, "output*"):  
#             filenameEE = filenameOE.replace("_result", "_ConInfo")

#             oeInfo = get_json_data(folder_oe_path, filenameOE)
#             oeDict = restructure_oe_result(oeInfo)
            
#             try:
#                 eeDict = get_json_data(folder_ee_path, filenameEE)
#             except:
#                 print(f"No matching file found in folder 2 for {filenameOE}")
#             # print(filenameEE)
#             df_rows = calc_LCA(oeDict, eeDict)
#             # print(df_rows)
#             df_dict.update(df_rows)
#             # print(filenameEE, "finish")
#     df_lists =list( df_dict.values())       
#     # df = pd.DataFrame.from_dict(df_dict, orient="index", columns=keylist)
#     df = pd.DataFrame(df_lists, columns=keylist)
#     excel_filename = "output3.xlsx"
#     df.to_excel(excel_filename)
#     # df.to_excel(excel_filename, index_label="RowName")
#     return df
