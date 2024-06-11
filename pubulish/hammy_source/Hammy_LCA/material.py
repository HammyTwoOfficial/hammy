import numpy as np


class Material():
    
    def __init__(self, **iMat):
        """
        Name,
        Bezugsgroesse,
        Bezugseinheit: qm / m2 / m3 / kg,
        Flaechengewicht,
        Rohdichte,
        Schichtdicke: standard thckness in database,
        Laengengewicht,
        Umrechungsfaktor_auf_1kg,
        PERT: Module A1-A3, C3-C4, D 
        PENRT: Module A1-A3, C3-C4, D 
        GWP: Module A1-A3, C3-C4, D 
        
        from Construction:
        duration
        thicknessConfig
        menge
        """
        for k, v in iMat.items():
            setattr(self, k, v)



    def calc_indicator_factors(self):
        if self.menge:
            factor = self.menge

        return factor
    
    
    
    def calc_replacetime(self):
        if self.duration == 50:
            replacetime = 0
        else:
            replacetime = int(50/self.duration)
        return replacetime



    def get_indicators(self):
        """ 
        This method get unit indicators from database, multiply by menge or the factor calc

        Returns:
            list : [a1a3, b4, c3c4, d]
        """
        gwp = [self.GWP_A1_A3, 0, self.GWP_C3_C4, self.GWP_D]

        replacetime = self.calc_replacetime()
        gwp[1] = sum(gwp) * replacetime

        factor = self.calc_indicator_factors()
        gwp = np.array(gwp) * factor

        return gwp
    
