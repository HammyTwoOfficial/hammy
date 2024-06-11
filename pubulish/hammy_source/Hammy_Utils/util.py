
import numpy as np
import math
import copy
TOL = 1e-3


def check_if_clockwise(pts):
        """ This method is to check if a list of pts is ordered clockwise or counterclockwise.

        Args:
            pts (np_array): array of pts, each pt in form of [x, y]

        Returns:
            bool: True as clockwise
        """
        pts_arr = np.asarray(pts)
        value = np.cross(pts_arr[1] - pts_arr[0], pts_arr[2] - pts_arr[0])
        # means clockwise -> hole
        return value < 0                                      


def is_equal_pt(pt1, pt2):
    """ 
    Check two points are the same

    Args:
        pt1 (list): [x1, y1]
        pt2 (list): [x2, y2]

    Returns:
        bool: True if equal
    """

    if abs(pt1[0] - pt2[0]) < TOL and abs(pt1[-1] - pt2[-1]) < TOL:
        return True
    else:
        return False
    
    
def is_equal_seg(seg1, seg2):
    """
    Check two segments are the same

    Args:
        seg1 (list(list)): 2,2
        seg2 (list(list)): 2,2

    Returns:
        bool: True if equal
    """
    if is_equal_pt(seg1[0], seg2[0]) and is_equal_pt(seg1[1], seg2[1]):
        return True
    else:
        return False
    
    
def pts_to_segs(pts, wrap = True):
    segs = []
    if wrap:
        for i in range(len(pts)):
            segs.append([pts[i], pts[(i+1)%len(pts)]])
    else:
        for i in range(len(pts)-1):
            segs.append([pts[i], pts[i+1]])
            
    return segs
        
   
def segs_to_pts(segs, isclose = True):
    
    pts = [s[0] for s in segs]

    if not isclose:
        pts.append(segs[-1][-1])
    return pts


def fp_segs_reverse(fp_segs):
    arr = np.asarray(fp_segs)
    rev_arr = arr[::-1][:, ::-1]
    return rev_arr.tolist()


def line_intersect(line1, line2):
    """
    Check if two lines intersect, are parallel, or if their extensions intersect.
    If the lines intersect or their extensions intersect, return the intersection point.
    Otherwise, return None.

    Args:
        line1 (list): [[x1, y1], [x2, y2]]
        line2 (list): [[x3, y3], [x4, y4]]

    Returns:
        tuple: 
            - An integer indicating the relationship between the lines:
                -1: Lines overlap
                0: Lines or extensions do not intersect 
                1: Lines do not intersect, but their extensions intersect
                2: Lines intersect
            - The intersection point as a list [x, y], or None.
    """

    x1, y1 = line1[0]
    x2, y2 = line1[-1]
    x3, y3 = line2[0] 
    x4, y4 = line2[-1] 

    # Vertical line
    m1 = math.inf if abs(x1 - x2) < TOL else (y2 - y1) / (x2 - x1)
    b1 = x1 if m1 == math.inf else y1 - m1 * x1

    m2 = math.inf if abs(x3 - x4) < TOL else (y4 - y3) / (x4 - x3)
    b2 = x3 if m2 == math.inf else y3 - m2 * x3
    
    # Check if lines are parallel or overlap
    if m1 == math.inf and m2 == math.inf or abs(m1-m2) < TOL:
        if abs(b1-b2) < TOL:
            return -1, None
        else:
            return 0, None
    
    # Find intersection point
    if m1 == math.inf:
        x = x1
        y = m2 * x + b2
    elif m2 == math.inf:
        x = x3
        y = m1 * x + b1
    else:
        x = (b2 - b1) / (m1 - m2)
        y = m1 * x + b1

    on_bd1 = (x-x1)*(x-x2) <= TOL
    on_bd2 = (x-x3)*(x-x4) <= TOL
    on_bd3 = (y-y1)*(y-y2) <= TOL
    on_bd4 = (y-y3)*(y-y4) <= TOL
    on_exten1 = (x-x2)*(x1-x2) < 0
    on_exten2 = (x-x4)*(x3-x4) < 0

    if on_bd1 and on_bd2 and on_bd3 and on_bd4:
        return 2, [x,y]
    elif (on_bd1 or on_exten1) and (on_bd2 or on_exten2):
        return 1, [x,y]
    else:
        # print((x-x1)*(x-x2), (x-x3)*(x-x4), (y-y1)*(y-y2) , (y-y3)*(y-y4), [x,y])
        return 0, None
    


