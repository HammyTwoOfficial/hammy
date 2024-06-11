from .material import Material
import numpy as np

class Construction():
    ref_con_lib = None
    constr_lib = None
    mat_lib_v23 = None
    mat_lib_v21 = None
    
    def __init__(self, iConPart, iConName, iSrfArea, iInsuThickness = None):
        
        self.con_name = iConName
        self.con_part = iConPart
        self.srf_area = iSrfArea
        self.insu_thickness = iInsuThickness
        self.con_info = Construction.constr_lib[iConName]
        self.mat_names = [mat[0] for mat in self.con_info]

        self.materials = self.make_materials()
        self.set_material_properties()
        self.gwp_e = self.calc_constr_EC()
    
    
    
    def make_materials(self):
        materials = []
        for mn in self.mat_names:
            try:
                mat = Material(**Construction.mat_lib_v23[mn])
            except:
                mat = Material(**Construction.mat_lib_v21[mn]) 
            materials.append(mat)
        return materials        
            
            
            
    def set_material_properties(self):
        for mat_info, mat in zip(self.con_info, self.materials):
            mat.duration = mat_info[2]
            mat.thickness = mat_info[3]
            mat.menge = mat_info[4]
            mat.replacetime = mat.calc_replacetime()
            mat.GWP = mat.get_indicators()
            if self.con_part in ["ExWall", "RoofCeiling"]:
                if "EPS" in mat.Name or "Daemmstoff" in mat.Name or "Waermedaemmputz" in mat.Name:
                    mat.GWP *= (self.insu_thickness / mat.thickness)
                    mat.thickness = self.insu_thickness
   
   
    def calc_constr_EC(self):
        """

        Returns:
            1darray (5,): [A1A3, B4, C3C4, D]
        """
        gwps = np.array([mat.GWP for mat in self.materials]) * self.srf_area
        
        gwp_constr_modules = np.sum(gwps, axis=0)
        # self.gwp_constr_total = np.sum(gwps)
        return gwp_constr_modules
        # return np.append(self.gwp_constr_modules, self.gwp_constr_total)

