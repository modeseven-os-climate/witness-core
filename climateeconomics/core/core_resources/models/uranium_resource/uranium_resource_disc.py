'''
Copyright 2022 Airbus SAS
Modifications on 2023/06/14-2023/11/03 Copyright 2023 Capgemini

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
from os.path import dirname, join

import numpy as np
import pandas as pd

from climateeconomics.core.core_resources.models.uranium_resource.uranium_resource_model import (
    UraniumResourceModel,
)
from climateeconomics.core.core_resources.resource_model.resource_disc import (
    ResourceDiscipline,
)
from climateeconomics.glossarycore import GlossaryCore
from sostrades_core.execution_engine.sos_wrapp import SoSWrapp


class UraniumResourceDiscipline(ResourceDiscipline):
    ''' Discipline intended to get oil parameters
    '''

    # ontology information
    _ontology_data = {
        'label': 'Uranium Resource Model',
        'type': 'Research',
        'source': 'SoSTrades Project',
        'validated': '',
        'validated_by': 'SoSTrades Project',
        'last_modification_date': '',
        'category': '',
        'definition': '',
        'icon': 'fas fa-oil-can fa-fw',
        'version': '',
    }
    default_year_start = GlossaryCore.YearStartDefault
    default_year_end = 2050
    default_production_start = 1970
    default_regression_start = 2015
    default_uranium_accessibility = 'recoverable'
    default_years = np.arange(default_year_start, default_year_end + 1, 1)
    default_stock_start = 0.0
    default_recycled_rate = 0.0
    default_lifespan = 0
    resource_name = UraniumResourceModel.resource_name

    prod_unit = 't'
    stock_unit = 't'
    price_unit = '$/k'

    # Get default data for resource
    default_resource_data = pd.read_csv(
        join(dirname(__file__), f'../resources_data/{resource_name}_data.csv'))
    default_resource_production_data = pd.read_csv(join(
        dirname(__file__), f'../resources_data/{resource_name}_production_data.csv'))
    default_resource_price_data = pd.read_csv(
        join(dirname(__file__), f'../resources_data/{resource_name}_price_data.csv'))
    default_resource_consumed_data = pd.read_csv(
        join(dirname(__file__), f'../resources_data/{resource_name}_consumed_data.csv'))

    DESC_IN = {'resource_data': {'type': 'dataframe', 'unit': '[-]', 'default': default_resource_data,
                                 'user_level': 2, 'namespace': 'ns_uranium_resource',
                                 'dataframe_descriptor':
                                     {
                                         GlossaryCore.Years: ('float', None, False),
                                         'Accessibility': ('string', None, True),
                                         'Price': ('float', None, True),
                                         'Price_unit': ('string', None, True),
                                         'Reserve': ('float', None, True),
                                         'Reserve_unit': ('string', None, True),
                                         'Region': ('string', None, True),
                                      }
                                 },
               'resource_production_data': {'type': 'dataframe', 'unit': 't', 'optional': True,
                                            'default': default_resource_production_data, 'user_level': 2, 'namespace': 'ns_uranium_resource',
                                            'dataframe_descriptor':{
                                                 GlossaryCore.Years: ('float', None, False),
                                                'uranium_40': ('float', None, True),
                                                 'uranium_80': ('float', None, True),
                                                 'uranium_130': ('float', None, True),
                                                 'uranium_260': ('float', None, True),
                                                 'uranium_260_consumption': ('float', None, True),
                                              }},
               'resource_price_data': {'type': 'dataframe', 'unit': '$/kg', 'default': default_resource_price_data, 'user_level': 2,
                                       'dataframe_descriptor': {
                                                 GlossaryCore.Years: ('float', None, False),
                                                 'uranium_40_consumption': ('float', None, True),
                                                 'uranium_80_consumption': ('float', None, True),
                                                 'uranium_130_consumption': ('float', None, True),
                                                 'uranium_260_consumption': ('float', None, True),
                                                 'resource_type': ('string', None, True),
                                           'price': ('float', None, True),
                                           'unit': ('string', None, True),
                                              },
                                       'namespace': 'ns_uranium_resource'},
               'resource_consumed_data': {'type': 'dataframe', 'unit': '[t]', 'default': default_resource_consumed_data,
                                          'user_level': 2, 'namespace': 'ns_uranium_resource',
                                          'dataframe_descriptor':
                                             {
                                                 GlossaryCore.Years: ('float', None, False),
                                                 'uranium_40_consumption': ('float', None, True),
                                                 'uranium_80_consumption': ('float', None, True),
                                                 'uranium_130_consumption': ('float', None, True),
                                                 'uranium_260_consumption': ('float', None, True),
                                                 'Reserve_unit': ('float', None, True),
                                              }
                                         },
               'production_start': {'type': 'int', 'default': default_production_start, 'unit': '[-]',
                                    'visibility': SoSWrapp.SHARED_VISIBILITY, 'namespace': 'ns_uranium_resource'},
               'regression_start': {'type': 'int', 'default': default_regression_start, 'unit': '[-]',
                                    'visibility': SoSWrapp.SHARED_VISIBILITY, 'namespace': 'ns_uranium_resource'},
               'stock_start': {'type': 'float', 'default': default_stock_start, 'unit': '[Mt]'},
               'recycled_rate': {'type': 'float', 'default': default_recycled_rate, 'unit': '[-]'},
               'lifespan': {'type': 'int', 'default': default_lifespan, 'unit': '[-]'},
               }

    DESC_IN.update(ResourceDiscipline.DESC_IN)

    DESC_OUT = {
        'resource_stock': {'type': 'dataframe', 'unit': stock_unit, },
        'resource_price': {'type': 'dataframe', 'unit': price_unit, },
        'use_stock': {'type': 'dataframe', 'unit': stock_unit, },
        'predictable_production': {'type': 'dataframe', 'unit': prod_unit, },
        'recycled_production': {
            'type': 'dataframe', 'unit': prod_unit}
    }
    DESC_OUT.update(ResourceDiscipline.DESC_OUT)

    def init_execution(self):
        inputs_dict = self.get_sosdisc_inputs()
        self.resource_model = UraniumResourceModel(self.resource_name)
        self.resource_model.configure_parameters(inputs_dict)