def is_pt_in_poly(pt, poly):
    """ 
    Check if a point is inside a closed polyline.

    Args:
        pt (list): [px, py]
        poly (list(list)): [[x1, y1], [x2, y2], ..., [xn, yn]]

    Returns:
        tuple:
            - is_out: The point is outside the polyline. 
            - is_in: The point is inside the polyline.
            - is_on: The point is on the boundary.
            - is_vert: The point overlaps with a vertice of the polyline.
    """
    px, py = pt
    is_out, is_in, is_on, is_vert = True, False, False, False

    for i, corner in enumerate(poly):
        
        next_i = i + 1 if i + 1 < len(poly) else 0
        x1, y1 = corner
        x2, y2 = poly[next_i]

        # if point is on vertex
        if ((abs(x1 - px) < TOL and abs(y1 - py) < TOL) or 
            (abs(x2 - px) < TOL and abs(y2 - py) < TOL)):
            
            is_in, is_on, is_vert = False, True, True
            break
        
        # horizontal edge
        if (abs(y1 - y2) < TOL and abs(py-y1) < TOL and (px - x1) * (px - x2) <= 0):   
            is_on = True
            
            
        if min(y1, y2) < py <= max(y1, y2):  
             
            x = x1 + (py - y1) * (x2 - x1) / (y2 - y1) 
            # if point is on edge
            if abs(x - px) < TOL:  

                is_in, is_on = False, True  
                break
            
            # if not on edge -> outside
            elif x > px:

                is_in = not is_in

    if is_in or is_on:
        is_out = False

    return is_out, is_in, is_on, is_vert




def is_line_in_poly(line, poly):
    """ 
    Check if a line is inside a closed polyline.
    - Do not intersect
    - All points inside

    Args:
        line (list): [[x1, y1], [x2, y2]]
        poly (list(list)): [[x1, y1], [x2, y2], ..., [xn, yn]]

    Returns:
        is_in (bool): The line is inside the polyline.
    """
    
    is_out0 = is_pt_in_poly(line[0], poly)[0]
    is_out1 = is_pt_in_poly(line[1], poly)[0]
    mid_pt = [(line[0][0] + line[1][0]) / 2, (line[0][1] + line[1][1]) / 2]
    is_out_mid = is_pt_in_poly(mid_pt, poly)[0]
    
    if is_out0 or is_out1 or is_out_mid:
        return False
    else:
        for seg in pts_to_segs(poly):
            condition, pt = line_intersect(line, seg)
            if condition == 2:
                if not is_equal_pt(line[0], pt) and not is_equal_pt(line[1], pt):
                    return False
    return True
        


def check_if_on_edge(pt, sp, ep):
    """ 
    This method is to check:
        - if pt is colinear with line [sp, ep]
        - if pt is between sp and ep

    Args:
        pt (list): point to be checked [x, y]
        sp (list): start point [x, y]
        ep (list): end point [x, y]
        tolerance (float): Tolerance for floating-point comparison

    Returns:
        bool: True if between
    """
    # Calculate vectors
    sp_pt = [pt[0] - sp[0], pt[1] - sp[1]]
    sp_ep = [ep[0] - sp[0], ep[1] - sp[1]]

    # Calculate dot products
    dot_product = sp_pt[0] * sp_ep[0] + sp_pt[1] * sp_ep[1]
    sp_ep_len_squared = sp_ep[0] ** 2 + sp_ep[1] ** 2

    # Check if the point is between the start and end points
    return (0 <= dot_product <= sp_ep_len_squared and 
            abs(sp_pt[0] * sp_ep[1] - sp_pt[1] * sp_ep[0]) < TOL)


