'''
Copyright 2023 Capgemini

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

from climateeconomics.sos_processes.iam.witness.witness_coarse_dev_optim_process.usecase_witness_optim_invest_distrib import \
    Study as StudyOptimInvestDistrib


class Study(StudyOptimInvestDistrib):
    def __init__(self, run_usecase=False, execution_engine=None, year_start=GlossaryCore.YearStartDefault, year_end=GlossaryCore.YearEndDefault, time_step=1):
        super().__init__(year_start=year_start,
                         year_end=year_end,
                         time_step=time_step,
                         file_path=__file__,
                         run_usecase=run_usecase,
                         execution_engine=execution_engine)

    def setup_usecase(self, study_folder_path=None):
        
        data_witness = super().setup_usecase()
        
        dspace = data_witness[f'{self.study_name}.{self.optim_name}.design_space']

        var_that_needs_lower_bound_augmentation = {
            'fossil.FossilSimpleTechno.fossil_FossilSimpleTechno_array_mix': [50.] * GlossaryCore.NB_POLES_COARSE,
            'fossil_FossilSimpleTechno_utilization_ratio_array': [30.] * GlossaryCore.NB_POLES_UTILIZATION_RATIO,
            'renewable.RenewableSimpleTechno.renewable_RenewableSimpleTechno_array_mix': [300.] * GlossaryCore.NB_POLES_COARSE,
            'renewable_RenewableSimpleTechno_utilization_ratio_array': [30.] * GlossaryCore.NB_POLES_UTILIZATION_RATIO,
            'carbon_capture.direct_air_capture.DirectAirCaptureTechno.carbon_capture_direct_air_capture_DirectAirCaptureTechno_array_mix': [100.] * GlossaryCore.NB_POLES_COARSE,
            'carbon_capture.direct_air_capture.DirectAirCaptureTechno_utilization_ratio_array': [30.] * GlossaryCore.NB_POLES_UTILIZATION_RATIO,
            'carbon_capture.flue_gas_capture.FlueGasTechno.carbon_capture_flue_gas_capture_FlueGasTechno_array_mix': [100.] * GlossaryCore.NB_POLES_COARSE,
            'carbon_capture.flue_gas_capture.FlueGasTechno_utilization_ratio_array': [30.] * GlossaryCore.NB_POLES_UTILIZATION_RATIO,
            'carbon_storage.CarbonStorageTechno.carbon_storage_CarbonStorageTechno_array_mix': [1.2] * GlossaryCore.NB_POLES_COARSE,
            'carbon_storage.CarbonStorageTechno_utilization_ratio_array': [30.] * GlossaryCore.NB_POLES_UTILIZATION_RATIO,
        }
        dspace = self.update_dspace_col(dspace, var_that_needs_lower_bound_augmentation)
        dspace = self.update_dspace_col(dspace, var_that_needs_lower_bound_augmentation, col="value")


        # Activate damage
        updated_data = {
            f'{self.study_name}.{self.optim_name}.{self.witness_uc.coupling_name}.{self.witness_uc.extra_name}.assumptions_dict': {
                'compute_gdp': True,
                'compute_climate_impact_on_gdp': True,
                'activate_climate_effect_population': True,
                'invest_co2_tax_in_renewables': False,
                'activate_pandemic_effects': False
            },
            f'{self.study_name}.{self.optim_name}.design_space': dspace,
        }

        data_witness.update(updated_data)

        # Put high tax
        data_witness.update({
            f"{self.study_name}.{self.optim_name}.{self.witness_uc.coupling_name}.{self.witness_uc.extra_name}.ccs_price_percentage": 100.0,
            f"{self.study_name}.{self.optim_name}.{self.witness_uc.coupling_name}.{self.witness_uc.extra_name}.co2_damage_price_percentage": 100.0,
        })

        return data_witness


if '__main__' == __name__:
    uc_cls = Study(run_usecase=True)
    uc_cls.test()
