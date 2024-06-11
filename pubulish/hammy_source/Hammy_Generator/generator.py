import numpy as np
from hammy.Hammy_Utils import util, util2, util3

from datetime import datetime

TOL = 1e-4

class Line:
    def __init__(self, d, theta_deg,angle_delta):
        self.d = d
        self.theta_deg = theta_deg
        self.angle_delta = angle_delta
        
        self.x = d * np.cos(np.deg2rad(theta_deg))
        self.y = d * np.sin(np.deg2rad(theta_deg))
        self.theta_deg += self.angle_delta
        
        self.m = np.tan(np.deg2rad(self.theta_deg - 90))
        self.n = 1
    
        if abs(theta_deg%180)== 0:
            self.n = 0
            self.m = 1

    
    def find_intersection(self, other):
        if abs(self.m - other.m) < TOL and abs(self.n - other.n) < TOL:
            return None
        elif self.m ==1 :
            x_intersection = self.x
            y_intersection = other.m * (self.x - other.x) + other.y
        elif other.m ==1:
            x_intersection = other.x
            y_intersection = self.m * (other.x - self.x) + self.y
        else:
            x_intersection = (other.y - self.y + self.m * self.x - other.m * other.x) / (self.m - other.m)
            y_intersection = self.m * (x_intersection - self.x) + self.y
        return [x_intersection, y_intersection]
    

class Segment:
    """
    iSegConfig=[100,45,30,0,30,0]
    [d,theta,delta_d_cty,delta_theta_cty,delta_d,delta_theta]
    """
   
    def __init__(self,iSegConfig) :
        
        self.d =iSegConfig[0]
        self.theta_deg = iSegConfig[1]
        self.cty_d =iSegConfig[2]
        self.cty_angle =iSegConfig[3]
        self.d_delta =iSegConfig[4]
        self.angle_delta = iSegConfig[5]
        
        
        self.bd_out = Line(self.d,self.theta_deg,0)
        self.bd_in = Line(self.d-self.d_delta,self.theta_deg,self.angle_delta)
        self.bd_cty = Line(self.d-self.cty_d,self.theta_deg,self.cty_angle)
        

class Refline:
    """   

    iSegList = 
    [
        [d,theta,delta_d_cty,delta_theta_cty,delta_d,delta_theta],
        [d,theta,delta_d_cty,delta_theta_cty,delta_d,delta_theta],
        [d,theta,delta_d_cty,delta_theta_cty,delta_d,delta_theta],
        [d,theta,delta_d_cty,delta_theta_cty,delta_d,delta_theta]
    ]
    """
    def __init__(self,iSegList) :
        segList = []
        self.segNum = len(iSegList)
        if self.segNum !=4:
            return None
        for i in range(self.segNum):
            segment = Segment(iSegList[i])
            segList.append(segment)
        self.segList = segList
        self.pts_out , self.pts_in,self.pts_cty = self.get_points()
    def get_points(self):
        pts_out =[]
        pts_in =[]
        pts_cty =[]
        for i in range(self.segNum):
            pt_out = self.segList[i].bd_out.find_intersection(self.segList[i-1].bd_out)
            pt_in = self.segList[i].bd_in.find_intersection(self.segList[i-1].bd_in)
            pt_cty = self.segList[i].bd_cty.find_intersection(self.segList[i-1].bd_cty)

            pts_cty.append(pt_cty)
            pts_out.append(pt_out)
            pts_in.append(pt_in)
       
        return pts_out,pts_in,pts_cty


class Floor:
    """ 
    example:  
    iFlorInfo = [
                    iSegList = [
                                    [d,theta,delta_d_cty,delta_theta_cty,delta_d,delta_theta],
                                    [d,theta,delta_d_cty,delta_theta_cty,delta_d,delta_theta],
                                    [d,theta,delta_d_cty,delta_theta_cty,delta_d,delta_theta],
                                    [d,theta,delta_d_cty,delta_theta_cty,delta_d,delta_theta]
                                ],
                    seg_pattern = [7,4,6,3]  ## this segment has how many floors
                ]
    if_corner_vertical = True or False
    fp_from_last =[
                    [pt1],[pt2],[pt3],.....
                    ] ## list of points from last floor footprint,  if this floor is 0G fp_from_last =[]

    """
    def __init__(self,iFlorInfo,building_seg_pattern):
        self.iSegList = iFlorInfo[0]
        self.seg_pattern = iFlorInfo[1]
        
        self.segNum = len(self.iSegList)
        self.refline= Refline(self.iSegList)
        self.building_seg_pattern = building_seg_pattern
        self.footprint = self.get_footprint()

    def __str__(self):
        return self.footprint
    def get_cty_footprint(self):
        return self.refline.pts_cty

    def get_footprint(self):
        seg_valid_num = sum(1 for num in self.seg_pattern if num > 0)
        self.seg_valid_num = seg_valid_num
        
        if self.seg_valid_num ==0:
            footprints=[]
            return footprints

        elif self.seg_valid_num == self.segNum:
            footprints = [self.refline.pts_out]
            return footprints
        else:
            pts_out = self.refline.pts_out
            pts_in = self.refline.pts_in
            seg_out = util.pts_to_segs(pts_out)
            seg_in = util.pts_to_segs(pts_in)
            insert_pos = []
            insert_element =[]
            insert_plus=0
            for i in range(len(self.building_seg_pattern)):
                if self.building_seg_pattern[i] == 0:
                    check_if_same_pt0 = util.is_equal_pt(pts_in[i],pts_out[i])
                    i_plus = (i+1)%len(seg_in)
                    if check_if_same_pt0 ==False:
                        insert_plus+=1
                        (x1,y1),(x2,y2) = seg_out[i-1]
                        vertical_line_start = [[x2,y2],[y2-y1+x2,x1-x2+y2]]
                        pts_in[i] = util2.straight_line_intersect(seg_in[i-1],vertical_line_start)
                        insert_pos.append(i+insert_plus)
                        insert_element.append(pts_in[i])
                        
                    check_if_same_pt1 = util.is_equal_pt(pts_in[i_plus],pts_out[i_plus])
                    if check_if_same_pt1 ==False:
                        insert_plus+=1
                        (x3,y3),(x4,y4) = seg_out[i_plus]
                        vertical_line_start = [[x3,y3],[y4-y3+x3,x3-x4+y3]]
                        pts_in[i_plus] = util2.straight_line_intersect(seg_in[i_plus],vertical_line_start)
                        insert_pos.append(i+insert_plus)
                        insert_element.append(pts_in[i_plus])
                        
            for j in range(len(insert_pos)):
                pts_out = pts_out[:insert_pos[j]] + [insert_element[j]] + pts_out[insert_pos[j]:]
                
            seg_out = util.pts_to_segs(pts_out)
            seg_in = util.pts_to_segs(pts_in)

            seg_total = util.boolean_difference(seg_out,seg_in,is_splited = False)[0]
            
            footprints=[]
            for i in range(len(seg_total)):
                footprint=util.segs_to_pts(seg_total[i])
                footprints.append(footprint)
            
        if len(footprints)>2:
            return None
        return footprints 