def insert_pt_in_colinear_poly(pt, poly):
    if len(poly) == 2:
        poly.insert(1, pt)
    else:
        for i in range(len(poly)-1):
            if check_if_on_edge(pt, poly[i], poly[i+1]):
                poly.insert(i+1, pt)
                break
   
                                
def split_footprints(poly_segs1_init, poly_segs2_init):
    """
    Use one polyline split a closed polyline footprint

    Args:
        poly_pts1 (list): [[x1, y1], [x2, y2], [x3, y3], ...] (m, 2)
        poly_pts2 (list): [[x1, y1], [x2, y2], [x3, y3], ...] (n, 2), (counter)clockwise

    Returns:
        list of splited segments: [[[x1, y1], [x2, y2]], [[x2, y2], [x3, y3]], ...] (k, 2 ,2) 
    """
    # # poly_segs1_init = pts_to_segs(poly_pts1)
    poly_segs1 = copy.deepcopy(poly_segs1_init)
    # # poly_segs2_init = pts_to_segs(poly_pts2)
    poly_segs2 = copy.deepcopy(poly_segs2_init)
    
    for i, s1 in enumerate(poly_segs1):
        
        for s2 in poly_segs2:            
            if is_equal_seg(s1, s2) or is_equal_pt(s1[0], s2[-1]) or is_equal_pt(s1[-1], s2[0]):
                continue        
            # print("..")
            intersect = line_intersect(s1, s2)
            ipt = intersect[1] if intersect[0] == 2 else None
            
            # print ("split",s1, "--------------" , s2, intersect)
            if ipt:
                _, _, is_on, is_vert = is_pt_in_poly(ipt, segs_to_pts(poly_segs2)) 

                if is_on and not is_vert: 
                    insert_pt_in_colinear_poly(ipt, s2) 

                if not is_equal_pt(ipt, s1[0]) and not is_equal_pt(ipt, s1[-1]):
                    insert_pt_in_colinear_poly(ipt, poly_segs1[i])

    res_segs1 = []
    for s in poly_segs1:
        if len(s) > 2:
            res_segs1.extend(pts_to_segs(s, False))
        else:
            res_segs1.append(s)
      
    res_segs2 = []     
    for s in poly_segs2:
        if len(s) > 2:
            res_segs2.extend(pts_to_segs(s, False))
        else:
            res_segs2.append(s)

    return res_segs1, res_segs2

                 
def remove_same_rows(arr1, arr2):
    """
    Removes rows from arr1 and arr2 that are close (within TOL).
    Returns new arrays with close rows removed.

    Args:
        arr1 (numpy.ndarray): 3D array with shape (k, 2, 2)
        arr2 (numpy.ndarray): 3D array with shape (k, 2, 2)

    Returns:
        tuple: (new_arr1, new_arr2)
            new_arr1 (numpy.ndarray): remain arr1
            new_arr2 (numpy.ndarray): remain arr2
            close_rows (numpy.ndarray): rows removed
            
    """
    arr1 = np.asarray(arr1)
    arr2 = np.asarray(arr2)

    # Reshape arrays to 2D
    arr1_2d = arr1.reshape(arr1.shape[0], -1)
    arr2_2d = arr2.reshape(arr2.shape[0], -1)

    # Compute differences between all pairs of rows
    diffs = np.abs(arr1_2d[:, None, :] - arr2_2d[None, :, :])
    close_rows_mask = np.all(diffs <= TOL, axis=2)

    # Get indices of rows to keep
    keep_rows1 = ~np.any(close_rows_mask, axis=1)
    keep_rows2 = ~np.any(close_rows_mask, axis=0)

    # Create new arrays with close rows removed
    new_arr1 = arr1[keep_rows1]
    new_arr2 = arr2[keep_rows2]
    
    # Get close rows
    close_rows1 = arr1[~keep_rows1].tolist()
    close_rows2 = arr2[~keep_rows2].tolist()
    close_rows = close_rows1 + close_rows2

    return new_arr1.tolist(), new_arr2.tolist(), close_rows


