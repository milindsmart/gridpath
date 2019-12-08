#!/usr/bin/env python
# Copyright 2019 Blue Marble Analytics LLC. All rights reserved.

"""
Load project operational chars data
"""

from db.utilities import project_operational_chars

def load_project_operational_chars(io, c, subscenario_input, data_input):
    """
    :param io:
    :param c:
    :param subscenario_input:
    :param data_input:
    :return:
    """

    operational_chars_integers = ['heat_rate_curves_scenario_id', 'min_up_time_hours', 'min_down_time_hours',
                                  'variable_generator_profile_scenario_id', 'hydro_operational_chars_scenario_id']
    operational_chars_non_integers = data_input.columns.difference(
        operational_chars_integers + ['project_operational_chars_scenario_id', 'project']).tolist()

    for i in subscenario_input.index:
        sc_id = int(subscenario_input['project_operational_chars_scenario_id'][i])
        sc_name = subscenario_input['name'][i]
        sc_description = subscenario_input['description'][i]

        data_input_subscenario = data_input.loc[(data_input['project_operational_chars_scenario_id'] == sc_id)]

        # Make subscenario and insert all projects into operational
        # characteristics table; we'll then update that table with the
        # operational characteristics each project needs
        project_operational_chars.make_scenario_and_insert_all_projects(
            io=io, c=c,
            project_operational_chars_scenario_id=sc_id,
            scenario_name=sc_name,
            scenario_description=sc_description
        )

        # ### Operational chars integers ### #
        for op_chars in operational_chars_integers:
            if data_input_subscenario[op_chars].notnull().sum() != 0:
                print("Loading " + op_chars)
                operational_chars_dict = dict()
                operational_chars_df = data_input_subscenario.loc[:, ['project', op_chars]].dropna()
                operational_chars_df[[op_chars]] = operational_chars_df[
                    [op_chars]].astype(int)  # Otherwise they could be floats or numpy ints
                operational_chars_dict = operational_chars_df.set_index(
                    'project')[op_chars].to_dict()

                project_operational_chars.update_project_opchar_column(
                    io=io, c=c,
                    project_operational_chars_scenario_id=sc_id,
                    column=op_chars,
                    project_char=operational_chars_dict
                )

        # ### Operational chars non-integers (strings and floats) ### #
        for op_chars in operational_chars_non_integers:
            if data_input_subscenario[op_chars].notnull().sum() != 0:
                print("Loading " + op_chars)
                operational_chars_dict = dict()
                operational_chars_dict = data_input_subscenario.loc[:, ['project', op_chars]].dropna().set_index(
                    'project')[op_chars].to_dict()

                project_operational_chars.update_project_opchar_column(
                    io=io, c=c,
                    project_operational_chars_scenario_id=sc_id,
                    column=op_chars,
                    project_char=operational_chars_dict
                )

def load_project_variable_profiles(io, c, subscenario_input, data_input):
    """
    Data dictionary is {project:{scenario_id:{stage_id:{timepoint: cap_factor}}}}
    :param io:
    :param c:
    :param subscenario_input:
    :param data_input:
    :return:
    """

    project_tmp_profiles = dict()
    project_tmp_profiles_scenarios = dict()

    for i in subscenario_input.index:
        sc_id = int(subscenario_input['variable_generator_profile_scenario_id'][i])
        sc_name = subscenario_input['name'][i]
        sc_description = subscenario_input['description'][i]
        prj = subscenario_input['project'][i]

        project_tmp_profiles_scenarios[prj] = dict()
        project_tmp_profiles_scenarios[prj][sc_id] = (sc_name, sc_description)

        project_tmp_profiles[prj] = dict()
        project_tmp_profiles[prj][sc_id] = dict()

        project_tmp_profiles_by_project = data_input.loc[
                (data_input['variable_generator_profile_scenario_id'] == sc_id) & (data_input['project'] == prj)]

        for st_id in project_tmp_profiles_by_project['stage_id'].unique():
            project_tmp_profiles_by_project_stage = project_tmp_profiles_by_project.loc[
                project_tmp_profiles_by_project['stage_id'] == st_id, ['timepoint', 'cap_factor']]
            project_tmp_profiles_by_project_stage[['timepoint']] = \
                project_tmp_profiles_by_project_stage[['timepoint']].astype(int)
            project_tmp_profiles[prj][sc_id][int(st_id)] = \
                project_tmp_profiles_by_project_stage.set_index('timepoint')['cap_factor'].to_dict()

    project_operational_chars.update_project_variable_profiles(
        io=io, c=c,
        proj_profile_names=project_tmp_profiles_scenarios,
        proj_tmp_profiles=project_tmp_profiles
    )

def load_project_hydro_opchar(io, c, subscenario_input, data_input):
    """
    Data output dictionary is {project:{scenario_id:{balancing_type:{horizon:{period, avg, min, max}}}}}
    :param io:
    :param c:
    :param subscenario_input:
    :param data_input:
    :return:
    """

    project_horizon_chars = dict()
    project_horizon_chars_scenarios = dict()

    for i in subscenario_input.index:
        sc_id = int(subscenario_input['hydro_operational_chars_scenario_id'][i])
        sc_name = subscenario_input['name'][i]
        sc_description = subscenario_input['description'][i]
        prj = subscenario_input['project'][i]

        project_horizon_chars_scenarios[prj] = dict()
        project_horizon_chars_scenarios[prj][sc_id] = (sc_name, sc_description)

        project_horizon_chars[prj] = dict()
        project_horizon_chars[prj][sc_id] = dict()

        project_horizon_chars_by_project = data_input.loc[
            (data_input['hydro_operational_chars_scenario_id'] == sc_id) & (data_input['project'] == prj)]

        for b_type in project_horizon_chars_by_project['balancing_type_project'].unique():
            project_horizon_chars_by_project_balancing_type = project_horizon_chars_by_project.loc[
                project_horizon_chars_by_project['balancing_type_project'] == b_type, ['horizon', 'period', 'avg', 'min', 'max']]
            project_horizon_chars_by_project_balancing_type[['horizon']] = \
                project_horizon_chars_by_project_balancing_type[['horizon']].astype(int)
            project_horizon_chars_by_project_balancing_type[['period']] = \
                project_horizon_chars_by_project_balancing_type[['period']].astype(int)
            project_horizon_chars[prj][sc_id][b_type] = \
                project_horizon_chars_by_project_balancing_type[[
                    'horizon', 'period', 'avg', 'min', 'max']].set_index(['horizon']).to_dict(orient='index')

    project_operational_chars.update_project_hydro_opchar(
        io=io, c=c,
        proj_opchar_names=project_horizon_chars_scenarios,
        proj_horizon_chars=project_horizon_chars
    )