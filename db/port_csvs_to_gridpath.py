#!/usr/bin/env python
# Copyright 2017 Blue Marble Analytics LLC. All rights reserved.

"""
Port India data to GridPath
"""

from collections import OrderedDict
import csv
import os
import sqlite3
import warnings
import pandas as pd
import calendar
import numpy as np
import csv
import xlrd
import scipy.stats as stats
import math
import time
import datetime as dt
import sys

# Relative path to directory
##path_to_gridpath_modules = os.path.abspath(os.path.join(__file__,"../../3repo/gridpath/db/utilities"))
# Absolute path to directory
#path_to_gridpath_modules = os.path.abspath(os.path.join(__file__,"/Users/ranjitster/Dropbox/GridPath/1repo/gridpath/db/utilities"))
##sys.path.insert(0, path_to_gridpath_modules)

# Data-import modules

from db.utilities import temporal, geography, project_list, project_zones, \
    project_operational_chars, project_availability, fuels, \
    project_portfolios, project_existing_params, project_new_costs, \
    project_new_potentials, project_prm, transmission_portfolios, \
    transmission_zones, transmission_capacities, simultaneous_flow_groups, \
    simultaneous_flows, transmission_hurdle_rates, carbon_cap, system_load, \
    system_reserves, system_prm, rps, scenario

from db.csvs_to_db_utilities import csvs_read, load_geography, load_system_load, load_system_reserves, \
    load_project_zones, load_project_list, load_project_operational_chars, load_project_availability, \
    load_project_portfolios, load_project_existing_params, load_project_new_costs, load_project_new_potentials


## INPUTS
# SQL database
sql_database = 'io.db'

# Input csv path
dbPath = os.path.join(os.getcwd(), "db")

# Policy and reserves list
policy_list = ['carbon_cap', 'prm', 'rps']
reserves_list = ['frequency_response', 'lf_reserves_down', 'lf_reserves_up',
                 'regulation_down', 'regulation_up', 'spinning_reserves']

# Connect to database
io = sqlite3.connect(
    os.path.join(dbPath, sql_database)
)

c2 = io.cursor()


#### MASTER CSV DATA ####
# if include flag is 1, then read the feature, subscenario_id, table, and path into a dictionary and call the specific function for the feature
# TODO: remove subscenario_id from master csv table. It's redundant.
folder_path = os.path.join(os.getcwd(),'db', 'csvs')
csv_data_master = pd.read_csv(os.path.join(folder_path, 'csv_data_master.csv'))

#### LOAD GEORGRAPHY DATA ####

#### LOAD LOAD DATA ####

## GEOGRAPHY ##
if csv_data_master.loc[csv_data_master['table'] == 'geography_load_zones', 'include'].iloc[0] != 1:
    print("ERROR: geography_load_zones table is required")
else:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'geography_load_zones', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_geography.load_geography_load_zones(io, c2, csv_subscenario_input, csv_data_input)

## PROJECT LOAD ZONES ##
if csv_data_master.loc[csv_data_master['table'] == 'project_load_zones', 'include'].iloc[0] != 1:
    print("ERROR: project_load_zones table is required")
else:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'project_load_zones', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_project_zones.load_project_load_zones(io, c2, csv_subscenario_input, csv_data_input)

## SYSTEM LOAD ##
if csv_data_master.loc[csv_data_master['table'] == 'system_load', 'include'].iloc[0] != 1:
    print("ERROR: system_load table is required")
else:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'system_load', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_system_load.load_system_static_load(io, c2, csv_subscenario_input, csv_data_input)

#### LOAD PROJECTS DATA ####

## PROJECT LIST AND OPERATIONAL CHARS ##
# Note projects list is pulled from the project_operational_chars table
if csv_data_master.loc[csv_data_master['table'] == 'project_operational_chars', 'include'].iloc[0] != 1:
    print("ERROR: project_operational_chars table is required")
else:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'project_operational_chars', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    # This function is essential before any other project data is loaded in db. It loads the projects list.
    load_project_list.load_project_list(io, c2, csv_subscenario_input, csv_data_input)
    load_project_operational_chars.load_project_operational_chars(io, c2, csv_subscenario_input, csv_data_input)

## PROJECT HYDRO GENERATOR PROFILES ##
if csv_data_master.loc[csv_data_master['table'] == 'project_hydro_operational_chars', 'include'].iloc[0] == 1:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'project_hydro_operational_chars', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_project_operational_chars.load_project_hydro_opchar(io, c2, csv_subscenario_input, csv_data_input)

## PROJECT VARIABLE GENERATOR PROFILES ##
if csv_data_master.loc[csv_data_master['table'] == 'project_variable_generator_profiles', 'include'].iloc[0] == 1:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'project_variable_generator_profiles', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_project_operational_chars.load_project_variable_profiles(io, c2, csv_subscenario_input, csv_data_input)

## PROJECT PORTFOLIOS ##
if csv_data_master.loc[csv_data_master['table'] == 'project_portfolios', 'include'].iloc[0] == 1:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'project_portfolios', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_project_portfolios.load_project_portfolios(io, c2, csv_subscenario_input, csv_data_input)

## PROJECT EXISTING CAPACITIES ##
if csv_data_master.loc[csv_data_master['table'] == 'project_existing_capacity', 'include'].iloc[0] == 1:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'project_existing_capacity', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_project_existing_params.load_project_existing_capacities(io, c2, csv_subscenario_input, csv_data_input)

