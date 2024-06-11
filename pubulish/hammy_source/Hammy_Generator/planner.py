from hammy.Hammy_Utils import util, util2

TOL = 1
class Planar:
    def __init__(self,iRequire,mass_data):
        """
        iRequire = {
        "raster_size" : 1.5
        "column_raster" : 4
        "facade_type" : 0
        "zone_type" :0
        "corridor_depth" :2
        }
        """
        self.mass_data = mass_data
        self.mass = self.mass_data.massing
        self.geo = self.mass.geo
        self.sample = self.geo.abs_info
        self.flr_height = self.geo.flr_height
        self.bldg_id = self.geo.bldg_id
        self.win_s = self.geo.abs_info[18]
        self.win_n = self.geo.abs_info[19]

        self.require = iRequire
        self.raster_size = self.require["raster_size"]
        self.column_raster = self.require["column_raster"]
        self.zone_type = self.require["zone_type"]
        self.corridor_depth = self.require["corridor_depth"]

        self.raster_lines,self.special_tiles_total ,self.divide_pts_in_total,self.divide_pts_out_total ,self.win_special_in_total= self.get_raster_lines()
        self.normal_tiles, self.special_tiles ,self.corridor_tiles= self.get_tiles()
        self.activity_zones, self.meeting_zones,  self.office_zones ,self.core_zones= self.set_zone_use()
        self.win_geo_total = self.set_win()

        self.plan_data = [
                            self.activity_zones, 
                            self.meeting_zones,  
                            self.office_zones ,
                            self.special_tiles,
                            self.corridor_tiles,
                            self.core_zones,
                            self.win_geo_total
                         ]
    
    def set_win(self):
        """
        win_ori:
            0: South
            1: North 
        """
        south_scale = self.win_s**0.5
        north_scale = self.win_n**0.5
        win_in_total = self.divide_pts_in_total
        win_out_total = self.divide_pts_out_total

        win_geo_total =[]
        for i, win_out_flr in enumerate(win_out_total):
            win_in_flr = win_in_total[i]
            
            for win_special_outline in self.win_special_in_total[i]:
                (x1,y1),(x2,y2) = win_special_outline
                distance_out_win = util2.calculate_distance((x1,y1),(x2,y2))
                if distance_out_win < TOL:
                    continue
                v_util = [(x2-x1)/distance_out_win,(y2-y1)/distance_out_win]
                vec_x = v_util[0]
                if vec_x < 0:
                    scale = north_scale
                else:
                    scale = south_scale
                hori_x_move_dist = (1-scale)/2*(x2-x1)
                hori_y_move_dist = (1-scale)/2*(y2-y1)
                
                verti_move_dist = (1-scale)/2*self.flr_height
                pt_base0 = win_special_outline[0]
                pt_base1 = win_special_outline[1]
                pt0 = [pt_base0[0]+hori_x_move_dist,pt_base0[1]+hori_y_move_dist,i*self.flr_height+verti_move_dist]
                pt1 = [pt_base1[0]-hori_x_move_dist,pt_base1[1]-hori_y_move_dist,i*self.flr_height+verti_move_dist]
                pt2 = [pt_base1[0]-hori_x_move_dist,pt_base1[1]-hori_y_move_dist,(i+1)*self.flr_height-verti_move_dist]
                pt3 = [pt_base0[0]+hori_x_move_dist,pt_base0[1]+hori_y_move_dist,(i+1)*self.flr_height-verti_move_dist]
                win_pts = [pt0,pt1,pt2,pt3]
                win_geo_total.append(win_pts)
        
            for j, win_out_seg in enumerate(win_out_flr):
                win_in_seg = win_in_flr[j]
                distance_out_seg = util2.calculate_distance(win_out_seg[0],win_out_seg[1])
                
                v_util = [(win_out_seg[1][0] - win_out_seg[0][0])/distance_out_seg,(win_out_seg[1][1] - win_out_seg[0][1])/distance_out_seg]
                vec_x = v_util[0]
                win_in_seg_segs = util.pts_to_segs(win_in_seg)
                win_out_seg_segs = util.pts_to_segs(win_out_seg)
                
                if vec_x < 0:
                    win_ori = 1
                else:
                    win_ori = 0
          
                for k in range(len(win_out_seg_segs)-1):
                    seg_length = util2.calculate_distance(win_out_seg_segs[k][1],win_out_seg_segs[k][0])
                    if seg_length < TOL:
                        continue
                    if win_ori == 0:
                        scale = south_scale
                    else:
                        scale = north_scale
                    
                    hori_x_move_dist = (1-scale)/2*(win_out_seg_segs[k][1][0]-win_out_seg_segs[k][0][0])
                    hori_y_move_dist = (1-scale)/2*(win_out_seg_segs[k][1][1]-win_out_seg_segs[k][0][1])
                    
                    verti_move_dist = (1-scale)/2*self.flr_height
                    pt_base0 = win_out_seg_segs[k][0]
                    pt_base1 = win_out_seg_segs[k][1]
                    pt0 = [pt_base0[0]+hori_x_move_dist,pt_base0[1]+hori_y_move_dist,i*self.flr_height+verti_move_dist]
                    pt1 = [pt_base1[0]-hori_x_move_dist,pt_base1[1]-hori_y_move_dist,i*self.flr_height+verti_move_dist]
                    pt2 = [pt_base1[0]-hori_x_move_dist,pt_base1[1]-hori_y_move_dist,(i+1)*self.flr_height-verti_move_dist]
                    pt3 = [pt_base0[0]+hori_x_move_dist,pt_base0[1]+hori_y_move_dist,(i+1)*self.flr_height-verti_move_dist]
                    win_pts = [pt0,pt1,pt2,pt3]
                    win_geo_total.append(win_pts)
                cty_pts = self.geo.bd_fp[1]
                cty_segs = util.pts_to_segs(cty_pts)
                for k in range(len(win_in_seg_segs)-1):
                    seg_length = util2.calculate_distance(win_in_seg_segs[k][0],win_in_seg_segs[k][1])
                    if seg_length < TOL:
                        continue
                    seg_invalid = False
                    for cty_seg in cty_segs:
                        check_pt0 = util.check_if_on_edge(win_in_seg_segs[k][0],cty_seg[0],cty_seg[1])
                        check_pt1 = util.check_if_on_edge(win_in_seg_segs[k][1],cty_seg[0],cty_seg[1])
                        if check_pt0 or check_pt1 :
                            seg_invalid = True
                            break

                    if i >= self.geo.cty_pattern or seg_invalid == False:
                        if win_ori == 0:
                            scale = north_scale
                        else:
                            scale = south_scale
                        
                        hori_x_move_dist = (1-scale)/2*(win_in_seg_segs[k][1][0]-win_in_seg_segs[k][0][0])
                        
                        hori_y_move_dist = (1-scale)/2*(win_in_seg_segs[k][1][1]-win_in_seg_segs[k][0][1])
                        verti_move_dist = (1-scale)/2*self.flr_height
                        pt_base0 = win_in_seg_segs[k][0]
                        pt_base1 = win_in_seg_segs[k][1]
                        pt0 = [pt_base0[0]+hori_x_move_dist,pt_base0[1]+hori_y_move_dist,i*self.flr_height+verti_move_dist]
                        pt1 = [pt_base1[0]-hori_x_move_dist,pt_base1[1]-hori_y_move_dist,i*self.flr_height+verti_move_dist]
                        pt2 = [pt_base1[0]-hori_x_move_dist,pt_base1[1]-hori_y_move_dist,(i+1)*self.flr_height-verti_move_dist]
                        pt3 = [pt_base0[0]+hori_x_move_dist,pt_base0[1]+hori_y_move_dist,(i+1)*self.flr_height-verti_move_dist]
                        win_pts = [pt0,pt1,pt2,pt3]
                        win_geo_total.append(win_pts)

        return win_geo_total




    def set_zone_use(self):
        zones = self.normal_tiles
        activity_zones =[]
        meeting_zones =[]
        office_zones =[]
        core_zones =[]


        for i, zone_eath_flr in enumerate(zones):
            activity_zones_flr =[]
            meeting_zones_flr =[]
            office_zones_flr =[]
            core_zones_flr =[]
            for j ,zone_each_seg in enumerate(zone_eath_flr):
                activity_zones_seg =[]
                meeting_zones_seg =[]
                office_zones_seg =[]
                core_zones_seg =[]
                for q, zone_each_side in enumerate(zone_each_seg):
                    activity_zones_side =[]
                    meeting_zones_side =[]
                    office_zones_side =[]
                    core_zones_side =[]
                    for k,zone_eath_tile in enumerate(zone_each_side):
                        if k ==0 and q == 0:
                            core_zones_side.append(zone_eath_tile)
                        elif i ==0 :
                            activity_zones_side.append(zone_eath_tile)
                        elif i == 1 and len(zones)>=6:
                            activity_zones_side.append(zone_eath_tile)
                        else:
                            if k < len(zone_each_seg)//3 or k >=len(zone_each_seg) - len(zone_each_seg)//2 :
                                office_zones_side.append(zone_eath_tile)
                            else:
                                meeting_zones_side.append(zone_eath_tile)
                    
                    activity_zones_seg.append(activity_zones_side)
                    meeting_zones_seg.append(meeting_zones_side)
                    office_zones_seg.append(office_zones_side)
                    core_zones_seg.append(core_zones_side)
                

                activity_zones_flr.append(activity_zones_seg)
                meeting_zones_flr.append(meeting_zones_seg)
                office_zones_flr.append(office_zones_seg)
                core_zones_flr.append(core_zones_seg)

            activity_zones.append(activity_zones_flr)
            meeting_zones.append(meeting_zones_flr)
            office_zones.append(office_zones_flr)
            core_zones.append(core_zones_flr)

        return [activity_zones, meeting_zones,  office_zones,core_zones]
    
    def get_tiles(self):
        raster_lines_total = self.raster_lines
        tiles_total = []
        
        corridor_total = []
        for raster_lines_per_floor in raster_lines_total:
            tiles_per_flr =[]
            
            corridor_per_flr =[]
            for i ,raster_lines_per_seg in enumerate(raster_lines_per_floor):
                
                first_raster_line = raster_lines_per_seg[0][-1]
                last_raster_line = raster_lines_per_seg[1][-1]
                
                raster_length = util2.calculate_distance(first_raster_line[0],first_raster_line[1])
                v_util = [(first_raster_line[0][0] - first_raster_line[1][0])/ raster_length, (first_raster_line[0][1] - first_raster_line[1][1])/ raster_length]
                if raster_length >= 12:
                    
                    v_utlize_plus = [v_util[0]*(raster_length/2-self.corridor_depth/2), v_util[1] *(raster_length/2-self.corridor_depth/2)]
                    v_utlize_minus = [-1*v_util[0]*(raster_length/2-self.corridor_depth/2), -1*v_util[1]*(raster_length/2-self.corridor_depth/2)]
                    corridor_pt0 = util2.move_point_by_vector(first_raster_line[0],v_utlize_minus)
                    corridor_pt1 = util2.move_point_by_vector(first_raster_line[1],v_utlize_plus)
                    corridor_pt2 = util2.move_point_by_vector(last_raster_line[1],v_utlize_plus)
                    corridor_pt3 = util2.move_point_by_vector(last_raster_line[0],v_utlize_minus)
                    corridor_per_seg = [[corridor_pt0,corridor_pt1,corridor_pt2,corridor_pt3]]
                else:
                
                    v_utlize_minus = [-1*v_util[0]*self.corridor_depth, -1*v_util[1]*self.corridor_depth]
                    corridor_pt0 = first_raster_line[0]
                    corridor_pt1 = util2.move_point_by_vector(first_raster_line[0],v_utlize_minus)
                    corridor_pt2 = util2.move_point_by_vector(last_raster_line[0],v_utlize_minus)
                    corridor_pt3 = last_raster_line[0]
                    corridor_per_seg = [[corridor_pt0,corridor_pt1,corridor_pt2,corridor_pt3]]
                corridor_per_flr.append(corridor_per_seg)
                
                tiles_per_seg =[]
                for side_tiles in raster_lines_per_seg:
                    tiles_per_seg_per_side =[]
                    for j in range(len(side_tiles)-1):
                        tile = side_tiles[j] + side_tiles[j+1][::-1]
                        
                        if raster_length >= 12:
                            
                            v_utlize_plus = [v_util[0]*(raster_length/2-self.corridor_depth/2), v_util[1]*(raster_length/2-self.corridor_depth/2)]
                            v_utlize_minus = [-1*v_util[0]*(raster_length/2-self.corridor_depth/2), -1*v_util[1]*(raster_length/2-self.corridor_depth/2)]
                            tile0_pt0 = tile[1]
                            tile0_pt1 = util2.move_point_by_vector(tile[1],v_utlize_plus)
                            tile0_pt2 = util2.move_point_by_vector(tile[2],v_utlize_plus)
                            tile0_pt3 = tile[2]
                            tile0 = [tile0_pt0,tile0_pt1,tile0_pt2,tile0_pt3]

                            tile1_pt0 = util2.move_point_by_vector(tile[0],v_utlize_minus)
                            tile1_pt1 = tile[0]
                            tile1_pt2 = tile[3]
                            tile1_pt3 = util2.move_point_by_vector(tile[3],v_utlize_minus)
                            tile1 = [tile1_pt0,tile1_pt1,tile1_pt2,tile1_pt3]

                            tiles_per_seg_per_side.append([tile0,tile1])
                        else:
                            v_utlize_minus = [-1*v_util[0]*self.corridor_depth, -1*v_util[1]*self.corridor_depth]
                            
                            tile0_pt0 = util2.move_point_by_vector(tile[0],v_utlize_minus)
                            tile0_pt1 = tile[1]
                            tile0_pt2 = tile[2]
                            tile0_pt3 = util2.move_point_by_vector(tile[3],v_utlize_minus)
                            tile0 = [tile0_pt0,tile0_pt1,tile0_pt2,tile0_pt3]

                            tiles_per_seg_per_side.append([tile0])
                    tiles_per_seg.append(tiles_per_seg_per_side) 

                
                tiles_per_flr.append(tiles_per_seg)
                
            tiles_total.append(tiles_per_flr)
            
            corridor_total.append(corridor_per_flr)
        return [tiles_total,self.special_tiles_total,corridor_total]
            
    def get_raster_lines(self):
        
        building_data  = self.geo.get_footprint_for_display()
        floor_fps = building_data[0]
        cty_fps = building_data[1]
        flo_seg_valid_nums = building_data[2]
        
        flr_patterns = self.geo.flr_patterns

        raster_lines_total = []
        special_tiles_total =[]
        divide_pts_in_total = []
        divide_pts_out_total =[]
        win_special_in_total =[]
        for m in range(len(floor_fps)):
            geo_flo_data = floor_fps[m]
            geo_segs = []
            for i in range(len(geo_flo_data)):
                segs = util.pts_to_segs(geo_flo_data[i])
                geo_segs.extend(segs)
            if flo_seg_valid_nums[m] == 4:
                segs_cty = util.pts_to_segs(cty_fps[::-1])
                geo_segs.extend(segs_cty)

            
            raster_lines_per_flor = []
            special_tiles_per_flor =[]
            divide_pts_in_flor = []
            divide_pts_out_flor =[]
            win_special_per_flor =[]
            
            for i in range(4):

                column_span = self.raster_size * self.column_raster
                if flr_patterns[m][i] != 0:
                    valid =0
                    
                    pt_out = util2.polar_to_cartesian(self.sample[i],self.sample[i+4])
                    pt_in = util2.polar_to_cartesian(self.sample[i]-self.sample[i+8],self.sample[i+4])

                    for i,seg in enumerate(geo_segs):

                        if_pt_out_on_seg = util.check_if_on_edge(pt_out,seg[0],seg[1])
                        if_pt_in_on_seg = util.check_if_on_edge(pt_in,seg[0],seg[1])

                        if if_pt_out_on_seg:
                            seg_out = seg
                            valid +=1
                        
                        if if_pt_in_on_seg:
                            seg_in = seg
                            valid +=1
                        if  valid != 2 and i == len(geo_segs)-1:
                            valid_special =0
                           
                            for i,seg in enumerate(geo_segs):
                                if_pt_out_on_seg_extend = util2.is_slope_matching((pt_out,seg[0]),(pt_out,seg[1]))
                                if_pt_in_on_seg_extend = util2.is_slope_matching((pt_in,seg[0]),(pt_in,seg[1]))
                                if if_pt_out_on_seg_extend:
                                    seg_out = seg
                                    valid_special +=1
                            
                                if if_pt_in_on_seg_extend:
                                    seg_in = seg
                                    valid_special +=1

                                if valid_special ==2:
                                    length_seg_in = util2.calculate_distance(seg_in[0],seg_in[1])
                                    if length_seg_in <column_span:
                                        column_span = length_seg_in-1
                                    vec_seg_in_move = [(seg_in[1][0] - seg_in[0][0])/length_seg_in*column_span,(seg_in[1][1] - seg_in[0][1])/length_seg_in*column_span]
                                    pt_in = util2.move_point_by_vector(seg_in[0],vec_seg_in_move)
                                    pt_out_polar = util2.getFootPoint(seg_out,pt_in)
                                    pt_out = util2.polar_to_cartesian(pt_out_polar[0],pt_out_polar[1])
                                    valid =2
                                  
                        if valid == 2:
                            try:
                                raster_lines_per_seg =[]
                                special_tiles_per_seg =[]
                                divide_pts_in_seg =[]
                                divide_pts_out_seg =[]
                                for k in range(2):

                                    divide_pts_in = util2.divide_line_by_length(pt_in,seg_in[k],column_span)
                                    

                                    if len(divide_pts_in)>2:
                                        distance_last_two = util2.calculate_distance(divide_pts_in[-1],divide_pts_in[-2])
                                    
                                        if distance_last_two < column_span/2:
                                            divide_pts_in = divide_pts_in[:-2] +divide_pts_in[-1:]
                                    divide_pts_out  = []

                                    
                                    v_pt_in_out = [pt_out[0]-pt_in[0],pt_out[1]-pt_in[1]]
                                    
                                    raster_lines_per_seg_per_side =[]
                                    special_tiles_per_seg_per_side =[]
                                    
                                    for i,pt in enumerate(divide_pts_in):
                                        
                                        divide_pt_out = util2.move_point_by_vector(pt,v_pt_in_out)

                                        if i == len(divide_pts_in)-1:
                                            check_if_equal_pt0 = util.is_equal_pt(divide_pt_out,seg_out[0])
                                            check_if_equal_pt1 = util.is_equal_pt(divide_pt_out,seg_out[1])
                                            if_pt_out_on_seg_out = util.check_if_on_edge(divide_pt_out,seg_out[0],seg_out[1])
                                            if check_if_equal_pt0 or check_if_equal_pt1 or if_pt_out_on_seg_out == False:
                                                if k == 0:
                                                    divide_pt_out = seg_out[1]
                                                    divide_pts_in[i] = seg_in[0]
                                                    
                                                    tiles_special_on_seg0 = [seg_in[0],seg_out[1],divide_pts_out[-1],divide_pts_in[i-1]]
                                                    # print(tiles_special_on_seg0)
                                                    win_special = [seg_out[1], seg_in[0]]
                                                else:
                                                    divide_pt_out = seg_out[0]
                                                    divide_pts_in[i] = seg_in[1]
                                                    
                                                    tiles_special_on_seg0 = [seg_in[1],seg_out[0],divide_pts_out[-1],divide_pts_in[i-1]]
                                                    # print(tiles_special_on_seg0)
                                                    win_special = [seg_in[1],seg_out[0]]
                                                for seg in geo_segs:
                                                    check_if_equal_seg = util.is_equal_seg(seg,win_special)
                                                    if check_if_equal_seg:
                                                        win_special_per_flor.append(win_special)
                                                divide_pts_out.append(divide_pt_out)
                                                special_tiles_per_seg_per_side.append(tiles_special_on_seg0)
                                                break

                                            
                                            if k ==0:
                                                tiles_special0 = [seg_in[0],seg_out[1],divide_pt_out]
                                                win_special = [divide_pt_out,seg_out[1]]
                                            else:
                                                tiles_special0 = [seg_in[1],seg_out[0],divide_pt_out]
                                                win_special = [seg_out[0],divide_pt_out]
                                            win_special_per_flor.append(win_special)
                                            special_tiles_per_seg_per_side.append(tiles_special0)
                                            for seg in geo_segs:
                                                if k == 0:
                                                    win_special = [seg_out[1],seg_in[0]]
                                                    check_if_equal_seg = util.is_equal_seg(seg,win_special)
                                                    if check_if_equal_seg:
                                                        win_special_per_flor.append(win_special)
                                                else:
                                                    win_special = [seg_in[1],seg_out[0]]
                                                    check_if_equal_seg = util.is_equal_seg(seg,win_special)
                                                    if check_if_equal_seg:
                                                        win_special_per_flor.append(win_special)
                                        raster_line = [pt,divide_pt_out]
                                        divide_pts_out.append(divide_pt_out)
                                        raster_lines_per_seg_per_side.append(raster_line)
                                    




                                    if k == 0:
                                        divide_pts_out_seg.extend(divide_pts_out[::-1])
                                        divide_pts_in_seg.extend(divide_pts_in[::-1])
                                    else:
                                        divide_pts_out_seg.extend(divide_pts_out[1:])
                                        divide_pts_in_seg.extend(divide_pts_in[1:])
                                    raster_lines_per_seg.append(raster_lines_per_seg_per_side)
                                    special_tiles_per_seg.append(special_tiles_per_seg_per_side)
                                divide_pts_in_flor.append(divide_pts_in_seg)
                                divide_pts_out_flor.append(divide_pts_out_seg[::-1])
                            
                                raster_lines_per_flor.append(raster_lines_per_seg)
                                special_tiles_per_flor.append(special_tiles_per_seg)
                                break
                            except:
                                pass
                    
            win_special_in_total.append(win_special_per_flor)
            divide_pts_in_total.append(divide_pts_in_flor)
            divide_pts_out_total.append(divide_pts_out_flor)
            raster_lines_total.append(raster_lines_per_flor)
            special_tiles_total.append(special_tiles_per_flor)
            
        return raster_lines_total,special_tiles_total,divide_pts_in_total,divide_pts_out_total,win_special_in_total