def regroup_segs(sep_segs, fp_pts):

    this_grp = []
    other_grp = []
    for s in sep_segs:

        # mid_pt = [(s[0][0] + s [1][0]) / 2, (s[0][1] + s [1][1]) / 2]
        # is_out = is_pt_in_poly(mid_pt, fp_pts)[0]
        is_out = not is_line_in_poly(s, fp_pts)

        if is_out:
            this_grp.append(s)
        else:
            rs = s[:]
            rs.reverse()
            other_grp.append(rs)

    return this_grp, other_grp   


def find_next_seg(segs, tar_val):
    """ 
    This function is used by group_sublists to find the next segment in the given list of segments whose first element matches the tar_val.

    Args:
        segs (list): A list of segments, where each segment is in the format [val1, val2].
        tar_val (float or int): The value to match against the first element of the segments.   

    Returns:
        seg (list): The first segment in segs whose first element matches tar_val, or None if no such segment is found.
    """
    for seg in segs:
        if is_equal_pt(seg[0], tar_val):
            return seg
    return None


def connect_segs(segs):
    """ 
    This function groups the given list of segments based on the following condition:
        - If the second element of a segment matches the first element of another segment, they belong to the same group.
        - The grouping continues until the second element of the last segment in the current group matches the first element of the first segment in the group (forming a cycle), or there are no more segments to add.
        - After grouping one set of segments, the function starts a new group with the next available segment.

    Args:
        segs (list): A list of segments, where each segment is in the format [value1, value2].

    Returns:
        res (list): A list of grouped segments, where each group is a list of segments that satisfy the grouping condition.
    """
    
    res = []
    rest_segs = segs.copy()
    while rest_segs:
        
        # initialize group, add first item, find the next segment
        cur_grp = []
        seg_0 = rest_segs.pop(0)
        cur_grp.append(seg_0)
        last_seg = seg_0
        next_seg = find_next_seg(rest_segs, last_seg[1])
        
        # continue to search for the next segment
        while next_seg is not None:
            cur_grp.append(next_seg)
            
            rest_segs.remove(next_seg)
            last_seg = next_seg
            next_seg = find_next_seg(rest_segs, last_seg[1])
             
            # end searching condition
            if next_seg is not None and is_equal_pt(next_seg[0] ,seg_0[0]):             
                cur_grp.append(next_seg)
                rest_segs.remove(next_seg)
                break
            
        res.append(cur_grp)
    
    return res

      
def boolean_difference(splited_fp1, splited_fp2, is_splited = False):
    """_summary_

    Args:
        splited_fp1 (_type_): segs
        splited_fp2 (_type_): _description_

    Returns:
        _type_: _description_
    """
    # print("____________boolean diff _______________________")
    if not is_splited:
        splited_fp1, splited_fp2 = split_footprints(splited_fp1, splited_fp2)

    fp1_segs, fp2_segs, _ = remove_same_rows(splited_fp1, splited_fp2) 

    grp1, temp2 = regroup_segs(fp1_segs, segs_to_pts(splited_fp2))
    grp2, temp1 = regroup_segs(fp2_segs, segs_to_pts(splited_fp1))

    sub1 = connect_segs(grp1 + temp1)
    sub2 = connect_segs(grp2 + temp2)

    # print("____________boolean diff end _______________________")
    return sub1, sub2



def boolean_intersection(fp1_segs, fp2_segs):
    
    # print("____________boolean intersection _______________________")
    splited_fp1, splited_fp2 = split_footprints(fp1_segs, fp2_segs)
    sub1, sub2 = boolean_difference(splited_fp1, splited_fp2, True)
    
    if not sub1 and not sub2:
        intersect = splited_fp1 
        
    elif not sub1 or not sub2:
        if not sub1:
            intersect = splited_fp1
            
        elif not sub2:
            intersect = splited_fp2
            
    else:  
        intersect = []    
        if len(sub1) <= len(sub2):
            for s in sub1:
                # [0] as the substracted part, [1] as sub1_1
                intersect.extend(boolean_difference(splited_fp1, s, True)[0])
        else:
            for s in sub2:
                intersect.extend(boolean_difference(splited_fp2, s, True)[0])
    # print("____________boolean intersection end _______________________")
    # print()
    return sub1, sub2, intersect
    
        


