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
import pandas as pd
from sostrades_optimization_plugins.models.func_manager.func_manager import (
    FunctionManager,
)
from sostrades_optimization_plugins.models.func_manager.func_manager_disc import (
    FunctionManagerDisc,
)

from climateeconomics.core.tools.ClimateEconomicsStudyManager import (
    ClimateEconomicsStudyManager,
)
from climateeconomics.glossarycore import GlossaryCore
from climateeconomics.sos_processes.iam.witness.witness_optim_story_telling_sub_process.usecase_witness_optim_sub import (
    Study as witness_optim_sub_usecase,
)
from climateeconomics.sos_processes.iam.witness.witness_optim_sub_process.usecase_witness_optim_sub import (
    COUPLING_NAME,
    EXTRA_NAME,
    OPTIM_NAME,
)


class Study(ClimateEconomicsStudyManager):

    def __init__(self, year_start=GlossaryCore.YearStartDefault, year_end=GlossaryCore.YearEndDefault, time_step=1, run_usecase=False,
                 execution_engine=None):
        # initialize usecase and set default values
        super().__init__(__file__, run_usecase=run_usecase, execution_engine=execution_engine)
        self.year_start = year_start
        self.year_end = year_end
        self.time_step = time_step
        self.optim_name = OPTIM_NAME
        self.coupling_name = COUPLING_NAME
        self.extra_name = EXTRA_NAME
        self.witness_uc = witness_optim_sub_usecase(
            self.year_start, self.year_end, self.time_step, execution_engine=execution_engine, sub_usecase='uc7')

    def setup_usecase(self, study_folder_path=None):

        ns = self.study_name

        values_dict = {}

        self.witness_uc.study_name = f'{ns}.{self.optim_name}'
        self.coupling_name = self.witness_uc.coupling_name
        witness_uc_data = self.witness_uc.setup_usecase()
        for dict_data in witness_uc_data:
            values_dict.update(dict_data)

        function_df_key = list(filter(lambda x: 'function_df' in x, values_dict.keys()))[0]
        function_df = values_dict[function_df_key]
        func_df = pd.DataFrame({
            'variable': [GlossaryCore.ConstraintCarbonNegative2050,],
            'parent': [
                'constraint_carbon_negative_2050'
            ],
            'ftype': FunctionManager.INEQ_CONSTRAINT,
            'weight': 1.,
            FunctionManager.AGGR: FunctionManager.INEQ_NEGATIVE_WHEN_SATIFIED_AND_SQUARE_IT,
            'namespace': [GlossaryCore.NS_FUNCTIONS]
        })
        function_df = pd.concat([function_df, func_df])

        values_dict[function_df_key] = function_df

        # design space WITNESS

        # optimization functions:
        optim_values_dict = {f'{ns}.epsilon0': 1,
                             f'{ns}.cache_type': 'SimpleCache',
                             f'{ns}.{self.optim_name}.objective_name': FunctionManagerDisc.OBJECTIVE_LAGR,  # GlossaryCore.UsableCapitalObjectiveName,
                             f'{ns}.{self.optim_name}.eq_constraints': [],
                             f'{ns}.{self.optim_name}.ineq_constraints': [],

                             # optimization parameters:
                             f'{ns}.{self.optim_name}.max_iter': 500,
                             f'{ns}.warm_start': False,
                             f'{ns}.{self.optim_name}.{self.witness_uc.coupling_name}.warm_start': False,
                             # SLSQP, NLOPT_SLSQP
                             f'{ns}.{self.optim_name}.algo': "L-BFGS-B",
                             f'{ns}.{self.optim_name}.formulation': 'DisciplinaryOpt',
                             f'{ns}.{self.optim_name}.differentiation_method': 'user',
                             f'{ns}.{self.optim_name}.algo_options': {"ftol_rel": 3e-16,
                                                                      "ftol_abs": 3e-16,
                                                                      "normalize_design_space": True,
                                                                      "maxls": 3 * 30,
                                                                      "maxcor": 30,
                                                                      "pg_tol": 1e-16,
                                                                      "xtol_rel": 1e-16,
                                                                      "xtol_abs": 1e-16,
                                                                      "max_iter": 1,
                                                                      "disp": 30},
                             # f'{ns}.{self.optim_name}.{witness_uc.coupling_name}.linear_solver_MDO':
                             # 'GMRES',
                             f'{ns}.{self.optim_name}.{self.witness_uc.coupling_name}.linear_solver_MDO_options': {
                                 'tol': 1.0e-10,
                                 'max_iter': 100},
                             # f'{ns}.{self.optim_name}.{self.witness_uc.coupling_name}.linear_solver_MDA':
                             # 'GMRES',
                             f'{ns}.{self.optim_name}.{self.witness_uc.coupling_name}.linear_solver_MDA_options': {
                                 'tol': 1.0e-10,
                                 'max_iter': 50000},
                             f'{ns}.{self.optim_name}.{self.witness_uc.coupling_name}.epsilon0': 1.0,
                             f'{ns}.{self.optim_name}.{self.witness_uc.coupling_name}.tolerance': 1.0e-10,
                             f'{ns}.{self.optim_name}.parallel_options': {"parallel": False,  # True
                                                                          "n_processes": 32,
                                                                          "use_threading": False,
                                                                          "wait_time_between_fork": 0},
                             f'{ns}.{self.optim_name}.{self.witness_uc.coupling_name}.sub_mda_class': 'GSPureNewtonMDA',
                             f'{ns}.{self.optim_name}.{self.witness_uc.coupling_name}.max_mda_iter': 50,
                             f'{ns}.{self.optim_name}.{self.witness_uc.coupling_name}.cache_type': None,
                             f'{ns}.{self.optim_name}.{self.witness_uc.coupling_name}.propagate_cache_to_children': True,
                             f'{self.witness_uc.witness_uc.study_name}.DesignVariables.is_val_level': False}

        return [values_dict] + [optim_values_dict]


if '__main__' == __name__:
    uc_cls = Study(run_usecase=True)
    uc_cls.load_data()
    uc_cls.run()
