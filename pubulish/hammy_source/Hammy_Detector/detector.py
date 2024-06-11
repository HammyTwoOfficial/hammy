import numpy as np
import math
from hammy.Hammy_Utils import util, util2
from functools import partial





class SiteDetector:
    def __init__(self,site_data):
        self.site_data = site_data
        self.site_info = self.get_site_info()
    
    def get_site_info(self):
        
        check_site_clockwise = util.check_if_clockwise(self.site_data)
        if check_site_clockwise:
            self.site_data = self.site_data[::-1]
                    
        self.seg_site_data = util.pts_to_segs(self.site_data)
        return self.site_detect()

    
    def get_clean_site(self):

        vertices_convex_site = util2.generate_convex_polygon(self.site_data)
        seg_convex_site = util.pts_to_segs(vertices_convex_site)

        removed_vertex_indices_in_site = util2.find_removed_items(self.seg_site_data, seg_convex_site)
        # the shift point are based on which point you want to delete
        for i in range(len(removed_vertex_indices_in_site)):
            removed_vertex_indices_in_site[i]+=1
        removes_segs_in_site = util2.remove_items_by_index(self.site_data,removed_vertex_indices_in_site)
        
        return removes_segs_in_site
    
    def site_detect(self):
        site_pts = self.get_clean_site()
        seg_cur_site = util.pts_to_segs(site_pts)
        site_info = []
        south_seg_index = 0
        min_sin = 4
        for i in range(len(seg_cur_site)):
            pattern = 0
            r,theta = util2.getFootPoint(seg_cur_site[i])
            theta_sin = math.sin(math.radians(theta))

            if theta_sin < min_sin:
                min_sin = theta_sin
                south_seg_index = i
            for j in range(len(self.seg_site_data)):
                is_equal_seg = util.is_equal_seg(seg_cur_site[i],self.seg_site_data[j])
                if is_equal_seg:
                    pattern = 1
            
            circle_cen = [site_pts[i][0]/2,site_pts[i][1]/2]
            circle_cen = [site_pts[i][0] / 2, site_pts[i][1] / 2]
            distance = [np.sqrt(x ** 2 + y ** 2) for (x, y) in [circle_cen]]
            site_seg_circle = circle_cen+distance

            site_seg_info = [pattern,r,theta,site_seg_circle]
            site_info.append(site_seg_info)

        site_info = site_info[south_seg_index:] + site_info[:south_seg_index]
        
        
        return site_info


