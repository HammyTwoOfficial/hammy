
import numpy as np
import math
TOL = 1e-4


"""


from this down useful functions

"""

leaning_lib = {
    "0": [0],
    "1": [-1],
    "2": [1],
    "3": [1,-1],
    "4": [-1,1]
}

def leaning(flo, dist, code):
    if str(code) not in leaning_lib:
        raise ValueError("Illegal Code!")

    pattern = leaning_lib[str(code)]
    ind = flo % len(pattern)

    return pattern[ind] * dist


zoning_lib = {
    (0, 0, 0, 0): [],
    (0, 0, 0, 1): [3, 7, 0],
    (0, 0, 1, 0): [2, 6, 3],
    (0, 0, 1, 1): [2, 6, 3, 7, 0],
    (0, 1, 0, 0): [1, 5, 2],
    (0, 1, 0, 1): [1, 5, 2, 3, 7, 0],
    (0, 1, 1, 0): [1, 5, 2, 6 ,3],
    (0, 1, 1, 1): [1, 5, 2, 6, 3, 7, 0],
    (1, 0, 0, 0): [0, 4, 1],
    (1, 0, 0, 1): [3, 7, 0, 4, 1],
    (1, 0, 1, 0): [0, 4, 1, 2, 6, 3],
    (1, 0, 1, 1): [2, 6, 3, 7, 0, 4, 1],
    (1, 1, 0, 0): [0, 4, 1, 5, 2],
    (1, 1, 0, 1): [3, 7, 0, 4, 1, 5, 2],
    (1, 1, 1, 0): [0, 4, 1, 5, 2, 6, 3],
    (1, 1, 1, 1): [0, 4, 1, 5, 2, 6, 3, 7]

}
zoning_lib_cty = {
    (0, 0, 0, 0): [8],
    (0, 0, 0, 1): [3, 7, 0,8],
    (0, 0, 1, 0): [2, 6, 3,8],
    (0, 0, 1, 1): [2, 6, 3, 7, 0,8],
    (0, 1, 0, 0): [1, 5, 2,8],
    (0, 1, 0, 1): [1, 5, 2, 3, 7, 0,8],
    (0, 1, 1, 0): [1, 5, 2, 6 ,3,8],
    (0, 1, 1, 1): [1, 5, 2, 6, 3, 7, 0,8],
    (1, 0, 0, 0): [0, 4, 1,8],
    (1, 0, 0, 1): [3, 7, 0, 4, 1,8],
    (1, 0, 1, 0): [0, 4, 1, 2, 6, 3,8],
    (1, 0, 1, 1): [2, 6, 3, 7, 0, 4, 1,8],
    (1, 1, 0, 0): [0, 4, 1, 5, 2,8],
    (1, 1, 0, 1): [3, 7, 0, 4, 1, 5, 2,8],
    (1, 1, 1, 0): [0, 4, 1, 5, 2, 6, 3,8],
    (1, 1, 1, 1): [0, 4, 1, 5, 2, 6, 3, 7,8]

}

def zoning_pattern(seg_pat,cty_exist=False):
    pattern = zoning_lib[seg_pat]
    if cty_exist:
        pattern = zoning_lib_cty[seg_pat]
    return pattern

# pattern = zoning_pattern(tuple([0,0,0,0]))
# print(pattern)

def get_segs_intersections(segs):
    """Find intersection points among segments
    Args:
        segments (list): List of line segments, each represented as a pair of endpoints
    Returns:
        list: List of intersection points
    """
    intersections = []

    # Iterate through all pairs of segments
    for i in range(len(segs)):
        
        intersection = straight_line_intersect(segs[i], segs[i-1])
        if intersection:
            intersections.append(intersection)

    return intersections

def straight_line_intersect(line1, line2):
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2

    m1 = (y2 - y1) / (x2 - x1) if x2 - x1 != 0 else 1
    m2 = (y4 - y3) / (x4 - x3) if x4 - x3 != 0 else 1

    if abs(m1 - m2) < TOL :
        raise Exception('Two lines are parallel, no intersection')
   
    elif m1 ==1 :
        x_intersection = x1
        y_intersection = m2 * (x1 - x3) + y3
    elif m2 ==1:
        x_intersection = x3
        y_intersection = m1 * (x3 - x1) + y1
    else:
        x_intersection = (y3 - y1 + m1 * x1 - m2 * x3) / (m1 - m2)
        y_intersection = m1 * (x_intersection - x1) + y1
    # x_intersection = round(x_intersection, 9)
    # y_intersection = round(y_intersection, 9)
    return [x_intersection, y_intersection]

