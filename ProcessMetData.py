#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Code that computes seasonal means / medians / distribution metrics
over 90 days prior to a specific date. Should be pretty self-
explanatory.

"""

__author__ = "Manon E. B. Sabot"
__version__ = "1.0 (01.09.2021)"
__email__ = "m.e.b.sabot@gmail.com"


# =====================================================================

# import general modules
import os  # check for files, paths, version on the system
import numpy as np  # array manipulations, math operators
import pandas as pd  # read/write dataframes, csv files


# =====================================================================

def main(infile, met_data):


    """
    Main function: creates csv output files of the same form as the
                   flowering data file, but with added temperature and
                   rainfall distribution data.

    Arguments:
    ----------
    infile: string
        input filename (without path), must be stored in the same
        folder as this script

    met_data: string
        folder within which the meteorological data is stored

    Returns:
    --------
    Saves the new files in this repository.

    """

    # read in flowering data
    fldts = pd.read_csv(os.path.join(os.getcwd(), infile))
    fldts['Date'] = pd.to_datetime(fldts['minimumfloweringdate'], dayfirst=True,
                                   errors='coerce')  # format dates

    for entry in os.scandir(os.path.join(os.getcwd(), '%s_data' % (met_data))):

        if entry.path.endswith('.csv'):
            if 'tmin' in entry.path:
                tmin = pd.read_csv(entry.path)

            if 'tmax' in entry.path:
                tmax = pd.read_csv(entry.path)

            if 'rain' in entry.path:
                rain = pd.read_csv(entry.path)

    tmid = pd.concat((tmin, tmax))  # halfway between the min and max
    tmid = tmid.groupby(tmid.index).mean()
    dfs = [tmin, tmax, tmid, rain]  # all dfs in a list

    for df in dfs:  # format dates

        try:  # station data
            df['Date'] = pd.to_datetime((df['Year'] * 10000 + df['Month'] * 100
                                         + df['Day']).apply(str), dayfirst=True)

        except KeyError:  # agcd / awap data
            try:
                df['Date'] = pd.to_datetime(df['date'], dayfirst=True,
                                            errors='coerce')

            except KeyError:  # the tmid doesn't have dates
                df['Date'] = dfs[0]['Date']

    new = calc_seasonal_variables(fldts, dfs)
    new.to_csv(os.path.join(os.getcwd(),
               '%s_%s_data.csv' % (os.path.splitext(infile)[0], met_data)))

    return


def calc_seasonal_variables(ref_df, met_dfs):

    """
    Calculates meteorological variables for a 90 day period prior to
    a specific date.

    Arguments:
    ----------
    ref_df: dataframe
        input dataframe containing the dates we're interested in

    met_dfs: list of dataframes
        the dataframes containing the met data are in the following
        order: minimum daily temperature, maximum daily temperature,
               midway daily temperature, daily rain

    Returns:
    --------
    The input dataframe + appended metrics

    """


    # new variables to be added to ref_df
    ref_df['avg_Tmin_degC'] = pd.np.nan
    ref_df['avg_Tmax_degC'] = pd.np.nan
    ref_df['med_Tmin_degC'] = pd.np.nan
    ref_df['med_Tmax_degC'] = pd.np.nan
    ref_df['min_Tmin_degC'] = pd.np.nan
    ref_df['max_Tmin_degC'] = pd.np.nan
    ref_df['min_Tmax_degC'] = pd.np.nan
    ref_df['max_Tmax_degC'] = pd.np.nan
    ref_df['avg_Tmid_degC'] = pd.np.nan
    ref_df['med_Tmid_degC'] = pd.np.nan
    ref_df['P5_Tmid_degC'] = pd.np.nan
    ref_df['P25_Tmid_degC'] = pd.np.nan
    ref_df['P75_Tmid_degC'] = pd.np.nan
    ref_df['P95_Tmid_degC'] = pd.np.nan
    ref_df['avg_Rain_mm'] = pd.np.nan
    ref_df['med_Rain_mm'] = pd.np.nan
    ref_df['max_Rain_mm'] = pd.np.nan
    ref_df['P5_Rain_mm'] = pd.np.nan
    ref_df['P25_Rain_mm'] = pd.np.nan
    ref_df['P75_Rain_mm'] = pd.np.nan
    ref_df['P95_Rain_mm'] = pd.np.nan

    for dt2 in ref_df['Date'].unique():

        # date 90 days prior (excl. dt2)
        dt1 = dt2 - pd.to_timedelta(91, unit='d')

        for i, cdf in enumerate(met_dfs):

            sub = cdf[np.logical_and(cdf['Date'] >= dt1, cdf['Date'] < dt2)]

            if i == 0:
                ref_df['avg_Tmin_degC'][ref_df['Date'] == dt2] = \
                    sub['value'].mean()
                ref_df['med_Tmin_degC'][ref_df['Date'] == dt2] = \
                    sub['value'].median()
                ref_df['min_Tmin_degC'][ref_df['Date'] == dt2] = \
                    sub['value'].min()
                ref_df['max_Tmin_degC'][ref_df['Date'] == dt2] = \
                    sub['value'].max()

            if i == 1:
                ref_df['avg_Tmax_degC'][ref_df['Date'] == dt2] = \
                    sub['value'].mean()
                ref_df['med_Tmax_degC'][ref_df['Date'] == dt2] = \
                    sub['value'].median()
                ref_df['min_Tmax_degC'][ref_df['Date'] == dt2] = \
                    sub['value'].min()
                ref_df['max_Tmax_degC'][ref_df['Date'] == dt2] = \
                    sub['value'].max()

            if i == 2:
                ref_df['avg_Tmid_degC'][ref_df['Date'] == dt2] = \
                    sub['value'].mean()
                ref_df['med_Tmid_degC'][ref_df['Date'] == dt2] = \
                    sub['value'].median()
                ref_df['P5_Tmid_degC'][ref_df['Date'] == dt2] = \
                    sub['value'].quantile(0.05)
                ref_df['P25_Tmid_degC'][ref_df['Date'] == dt2] = \
                    sub['value'].quantile(0.25)
                ref_df['P75_Tmid_degC'][ref_df['Date'] == dt2] = \
                    sub['value'].quantile(0.75)
                ref_df['P95_Tmid_degC'][ref_df['Date'] == dt2] = \
                    sub['value'].quantile(0.95)

            else:
                ref_df['avg_Rain_mm'][ref_df['Date'] == dt2] = \
                    sub['value'].mean()
                ref_df['med_Rain_mm'][ref_df['Date'] == dt2] = \
                    sub['value'].median()
                ref_df['max_Rain_mm'][ref_df['Date'] == dt2] = \
                    sub['value'].max()
                ref_df['P5_Rain_mm'][ref_df['Date'] == dt2] = \
                    sub['value'].quantile(0.05)
                ref_df['P25_Rain_mm'][ref_df['Date'] == dt2] = \
                    sub['value'].quantile(0.25)
                ref_df['P75_Rain_mm'][ref_df['Date'] == dt2] = \
                    sub['value'].quantile(0.75)
                ref_df['P95_Rain_mm'][ref_df['Date'] == dt2] = \
                    sub['value'].quantile(0.95)

    return ref_df


if __name__ == "__main__":

    # user inputs
    input = 'floweringdatawithminimumdate.csv'
    met_data = 'station'  # which kind of met data do we want?
    #met_data = 'agcd_nearest'
    #met_data = 'agcd_weighted'

    main(input, met_data)
