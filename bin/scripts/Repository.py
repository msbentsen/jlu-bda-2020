import numpy as np
import pandas as pd

import ast

#This class parses csv files with previous generated Data containing dataframes.
#As reading them while sustaining the dataframe is now possible

class Repository:
    
    def from_np_array(self, array_string):
        array_string = array_string.replace('  ', ' ')
        array_string = ','.join(array_string.replace('[ ', '[').split())
        return np.array(ast.literal_eval(array_string))

    def from_float_string(self, float_string):
        return ast.literal_eval(float_string.replace(',', '.'))
        
    def read_csv(self, filename):
        return pd.read_csv(filename, converters={'Means': self.from_np_array, 'Covariances': self.from_np_array, 'weights': self.from_float_string})



if __name__ == '__main__':

    testfile = 'test_store_dataframe.csv'

    data_array = []
    data_array.append([np.array([71.41522895,56.06861296]), np.array([np.array([96.98543111,-92.51709171]), np.array([-92.51709171,114.56871922])]), 0.2783172524527151, 1])
    data_array.append([np.array([25.52717446,75.51856035]), np.array([np.array([155.57981472,19.54069626]), np.array([19.54069626,183.53027153])]), 0.11208827843909515, 0])
    data_array.append([np.array([12.69900151,21.22815574]), np.array([np.array([53.82297412,2.79626762]), np.array([2.79626762,187.71409543])]), 0.09174096173272588, 1])                
    df = pd.DataFrame(data_array, columns=('Means','Covariances','weights', 'labels'))
    df.to_csv(testfile, index=False)

    df2 = Repository().read_csv(testfile)
    print(df2.values)



#   Means                             Covariances                                                         weights 
# [[array([71.41522895, 56.06861296]) array([[ 96.98543111, -92.51709171], [-92.51709171, 114.56871922]]) 0.2783172524527151 1]
#  [array([25.52717446, 75.51856035]) array([[155.57981472,  19.54069626], [ 19.54069626, 183.53027153]]) 0.11208827843909515 0]
#  [array([12.69900151, 21.22815574]) array([[ 53.82297412,   2.79626762], [  2.79626762, 187.71409543]]) 0.09174096173272588 1]
#  [array([59.90942787, 53.00422143]) array([[312.71372653,  56.73105654], [ 56.73105654, 369.29227714]]) 0.372758811900621 1]
#  [array([54.84906241, 11.65264727]) array([[523.64082412,   5.85675637], [  5.85675637,  49.44242504]]) 0.14509469547484286 0]]