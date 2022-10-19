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
from climateeconomics.core.core_witness.climateeco_discipline import ClimateEcoDiscipline
from sos_trades_core.tools.post_processing.charts.chart_filter import ChartFilter
from climateeconomics.core.core_sectorization.labor_market_sectorisation import LaborMarketModel
from sos_trades_core.tools.post_processing.charts.two_axes_instanciated_chart import InstanciatedSeries, \
    TwoAxesInstanciatedChart
import numpy as np
import pandas as pd
from copy import deepcopy


class LaborMarketDiscipline(ClimateEcoDiscipline):
    ''' Discipline intended to agregate resource parameters
    '''

    # ontology information
    _ontology_data = {
        'label': 'Macroeconomics Model',
        'type': 'Research',
        'source': 'SoSTrades Project',
        'validated': '',
        'validated_by': 'SoSTrades Project',
        'last_modification_date': '',
        'category': '',
        'definition': '',
        'icon': 'fa-solid fa-city',
        'version': '',
    }

    DESC_IN = {'year_start': ClimateEcoDiscipline.YEAR_START_DESC_IN,
               'year_end': ClimateEcoDiscipline.YEAR_END_DESC_IN,
               'time_step': ClimateEcoDiscipline.TIMESTEP_DESC_IN,
               'sector_list': {'type': 'list', 'subtype_descriptor': {'list': 'string'},
                               'default': LaborMarketModel.SECTORS_LIST,
                               'visibility': ClimateEcoDiscipline.SHARED_VISIBILITY,
                               'namespace': 'ns_witness', 'editable': False, 'structuring': True},
               # Employment rate param
               'employment_a_param': {'type': 'float', 'default': 0.6335, 'user_level': 3, 'unit': '-'},
               'employment_power_param': {'type': 'float', 'default': 0.0156, 'user_level': 3, 'unit': '-'},
               'employment_rate_base_value': {'type': 'float', 'default': 0.659, 'user_level': 3, 'unit': '-'},
               'working_age_population_df': {'type': 'dataframe', 'unit': 'millions of people', 'visibility': 'Shared', 'namespace': 'ns_witness'},
              }
    DESC_OUT = {
        'workforce_df': {'type': 'dataframe', 'unit': 'millions of people', 'visibility': ClimateEcoDiscipline.SHARED_VISIBILITY,
                         'namespace': 'ns_witness'},
        'employment_df': {'type': 'dataframe', 'unit': '-'}
    }

    def init_execution(self):
        inputs_dict = self.get_sosdisc_inputs()
        self.labor_model = LaborMarketModel(inputs_dict)

    def setup_sos_disciplines(self):

        dynamic_inputs = {}
        if self._data_in is not None:
            if 'sector_list' in self._data_in:
                sector_list = self.get_sosdisc_inputs('sector_list')
                df_descriptor = {'years': ('float', None, False)}
                df_descriptor.update({col: ('float', None, True)
                                 for col in sector_list})
                
                dynamic_inputs['workforce_share_per_sector'] = {'type': 'dataframe', 'unit': '%',
                                                'dataframe_descriptor': df_descriptor,
                                                'dataframe_edition_locked': False}
              
            self.add_inputs(dynamic_inputs)


    def run(self):

        # -- get inputs
        inputs_dict = self.get_sosdisc_inputs()
        # -- configure class with inputs
        self.labor_model.configure_parameters(inputs_dict)

        # -- compute
        workforce_df, employment_df  = self.labor_model.compute(inputs_dict)

        outputs_dict = {'workforce_df': workforce_df,
                        'employment_df': employment_df}

        # -- store outputs
        self.store_sos_outputs_values(outputs_dict)

    def compute_sos_jacobian(self):
        """
        Compute jacobian for each coupling variable
        gradient of coupling variable to compute:
        net_output and invest wrt sector net_output 
        """
        sector_list = self.get_sosdisc_inputs('sector_list')
        # Gradient wrt working age population
        grad_workforcetotal = self.labor_model.compute_dworkforcetotal_dworkagepop()
        self.set_partial_derivative_for_other_types(('workforce_df', 'workforce'),
                                                        ('working_age_population_df', 'population_1570'),
                                                        grad_workforcetotal)
        for sector in sector_list:
            grad_workforcesector = self.labor_model.compute_dworkforcesector_dworkagepop(sector)
            self.set_partial_derivative_for_other_types(('workforce_df', sector),
                                                        ('working_age_population_df', 'population_1570'),
                                                        grad_workforcesector)
            

    def get_chart_filter_list(self):

        chart_filters = []

        chart_list = ['workforce per sector', 'total workforce', 'employment rate','workforce share per sector']

        chart_filters.append(ChartFilter(
            'Charts filter', chart_list, chart_list, 'charts'))

        return chart_filters

    def get_post_processing_list(self, chart_filters=None):

        instanciated_charts = []

        # Overload default value with chart filter
        if chart_filters is not None:
            for chart_filter in chart_filters:
                if chart_filter.filter_key == 'charts':
                    chart_list = chart_filter.selected_values

        workforce_df = deepcopy(self.get_sosdisc_outputs('workforce_df'))
        employment_df = deepcopy(self.get_sosdisc_outputs('employment_df'))
        sector_list = self.get_sosdisc_inputs('sector_list')

        # Overload default value with chart filter
        if chart_filters is not None:
            for chart_filter in chart_filters:
                if chart_filter.filter_key == 'charts':
                    chart_list = chart_filter.selected_values

        if 'employment rate' in chart_list:

            years = list(employment_df.index)

            year_start = years[0]
            year_end = years[len(years) - 1]

            min_value, max_value = 0, 1

            chart_name = 'Employment rate'

            new_chart = TwoAxesInstanciatedChart('years', 'employment rate',
                                                 [year_start - 5, year_end + 5],
                                                 [min_value, max_value],
                                                 chart_name)

            visible_line = True
            ordonate_data = list(employment_df['employment_rate'])

            new_series = InstanciatedSeries(
                years, ordonate_data, 'employment_rate', 'lines', visible_line)

            new_chart.series.append(new_series)
            instanciated_charts.append(new_chart)

        if 'total workforce' in chart_list:

            working_age_pop_df = self.get_sosdisc_inputs(
                'working_age_population_df')
            years = list(workforce_df.index)

            year_start = years[0]
            year_end = years[len(years) - 1]

            min_value, max_value = self.get_greataxisrange(
                working_age_pop_df['population_1570'])

            chart_name = 'Workforce'

            new_chart = TwoAxesInstanciatedChart('years', 'Number of people [million]',
                                                 [year_start - 5, year_end + 5],
                                                 [min_value, max_value],
                                                 chart_name)

            visible_line = True
            ordonate_data = list(workforce_df['workforce'])
            new_series = InstanciatedSeries(
                years, ordonate_data, 'Workforce', 'lines', visible_line)
            ordonate_data_bis = list(working_age_pop_df['population_1570'])
            new_chart.series.append(new_series)
            new_series = InstanciatedSeries(
                years, ordonate_data_bis, 'Working-age population', 'lines', visible_line)
            new_chart.series.append(new_series)
            instanciated_charts.append(new_chart)

        if 'workforce per sector' in chart_list:
            chart_name = 'Workforce per economic sector'
            new_chart = TwoAxesInstanciatedChart('years', 'Workforce per sector',
                                                 [year_start - 5, year_end + 5],
                                                 chart_name=chart_name)

            for sector in sector_list:
                sector_workforce = workforce_df[sector].values
                visible_line = True
                ordonate_data = list(sector_workforce)
                new_series = InstanciatedSeries(years, ordonate_data,
                                                f'{sector} workforce', 'lines', visible_line)
                new_chart.series.append(new_series)

            instanciated_charts.append(new_chart)

        if 'workforce share per sector' in chart_list:
            share_workforce = self.get_sosdisc_inputs('workforce_share_per_sector')
            chart_name = 'Workforce distribution per sector'
            new_chart = TwoAxesInstanciatedChart('years', 'share of total workforce [%]',
                                                 [year_start - 5, year_end + 5], stacked_bar=True,
                                                 chart_name=chart_name)

            for sector in sector_list:
                share = share_workforce[sector].values
                visible_line = True
                ordonate_data = list(share)
                new_series = InstanciatedSeries(years, ordonate_data,
                                                f'{sector} share of total workforce', 'bar', visible_line)
                new_chart.series.append(new_series)

            instanciated_charts.append(new_chart)

        return instanciated_charts
