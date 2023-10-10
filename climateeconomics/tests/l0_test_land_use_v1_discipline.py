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
from climateeconomics.glossarycore import GlossaryCore

'''
mode: python; py-indent-offset: 4; tab-width: 8; coding: utf-8
'''
import unittest
from os.path import join, dirname
from pandas import read_csv
from climateeconomics.core.core_land_use.land_use_v1 import LandUseV1
from sostrades_core.execution_engine.execution_engine import ExecutionEngine
from pathlib import Path

import numpy as np
import pandas as pd


class LandUseV1TestCase(unittest.TestCase):

    def setUp(self):
        '''
        Initialize third data needed for testing
        '''
        self.year_start = 2020
        self.year_end = 2055
        years = np.arange(self.year_start, self.year_end + 1, 1)
        year_range = self.year_end - self.year_start + 1

        data_dir = join(dirname(__file__), 'data')

        self.energy_land_demand_df = read_csv(
            join(data_dir, 'land_demand.csv'))
        # part to adapt lenght to the year range
        self.energy_land_demand_df = self.energy_land_demand_df.loc[self.energy_land_demand_df[GlossaryCore.Years]
                                                                    >= self.year_start]
        self.energy_land_demand_df = self.energy_land_demand_df.loc[self.energy_land_demand_df[GlossaryCore.Years]
                                                                    <= self.year_end]
        self.total_food_land_surface = pd.DataFrame(
            index=years,
            columns=[GlossaryCore.Years,
                     'total surface (Gha)'])
        self.total_food_land_surface[GlossaryCore.Years] = years
        self.total_food_land_surface['total surface (Gha)'] = np.linspace(
            5, 4, year_range)
        self.deforested_surface_df = pd.DataFrame(
            index=years,
            columns=[GlossaryCore.Years,
                     'forest_surface_evol'])
        self.deforested_surface_df[GlossaryCore.Years] = years
        # Gha
        self.deforested_surface_df['forest_surface_evol'] = np.linspace(
            -0.01, 0, year_range)

        self.param = {'land_demand_df': self.energy_land_demand_df,
                      GlossaryCore.YearStart: self.year_start,
                      GlossaryCore.YearEnd: self.year_end,
                      'total_food_land_surface': self.total_food_land_surface,
                      'forest_surface_df': self.deforested_surface_df,
                      'land_use_constraint_ref': 0.01
                      }

    def test_land_use_v1_model(self):
        ''' 
        Basic test of land use pyworld3
        Mainly check the overal run without value checks (will be done in another test)
        '''

        land_use = LandUseV1(self.param)

        land_use.compute(self.energy_land_demand_df,
                         self.total_food_land_surface, self.deforested_surface_df)

    def test_land_use_v1_discipline(self):
        ''' 
        Check discipline setup and run
        '''

        name = 'Test'
        model_name = 'land_use_v1'
        ee = ExecutionEngine(name)
        ns_dict = {'ns_public': f'{name}',
                   'ns_witness': f'{name}.{model_name}',
                   'ns_functions': f'{name}.{model_name}',
                   'ns_land_use': f'{name}.{model_name}',
                   'ns_ref': f'{name}.{model_name}'}
        ee.ns_manager.add_ns_def(ns_dict)

        mod_path = 'climateeconomics.sos_wrapping.sos_wrapping_land_use.land_use.land_use_v1_disc.LandUseV1Discipline'
        builder = ee.factory.get_builder_from_module(model_name, mod_path)

        ee.factory.set_builders_to_coupling_builder(builder)

        ee.configure()
        ee.display_treeview_nodes()

        inputs_dict = {f'{name}.{GlossaryCore.YearStart}': self.year_start,
                       f'{name}.{GlossaryCore.YearEnd}': self.year_end,
                       f'{name}.{model_name}.{LandUseV1.TOTAL_FOOD_LAND_SURFACE}': self.total_food_land_surface,
                       f'{name}.{model_name}.{LandUseV1.LAND_DEMAND_DF}': self.energy_land_demand_df,
                       f'{name}.{model_name}.{LandUseV1.DEFORESTED_SURFACE_DF}': self.deforested_surface_df,
                       }

        ee.load_study_from_input_dict(inputs_dict)

        ee.execute()

        disc = ee.dm.get_disciplines_with_name(
            f'{name}.{model_name}')[0]
        filter = disc.get_chart_filter_list()
        graph_list = disc.get_post_processing_list(filter)
        # for graph in graph_list:
        #     graph.to_plotly().show()
