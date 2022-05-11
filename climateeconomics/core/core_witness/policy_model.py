'''
Copyright 2022 Airbus SAS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
import numpy as np
import pandas as pd
from sos_trades_core.tools.cst_manager.func_manager_common import smooth_maximum_vect,\
    get_dsmooth_dvariable_vect


class PolicyModel():
    '''
    Used to compute carbon emissions from gross output 
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.CO2_tax = pd.DataFrame()
        self.CO2_damage_price = None
        self.CCS_price = None
        self.ccs_price_percentage = None
        self.co2_damage_price_percentage = None

    def compute_smax(self, param):
        """
        Compute CO2 tax based on ccs_price and co2_damage_price
        """
        self.CO2_damage_price = param['CO2_damage_price']
        self.CCS_price = param['CCS_price']
        self.ccs_price_percentage = param['ccs_price_percentage'] / 100.
        self.co2_damage_price_percentage = param['co2_damage_price_percentage'] / 100.
        self.CO2_tax['years'] = self.CO2_damage_price['years'].values
        CO2_damage_price_array = self.co2_damage_price_percentage * self.CO2_damage_price['CO2_damage_price'].values
        CCS_price_array = self.ccs_price_percentage * self.CCS_price['ccs_price_per_tCO2'].values
        self.CO2_tax['CO2_tax'] = smooth_maximum_vect(
            np.array([CO2_damage_price_array, CCS_price_array, 0.0 * CCS_price_array]).T)


    def compute_CO2_tax_dCCS_dCO2_damage_smooth(self):
        """
        compute dCO2_tax/dCO2_damage and dCO2_tax/dCCS_price
        """

        CO2_damage_price_array = self.co2_damage_price_percentage * self.CO2_damage_price['CO2_damage_price'].values
        CCS_price_array = self.ccs_price_percentage * self.CCS_price['ccs_price_per_tCO2'].values
        dsmooth = get_dsmooth_dvariable_vect(
            np.array([CO2_damage_price_array, CCS_price_array, 0.0 * CCS_price_array]).T)
        l_CO2, l_CCS =self.co2_damage_price_percentage * dsmooth.T[0], self.ccs_price_percentage * dsmooth.T[1]
        return l_CO2, l_CCS