class Geometry:
    """
    example : 
        new_iBdConfig = {
        "bldg_id": 21,
        "flr_height": 4.5,
        "seg_standard_info": [
            [40, 20, 20, 0],
            [40, 90, 20, 0],
            [40, -180, 20, 0],
            [40, 270, 20, 0]
        ],
      
        "seg_pattern": [7,4,6,3],
        "courtyard_pattern":5
    }
    """
    def __init__(self,abs_info):
        self.abs_info = self.get_stable_sample(abs_info)
        self.bldg_id = self.make_iter_id()
        self.seg_pattern = [self.abs_info[12],self.abs_info[13],self.abs_info[14],self.abs_info[15]]
        self.flr_height = self.abs_info[22]
        self.cty_pattern = self.abs_info[16]
        self.cty_form = self.abs_info[17]


        self.seg_standard_info = [
                                        [self.abs_info[0], self.abs_info[4], self.abs_info[8], 0],
                                        [self.abs_info[1],self.abs_info[5],self.abs_info[9], 0],
                                        [self.abs_info[2],self.abs_info[6],self.abs_info[10], 0],
                                        [self.abs_info[3],self.abs_info[7],self.abs_info[11], 0]
                                    ]

        for i in range(len(self.seg_pattern)):
            if self.seg_pattern[i]==0:
                self.seg_standard_info[i][3] =  (self.seg_standard_info[i-2][1]+180)-self.seg_standard_info[i][1]
        self.max_seg_flo_num = max(self.seg_pattern)
        self.max_flo_num = max(self.max_seg_flo_num,self.cty_pattern)
        
        self.flr_patterns = util.pattern_tranfer(self.seg_pattern)
        self.bd_fp = self.get_floor_footprint()
    
    @staticmethod
    def get_stable_sample(sample):
        sample[12] = int(sample[12])
        sample[13] = int(sample[13])
        sample[14] = int(sample[14])
        sample[15] = int(sample[15])
        sample[16] = int(sample[16])
        sample[17] = int(sample[17])
        sample[20] = int(sample[20])
        return sample

    @staticmethod
    def make_iter_id():
        curr_datetime = datetime.now()
        iter_id = curr_datetime.strftime("%m%d%H%M%S%f")
        return iter_id
    def get_floor_footprint(self):
        
        seg_old_info = self.seg_standard_info
        floors_fp = []
        flo_seg_valid_nums =[]
        seg_new_info = seg_old_info

        self.flr_patterns = util.pattern_tranfer(self.seg_pattern)
        if self.seg_pattern == [0,0,0,0]:
            flo_pattern = [0,0,0,0]
            for j in range(len(flo_pattern)):
                seg_new_info[j].extend([0,0])
            iFlorInfo = [self.seg_standard_info,flo_pattern]
            floor = Floor(iFlorInfo,[0,0,0,0])
            cty_fp =  floor.refline.pts_cty
        else:
            for i in range(self.max_seg_flo_num):
                
                flo_pattern = self.flr_patterns[i]

                
                for j in range(len(flo_pattern)):                   
                    
                    seg_new_info[j]= [seg_new_info[j][0],seg_new_info[j][1],seg_new_info[j][2],seg_new_info[j][3],seg_new_info[j][2],seg_new_info[j][3]]
                    if flo_pattern[j] == 0:
                        seg_new_info[j]= [seg_new_info[j][0],seg_new_info[j][1],seg_new_info[j][2],seg_new_info[j][3],0,0]
     
                iFlorInfo = [self.seg_standard_info,flo_pattern]
                floor = Floor(iFlorInfo,self.seg_pattern)
                
                flo_seg_valid_num = floor.seg_valid_num
                floor_fp = floor.footprint
                cty_fp = floor.refline.pts_cty
                
                flo_seg_valid_nums.append(flo_seg_valid_num)
                floors_fp.append(floor_fp)
                    
        
        res_flr_fp = floors_fp
        self.flo_seg_valid_nums = flo_seg_valid_nums
        
        return res_flr_fp, cty_fp
    
    
    
    def get_footprint_for_display(self):
        return [self.bd_fp[0],self.bd_fp[1],self.flo_seg_valid_nums,self.flr_height,self.cty_pattern]









