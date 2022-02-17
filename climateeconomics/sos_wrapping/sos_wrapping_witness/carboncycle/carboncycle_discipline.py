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
# coding: utf-8
from climateeconomics.core.core_witness.climateeco_discipline import ClimateEcoDiscipline
from climateeconomics.core.core_witness.carbon_cycle_model import CarbonCycle
from sos_trades_core.tools.post_processing.charts.two_axes_instanciated_chart import InstanciatedSeries, TwoAxesInstanciatedChart
from sos_trades_core.tools.post_processing.charts.chart_filter import ChartFilter
import numpy as np

import pandas as pd
from copy import deepcopy


class CarbonCycleDiscipline(ClimateEcoDiscipline):

    # ontology information
    _ontology_data = {
        'label': 'Carbon Cycle WITNESS Model',
        'type': 'Research',
        'source': 'SoSTrades Project',
        'validated': '',
        'validated_by': 'SoSTrades Project',
        'last_modification_date': '',
        'category': '',
        'definition': '',
        'icon': 'fas fa-recycle fa-fw',
        'version': '',
    }
    _maturity = 'Research'

    years = np.arange(2020, 2101)
    DESC_IN = {
        'year_start': {'type': 'int', 'default': 2020, 'possible_values': years, 'unit': 'year', 'visibility': 'Shared', 'namespace': 'ns_witness'},
        'year_end': {'type': 'int', 'default': 2100, 'possible_values': years, 'unit': 'year', 'visibility': 'Shared', 'namespace': 'ns_witness'},
        'time_step': {'type': 'int', 'default': 1, 'unit': 'year per period', 'visibility': 'Shared', 'namespace': 'ns_witness'},
        'conc_lower_strata': {'type': 'int', 'default': 1720, 'unit': 'Gtc', 'user_level': 2},
        'conc_upper_strata': {'type': 'int', 'default': 360, 'unit': 'Gtc', 'user_level': 2},
        'conc_atmo': {'type': 'int', 'default': 588, 'unit': 'Gtc', 'user_level': 2},
        'init_conc_atmo': {'type': 'float', 'default': 878.412, 'unit': 'Gtc', 'user_level': 2},
        'init_upper_strata': {'type': 'int', 'default': 460, 'unit': 'Gtc', 'user_level': 2},
        'init_lower_strata': {'type': 'int', 'default': 1740, 'unit': 'Gtc', 'user_level': 2},
        'b_twelve': {'type': 'float', 'visibility': ClimateEcoDiscipline.INTERNAL_VISIBILITY, 'default': 0.12, 'unit': '[-]', 'user_level': 3},
        'b_twentythree': {'type': 'float', 'visibility': ClimateEcoDiscipline.INTERNAL_VISIBILITY, 'default': 0.007, 'unit': '[-]', 'user_level': 3},
        'lo_mat': {'type': 'float', 'default': 10, 'user_level': 2},
        'lo_mu': {'type': 'float', 'default': 100, 'user_level': 2},
        'lo_ml': {'type': 'float', 'default': 1000, 'user_level': 2},
        'CO2_emissions_df': {'type': 'dataframe', 'visibility': 'Shared', 'namespace': 'ns_witness'},
        'ppm_ref': {'type': 'float', 'default': 280, 'user_level': 2, 'visibility': ClimateEcoDiscipline.SHARED_VISIBILITY, 'namespace': 'ns_ref'},
        'rockstrom_constraint_ref': {'type': 'float', 'default': 490, 'user_level': 2, 'visibility': ClimateEcoDiscipline.SHARED_VISIBILITY, 'namespace': 'ns_ref'},
        'alpha': {'type': 'float', 'range': [0., 1.], 'default': 0.5, 'unit': '-',
                  'visibility': ClimateEcoDiscipline.SHARED_VISIBILITY, 'namespace': 'ns_witness'},
        'beta': {'type': 'float', 'range': [0., 1.], 'default': 0.5, 'unit': '-',
                 'visibility': ClimateEcoDiscipline.SHARED_VISIBILITY, 'namespace': 'ns_witness'},
        'scale_factor_atmo_conc': {'type': 'float', 'default': 0.01, 'user_level': 2, 'visibility': 'Shared',
                                   'namespace': 'ns_witness'},
        'minimum_ppm_limit': {'type': 'float', 'default': 250, 'user_level': 2},
        'minimum_ppm_constraint_ref': {'type': 'float', 'default': 10, 'user_level': 2, 'visibility': ClimateEcoDiscipline.SHARED_VISIBILITY, 'namespace': 'ns_ref'},

    }

    DESC_OUT = {
        'carboncycle_df': {'type': 'dataframe', 'visibility': 'Shared', 'namespace': 'ns_witness'},
        'carboncycle_detail_df': {'type': 'dataframe'},
        'ppm_objective': {'type': 'array', 'visibility': 'Shared', 'namespace': 'ns_witness'},
        'rockstrom_limit_constraint': {'type': 'array', 'visibility': 'Shared', 'namespace': 'ns_witness'},
        'minimum_ppm_constraint': {'type': 'array', 'visibility': 'Shared', 'namespace': 'ns_witness'}
    }

    def init_execution(self):
        param_in = self.get_sosdisc_inputs()
        self.carboncycle = CarbonCycle(param_in)

    def run(self):
        # get input of discipline
        param_in = self.get_sosdisc_inputs()

        # compute output
        carboncycle_df, ppm_objective = self.carboncycle.compute(
            param_in)
        dict_values = {
            'carboncycle_detail_df': carboncycle_df,
            'carboncycle_df': carboncycle_df[['years', 'atmo_conc']],
            'ppm_objective': ppm_objective,
            'rockstrom_limit_constraint': self.carboncycle.rockstrom_limit_constraint,
            'minimum_ppm_constraint': self.carboncycle.minimum_ppm_constraint}

        # store data
        self.store_sos_outputs_values(dict_values)

    def compute_sos_jacobian(self):
        """ 
        Compute jacobian for each coupling variable 
        gradient of coupling variable to compute: 
        carboncycle_df
          - 'atmo_conc':
                - CO2_emissions_df, 'total_emissions'
          - 'lower_ocean_conc':
                - CO2_emissions_df, 'total_emissions'
          - 'shallow_ocean_conc':
                - CO2_emissions_df, 'total_emissions'
          - 'ppm':
                - CO2_emissions_df, 'total_emissions'
          - 'atmo_share_since1850':
                - CO2_emissions_df, 'total_emissions'
                - CO2_emissions_df, 'cum_total_emissions'
          - 'atmo_share_sinceystart':
                - CO2_emissions_df, 'total_emissions'
                - CO2_emissions_df, 'cum_total_emissions'
        """
        d_atmoconc_d_totalemissions, d_lower_d_totalemissions, d_swallow_d_totalemissions, \
            d_atmo1850_dtotalemission, d_atmotoday_dtotalemission = self.carboncycle.compute_d_total_emissions()

        self.set_partial_derivative_for_other_types(
            ('carboncycle_df', 'atmo_conc'), ('CO2_emissions_df', 'total_emissions'),  d_atmoconc_d_totalemissions)

        d_ppm_d_totalemissions = self.carboncycle.compute_d_ppm(
            d_atmoconc_d_totalemissions)
        d_ppm_objective_d_totalemissions = self.carboncycle.compute_d_objective(
            d_ppm_d_totalemissions)
        self.set_partial_derivative_for_other_types(
            ('ppm_objective', ), ('CO2_emissions_df', 'total_emissions'),  d_ppm_objective_d_totalemissions)

        self.set_partial_derivative_for_other_types(
            ('rockstrom_limit_constraint', ), ('CO2_emissions_df', 'total_emissions'),  -d_ppm_d_totalemissions / self.carboncycle.rockstrom_constraint_ref)
        self.set_partial_derivative_for_other_types(
            ('minimum_ppm_constraint', ), ('CO2_emissions_df', 'total_emissions'),  d_ppm_d_totalemissions / self.carboncycle.minimum_ppm_constraint_ref)

    def get_chart_filter_list(self):

        # For the outputs, making a graph for tco vs year for each range and for specific
        # value of ToT with a shift of five year between then

        chart_filters = []

        chart_list = ['atmosphere concentration',
                      'Atmospheric concentrations parts per million']
        # First filter to deal with the view : program or actor
        chart_filters.append(ChartFilter(
            'Charts', chart_list, chart_list, 'charts'))

        return chart_filters

    def get_post_processing_list(self, chart_filters=None):

        # For the outputs, making a graph for tco vs year for each range and for specific
        # value of ToT with a shift of five year between then

        instanciated_charts = []

        # Overload default value with chart filter
        if chart_filters is not None:
            for chart_filter in chart_filters:
                if chart_filter.filter_key == 'charts':
                    chart_list = chart_filter.selected_values
        carboncycle_df = deepcopy(
            self.get_sosdisc_outputs('carboncycle_detail_df'))
        scale_factor_atmo_conc = self.get_sosdisc_inputs(
            'scale_factor_atmo_conc')
        if 'atmosphere concentration' in chart_list:

            #carboncycle_df = discipline.get_sosdisc_outputs('carboncycle_df')
            atmo_conc = carboncycle_df['atmo_conc'] / scale_factor_atmo_conc

            years = list(atmo_conc.index)

            year_start = years[0]
            year_end = years[len(years) - 1]
            min_value, max_value = self.get_greataxisrange(atmo_conc)

            chart_name = 'Atmosphere concentration of carbon'

            new_chart = TwoAxesInstanciatedChart('years', 'carbon concentration (Gtc)',
                                                 [year_start - 5, year_end + 5],
                                                 [min_value, max_value],
                                                 chart_name)

            visible_line = True

            ordonate_data = list(atmo_conc)

            new_series = InstanciatedSeries(
                years, ordonate_data, 'atmosphere concentration', 'lines', visible_line)

            new_chart.series.append(new_series)

            instanciated_charts.append(new_chart)

        if 'Atmospheric concentrations parts per million' in chart_list:

            #carboncycle_df = discipline.get_sosdisc_outputs('carboncycle_df')
            ppm = carboncycle_df['ppm']

            years = list(ppm.index)

            chart_name = 'Atmospheric concentrations parts per million'

            year_start = years[0]
            year_end = years[len(years) - 1]

            min_value, max_value = self.get_greataxisrange(ppm)

            new_chart = TwoAxesInstanciatedChart('years', 'Atmospheric concentrations parts per million',
                                                 [year_start - 5, year_end + 5],
                                                 [min_value, max_value], chart_name)

            visible_line = True

            ordonate_data = list(ppm)

            new_series = InstanciatedSeries(
                years, ordonate_data, 'ppm', 'lines', visible_line)

            new_chart.series.append(new_series)

            # Rockstrom Limit

            ordonate_data = [450] * int(len(years) / 5)
            abscisse_data = np.linspace(
                year_start, year_end, int(len(years) / 5))
            new_series = InstanciatedSeries(
                abscisse_data.tolist(), ordonate_data, 'Rockstrom limit', 'scatter')

            note = {'Rockstrom limit': 'Scientifical limit of the Earth'}

            new_chart.series.append(new_series)

            # Minimum PPM constraint

            ordonate_data = [self.get_sosdisc_inputs(
                'minimum_ppm_limit')] * int(len(years) / 5)
            abscisse_data = np.linspace(
                year_start, year_end, int(len(years) / 5))
            new_series = InstanciatedSeries(
                abscisse_data.tolist(), ordonate_data, 'Minimum ppm limit', 'scatter')

            note['Minimum ppm limit'] = 'used in constraint calculation'
            new_chart.annotation_upper_left = note

            new_chart.series.append(new_series)

            instanciated_charts.append(new_chart)

        return instanciated_charts