def find_removed_items (list1, list2):
    """Find the indices of the removed vertices from the original list
    Args:
        list1 (list)
        list2 (list)
    Returns:
        list: Indices of the removed vertices
    """
    removed_vertex_indices = []

    # Iterate through the vertices of the original polygon
    for i, vertex in enumerate(list1):
        # Check if the vertex is not present in the modified polygon
        if vertex not in list2:
            removed_vertex_indices.append(i)

    return removed_vertex_indices

def remove_items_by_index(lst, indices_to_remove):
    """Remove items from list by index
    Args:
        lst (list): List from which items are to be removed
        indices_to_remove (list): List of indices of items to be removed
    Returns:
        list: Updated list after removing items
    """
    new_lst = []
    for i in range(len(lst)):
        if i not in indices_to_remove:
            new_lst.append(lst[i])
    return new_lst


def reorder_counterclockwise(pts):
    
    pp = np.array(pts)  
    
    if (pp[0] == pp[-1]).all():
        pp = np.delete(pp, -1, axis=0)
    x = pp[:, 0]
    y = pp[:, 1]
    
    max_y_index = np.argmax(y)    
    
    pre_index = max_y_index -1
    next_index = 0 if max_y_index == len(pp) - 1 else max_y_index + 1        
 
    if x[pre_index] < x[next_index]:
        
        return pts[::-1]
    else:
        
        return pts

    
def is_slope_matching(line1, line2, tol=0.01):
    
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2
    
    slope1 = (y2 - y1) / (x2 - x1) if x2 - x1 != 0 else float('inf')
    slope2 = (y4 - y3) / (x4 - x3) if x4 - x3 != 0 else float('inf')
    return abs(slope1 - slope2) <= tol



def is_distance_matching(line1, line2, tol=5):
    
    (x1, y1), (x2, y2) = line1
    point = [(x1+x2)/2,(y1+y2)/2]
   
    (x3, y3), (x4, y4) = line2
    
    a = y4 - y3
    b = x3 - x4
    c = (x4 - x3) * y3 + (y3 - y4) * x3
    

    distance = abs(a * point[0] + b * point[1] + c) / np.sqrt(a**2 + b**2)
    # print("is_distance_matching",distance < tol)
    return distance < tol

def set_building_program_by_ratio(name,ratio):

    """
    ratio=[
        openoffice
        closedoffice
        conference
        core,                                   ###must have those rooms

        dining,
        corridor
        breakroom
        lobby
        activity/multi function room
        utility                                 ##other rooms
    ]

    """
    from honeybee_energy.programtype import ProgramType
    from honeybee_energy.lib.programtypes import program_type_by_identifier,  building_program_type_by_identifier
 
    core_programs=  [
                        program_type_by_identifier("2013::LargeOffice::Elevator Shaft"),
                        program_type_by_identifier("2013::LargeOffice::Restroom"),
                        program_type_by_identifier("2013::LargeOffice::Elevator Lobby"),
                        program_type_by_identifier("2013::LargeOffice::Stair")
                    ]

    core_ratios_ =  [
                        0.2,
                        0.4,
                        0.2,
                        0.2
                    ]

    core_name = "Large Office Core"
    core_program = ProgramType.average(core_name, core_programs, core_ratios_)

    _programs=      [
                        program_type_by_identifier("2013::LargeOffice::OpenOffice"),
                        program_type_by_identifier("2013::LargeOffice::ClosedOffice"),
                        program_type_by_identifier("2013::LargeOffice::Conference"),
                        core_program,

                        program_type_by_identifier("2013::LargeOffice::Dining"),
                        program_type_by_identifier("2013::LargeOffice::Corridor"),
                        program_type_by_identifier("2013::LargeOffice::BreakRoom"),
                        program_type_by_identifier("2013::LargeOffice::Lobby"),
                        program_type_by_identifier("2013::SmallHotel::Exercise"),
                        program_type_by_identifier("2013::Courthouse::Utility")     
                    ]
       
    
    program = ProgramType.average(name, _programs, ratio)

    schedules = program.schedules
    schedules_dict =[]
    for i in range(len(schedules)):
        schedule_dict = schedules[i].to_dict(abridged=True)
        schedules_dict.append(schedule_dict)

    model_dict = program.to_dict(abridged=True)
    return model_dict , schedules_dict

