'''
Copyright 2024 Capgemini

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
import unittest

import numpy as np
import pandas as pd

from climateeconomics.glossarycore import GlossaryCore
from sostrades_core.execution_engine.execution_engine import ExecutionEngine


class CarbonEmissionDiscTestCheckRange(unittest.TestCase):

    def setUp(self):

        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        self.years = np.arange(GlossaryCore.YearStartDefault, GlossaryCore.YearEndDefault + 1)
        self.economics_df = pd.DataFrame({
            GlossaryCore.Years: self.years,
            GlossaryCore.GrossOutput: np.linspace(121, 91, len(self.years)),
        })

        self.energy_supply_df_all = pd.DataFrame({
            GlossaryCore.Years: self.years,
            GlossaryCore.TotalCO2Emissions: np.linspace(35, 0, len(self.years))
        })

        self.co2_emissions_ccus_Gt = pd.DataFrame({
            GlossaryCore.Years: self.years,
            'carbon_storage Limited by capture (Gt)': 0.02
        })

        self.CO2_emissions_by_use_sinks = pd.DataFrame({
            GlossaryCore.Years: self.years,
            'CO2 removed by energy mix (Gt)': 0.0
        })

        self.co2_emissions_needed_by_energy_mix = pd.DataFrame({
            GlossaryCore.Years: self.years,
            'carbon_capture needed by energy mix (Gt)': 0.0
        })

    def test_check_range(self):
        """
        Test check range is correct
        """
        self.model_name = 'carbonemission'
        ns_dict = {GlossaryCore.NS_WITNESS: f'{self.name}',
                   'ns_public': f'{self.name}',
                   GlossaryCore.NS_ENERGY_MIX: f'{self.name}',
                   GlossaryCore.NS_REFERENCE: f'{self.name}',
                   GlossaryCore.NS_CCS: f'{self.name}',
                   'ns_energy': f'{self.name}'}

        self.ee.ns_manager.add_ns_def(ns_dict)

        mod_path = 'climateeconomics.sos_wrapping.sos_wrapping_witness.carbonemissions.carbonemissions_discipline.CarbonemissionsDiscipline'
        builder = self.ee.factory.get_builder_from_module(
            self.model_name, mod_path)

        self.ee.factory.set_builders_to_coupling_builder(builder)

        self.ee.configure()
        self.ee.display_treeview_nodes()

        self.years = np.arange(GlossaryCore.YearStartDefault, GlossaryCore.YearEndDefault + 1)
        self.economics_df = pd.DataFrame({
            GlossaryCore.Years: self.years,
            GlossaryCore.GrossOutput: np.linspace(121, 91, len(self.years)),
        })

        CO2_emissions_by_use_sources = pd.DataFrame({
            GlossaryCore.Years: self.years,
            'CO2 from energy mix (Gt)': 0.0,
            'carbon_capture from energy mix (Gt)': 0.0,
            'Total CO2 by use (Gt)': 20.0,
            'Total CO2 from Flue Gas (Gt)': 3.2
        })

        CO2_emitted_forest = pd.DataFrame({
            GlossaryCore.Years: self.years,
            'emitted_CO2_evol_cumulative': np.cumsum(np.linspace(0.01, 0.10, len(self.years))) + 3.21
        })

        values_dict = {f'{self.name}.{GlossaryCore.EconomicsDfValue}': self.economics_df,
                       f'{self.name}.{GlossaryCore.CO2EmissionsGtValue}': self.energy_supply_df_all,
                       f'{self.name}.{GlossaryCore.insertGHGAgriLandEmissions.format(GlossaryCore.CO2)}': CO2_emitted_forest,
                       f'{self.name}.co2_emissions_ccus_Gt': self.co2_emissions_ccus_Gt,
                       f'{self.name}.CO2_emissions_by_use_sources': CO2_emissions_by_use_sources,
                       f'{self.name}.CO2_emissions_by_use_sinks': self.CO2_emissions_by_use_sinks,
                       f'{self.name}.co2_emissions_needed_by_energy_mix': self.co2_emissions_needed_by_energy_mix,
                       f'{self.name}.{GlossaryCore.CheckRangeBeforeRunBoolName}': False} # activate check before run

        self.ee.load_study_from_input_dict(values_dict)

        self.ee.execute()


    def test_failing_check_range_input(self):
        """
        Test failing check range
        Put year of dataframe CO2_land_emissions outside of range
        """

        self.model_name = 'carbonemission'
        ns_dict = {GlossaryCore.NS_WITNESS: f'{self.name}',
                   'ns_public': f'{self.name}',
                   GlossaryCore.NS_ENERGY_MIX: f'{self.name}',
                   GlossaryCore.NS_REFERENCE: f'{self.name}',
                   GlossaryCore.NS_CCS: f'{self.name}',
                   'ns_energy': f'{self.name}'}

        self.ee.ns_manager.add_ns_def(ns_dict)

        mod_path = 'climateeconomics.sos_wrapping.sos_wrapping_witness.carbonemissions.carbonemissions_discipline.CarbonemissionsDiscipline'
        builder = self.ee.factory.get_builder_from_module(
            self.model_name, mod_path)

        self.ee.factory.set_builders_to_coupling_builder(builder)

        self.ee.configure()
        self.ee.display_treeview_nodes()

        CO2_emissions_by_use_sources = pd.DataFrame({
            GlossaryCore.Years: self.years,
            'CO2 from energy mix (Gt)': 0.0,
            'carbon_capture from energy mix (Gt)': 0.0,
            'Total CO2 by use (Gt)': 20.0,
            'Total CO2 from Flue Gas (Gt)': 3.2
        })


        min_co2_objective = -1000.0
        self.energy_supply_df_all[GlossaryCore.TotalCO2Emissions] = np.linspace(
            0, -100000, len(self.years))

        years = np.copy(self.years)
        years[0] = 1950
        CO2_emitted_forest = pd.DataFrame({
            GlossaryCore.Years: years,
            'emitted_CO2_evol': np.linspace(0.04, 0.04, len(self.years)),
            'emitted_CO2_evol_cumulative': np.cumsum(np.linspace(0.04, 0.04, len(self.years))) + 3.21
        })

        values_dict = {f'{self.name}.{GlossaryCore.EconomicsDfValue}': self.economics_df,
                       f'{self.name}.{GlossaryCore.CO2EmissionsGtValue}': self.energy_supply_df_all,
                       f'{self.name}.{GlossaryCore.insertGHGAgriLandEmissions.format(GlossaryCore.CO2)}': CO2_emitted_forest,
                       f'{self.name}.{self.model_name}.min_co2_objective': min_co2_objective,
                       f'{self.name}.co2_emissions_ccus_Gt': self.co2_emissions_ccus_Gt,
                       f'{self.name}.CO2_emissions_by_use_sources': CO2_emissions_by_use_sources,
                       f'{self.name}.CO2_emissions_by_use_sinks': self.CO2_emissions_by_use_sinks,
                       f'{self.name}.co2_emissions_needed_by_energy_mix': self.co2_emissions_needed_by_energy_mix,
                       f'{self.name}.{GlossaryCore.CheckRangeBeforeRunBoolName}': True}

        self.ee.load_study_from_input_dict(values_dict)
        # check test will fail because year of CO2_land_emissions is not in correct range
        with self.assertRaises(ValueError, msg="Expected ValueError due to incorrect range"):
            self.ee.execute()

    def test_failing_check_range_output(self):
        """
        Test failing check range
        Put very high emissions values as input so that output total emissions go beyond range
        """

        self.model_name = 'carbonemission'
        ns_dict = {GlossaryCore.NS_WITNESS: f'{self.name}',
                   'ns_public': f'{self.name}',
                   GlossaryCore.NS_ENERGY_MIX: f'{self.name}',
                   GlossaryCore.NS_REFERENCE: f'{self.name}',
                   GlossaryCore.NS_CCS: f'{self.name}',
                   'ns_energy': f'{self.name}'}

        self.ee.ns_manager.add_ns_def(ns_dict)

        mod_path = 'climateeconomics.sos_wrapping.sos_wrapping_witness.carbonemissions.carbonemissions_discipline.CarbonemissionsDiscipline'
        builder = self.ee.factory.get_builder_from_module(
            self.model_name, mod_path)

        self.ee.factory.set_builders_to_coupling_builder(builder)

        self.ee.configure()
        self.ee.display_treeview_nodes()

        CO2_emissions_by_use_sources = pd.DataFrame({
            GlossaryCore.Years: self.years,
            'CO2 from energy mix (Gt)': 1.e9,
            'carbon_capture from energy mix (Gt)': 0.0,
            'Total CO2 by use (Gt)': 1.e9,
            'Total CO2 from Flue Gas (Gt)': 3.2
        })


        min_co2_objective = -1000.0
        self.energy_supply_df_all[GlossaryCore.TotalCO2Emissions] = np.linspace(
            0, -100000, len(self.years))

        CO2_emitted_forest = pd.DataFrame({
            GlossaryCore.Years: self.years,
            'emitted_CO2_evol': np.linspace(1.e6, 1.e6, len(self.years)),
            'emitted_CO2_evol_cumulative': np.cumsum(np.linspace(1.e6, 1.e6, len(self.years))) + 1.e9
        })

        values_dict = {f'{self.name}.{GlossaryCore.EconomicsDfValue}': self.economics_df,
                       f'{self.name}.{GlossaryCore.CO2EmissionsGtValue}': self.energy_supply_df_all,
                       f'{self.name}.{GlossaryCore.insertGHGAgriLandEmissions.format(GlossaryCore.CO2)}': CO2_emitted_forest,
                       f'{self.name}.{self.model_name}.min_co2_objective': min_co2_objective,
                       f'{self.name}.co2_emissions_ccus_Gt': self.co2_emissions_ccus_Gt,
                       f'{self.name}.CO2_emissions_by_use_sources': CO2_emissions_by_use_sources,
                       f'{self.name}.CO2_emissions_by_use_sinks': self.CO2_emissions_by_use_sinks,
                       f'{self.name}.co2_emissions_needed_by_energy_mix': self.co2_emissions_needed_by_energy_mix,
                       f'{self.name}.{GlossaryCore.CheckRangeBeforeRunBoolName}': True
                       }

        self.ee.load_study_from_input_dict(values_dict)
        # check test will fail because year of CO2_land_emissions is not in correct range
        with self.assertRaises(ValueError, msg="Expected ValueError due to incorrect range"):
            self.ee.execute()

