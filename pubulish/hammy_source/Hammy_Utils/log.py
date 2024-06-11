
class Entity:
    def __init__(self, 
                 detection,      # optional
                 sample,        # optional
                 geometry,       
                 objectives,    # optional 
                 zoning,        # optional 
                 criteria       # optional 
                 ):
    
        self.detection = detection
        self.sample = sample
        self.geometry = geometry
        self.objectives = objectives
        self.zoning = zoning
        self.criteria = criteria
        
        # get from geo
        self.bldg_id = None
        self.abs_sample = None
        
        # get from detection
        self.uv_sample = None
        self.area_req = None
        self.user_reqs = None
        self.requirements = []
        
        # get from objectives
        self.isValid = None
        self.design_objs = None
        self.mat_objs = None
        self.energy_carbon_objs = None
        self.daylight_objs = None
        self.obj_log = []
        
        # get from zoning
        self.plan_settings = None
        
        # get from criteria
        self.crit_ori = None
        self.crit_p = None
        
        self.penalty_items = None
        self.penalty_val = None
        self.penalty_attributes = None
        
        self.penalty_thresholds = None
        self.calibrations = None
        
        self.penalty_log = []
        self.criteria_log = []

        # setting log
        self.setting_log = []

        self.entity_info = self.get_entity_info()
    
    def get_entity_info(self):

        self.bldg_id = self.geometry.bldg_id
        self.abs_sample = self.geometry.abs_info
                
        if self.detection:
            self.uv_sample = self.sample
            self.area_req = self.detection.area_req
            self.user_reqs = self.detection.user_reqs
            self.requirements = [self.area_req, self.user_reqs]
        
        if self.objectives:
            self.isValid = self.objectives.check_valid
            
            self.design_objs = self.objectives.design_fact_arr 
            self.mat_objs = self.objectives.mat_fact_arr
            self.energy_carbon_objs = self.objectives.energy_carbon_arr
            self.daylight_objs = self.objectives.daylight_objs_arr
            self.obj_log = self.design_objs + self.mat_objs + self.energy_carbon_objs + self.daylight_objs
        
        if self.zoning:
            self.plan_settings = self.zoning.require
              
        if self.criteria:
            self.crit_ori = self.criteria.criteria
            self.crit_p = self.criteria.p_criteria
            
            self.penalty_items = self.criteria.p_items
            self.penalty_val = self.criteria.penalty_val
            self.penalty_attributes = self.criteria.attributes
            
            self.penalty_assumptions = self.criteria.penalty.assumptions
            
        self.penalty_log = [self.penalty_items, self.penalty_val]    
        self.criteria_log = [self.crit_ori, self.crit_p]
        self.setting_log = [
            self.plan_settings,
            self.penalty_assumptions,
            self.penalty_attributes
        ]
        
        entity_info  = [
            self.isValid,
            self.bldg_id,
            self.uv_sample,
            self.abs_sample,
            self.obj_log,
            self.criteria_log,
            self.penalty_log,
            self.requirements,
            self.setting_log
        ]
    
        return entity_info