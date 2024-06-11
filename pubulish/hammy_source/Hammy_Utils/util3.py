ref_form = {
    "I": [
        [0, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [1, 0, 0, 0]
    ],
    "L": [
        [0, 0, 1, 1],
        [0, 1, 1, 0],
        [1, 1, 0, 0],
        [1, 0, 0, 1]
    ],
    "U": [
        [0, 1, 1, 1],
        [1, 1, 1, 0],
        [1, 1, 0, 1],
        [1, 0, 1, 1]
    ],
    "II": [
        [0, 1, 0, 1],
        [1, 0, 1, 0]
    ],
    "O": [
        [1, 1, 1, 1]
    ]
}


def get_bldg_form_flr(bldg_pattern_flr, ctyd_pattern_flr, ctyd_form):
        """_summary_

        Args:
            bldg_pattern_flr (list): one-hot pattern for single flr e.x. [1, 1, 0, 1]
            ctyd_pattern_flr (int): one-hot pattern for single flr {0, 1}
            ctyd_form (int): 0: indoor-air, 1: indoor-wall, 2: massive

        Returns:
            str: {I, T, L, L+, U, U+, II, H, O, O+} or
            int: {0, 1, 2, 3,  4, 5,  6,  7, 8, 9 }
        """
        ref_pattern = ref_form
        
        if bldg_pattern_flr in ref_pattern["I"]:
            if ctyd_pattern_flr and ctyd_form == 1:
                form = "T", 2
            else:
                form = "I", 0
        elif bldg_pattern_flr in ref_pattern["L"]:
            if ctyd_pattern_flr and ctyd_form == 1:
                form = "L+", 3
            else:
                form = "L", 1
        elif bldg_pattern_flr in ref_pattern["U"]:
            if ctyd_pattern_flr and ctyd_form == 1:
                form = "U+", 5
            else:
                form = "U", 4
        elif bldg_pattern_flr in ref_pattern["II"]:
            if ctyd_pattern_flr and ctyd_form == 1:
                form = "H", 8
            else:
                form = "II", 7      
        elif bldg_pattern_flr in ref_pattern["O"]:
            if ctyd_pattern_flr and ctyd_form == 1:
                form = "O+", 0
            else:
                form = "O", 6
        return form