def boolean_union(fp1_segs, fp2_segs):
    """
    Merge two neighbouring footprints into one

    Args:
        splited_fp1 (list(list)): counterclockwise
        splited_fp2 (list(list)): counterclockwise

    Returns:
        list(list): counterclockwise
    """

    splited_fp1, splited_fp2 = split_footprints(fp1_segs, fp2_segs)
    fp_segs1, fp_segs2, _ = remove_same_rows(splited_fp1, fp_segs_reverse(splited_fp2))
    res_segs = connect_segs(fp_segs1 + fp_segs_reverse(fp_segs2))[0]
    return res_segs


def boolean_union_multi(fp1_segs, fp2_segs):
    """
    Merge two neighbouring footprints into one

    Args:
        fp1 (list(list(list))): counterclockwise
        fp2 (list(list)): counterclockwise

    Returns:
        list(list): counterclockwise
    """
    if not fp1_segs:
        return fp2_segs
    cur_fp1_segs = fp1_segs[0]
    fp2_segs = boolean_union(cur_fp1_segs, fp2_segs)
    return boolean_union_multi(fp1_segs[1:], fp2_segs)

    

def min_distance_pt(pt, pts):
    """
    Find the pt in the list of pts with the minimum Euclidean distance to the given pt.

    Args:
        pt (numpy.ndarray): Coordinates of the given pt.
        pts (numpy.ndarray): Array of coordinates of pts to compare against.

    Returns:
        numpy.ndarray: Coordinates of the pt with the minimum distance.
    """
    
    dist = np.linalg.norm(np.asarray(pts) - np.asarray(pt), axis=1)
    min_id = np.argmin(dist)
    
    return pts[min_id]



def shift_list_by_closest(pt, pts):
    """
    Find the pt in the list of pts with the minimum distance to the given pt.

    Args:
        pt (numpy.ndarray): Coordinates of the given pt.
        pts (numpy.ndarray): Array of coordinates of pts to compare against.

    Returns:
        numpy.ndarray: Shifted list of points.
    """
    
    dist = np.linalg.norm(np.asarray(pts) - np.asarray(pt), axis=1)
    min_id = np.argmin(dist)
    shifted_pts = np.roll(pts, -min_id, axis=0)
    
    return shifted_pts.tolist()


