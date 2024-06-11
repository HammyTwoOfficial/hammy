
# var_range = {
            # "seg0_dist" : [10.5,50,0.01],     0
            # "seg1_dist" : [10.5,50,0.01],     1
            # "seg2_dist" : [10.5,50,0.01],     2
            # "seg3_dist" : [10.5,50,0.01],     3

            # "seg0_theta" : [-120,-60,0.1],    4
            # "seg1_theta" : [-30,30,0.1],      5
            # "seg2_theta" : [60,120,0.1],      6
            # "seg3_theta" : [150,210,0.1],     7

            # "seg0_dep" : [9,14,0.01],       8
            # "seg1_dep" : [9,14,0.01],       9
            # "seg2_dep" : [9,14,0.01],       10
            # "seg3_dep" : [9,14,0.01],       11

            # "seg0_pat" : [0,10,1],            12
            # "seg1_pat" : [0,10,1],            13
            # "seg2_pat" : [0,10,1],            14
            # "seg3_pat" : [0,10,1],            15


            # "cty_pat" : [0,10,1],             16
            # "cty_form" : [0,2,1],             17

            # "win_ratio":[0,1,0.01], s         18
            # "win_ratio":[0,1,0.01], n         19

            # "mat_typ":[0,2,1],                20
            # "mat_qua":[0,2,1]                 21
#                     }

# site_info = [[1, 29.527944155921585, -93.88640490526176,[-18.759864, -13.523554, 23.126154]], 
#            [0, 35.6573130052123, -5.403576051509738, [16.403078, -15.912341, 22.853087]], 
#            [1, 29.20994049951431, 86.11359509473822, [19.169734, 13.336342, 23.352446]], 
#            [1, 35.60023307401975, 176.11359509473823, [-16.769279, 15.777851, 23.024971]]]

                    # ([site_seg_valid,site_dist,site_theta,site_min_valid_theta,site_max_valid_theta])
          
# geo_info = [seg0_dist,seg1_dist,seg2_dist,seg3_dist,
#       seg0_theta,seg1_theta,seg2_theta,seg3_theta,
#       seg0_dep,seg1_dep,seg2_dep,seg3_dep,
#       seg0_pat,,seg1_pat,seg2_pat,seg3_pat,
#       cty_pat,cty_form,
#       win_ratio,
#       mat_typ,mat_qua]
# ]



from hammy.Hammy_Utils import util, util2