def find_ymax(data):
    """Find the point with the largest y coordinate in the closed figure
        If there is more than one point with the largest y coordinate, find the point with the largest x coordinate
     Args:
         data (list): closed graph point set
     Returns:
         The first convex point in the closed figure
     """
    ploy = np.array(data)
    y = ploy[:,1]
    y_max = y.max()
    Conv_list = list()
    for p in data:
        if p[1] == y_max:
            Conv_list.append(p)
    
    if len(Conv_list) != 1:
        temp_list = []
        for p in Conv_list:
            temp_list.append(p[0])
        return Conv_list[temp_list.index(max(temp_list))]
    else:
        return Conv_list[0]
    
def conv(data):
    """Judge the concavity and convexity of each point of the polygon
     Args:
         data (list): closed graph point set
     Returns:
         [list]: Collection of coordinates of convex points in polygons
     """
    Norm_dot = find_ymax(data)
    num = len(data)
    Ind = data.index(Norm_dot)
    Conv_dots = []
   
    Vec_A = [data[Ind%num][0] - data[(Ind-1)%num][0], data[Ind%num][1] - data[(Ind-1)%num][1]]
    Vec_B = [data[(Ind+1)%num][0] - data[Ind%num][0], data[(Ind+1)%num][1] - data[Ind%num][1]]
    Vect_Norm = (Vec_A[0] * Vec_B[1]) - (Vec_A[1] * Vec_B[0])
    
    for i in range(num):
        V_A = [data[(i)%num][0] - data[(i-1)%num][0], data[(i)%num][1] - data[(i-1)%num][1]]
        V_B = [data[(i+1)%num][0] - data[(i)%num][0], data[(i+1)%num][1] - data[(i)%num][1]]
        Vec_Cross = (V_A[0] * V_B[1]) - (V_A[1] * V_B[0])
        if (Vec_Cross * Vect_Norm) >= 0:  
            Conv_dots.append(data[(i) % num])
    
    if len(Conv_dots) != len(data):
        return conv(Conv_dots) 
    else:
        return Conv_dots

def remove_collinear(data):
    """Remove collinear points from the polygon
     Args:
         data (list): closed graph point set
     Returns:
         [list]: List of coordinates after removing collinear points
     """
    num = len(data)
    Conv_dots = []
   
    for i in range(num):
        prev_point = data[(i-1) % num]
        current_point = data[i]
        next_point = data[(i+1) % num]
        
        if not is_collinear(prev_point, current_point, next_point):
            Conv_dots.append(current_point)
    
    return Conv_dots

def is_collinear(p1, p2, p3):
    """Check if three points are collinear
    Args:
        p1, p2, p3 (tuple): Three points in the form of (x, y)
    Returns:
        bool: True if collinear, False otherwise
    """

    return (p2[0] - p1[0]) * (p3[1] - p1[1]) == (p3[0] - p1[0]) * (p2[1] - p1[1])

def generate_convex_polygon(data):
    """Generate a convex polygon from a set of points
     Args:
         data (list): closed graph point set
     Returns:
         [list]: List of coordinates of convex points in the generated polygon
     """
    result = conv(data)
    remove = remove_collinear(result)
    return remove

def find_perpendicular_intersection(seg):
    (x1, y1), (x2, y2) = seg
    if x2 - x1 != 0:  # Make sure it's not a vertical line
        m = (y2 - y1) / (x2 - x1)
    else:  # Vertical line, slope is infinite
        return (x1, 0) if x1 == 0 else (x2, 0)  # Intersection is at the point where x=0

    # Step 3: Calculate slope of the perpendicular line
    if m != 0:  # Make sure it's not a horizontal line
        perpendicular_m = -1 / m
    else:  # Horizontal line, slope is 0
        return (0, y1) if y1 == 0 else (0, y2)  # Intersection is at the point where y=0

    # Step 4: Calculate equation of the perpendicular line passing through the origin
    # Point-slope form: y - y1 = m(x - x1), (x1, y1) is the point on the line
    # For the perpendicular line passing through the origin, (x1, y1) = (0, 0)
    # So the equation simplifies to: y = perpendicular_m * x

    # Step 5: Calculate intersection point
    intersection_x = 0
    intersection_y = perpendicular_m * intersection_x

    return [intersection_x, intersection_y]

def getFootPoint( seg,pt = [0,0]):
     
    x0 = pt[0]
    y0 = pt[1]
    
    (x1, y1), (x2, y2) = seg
  
    k = -((x1 - x0) * (x2 - x1) + (y1 - y0) * (y2 - y1) ) / \
    ((x2 - x1) ** 2 + (y2 - y1) ** 2 )*1.0

    xn = k * (x2 - x1) + x1
    yn = k * (y2 - y1) + y1
    

    return cartesian_to_polar([xn, yn])