def make_donut(bound_pts, hole_pts, rev = False):
    """_summary_

    Args:
        bound_pts (_type_): Counterclockwise
        hole_pts (_type_): Counterclockwise
        rev (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    if rev:
        hole_pts.reverse()
    shifted_hole_pts = shift_list_by_closest(bound_pts[3], hole_pts)
    donut = bound_pts + shifted_hole_pts + [shifted_hole_pts[0]] + [bound_pts[3]]
    # donut = [bound_pts[0]] + shifted_hole_pts + [shifted_hole_pts[0]] + bound_pts
    return donut
    
    
def add_z_coordinate_to_pts(pts, z):
    res = [pt + [z] for pt in pts] 
    return res



def make_flr_from_pts(pts, z):
    res = add_z_coordinate_to_pts(pts[::-1], z)
    return res


    
# def make_walls_from_segs(fp_segs, z0, z1):
#     res = [add_z_coordinate_to_pts(s, z0) + add_z_coordinate_to_pts(s[::-1], z1)  for s in fp_segs]
#     return res 

def make_wall_from_seg(seg, z0, z1):
    res = [seg[0]+[z1], seg[0]+[z0], seg[1]+[z0], seg[1]+[z1]]
    return res


def pattern_tranfer(seg_ps):
    max_num = max(seg_ps)
    flr_ps = []
    for i in range(max_num):
        row = [1 if p > i else 0 for p in seg_ps]
        flr_ps.append(row)
    return flr_ps



def calc_fp_area(fp_pts):
    n = len(fp_pts)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += fp_pts[i][0] * fp_pts[j][1]
        area -= fp_pts[j][0] * fp_pts[i][1]
    area = abs(area) / 2.0
    return area



def normalize_vector(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def make_face_vectors(face_pts):
    face_pts = np.asarray(face_pts)

    # Define edge vectors
    edge1 = face_pts[1] - face_pts[0]
    edge2 = face_pts[-1] - face_pts[0]
    
    # Compute the normal vector
    n = np.cross(edge1, edge2)
    
    # Normalize the normal vector
    n_norm = normalize_vector(n)
    x_norm = [n_norm[1], -n_norm[0], n_norm[2]]
    
    return n_norm.tolist(), x_norm
    


def scale_seg(seg, ratio):

    seg = np.asarray(seg)
    central_pt = np.mean(seg, axis=0)
    scaled_line = (seg - central_pt) * ratio + central_pt

    return scaled_line.tolist() 

def scale_polygon(polygon, ratio):
    
    center = np.mean(polygon, axis=0)
    translated_polygon = polygon - center
    scaled_polygon = translated_polygon * ratio
    scaled_polygon += center
    return scaled_polygon.tolist()

def make_face_center_hori(pts):
    x = (pts[0][0] + pts[2][0]) / 2
    y = (pts[0][1] + pts[2][1]) / 2
    return [x,y]


def check_has_intersect(pts0, pts1):
    cpt = make_face_center_hori(pts1)
    if is_pt_in_poly(cpt, pts0)[1]:
        return True
    else:
        return False
    

def dist_to_poly_sides(poly_pts, cpt = None):

    poly_pts = np.asarray(poly_pts)
    if not cpt:
        cpt = np.mean(poly_pts, axis=0)
    
    dist = []
    n = len(poly_pts)
    for i in range(n):
        p1 = poly_pts[i]
        p2 = poly_pts[(i + 1) % n]
        dist.append(np.abs(np.cross(p2 - p1, cpt - p1)) / np.linalg.norm(p2 - p1))
    
    return dist


def calc_dist_x_y(seg):
    x1, y1 = seg[0][:2]
    x2, y2 = seg[1][:2]
    
    dx = abs(x1-x2)
    dy = abs(y1-y2)
    
    return dx, dy

def calc_dist_two_pts(pt1, pt2):
    pt1 = np.asarray(pt1)
    pt2 = np.asarray(pt2)
    dist = np.linalg.norm(pt1 - pt2)
    return dist


def calc_poly_side_lengths(poly):
    poly = np.asarray(poly)
    num_vertices = len(poly)
    side_lengths = []
    for i in range(num_vertices):
        j = (i + 1) % num_vertices
        side_length = np.linalg.norm(poly[j] - poly[i])
        side_lengths.append(side_length)
        
    return side_lengths

def calc_min_dists(pts):
    pts = np.asarray(pts)
    min_dist = np.inf  # Initialize with infinity
    pts_nr = len(pts)
    for i in range(pts_nr):
        for j in range(i + 1, pts_nr):
            dist = np.linalg.norm(pts[i] - pts[j])
            min_dist = min(min_dist, dist)
    return min_dist


def calc_vec_angle(v1, v2):
    
    dot_product = np.dot(v1, v2)
    
    mag1 = np.linalg.norm(v1)
    mag2 = np.linalg.norm(v2)
    
    if mag1 * mag2 != 0:
        cosine_angle = dot_product / (mag1 * mag2)
        angle_degrees = np.degrees(np.arccos(cosine_angle))
    else:
        angle_degrees = 0
    return angle_degrees


def calc_poly_angles(poly):
    poly = np.asarray(poly)
    num_vertices = len(poly)
    angles = []
    
    for i in range(num_vertices):
        p1 = poly[i - 1]
        p2 = poly[i]
        p3 = poly[(i + 1) % num_vertices]
        
        v1 = p1 - p2
        v2 = p3 - p2
    
        angle = calc_vec_angle(v1, v2)
        angles.append(angle)
        
    return angles