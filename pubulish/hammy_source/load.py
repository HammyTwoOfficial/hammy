
import os
path = os.path.abspath(os.path.dirname(__file__)) 
import json
import numpy as np

keys_all_vars_objs = [
        "seg0_dist",        #0
        "seg1_dist",        #1
        "seg2_dist",        #2
        "seg3_dist",        #3
        
        "seg0_theta",       #4
        "seg1_theta",       #5
        "seg2_theta",       #6
        "seg3_theta",       #7
        
        "seg0_dep",         #8
        "seg1_dep",         #9
        "seg2_dep",         #10
        "seg3_dep",         #11

        "seg0_pat",         #12
        "seg1_pat",         #13
        "seg2_pat",         #14
        "seg3_pat",         #15

        "cty_pat",          #16
        
        "cty_form",         #17

        "win_ratio_s",        #18
        "win_ratio_n",        #19

        "mat_typ",          #20
        "mat_qua",          #21
        "Max. Flr Nr",                # [0]22
        "Floor Area",                 # [1]23
        "Wall to Flr Ratio",          # [2]24
        "Shape Coef.",                # [3]25
        "Avg. Building Depth",        # [4]26
        "Courtyard Depth",            # [5]27
        
        "Window Ratio Avg.",          # [6]28
        "Window Ratio S",             # [7]29
        "Window Ratio N",             # [8]30
        "Facade Gls. Ratio",          # [9]31
        "Envelop Gls. Ratio",         # [10]32
        "Gls. to Flr Ratio South",    # [11]33
        
        "Facade SW Ratio",            # [12]34
        
        "Courtyard Form Factor",      # [13]35
        "Building Form Factor",       # [14]36
        
        "Material System",            # [15]37
        "Insu Thickness ExWall",      # [16]38
        "Insu Thickness Roof",        # [17]39
        "U-Value ExWall",             # [18]40
        "U-Value RoofCeiling",         # [19]41
        
        "Energy Heating",             # [20]42
        "Energy Cooling",             # [21]43
        "Total Energy Demand",        # [22]44
        "GWP A1-A3",                  # [23]45
        "GWP B4",                     # [24]46
        "GWP C3-C4",                  # [25]47
        "GWP D",                      # [26]48
        "GWP Embed.",                 # [27]49
        "GWP Oper.",                  # [28]50
        "GWP Total"                   # [29]51
]


ref_lib_path = path + r'\data\lib\mass_lib\ref_lib.json'
con_lib_path = path + r'\data\lib\mass_lib\con_lib.json'
# hbjson_path = path + r'\data\03_hbjson.json'

mat_lib_v21_path = path + r'\data\lib\lca_lib\mat_lib_v21.json'
mat_lib_v23_path = path + r'\data\lib\lca_lib\mat_lib_v23.json'
constr_lib_path = path + r'\data\lib\lca_lib\constr_info_ee.json'

# epw_path =  path + r'\lib\siminput\DEU_BW_Stuttgart-Weissenburg.107370_TMYx.epw'
# # epw_path =  path + r'\lib\siminput\TUR_OR_Ordu.170330_TMYx.epw'
# epw_path_2050 =  path + r'\lib\siminput\GRC_TC_Larisa.AP.166480_TMYx.epw'
# epw_path_2070 =  path + r'\lib\siminput\TUR_OR_Ordu.170330_TMYx.epw'





surrogate_daylight_ASE_path = path + r'\data\surrogate_models\ASE_rf_reg_pred_mod.pkl'
surrogate_daylight_sDA_path = path + r'\data\surrogate_models\sDA_rf_reg_pred_mod.pkl'
surrogate_energy_path = path + r'\data\surrogate_models\total_energy_demand_mlp_reg_pred_mod.pkl'
surrogate_energy_2050_path = path + r'\data\surrogate_models\total_energy_demand_mlp_reg_2050_pred_mod.pkl'
surrogate_energy_2070_path = path + r'\data\surrogate_models\total_energy_demand_rf_reg_2070_pred_mod.pkl'

sDA_scalar_path = path + r'\data\surrogate_models\sDA_scaler_model.pkl'
ASE_scalar_path = path + r'\data\surrogate_models\ASE_scaler_model.pkl'
energy_scalar_path = path + r'\data\surrogate_models\energy_scaler_model.pkl'


samples_path = path + r'\data\temp\outputs\00_sample.json'
geo_data_path = path + r'\data\temp\outputs\01_geo_data.json'
result_repos_path = path + r'\data\temp\outputs\02_res_repo.json'
objectives_path = path + r'\data\temp\outputs\03_objs.json'

error_repo_path = path + r'\data\temp\outputs\error_repo\err_samples.json'

sDA_used_feature_ids = [33,24,16,17,26,35,25,23]
sDA_used_feature_ids.sort()
sDA_used_feature_names =[keys_all_vars_objs[idx] for idx in sDA_used_feature_ids]
# sDA_used_feature_ids = [i for i in range(42)]

ASE_used_feature_ids = [33,29,16,35,26,25,34,24,17]
ASE_used_feature_ids.sort()
ASE_used_feature_names =[keys_all_vars_objs[idx] for idx in ASE_used_feature_ids]
# ASE_used_feature_ids = [i for i in range(42)]
# energy_used_feature_ids =  [3,4,2,10,13,7,11,18,19]
energy_used_feature_ids =  [25,26,24,32,35,29,33,40,41]
energy_used_feature_ids.sort()
energy_used_feature_names =[keys_all_vars_objs[idx] for idx in energy_used_feature_ids]
# energy_used_feature_ids = [i for i in range(20)]


pred_settings = {
    'sDA' :{
        'scalar_path': sDA_scalar_path,
        'model_path': surrogate_daylight_sDA_path ,
        'feature_ids' :sDA_used_feature_ids,
        'feature_names' : sDA_used_feature_names
    },
    'ASE' :{
        'scalar_path': ASE_scalar_path,
        'model_path': surrogate_daylight_ASE_path ,
        'feature_ids' :ASE_used_feature_ids,
        'feature_names' : ASE_used_feature_names
    },
    'energy_DE' :{
        'scalar_path': energy_scalar_path,
        'model_path': surrogate_energy_path ,
        'feature_ids' :energy_used_feature_ids,
        'feature_names' : energy_used_feature_names
    },
    'energy_GR' :{
        'scalar_path': energy_scalar_path,
        'model_path': surrogate_energy_2050_path ,
        'feature_ids' :energy_used_feature_ids,
        'feature_names' : energy_used_feature_names
    },
    'energy_TU' :{
        'scalar_path': energy_scalar_path,
        'model_path': surrogate_energy_2070_path ,
        'feature_ids' :energy_used_feature_ids,
        'feature_names' : energy_used_feature_names
    },
    
}


penalty_attributes_path = path + r'\data\penalty_attributes.json'
with open(penalty_attributes_path,"r") as f:
    penalty_attributes = json.loads(f.read())


with open(ref_lib_path,"r") as f:
    ref_lib = json.loads(f.read())
with open(con_lib_path,"r") as f:
    con_lib = json.loads(f.read())
    
with open(mat_lib_v21_path,'r') as f:
    mat_lib_v21 = json.load(f)
with open(mat_lib_v23_path,"r") as f:
    mat_lib_v23 = json.loads(f.read())
with open(constr_lib_path,"r") as f:
    constr_lib = json.loads(f.read()) 