def cartesian_to_polar(pt):
    x,y = pt
    # Calculate the distance from the origin
    r = math.sqrt(x**2 + y**2)
    
    # Calculate the angle with respect to the positive x-axis
    theta = math.degrees(math.atan2(y, x))
    return [r, theta]
def polar_to_cartesian(r, theta):
    # Convert angle from degrees to radians
    theta_rad = math.radians(theta)
    
    # Calculate x and y coordinates
    x = r * math.cos(theta_rad)
    y = r * math.sin(theta_rad)
    
    return [x, y]


def angle_sort(center,pt):
    return (np.arctan2(center[1] - pt[1], center[0] - pt[0]) + 2 * np.pi) % (2 * np.pi)


def check_if_pt_in_circle_area(pt,circle):
    """
        pt = [x,y]
        circle = [x,y,radiius]

        returns : 0 outside circle
                  1 inside circle
                  2 on circle
    """
    point1 = np.array(pt)
    point2 = np.array([circle[0], circle[1]])

    distance = np.linalg.norm(point2 - point1)
    if distance > circle[2]:
        return 0
    elif distance < circle[2]:
        return 1
    else:
        return 2
    
def two_circle_intersection(circle0,circle1):

    """
    circle = [x,y,radiius]

    return pts = [[x,y],[x,y]]
    """
    x1, y1, r1 = circle0 
    x2, y2, r2 = circle1

    d = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    a = (r1**2 - r2**2 + d**2) / (2 * d)

    x_center = x1 + a * (x2 - x1) / d
    y_center = y1 + a * (y2 - y1) / d

    h = np.sqrt(r1**2 - a**2)

    x_intersection1 = x_center + h * (y2 - y1) / d
    y_intersection1 = y_center - h * (x2 - x1) / d

    x_intersection2 = x_center - h * (y2 - y1) / d
    y_intersection2 = y_center + h * (x2 - x1) / d

    return [[x_intersection1, y_intersection1], [x_intersection2, y_intersection2]]


def theta_range_in_this_depth(circle0,circle1,circle_center):
    pts_circle0 = two_circle_intersection(circle0,circle_center)
    pts_circle1 = two_circle_intersection(circle1,circle_center)
    for pt_0 in pts_circle0:
        check_if_pt_in_circle = check_if_pt_in_circle_area(pt_0,circle1)
        if check_if_pt_in_circle  != 0:
            r2,theta2 = cartesian_to_polar(pt_0)
    for pt_1 in pts_circle1:
        check_if_pt_in_circle = check_if_pt_in_circle_area(pt_1,circle0)
        if check_if_pt_in_circle != 0:
            r1,theta1 = cartesian_to_polar(pt_1)
    if theta1>0 and theta2<0:
        theta2 +=360
    result_range = [theta1, theta2]
    return result_range



def remap(value, input_range, output_range):
    input_min, input_max = input_range
    output_min, output_max = output_range
    if input_max - input_min ==0 :
        return (output_min + output_max)/2
    input_ratio = (value - input_min) / (input_max - input_min)
    output_value = output_min + input_ratio * (output_max - output_min)
    
    return output_value

def exponential_remap(value,middle_value,input_range,output_range):

    """
        using exponential functin to remap a range
    """
    print("output_range",output_range)
    input_ratio = (middle_value-output_range[1])/(output_range[0]-middle_value)
    if abs(1-input_ratio) < TOL:
        remap_result = remap(value,input_range,output_range)
    print("input_ratio",input_ratio)
    input_range[0] = input_ratio**(input_range[0])
    input_range[1] = input_ratio**(input_range[1])
    
    exponential_y = input_ratio**value
    remap_result = remap(exponential_y,input_range,output_range)

    return remap_result



def ratio_remap(value,middle_value,theta_range):
    if value == 0:
        remap_result = middle_value
    elif value > 0:
        remap_result = remap(value,[0,1],[middle_value,theta_range[1]])
    else:
        remap_result = remap(value,[-1,0],[theta_range[0],middle_value])
    return remap_result

def ratio_premap(value,middle_value,theta_range):
    if value -middle_value < TOL:
        remap_result = 0
    elif value > middle_value:
        remap_result = remap(value,[middle_value,theta_range[1]],[0,1])
    else:
        remap_result = remap(value,[theta_range[0],middle_value],[-1,0])
    return remap_result