## PROJECT EXISTING FIXED COSTS ##
if csv_data_master.loc[csv_data_master['table'] == 'project_existing_fixed_cost', 'include'].iloc[0] == 1:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'project_existing_fixed_cost', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_project_existing_params.load_project_existing_fixed_costs(io, c2, csv_subscenario_input, csv_data_input)

## PROJECT NEW POTENTIAL ##
if csv_data_master.loc[csv_data_master['table'] == 'project_new_potential', 'include'].iloc[0] == 1:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'project_new_potential', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_project_new_potentials.load_project_new_potentials(io, c2, csv_subscenario_input, csv_data_input)

## PROJECT NEW COSTS ##
if csv_data_master.loc[csv_data_master['table'] == 'project_new_cost', 'include'].iloc[0] == 1:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'project_new_cost', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_project_new_costs.load_project_new_costs(io, c2, csv_subscenario_input, csv_data_input)

# subscenario_input = csv_subscenario_input
# data_input = csv_data_input

#### LOAD PROJECT AVAILABILITY DATA ####

## PROJECT AVAILABILITY TYPES ##
if csv_data_master.loc[csv_data_master['table'] == 'project_availability_types', 'include'].iloc[0] == 1:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'project_availability_types', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_project_availability.load_project_availability_types(io, c2, csv_subscenario_input, csv_data_input)

## PROJECT AVAILABILITY EXOGENOUS ##
if csv_data_master.loc[csv_data_master['table'] == 'project_availability_exogenous', 'include'].iloc[0] == 1:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'project_availability_exogenous', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_project_availability.load_project_availability_exogenous(io, c2, csv_subscenario_input, csv_data_input)

#### LOAD POLICY DATA ####

## GEOGRAPHY CARBON CAP ZONES ##
if csv_data_master.loc[csv_data_master['table'] == 'geography_carbon_cap_zones', 'include'].iloc[0] == 1:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'geography_carbon_cap_zones', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_geography.load_geography_carbon_cap_zones(io, c2, csv_subscenario_input, csv_data_input)

## GEOGRAPHY LOCAL CAPACITY ZONES ##
if csv_data_master.loc[csv_data_master['table'] == 'geography_local_capacity_zones', 'include'].iloc[0] == 1:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'geography_local_capacity_zones', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_geography.load_geography_local_capacity_zones(io, c2, csv_subscenario_input, csv_data_input)

## GEOGRAPHY PRM ZONES ##
if csv_data_master.loc[csv_data_master['table'] == 'geography_prm_zones', 'include'].iloc[0] == 1:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'geography_prm_zones', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_geography.load_geography_prm_zones(io, c2, csv_subscenario_input, csv_data_input)

## GEOGRAPHY RPS ZONES ##
if csv_data_master.loc[csv_data_master['table'] == 'geography_rps_zones', 'include'].iloc[0] == 1:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'geography_rps_zones', 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_geography.load_geography_rps_zones(io, c2, csv_subscenario_input, csv_data_input)

## PROJECT POLICY (CARBON CAP, PRM, RPS) ZONES ##
for policy_type in policy_list:
    if csv_data_master.loc[csv_data_master['table'] == 'project_' + policy_type + '_zones', 'include'].iloc[0] == 1:
        data_folder_path = os.path.join(folder_path, csv_data_master.loc[
            csv_data_master['table'] == 'project_' + policy_type + '_zones', 'path'].iloc[0])
        (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
        load_project_zones.load_project_policy_zones(io, c2, csv_subscenario_input, csv_data_input, policy_type)


#### LOAD RESERVES DATA ####

## GEOGRAPHY BAS ##
for reserve_type in reserves_list:
    if csv_data_master.loc[csv_data_master['table'] == 'geography_' + reserve_type + '_bas', 'include'].iloc[0] == 1:
        data_folder_path = os.path.join(folder_path, csv_data_master.loc[
            csv_data_master['table'] == 'geography_' + reserve_type + '_bas', 'path'].iloc[0])
        (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
        load_geography.load_geography_reserves_bas(io, c2, csv_subscenario_input, csv_data_input, reserve_type)

## PROJECT RESERVES BAS ##
for reserve_type in reserves_list:
    if csv_data_master.loc[csv_data_master['table'] == 'project_' + reserve_type + '_bas', 'include'].iloc[0] == 1:
        data_folder_path = os.path.join(folder_path, csv_data_master.loc[
            csv_data_master['table'] == 'project_' + reserve_type + '_bas', 'path'].iloc[0])
        (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
        load_project_zones.load_project_reserve_bas(io, c2, csv_subscenario_input, csv_data_input, reserve_type)

## SYSTEM RESERVES ##
if csv_data_master.loc[csv_data_master['table'] == 'system_' + reserve_type, 'include'].iloc[0] == 1:
    data_folder_path = os.path.join(folder_path, csv_data_master.loc[
        csv_data_master['table'] == 'system_' + reserve_type, 'path'].iloc[0])
    (csv_subscenario_input, csv_data_input) = csvs_read.csv_read_data(data_folder_path)
    load_system_reserves.load_system_reserves(io, c2, csv_subscenario_input, csv_data_input, reserve_type)