class Filter:
    def __init__(self,detection):
        var_range = [[0,1,0.01],
                    [0,1,0.01],
                    [0,1,0.01],
                    [0,1,0.01],

                    [-1,1,0.01],
                    [-1,1,0.01],
                    [-1,1,0.01],
                    [-1,1,0.01],

                    [12,16,0.01],
                    [12,16,0.01],
                    [12,16,0.01],
                    [12,16,0.01],

                    [0,10,1],
                    [0,10,1],
                    [0,10,1],
                    [0,10,1],

                    [0,10,1],
                    [0,1,1],

                    [0.3,0.9,0.01],
                    [0.6,0.6,0.01],

                    [1,3,1],
                    [0.5,1.5,0.01],
                    [2.5,6,0.01]
                    ]
        
        self.var_range = var_range
        self.detection = detection
        self.site_info = self.detection.site_info
        self.geo_uv_info = self.detection.geo_detection.geo_uv_info
        
        self.flr_height = self.detection.flr_height
        self.height_limit= self.detection.height_limit
        self.user_reqs = self.detection.user_reqs
        self.get_var_range()
    
    def get_var_range(self):
        self.constrain()
        for require in self.user_reqs:
            self.set_var_range(require)
        
    ##### function lib #######
    
    def set_var_range(self,require):
        
        ##### flexibility require ###########
        if require == "align with site0":
            self.align_site(0)
        elif require == "align with site1":
            self.align_site(1)
        elif require == "align with site2":
            self.align_site(2)
        elif require == "align with site3":
            self.align_site(3)

        elif require =="coincide_site0":
            self.coincide_site(0)
        elif require =="coincide_site1":
            self.coincide_site(1)
        elif require =="coincide_site2":
            self.coincide_site(2)
        elif require =="coincide_site3":
            self.coincide_site(3)
        
        elif require == "keep_seg0_theta":
            self.keep_seg_theta(0)
        elif require == "keep_seg1_theta":
            self.keep_seg_theta(1)
        elif require == "keep_seg2_theta":
            self.keep_seg_theta(2)
        elif require == "keep_seg3_theta":
            self.keep_seg_theta(3)

        elif require == "keep_seg0_dist":
            self.keep_seg_dist(0)
        elif require == "keep_seg1_dist":
            self.keep_seg_dist(1)
        elif require == "keep_seg2_dist":
            self.keep_seg_dist(2)
        elif require == "keep_seg3_dist":
            self.keep_seg_dist(3)
        
        elif require == "keep_seg0_depth":
            self.keep_seg_depth(0)
        elif require == "keep_seg1_depth":
            self.keep_seg_depth(1)
        elif require == "keep_seg2_depth":
            self.keep_seg_depth(2)
        elif require == "keep_seg3_depth":
            self.keep_seg_depth(3)

        elif require == "freeze_seg0":
            self.freeze_seg(0)
        elif require == "freeze_seg1":
            self.freeze_seg(1)
        elif require == "freeze_seg2":
            self.freeze_seg(2)
        elif require == "freeze_seg3":
            self.freeze_seg(3)

        ##### Grouping require ###########
        elif require == "group_orientation":
            self.group_orientation()
        elif require == "group_shape_factor":
            self.group_shape_factor()
        elif require == "group_functional_factor":
            self.group_functional_factor()
        elif require == "group_cty_bd_form":
            self.group_cty_bd_form()
            
        elif require == "group_material_factor":
            self.group_material_factor()

        elif require == "group_dist":
            self.group_dist()
        elif require == "group_theta":
            self.group_theta()
        elif require == "group_dep":
            self.group_dep()
        elif require == "group_seg_pa":
            self.group_seg_pa()
        elif require == "group_cty_pa":
            self.group_cty_pa()
        elif require == "group_cty_form":
            self.group_cty_form()
        elif require == "group_win_ratio":
            self.group_win_ratio()
        
        elif require == "group_win_and_orientation":
            self.group_win_and_orientation()
        elif require == "group_win_and_area":
            self.group_win_and_area()



        else:
            pass

    ##### Grouping ###########
    def group_dist(self):
        
        fixed_indices = [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
        var_range = self.var_range
        for ind in fixed_indices:
            var_range[ind][0] = var_range[ind][1] =self.geo_uv_info[ind]
        self.var_range = var_range
    
    def group_theta(self):
        
        fixed_indices = [0,1,2,3,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
        var_range = self.var_range
        for ind in fixed_indices:
            var_range[ind][0] = var_range[ind][1] =self.geo_uv_info[ind]
        self.var_range = var_range
    
    def group_dep(self):
        
        fixed_indices = [0,1,2,3,4,5,6,7,12,13,14,15,16,17,18,19,20,21]
        var_range = self.var_range
        for ind in fixed_indices:
            var_range[ind][0] = var_range[ind][1] =self.geo_uv_info[ind]
        self.var_range = var_range
    
    def group_seg_pa(self):
       
        fixed_indices = [0,1,2,3,4,5,6,7,8,9,10,11,16,17,18,19,20,21]
        var_range = self.var_range
        for ind in fixed_indices:
            var_range[ind][0] = var_range[ind][1] =self.geo_uv_info[ind]
        self.var_range = var_range
    
    def group_cty_pa(self):
        
        fixed_indices = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,17,18,19,20,21]
        var_range = self.var_range
        for ind in fixed_indices:
            var_range[ind][0] = var_range[ind][1] =self.geo_uv_info[ind]
        self.var_range = var_range
    
    def group_cty_form(self):
        
        fixed_indices = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,18,19,20,21]
        var_range = self.var_range
        for ind in fixed_indices:
            var_range[ind][0] = var_range[ind][1] =self.geo_uv_info[ind]
        self.var_range = var_range
    
    def group_win_ratio(self):
       
        fixed_indices = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,20,21]
        var_range = self.var_range
        for ind in fixed_indices:
            var_range[ind][0] = var_range[ind][1] =self.geo_uv_info[ind]
        self.var_range = var_range
    
  
    def group_win_and_orientation(self):
        # - all dists
        # - all thetas
        fixed_indices = [8,9,10,11,12,13,14,15,16,17,20,21]
        var_range = self.var_range
        for ind in fixed_indices:
            var_range[ind][0] = var_range[ind][1] =self.geo_uv_info[ind]
        self.var_range = var_range

    def group_win_and_area(self):
        # - all dists
        # - all thetas
        fixed_indices = [4,5,6,7,12,13,14,15,16,17,20,21]
        var_range = self.var_range
        for ind in fixed_indices:
            var_range[ind][0] = var_range[ind][1] =self.geo_uv_info[ind]
        self.var_range = var_range



    def group_orientation(self):
        # - all dists
        # - all thetas
        fixed_indices = [8,9,10,11,12,13,14,15,16,17,18,19,20,21]
        var_range = self.var_range
        for ind in fixed_indices:
            var_range[ind][0] = var_range[ind][1] =self.geo_uv_info[ind]
        self.var_range = var_range

    def group_shape_factor(self):
        # - all dists
        # - all thetas
        # - all depths
        # - all seg patterns
        # - ctyd pattern
        fixed_indices = [17,18,19,20,21]
        var_range = self.var_range
        for ind in fixed_indices:
            var_range[ind][0] = var_range[ind][1] =self.geo_uv_info[ind]
        self.var_range = var_range
    
    def group_functional_factor(self):
        # - all dists
        # - all depths    
        fixed_indices = [4,5,6,7,12,13,14,15,16,17,18,19,20,21]
        var_range = self.var_range
        for ind in fixed_indices:
            var_range[ind][0] = var_range[ind][1] =self.geo_uv_info[ind]
        self.var_range = var_range
    
    def group_cty_bd_form(self):
        # - all seg patterns
        # - ctyd pattern
        fixed_indices = [0,1,2,3,4,5,6,7,8,9,10,11,17,18,19,20,21]
        var_range = self.var_range
        for ind in fixed_indices:
            var_range[ind][0] = var_range[ind][1] =self.geo_uv_info[ind]
        self.var_range = var_range
    

    def group_material_factor(self):
        # - mat_typ
        # - mat_quality
        fixed_indices = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
        var_range = self.var_range
        for ind in fixed_indices:
            var_range[ind][0] = var_range[ind][1] =self.geo_uv_info[ind]
        self.var_range = var_range

    ##### flexibility ###########

    def coincide_site(self,seg_ind):
        var_range = self.var_range
        var_range[seg_ind][0] =var_range[seg_ind][1] = self.geo_uv_info[seg_ind]
        var_range[seg_ind+4][0] = var_range[seg_ind+4][1] = self.site_info[seg_ind][2]
        self.var_range = var_range

    def align_site(self,seg_ind):
        var_range = self.var_range
        var_range[seg_ind+4][0] = var_range[seg_ind+4][1] = self.site_info[seg_ind][2]
        self.var_range = var_range

    def freeze_seg(self,seg_ind):
        var_range = self.var_range
        var_range[seg_ind][0] =var_range[seg_ind][1] = self.geo_uv_info[seg_ind]
        var_range[seg_ind+4][0] = var_range[seg_ind+4][1] = self.geo_uv_info[seg_ind+4]
        var_range[seg_ind+8][0] =var_range[seg_ind+8][1] = self.geo_uv_info[seg_ind+8]
        self.var_range = var_range

    def keep_seg_theta(self,seg_ind):
        var_range = self.var_range
        var_range[seg_ind+4][0] = var_range[seg_ind+4][1] = self.geo_uv_info[seg_ind+4]
        self.var_range = var_range

    def keep_seg_depth(self,seg_ind):
        var_range = self.var_range
        var_range[seg_ind+8][0] =var_range[seg_ind+8][1] = self.geo_uv_info[seg_ind+8]
        self.var_range = var_range
        
    def keep_seg_dist(self,seg_ind):
        var_range = self.var_range
        var_range[seg_ind][0] =var_range[seg_ind][1] = self.geo_uv_info[seg_ind]
        self.var_range = var_range
    
    #######   constrains #############
    def constrain(self):
        self.height_constrain()
        self.site_constrain()
        self.ini_geo_constrain()

    def height_constrain(self):
        var_range = self.var_range
        floor_num_lim = self.height_limit//self.flr_height
        var_range[12][1] = floor_num_lim
        var_range[13][1] = floor_num_lim
        var_range[14][1] = floor_num_lim
        var_range[15][1] = floor_num_lim
        var_range[16][1] = floor_num_lim
        self.var_range = var_range
    def ini_geo_constrain(self):
        var_range = self.var_range
        for i in range(4):
            # geo depth influence segment depth range
            if self.geo_uv_info[i+8] > var_range[i+8][1]:
                var_range[i+8][1] = self.geo_uv_info[i+8]
            elif self.geo_uv_info[i+8] < var_range[i+8][0]:
                var_range[i+8][0] = self.geo_uv_info[i+8]
            else:
                pass
        if self.geo_uv_info[17] ==1:
            var_range[17] == [1,1,1]
        var_range[22] = [self.flr_height-0.5,self.flr_height+0.5,0.1]
        self.var_range = var_range
    def site_constrain(self):
        var_range = self.var_range
        for i in range(4):  
            if_site_valid = self.site_info[i][0]  
            site_depth = self.site_info[i][1] - 3
            depth_site_depth_preremap = util2.remap(site_depth,[0,self.site_info[i][1]],[0,1])
            # site_theta = self.site_info[i][2]
            # site_depth influence segment dist and depth range
            var_range[i][1] = site_depth  
            if site_depth < 12:
                var_range[i] = [depth_site_depth_preremap,depth_site_depth_preremap,0.01]
                var_range[i+4] = [0,0,0.01]
                var_range[i+8] = [1,1,0.01]
                var_range[i+12] = [0,0,1]
                
            elif site_depth < 16 and site_depth >= 12:
                var_range[i] = [depth_site_depth_preremap,depth_site_depth_preremap,0.01]
                var_range[i+4] = [0,0,0.01]
                var_range[i+8][1] = site_depth
            else:
                depth_16_preremap =  util2.remap(16,[0,self.site_info[i][1]],[0,1])
                # depth_site_depth_preremap = util2.remap(site_depth,self.site_info[i][1],[0,1])
                var_range[i] = [depth_16_preremap,depth_site_depth_preremap,0.01]
            
            # site valid influence segemnt valid
            if if_site_valid == 0 :
                var_range[i+12] = [0,0,1]
              
            if self.geo_uv_info[17] ==1:
                var_range[i+8] = [1,site_depth-3,0.01]     

             

        self.var_range = var_range
    
