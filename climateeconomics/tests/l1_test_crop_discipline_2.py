'''
Copyright 2024 Capgemini
Modifications on 2023/06/21-2023/11/03 Copyright 2023 Capgemini

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
from os.path import dirname

import numpy as np
import pandas as pd
from sostrades_core.execution_engine.execution_engine import ExecutionEngine
from sostrades_core.tests.core.abstract_jacobian_unit_test import (
    AbstractJacobianUnittest,
)

from climateeconomics.database import DatabaseWitnessCore
from climateeconomics.glossarycore import GlossaryCore
from climateeconomics.sos_wrapping.sos_wrapping_agriculture.crop_2.crop_disc_2 import (
    CropDiscipline,
)


class Crop2JacobianTestCase(AbstractJacobianUnittest):

    def analytic_grad_entry(self):
        return []


    def setUp(self):
        '''
        Initialize third data needed for testing
        '''
        self.name = 'Test'
        self.model_name = 'crop_food'

        self.year_start = 2021
        self.year_end = GlossaryCore.YearEndDefaultTest
        self.years = np.arange(self.year_start, self.year_end + 1, 1)
        year_range = self.year_end - self.year_start + 1

        self.crop_productivity_reduction = pd.DataFrame({
            GlossaryCore.Years: self.years,
            GlossaryCore.CropProductivityReductionName: np.linspace(0, 12, year_range),  # fake
        })

        self.damage_fraction = pd.DataFrame({
            GlossaryCore.Years: self.years,
            GlossaryCore.DamageFractionOutput: np.linspace(0 /100., 12 / 100., year_range), # 2020 value
        })

        self.investments_food_types = pd.DataFrame({
            GlossaryCore.Years: self.years,  # 0.61 T$ (2020 value)
            **{food_type: DatabaseWitnessCore.SectorAgricultureInvest.get_value_at_year(2021) * GlossaryCore.crop_calibration_data['invest_food_type_share_start'][food_type] / 100. * 1000. for food_type in GlossaryCore.DefaultFoodTypesV2}  # convert to G$
        })
        self.workforce_df = pd.DataFrame({
            GlossaryCore.Years: self.years,
            GlossaryCore.SectorAgriculture: np.linspace(935., 935. * 1.2, year_range),  # millions of people (2020 value)
        })
        population_2021 = 7_954_448_391
        self.population_df = pd.DataFrame({
            GlossaryCore.Years: self.years,
            GlossaryCore.PopulationValue: np.linspace(population_2021 / 1e6, 7870 * 1.2, year_range),  # millions of people (2021 value)
        })

        self.enegy_agri = pd.DataFrame({
            GlossaryCore.Years: self.years,
            GlossaryCore.TotalProductionValue: 2591. /1000.,  # PWh, 2020 value
        })

        inputs_dict = {
            f'{self.name}.{GlossaryCore.YearStart}': self.year_start,
            f'{self.name}.{GlossaryCore.YearEnd}': self.year_end,
            f'{self.name}.{GlossaryCore.CropProductivityReductionName}': self.crop_productivity_reduction,
            f'{self.name}.{GlossaryCore.WorkforceDfValue}': self.workforce_df,
            f'{self.name}.{GlossaryCore.PopulationDfValue}': self.population_df,
            f'{self.name}.{GlossaryCore.DamageFractionDfValue}': self.damage_fraction,
            f'{self.name}.{GlossaryCore.SectorAgriculture}.{GlossaryCore.EnergyProductionValue}': self.enegy_agri,
            f'{self.name}.{GlossaryCore.FoodTypesInvestName}': self.investments_food_types,
        }

        self.inputs_dict = inputs_dict

        self.ee = ExecutionEngine(self.name)
        ns_dict = {
            'ns_public': self.name,
            GlossaryCore.NS_WITNESS: self.name,
            GlossaryCore.NS_CROP: f'{self.name}',
            'ns_sectors': f'{self.name}',
        }

        self.ee.ns_manager.add_ns_def(ns_dict)

        mod_path = 'climateeconomics.sos_wrapping.sos_wrapping_agriculture.crop_2.crop_disc_2.CropDiscipline'
        builder = self.ee.factory.get_builder_from_module(self.model_name, mod_path)

        self.ee.factory.set_builders_to_coupling_builder(builder)

        self.ee.configure()
        self.ee.display_treeview_nodes()

        self.coupling_inputs = [
            f'{self.name}.{GlossaryCore.CropProductivityReductionName}',
            f'{self.name}.{GlossaryCore.WorkforceDfValue}',
            f'{self.name}.{GlossaryCore.PopulationDfValue}',
            f'{self.name}.{GlossaryCore.DamageFractionDfValue}',
            f'{self.name}.{GlossaryCore.SectorAgriculture}.{GlossaryCore.EnergyProductionValue}',
            f'{self.name}.{GlossaryCore.FoodTypesInvestName}',
        ]
        self.coupling_outputs = [
            f"{self.name}.{GlossaryCore.CropFoodLandUseName}",
            f"{self.name}.{GlossaryCore.CropFoodEmissionsName}",
            f"{self.name}.{GlossaryCore.CaloriesPerCapitaValue}",
            f"{self.name}.{self.model_name}.non_used_capital",
            f"{self.name}.{GlossaryCore.FoodTypeDeliveredToConsumersName}",
            f"{self.name}.{GlossaryCore.FoodTypeCapitalName}",
        ]
        self.coupling_outputs.extend(
            [f'{self.name}.{GlossaryCore.CropProdForStreamName.format(stream)}' for stream in CropDiscipline.streams_energy_prod]
        )

    def test_crop_discipline_2(self):
        '''
        Check discipline setup and run
        '''
        self.ee.load_study_from_input_dict(self.inputs_dict)

        self.ee.execute()

        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.{self.model_name}')[0]
        filter = disc.get_chart_filter_list()
        graph_list = disc.get_post_processing_list(filter)
        for graph in graph_list:
            #graph.to_plotly().show()
            pass

        disc_techno = self.ee.root_process.proxy_disciplines[0].discipline_wrapp.discipline
        #self.override_dump_jacobian = 1
        self.check_jacobian(location=dirname(__file__), filename='jacobian_crop_discipline_2.pkl',
                            discipline=disc_techno, step=1e-15, derr_approx='complex_step', local_data=disc_techno.local_data,
                            inputs=self.coupling_inputs,
                            outputs=self.coupling_outputs)