class GeoDetector:
    def __init__(self,geo_data,site_info,flr_height):
        self.geo_data = geo_data
        self.site_info = site_info
        self.flr_height = flr_height
        self.geo_abs_info = self.get_geo_info()
        self.geo_uv_info = self.get_geo_uv_info()
    def get_geo_info(self):
        if self.geo_data == None:
            return self.default_geo()
        else:
            return self.geo_detect()
    def get_geo_uv_info(self):
        geo_abs_info = self.geo_abs_info.copy()
        geo_uv_info = util2.get_premap_samples(geo_abs_info,self.site_info)
        return geo_uv_info

    def default_geo(self):
        geo_info = [40,40,40,40,-90,0,90,180,10,10,10,10,1,1,1,1,0,0,0.6,0.6,3,1,4.25]
        return geo_info
    def geo_detect(self):
        geo_info = self.default_geo()
        segs_list_first =[]
        segs_patterns_list = []
        for m in range(len(self.geo_data)):

            geo_flo_data = self.geo_data[m]
            geo_segs = []
            for i in range(len(geo_flo_data)):
                segs = util.pts_to_segs(geo_flo_data[i])
                geo_segs.extend(segs)

            # get site vertival line intersect with segs
            segs_pattern = []
            segs_list = []
            for i in range(4):
                pattern = 0
                seg_list =[]
                seg_num =0
                x,y = util2.polar_to_cartesian(self.site_info[i][1],self.site_info[i][2])
                ver_site = [[0,0],[x,y]]
            
                for j in range(len(geo_segs)):
                    
                    get_intersect = util.line_intersect(ver_site,geo_segs[j])
                    valid,pt = get_intersect
                   
                    if valid == 2:
                        seg_list.append(geo_segs[j])
                        seg_num +=1
                    if seg_num == 2:
                        pattern = 1
                        break
                segs_pattern.append(pattern)
                segs_list.append(seg_list)
                if m == 0 :
                    segs_list_first = segs_list
                    
            segs_patterns_list.append(segs_pattern)
        
        segs_patterns_list = np.array(segs_patterns_list)
        segs_patterns = np.sum(segs_patterns_list, axis=0).tolist()

        ref_seg = []
        has_pat0 =False
        pat0_len =0
        for k in range(len(segs_patterns)):
            if segs_patterns[k] == 0:
                has_pat0 =True
                pat0_len +=1
                geo_info[k] = self.site_info[k][1]
                geo_info[k+4] = self.site_info[k][2]
                if self.site_info[k][1] < 12:
                    geo_info[k+8] = 1
                else:
                    geo_info[k+8] = 12
            else:
                r0,theta0 = util2.getFootPoint(segs_list_first[k][0])
                r1,theta1 = util2.getFootPoint(segs_list_first[k][1])
                if r0>r1:
                    ref_seg.extend(segs_list_first[k][0])
                else:
                    ref_seg.extend(segs_list_first[k][1])
                geo_info[k] = max(r0,r1)
                geo_info[k+4] = theta0
                geo_info[k+8] = abs(r0-r1)
            geo_info[k+12] = segs_patterns[k]
        
        if has_pat0 :

            ref_pts = [list(point) for point in set(tuple(row) for row in ref_seg)]
            if len(ref_pts) ==4:

                center = np.mean(ref_pts, axis=0)
                sorted_points = sorted(ref_pts, key=partial(util2.angle_sort, center))
                total_segs = util.pts_to_segs(sorted_points)
                for seg in total_segs:
                    r,theta = util2.getFootPoint(seg)
                    for u in range(4):
                        if abs(theta-geo_info[u+4])  < 30 :
                           
                            geo_info[u] = r
                            geo_info[u+4] = theta
                            x,y = util2.polar_to_cartesian(r,theta)
            elif len(ref_pts) == 3:
                
                if len(self.geo_data[0]) ==1:
                    segs = util.pts_to_segs(self.geo_data[0][0])
                    non_valid_segs = []
                    for seg in segs:
                        if seg[0] in ref_pts and seg[1] not in ref_pts: 
                            non_valid_segs.append(seg)
                        elif seg[1] in ref_pts and seg[0] not in ref_pts:
                            non_valid_segs.append(seg)
                        else:
                            pass
                    if len(non_valid_segs) ==2:
                        non_valid_pt = util2.straight_line_intersect(non_valid_segs[0],non_valid_segs[1])
                        ref_pts.append(non_valid_pt)  
                else:
                    pass
                center = np.mean(ref_pts, axis=0)
                sorted_points = sorted(ref_pts, key=partial(util2.angle_sort, center))
                total_segs = util.pts_to_segs(sorted_points)
                for seg in total_segs:
                    r,theta = util2.getFootPoint(seg)
                    for u in range(4):
                        if abs(theta-geo_info[u+4])< 30:
                            geo_info[u] = r
                            geo_info[u+4] = theta
            elif len(ref_pts) ==2:
                if len(self.geo_data[0]) ==1:
                    segs = util.pts_to_segs(self.geo_data[0][0])
                    non_valid_segs = []
                    for seg in segs:
                        if seg[0] in ref_pts and seg[1] not in ref_pts: 
                            non_valid_segs.append(seg)
                        elif seg[1] in ref_pts and seg[0] not in ref_pts:
                            non_valid_segs.append(seg)
                        else:
                            pass
                    for non_seg in non_valid_segs:
                        r,theta = util2.getFootPoint(non_seg)
                        for u in range(4):
                            if abs(theta-geo_info[u+4])< 30:
                                geo_info[u] = r
                                geo_info[u+4] = theta                      
            else:
                pass
        if pat0_len ==4:
            geo_info[16] = len(self.geo_data)
            geo_info[17] = 1
            segs = util.pts_to_segs(geo_flo_data[0])
            for q in range(len(segs_pattern)):
                geo_flo_data = self.geo_data[q]
                
                
                r,theta = util2.getFootPoint(segs[q])
                for u in range(4):
                    if abs(theta-geo_info[u+4])  < 30 :
                        geo_info[u+8] = abs(geo_info[u]-r)

        geo_info[22] = self.flr_height
        return geo_info




        

    def get_seg_info(segs):
        segs_info =[]
        for i in range(len(segs)):
            seg_info = util2.get_vertical_line([0,0],segs[i])
            segs_info.append(seg_info)
        return segs_info


class Detection:
    '''
    ini_data = [
    
        site_data = self.ini_data[0]
        geo_data = self.ini_data[1]
        flr_height = self.ini_data[2]
        height_limit = self.ini_data[3]
        area_req = self.ini_data[4]
        user_reqs = self.ini_data[5]
    ]
    

    '''
    def __init__(self,ini_data):
        self.ini_data = ini_data
        self.site_data = self.ini_data[0]
        self.geo_data = self.ini_data[1]
        self.flr_height = self.ini_data[2]
        self.height_limit = self.ini_data[3]
        self.area_req = self.ini_data[4]
        self.user_reqs = self.ini_data[5]

        self.site_detection = SiteDetector(self.site_data)
        self.site_info = self.site_detection.site_info
        self.geo_detection = GeoDetector(self.geo_data,self.site_info,self.flr_height)
        