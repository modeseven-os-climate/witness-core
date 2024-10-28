'''
Copyright 2022 Airbus SAS
Modifications on 2023/09/06-2023/11/03 Copyright 2023 Capgemini

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

from climateeconomics.glossarycore import GlossaryCore


class PolicyDiscTest(AbstractJacobianUnittest):

    def setUp(self):

        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        self.checked_inputs = [f'{self.name}.CCS_price', f'{self.name}.{GlossaryCore.CO2DamagePrice}']
        self.checked_outputs = [f'{self.name}.CO2_taxes']

    def analytic_grad_entry(self):
        return [
            self.test_policy_analytic_grad
        ]

    def test_policy_analytic_grad(self):

        self.model_name = 'policy'
        ns_dict = {GlossaryCore.NS_WITNESS: f'{self.name}',
                   'ns_public': f'{self.name}',
                   GlossaryCore.NS_REFERENCE: f'{self.name}'}

        self.ee.ns_manager.add_ns_def(ns_dict)

        mod_path = 'climateeconomics.sos_wrapping.sos_wrapping_witness.policymodel.policy_discipline.PolicyDiscipline'
        builder = self.ee.factory.get_builder_from_module(
            self.model_name, mod_path)

        self.ee.factory.set_builders_to_coupling_builder(builder)

        self.ee.configure()
        self.ee.display_treeview_nodes()

        years = np.arange(GlossaryCore.YearStartDefault, GlossaryCore.YearEndDefault + 1)
        CCS_price = pd.DataFrame(
            {GlossaryCore.Years: years, 'ccs_price_per_tCO2': np.linspace(100, 900, len(years))})
        CO2_damage = pd.DataFrame(
            {GlossaryCore.Years: years, GlossaryCore.CO2DamagePrice: np.linspace(300, 700, len(years))})

        values_dict = {f'{self.name}.CCS_price': CCS_price,
                       f'{self.name}.{GlossaryCore.CO2DamagePrice}': CO2_damage,
                       f'{self.name}.ccs_price_percentage': 50.,
                       f'{self.name}.co2_damage_price_percentage': 70.
                       }

        self.ee.load_study_from_input_dict(values_dict)
        self.ee.execute()

        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.{self.model_name}')[0].discipline_wrapp.mdo_discipline
        self.check_jacobian(location=dirname(__file__), filename='jacobian_policy_discipline.pkl',
                            local_data = disc.local_data,discipline=disc, inputs=self.checked_inputs,
                            outputs=[f'{self.name}.{GlossaryCore.CO2TaxesValue}'], step=1e-15, derr_approx='complex_step')

    def test_policy_analytic_grad_2(self):

        self.model_name = 'policy'
        ns_dict = {GlossaryCore.NS_WITNESS: f'{self.name}',
                   'ns_public': f'{self.name}',
                   GlossaryCore.NS_REFERENCE: f'{self.name}'}

        self.ee.ns_manager.add_ns_def(ns_dict)

        mod_path = 'climateeconomics.sos_wrapping.sos_wrapping_witness.policymodel.policy_discipline.PolicyDiscipline'
        builder = self.ee.factory.get_builder_from_module(
            self.model_name, mod_path)

        self.ee.factory.set_builders_to_coupling_builder(builder)

        self.ee.configure()
        self.ee.display_treeview_nodes()

        years = np.arange(GlossaryCore.YearStartDefault, GlossaryCore.YearEndDefault + 1)
        CCS_price = pd.DataFrame(
            {GlossaryCore.Years: years, 'ccs_price_per_tCO2': np.linspace(900, 900, len(years))})
        CO2_damage = pd.DataFrame(
            {GlossaryCore.Years: years, GlossaryCore.CO2DamagePrice: np.linspace(300, 700, len(years))})

        values_dict = {f'{self.name}.CCS_price': CCS_price,
                       f'{self.name}.{GlossaryCore.CO2DamagePrice}': CO2_damage,
                       f'{self.name}.ccs_price_percentage': 50.,
                       f'{self.name}.co2_damage_price_percentage': 70.
                       }

        self.ee.load_study_from_input_dict(values_dict)
        self.ee.execute()
        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.{self.model_name}')[0].discipline_wrapp.mdo_discipline
        self.check_jacobian(location=dirname(__file__), filename='jacobian_policy_discipline2.pkl', discipline=disc, local_data = disc.local_data,inputs=self.checked_inputs,
                            outputs=[f'{self.name}.{GlossaryCore.CO2TaxesValue}'], step=1e-15, derr_approx='complex_step')

    def test_policy_analytic_grad_3(self):

        self.model_name = 'policy'
        ns_dict = {GlossaryCore.NS_WITNESS: f'{self.name}',
                   'ns_public': f'{self.name}',
                   GlossaryCore.NS_REFERENCE: f'{self.name}'}

        self.ee.ns_manager.add_ns_def(ns_dict)

        mod_path = 'climateeconomics.sos_wrapping.sos_wrapping_witness.policymodel.policy_discipline.PolicyDiscipline'
        builder = self.ee.factory.get_builder_from_module(
            self.model_name, mod_path)

        self.ee.factory.set_builders_to_coupling_builder(builder)

        self.ee.configure()
        self.ee.display_treeview_nodes()

        years = np.arange(GlossaryCore.YearStartDefault, GlossaryCore.YearEndDefault + 1)
        CCS_price = pd.DataFrame(
            {GlossaryCore.Years: years, 'ccs_price_per_tCO2': np.linspace(-100, -900, len(years))})
        CO2_damage = pd.DataFrame(
            {GlossaryCore.Years: years, GlossaryCore.CO2DamagePrice: np.linspace(-300, -700, len(years))})

        values_dict = {f'{self.name}.CCS_price': CCS_price,
                       f'{self.name}.{GlossaryCore.CO2DamagePrice}': CO2_damage,
                       f'{self.name}.ccs_price_percentage': 50.,
                       f'{self.name}.co2_damage_price_percentage': 60.
                       }

        self.ee.load_study_from_input_dict(values_dict)
        self.ee.execute()
        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.{self.model_name}')[0].discipline_wrapp.mdo_discipline
        self.check_jacobian(location=dirname(__file__), filename='jacobian_policy_discipline3.pkl', discipline=disc, local_data = disc.local_data,inputs=self.checked_inputs,
                            outputs=[f'{self.name}.{GlossaryCore.CO2TaxesValue}'], step=1e-15, derr_approx='complex_step')

    def _test_problematic_optim_point(self):
        #self.override_dump_jacobian = 1
        self.model_name = 'policy'
        ns_dict = {GlossaryCore.NS_WITNESS: f'{self.name}',
                   'ns_public': f'{self.name}',
                   GlossaryCore.NS_REFERENCE: f'{self.name}'}

        self.ee.ns_manager.add_ns_def(ns_dict)

        mod_path = 'climateeconomics.sos_wrapping.sos_wrapping_witness.policymodel.policy_discipline.PolicyDiscipline'

        builder = self.ee.factory.get_builder_from_module(
            self.model_name, mod_path)
        self.ee.factory.set_builders_to_coupling_builder(builder)

        self.ee.configure()
        self.ee.display_treeview_nodes()

        import os
        import pickle
        with open(os.path.join("data", "uc4optim.pkl"), "rb") as f:
            dict_input_optimized_point = pickle.load(f)

        def find_var_in_dict(varname: str):
            try:
                varname_in_dict_optimized = list(filter(lambda x: f".{varname}" in x, dict_input_optimized_point.keys()))[0]
                var_value = dict_input_optimized_point[varname_in_dict_optimized]
                return var_value
            except IndexError:
                print(varname)

        var_to_have = ['CCS_price', 'CO2_damage_price']
        inputs_dict = {
            f"{self.name}.{varname}": find_var_in_dict(varname) for varname in var_to_have
        }
        self.ee.load_study_from_input_dict(inputs_dict)
        self.ee.execute()

        disc_techno = self.ee.root_process.proxy_disciplines[0].discipline_wrapp.mdo_discipline

        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.{self.model_name}')[0]
        filterr = disc.get_chart_filter_list()
        graph_list = disc.get_post_processing_list(filterr)
        for graph in graph_list:
            # graph.to_plotly().show()
            pass

        self.check_jacobian(location=dirname(__file__),
                            filename='jacobian_at_opt_point_uc4.pkl',
                            discipline=disc_techno, step=1e-15, derr_approx='complex_step',
                            local_data=disc_techno.local_data,
                            inputs=self.checked_inputs,
                            outputs=self.checked_outputs)
