#!/usr/bin/env python
# Copyright 2017 Blue Marble Analytics LLC. All rights reserved.

from __future__ import print_function

from builtins import str
from collections import OrderedDict
from importlib import import_module
import os.path
import sys
import unittest

from tests.common_functions import create_abstract_model, \
    add_components_and_load_data

TEST_DATA_DIRECTORY = \
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "test_data")

# Import prerequisite modules
PREREQUISITE_MODULE_NAMES = [
    "temporal.operations.timepoints", "temporal.operations.horizons",
    "temporal.investment.periods", "geography.load_zones",
    "geography.local_capacity_zones", "project", "project.capacity.capacity",
    "project.reliability.local_capacity"
]
NAME_OF_MODULE_BEING_TESTED = \
    "project.reliability.local_capacity.local_capacity_contribution"
IMPORTED_PREREQ_MODULES = list()
for mdl in PREREQUISITE_MODULE_NAMES:
    try:
        imported_module = import_module("." + str(mdl), package="gridpath")
        IMPORTED_PREREQ_MODULES.append(imported_module)
    except ImportError:
        print("ERROR! Module " + str(mdl) + " not found.")
        sys.exit(1)
# Import the module we'll test
try:
    MODULE_BEING_TESTED = import_module("." + NAME_OF_MODULE_BEING_TESTED,
                                        package="gridpath")
except ImportError:
    print("ERROR! Couldn't import module " + NAME_OF_MODULE_BEING_TESTED +
          " to test.")


class TestProjPRMSimple(unittest.TestCase):
    """

    """

    def test_add_model_components(self):
        """
        Test that there are no errors when adding model components
        :return:
        """
        create_abstract_model(prereq_modules=IMPORTED_PREREQ_MODULES,
                              module_to_test=MODULE_BEING_TESTED,
                              test_data_dir=TEST_DATA_DIRECTORY,
                              horizon="",
                              stage=""
                              )

    def test_load_model_data(self):
        """
        Test that data are loaded with no errors
        :return:
        """
        add_components_and_load_data(prereq_modules=IMPORTED_PREREQ_MODULES,
                                     module_to_test=MODULE_BEING_TESTED,
                                     test_data_dir=TEST_DATA_DIRECTORY,
                                     horizon="",
                                     stage=""
                                     )

    def test_data_loaded_correctly(self):
        """
        Test that the data loaded are as expected
        :return:
        """
        m, data = add_components_and_load_data(
            prereq_modules=IMPORTED_PREREQ_MODULES,
            module_to_test=MODULE_BEING_TESTED,
            test_data_dir=TEST_DATA_DIRECTORY,
            horizon="",
            stage=""
        )
        instance = m.create_instance(data)

        # Params: prm_simple_fraction
        expected_frac = OrderedDict(
            sorted(
                {"Nuclear": 1, "Gas_CCGT": 1, "Coal": 1, "Gas_CT": 1,
                 "Gas_CCGT_New": 1, "Gas_CT_New": 1, "Battery": 0.6,
                 "Battery_Specified": 0.5, "Hydro": 0.5,
                 "Hydro_NonCurtailable": 1, "Disp_Binary_Commit": 1,
                 "Disp_Cont_Commit": 1, "Disp_No_Commit": 1,
                 "Clunky_Old_Gen": 1, "Nuclear_Flexible": 1,
                 "Shift_DR": 0.2
                 }.items()
            )
        )
        actual_frac = OrderedDict(
            sorted(
                {prj: instance.local_capacity_fraction[prj] for prj in
                 instance.LOCAL_CAPACITY_PROJECTS}.items()
            )
        )

        self.assertDictEqual(expected_frac, actual_frac)