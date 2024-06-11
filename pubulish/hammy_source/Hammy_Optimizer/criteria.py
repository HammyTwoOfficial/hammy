import numpy as np

class Criteria:
    def __init__(self, 
                 objectives, 
                 penalty, 
                 attributes = {
                     "weight_gwp": 0.616,
                     "weight_p_hierachy": [0.5, 0.5, 0.25],     # or [0.6, 0.3, 0.1] for ws
                     "weight_penalty": 1,                       # {1, 0.5} for ws / wp
                     "items_p_func": [
                            "exp",                              # p_shape           [0]
                            "sqrt",                             # p_min_area        [1]
                            "linear",                           # p_max_area        [2]
                            "sqrt",                             # p_site            [3]
                            "sqrt",                             # p_seg_size        [4]
                            "linear",                           # p_ct_size         [5]
                            "sqrt",                             # p_angle           [6]
                            "sqrt",                             # p_sda             [7]
                            "sqrt",                             # p_ase             [8]
                            "linear",                           # p_mat             [9]
                            "sqrt",                             # p_seg_height      [10]
                            "sqrt",                             # p_ct_height       [11]
                            "sqrt",                             # p_ct_form         [12]
                            "sqrt"                              # p_ct_area         [13]
                        ],
                     "item_strategy": "weighted_prod",          # or "weighted_sum"
                     "p_strategy": "weighted_prod",             # or "weighted_sum"
                     "c_strategy": "weighted_prod"              # or "weighted_sum"
                    }
                 ):

        
        self.objectives = objectives
        self.penalty = penalty
        self.attributes = attributes
        
        self.weight_gwp = self.attributes["weight_gwp"]
        self.weight_energy = 1- self.weight_gwp
        self.weight_penalty = self.attributes["weight_penalty"]
        
        self.items_p_func = self.attributes["items_p_func"]
        self.w_valid, self.w_functional, self.w_prefer = self.attributes["weight_p_hierachy"]
        
        # get strategies
        self.p_item_strategy = self.attributes["item_strategy"]
        self.p_strategy = self.attributes["p_strategy"]
        self.c_strategy = self.attributes["c_strategy"]
        
        self.tot_energy = self.objectives.energy_carbon_arr[2]
        self.gwp_embed = self.objectives.energy_carbon_arr[7]
        self.criteria = self.calc_criteria()

        self.p_items = self.apply_p_functions()
        self.group_penalty()
        self.penalty_val = self.apply_penalty_strategy()
        self.p_criteria = self.calc_penalized_criteria()
        
    
    def calc_criteria(self):
        self.gwp_embed_norm = self.gwp_embed / 10
        self.tot_energy_norm = (self.tot_energy - 90) / (600 - 90)
        
        if self.gwp_embed_norm > 1:
            self.gwp_embed_norm = 1
        if self.tot_energy_norm > 1:
            self.tot_energy_norm = 1
        
        criteria = self.weight_gwp * self.gwp_embed_norm + self.weight_energy * self.tot_energy_norm
        return criteria

        
        
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
    
    def apply_p_functions(self):
        p_arr = []
        for p, func in zip(self.penalty.p_items, self.items_p_func):
            p = self.p_func(p, func)
            p_arr.append(p)
        return p_arr       



    def group_penalty(self):
        p_shape = self.p_items[0]
        p_area = max(self.p_items[1], self.p_items[2])
        p_site = self.p_items[3]
        p_size = max(self.p_items[4], self.p_items[5])
        p_angle = self.p_items[6]
        p_visual = self.p_items[7] + self.p_items[8]
        p_mat = self.p_items[9]
        p_seg_h = self.p_items[10]
        p_ct_h = max(self.p_items[11], self.p_items[12])
        p_ct_area = self.p_items[13]
        
        self.p_valid_arr = [
            p_shape,
            p_area,
            p_site
        ]
        
        self.p_functional_arr = [
            p_size,
            p_angle,
            p_visual,
            p_mat
        ]

        self.p_prefer_arr = [
            p_seg_h,
            p_ct_h,
            p_ct_area
        ]
        
        self.p_grps_arr = self.p_valid_arr + self.p_functional_arr + self.p_prefer_arr
        
        # calculate group penalty in hierachy
        if self.p_item_strategy == "weighted_sum":
            self.p_valid = sum(self.p_valid_arr)
            self.p_functional = sum(self.p_functional_arr)
            self.p_prefer = sum(self.p_prefer_arr)
        else:
            self.p_valid = float(np.prod(np.asarray(self.p_valid_arr) + 1))
            self.p_functional = float(np.prod(np.asarray(self.p_functional_arr) + 1))
            self.p_prefer = float(np.prod(np.asarray(self.p_prefer_arr) + 1))
        
        
        
    def apply_penalty_strategy(self):
        
        if self.p_strategy == "weighted_sum":
            max_p = 2 * self.w_valid + 4 * self.w_functional + 3 * self.w_prefer
            # normalized for weighted sum
            p_val = (self.p_valid * self.w_valid + self.p_functional * self.w_functional + self.p_prefer * self.w_prefer) / max_p
            
        else:
            p_val = self.p_valid ** self.w_valid * self.p_functional ** self.w_functional * self.p_prefer ** self.w_prefer
            
        return p_val
    
    
    def calc_penalized_criteria(self):
        if self.c_strategy == "weighted_sum":
            p_criteria = self.criteria + self.penalty_val * self.weight_penalty
        else:
            p_criteria = self.criteria * self.penalty_val ** self.weight_penalty
            
        return p_criteria