def logarithmic_remap(value, middle_value, input_range, output_range):
    """
    using logarithmic functin to remap a range
    """
    input_ratio = (middle_value - output_range[1]) / (output_range[0] - middle_value)
    if 1-input_ratio < TOL:
        remap_result = remap(value,input_range,output_range)
    input_range[0] = 1 / (input_ratio ** input_range[0])
    input_range[1] = 1 / (input_ratio ** input_range[1])

    logarithmic_y = 1 / (value ** input_ratio)
    remap_result = remap(logarithmic_y, input_range, output_range)

    return remap_result
def normalize_angle(angle):
   
    return angle % 360

def angle_difference(theta1, theta2):
    
    theta1_normalized = normalize_angle(theta1)
    theta2_normalized = normalize_angle(theta2)
    
   
    angle_diff = abs(theta1_normalized - theta2_normalized)
    
    if angle_diff > 180:
        angle_diff = 360 - angle_diff
    
    return angle_diff
def get_remap_samples(sample,site_info):
    for i in range(4):
        i_plus = (i+1)%4
        dist_range = [0,site_info[i][1]]
        sample[i] = remap(sample[i],[0,1],dist_range)
        theta_range = theta_range_in_this_depth(site_info[i][3],site_info[i_plus][3],[0,0,sample[i]])
        
        theta_range[0] = site_info[i][2] -angle_difference(theta_range[0],site_info[i][2])
        theta_range[1] = site_info[i][2] + angle_difference(theta_range[1],site_info[i][2])
    
        sample[i+4] = ratio_remap(sample[i+4],site_info[i][2],theta_range)
    return sample

def get_premap_samples(sample,site_info):
    for i in range(4):
        i_plus = (i+1)%4
        dist_range = [0,site_info[i][1]]
        sample[i] = remap(sample[i],dist_range,[0,1])
        theta_range = theta_range_in_this_depth(site_info[i][3],site_info[i_plus][3],[0,0,sample[i]])
        
        theta_range[0] = site_info[i][2] -angle_difference(theta_range[0],site_info[i][2])
        theta_range[1] = site_info[i][2] + angle_difference(theta_range[1],site_info[i][2])
    
        sample[i+4] = ratio_premap(sample[i+4],site_info[i][2],theta_range)
    return sample

def calculate_distance(p1, p2):
    """
    Calculate the Euclidean distance between two points p1 and p2 in 2D space.
    """
    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

def divide_line_by_length(p1, p2, divide_length):
    """
    Divide the line segment defined by points p1 and p2 into segments of specified length.
    Returns a list of points representing the divided points.
    """
    # Calculate the length of the line segment
    length = calculate_distance(p1, p2)

    # Determine the number of segments needed
    num_segments = int((length / divide_length)+1 )  # Round up to cover the entire length
    v = [p2[0] - p1[0], p2[1] - p1[1]]
    u = [v[0] / length*divide_length, v[1] / length*divide_length]

    # Generate equally spaced points along the line using linear interpolation
    points = []
    for i in range(num_segments):  # Include endpoints
        
        interpolated_point = [p1[0]+u[0]*i, p1[1]+u[1]*i]
        points.append(interpolated_point)
    points.append(p2)

    return points  # Exclude the first and last points to avoid duplicates
def move_point_by_vector(point, vector):
    # point is a tuple (x, y)
    # vector is a tuple (a, b)
    x_new = point[0] + vector[0]  # New x-coordinate
    y_new = point[1] + vector[1]  # New y-coordinate
    return [x_new, y_new]  # Return the new point as a tuple

def midpoint(x1, y1, x2, y2):
    # Calculate the midpoint coordinates
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2
    return [mx, my]

# def calculate_distance(x1, y1, x2, y2):
#     # Calculate the distance between points (x1, y1) and (x2, y2)
#     distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
#     return distance

def distance_between_line_centers(line0, line1):
    # Calculate midpoint of first line (line1)
    ( (x1, y1), (x2, y2)) =line0
    pt0 = midpoint(x1, y1, x2, y2)
    
    # Calculate midpoint of second line (line2)
    ((x3, y3), ( x4, y4)) =line1
    pt1 = midpoint(x3, y3, x4, y4)
    
    # Calculate distance between midpoints
    distance = calculate_distance(pt0,pt1)
    
    return distance

def check_if_on_edge(pt, sp, ep):
    distance_seg = calculate_distance(sp,ep)
    distance0 = calculate_distance(pt,sp)
    distance1 = calculate_distance(pt,ep)
    if distance0+distance1 - distance_seg < TOL:
        return True
    return False