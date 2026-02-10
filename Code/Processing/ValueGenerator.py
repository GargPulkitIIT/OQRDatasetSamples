import numpy as np
from Processing.qrcode import constants, main
import string
import random

class ValueGenerator:
    maxSize = { 'L':[17, 32, 53, 78, 106, 134, 154, 192, 230, 271, 321, 367, 425, 458, 520, 586, 644, 718, 792, 858],
		    'M':[14, 26, 42, 62, 84, 106, 122, 152, 180, 213, 251, 287, 331, 362, 412, 450, 504, 560, 624, 666],
		    'Q':[11, 20, 32, 46, 60, 74, 86, 108, 130, 151, 177, 203, 241, 258, 292, 322, 364, 394, 442, 482],
		    'H':[7, 14, 24, 34, 44, 58, 64, 84, 98, 119, 137, 155, 177, 194, 220, 250, 280, 310, 338, 382] }
    
    errorCorrection = {"L": constants.ERROR_CORRECT_L, "M": constants.ERROR_CORRECT_M, "Q": constants.ERROR_CORRECT_Q, "H": constants.ERROR_CORRECT_H}
    
    qrSize = [x*x for x in range(21, 70, 4)]
    
    def __init__(self):
            pass
    
    def randomString(self, x):
        return ''.join(random.choices(string.ascii_letters, k = x))
    
    def provideString(self, s1, s2, version, ecc): # Modify String s2 corresponding to String s1
        q1 = main.QRCode(version = version, error_correction=self.errorCorrection[ecc], border = 0, mask_pattern = 0)
        q1.add_data(s1)

        curLength = len(s2)
        maxLength = self.maxSize[ecc][version-1]-len(s2)
        
        lowestV = 10000
        lowestS = ""
        t=0
        while(t<100):
            t+=1
            temp = self.randomString(random.randint(1,maxLength))
            temp_s2 = s2 + temp
            q2 = main.QRCode(version = version, error_correction=self.errorCorrection[ecc], border = 0, mask_pattern = 0)
            q2.add_data(temp_s2)
            nonSim = self.qrSize[version-1] - (np.sum((np.array(q1.get_matrix()) == np.array(q2.get_matrix()))))

            if nonSim<lowestV:
                lowestS = temp_s2
                lowestV = nonSim
                
        return lowestS