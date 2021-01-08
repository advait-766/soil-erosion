import os
import sys
import csv
import argparse
import logging
import numpy as np

if sys.version_info.major >= 3:
    from configparser import ConfigParser, NoSectionError, NoOptionError
else:
    from ConfigParser import ConfigParser, NoSectionError, NoOptionError

from smoderp2d.core.general import Globals
import math
from smoderp2d.providers.base import BaseProvider, Logger, CompType, \
    BaseWritter
from smoderp2d.providers.base.data_preparation import PrepareDataBase
from smoderp2d.providers.cmd import CmdWritter, CmdArgumentParser
from smoderp2d.exceptions import ConfigError, ProviderError


class NoGisProvider(BaseProvider, PrepareDataBase):
    def __init__(self, config_file=None):
        super(NoGisProvider, self).__init__()

        # load configuration
        cloader = CmdArgumentParser(config_file)
        # no gis has only roff comp type
        self.args.config_file, self.args.typecomp = cloader.set_config(
            "Run SMODERP1D.", typecomp='roff')
        self._config = self._load_config()

        # define storage writter
        self.storage = CmdWritter()

    def _load_input_data(self, filename_indata, filename_soil_types):
        """Load configuration data from roff computation procedure.

        :param str filename_indata: input CSV file
        :param str filename_soil_types: soil types CSV file

        :return: loaded data in numpy structured array
        """
        indata = self._load_csv_data(filename_indata)
        soil_types = self._load_csv_data(filename_soil_types)

        return self._join_indata_soils(indata, soil_types)

    @staticmethod
    def _load_csv_data(filename):
        """Get data from a CSV file in a dict-like form.

        :param filename: Path to the CSV file
        :return: numpy structured array
        """
        try:
            data = np.genfromtxt(filename, delimiter=';', names=True, dtype=None,
                                 encoding='utf-8-sig', deletechars='')
        except IndexError:
            raise ProviderError("Input file '{}' empty or invalid".format(filename))
        if data.size == 1:
            data = data.reshape(1)

        return data

    @staticmethod
    def _join_indata_soils(indata, soil_types):
        """Join data with slopes with corresponding parameters from soil types.

        :param indata: Data with slope attributes from input CSV file
        :param soil_types: Data with soil type attributes from input CSV file
        :return: joint and filtered data in numpy structured array
        """
        from numpy.lib.recfunctions import append_fields

        filtered_soilvegs = None
        soil_types_soilveg = soil_types['soilveg']

        for index in range(len(indata)):
            soilveg = indata['puda'][index] + indata['povrch'][index]

            # check for the misusage of comma for deciamls
            if any([',' in i for i in indata[index] if isinstance(i, str)]):
                raise ConfigError(
                    'Commas are not allowed characters in the data-data1d '
                    'CSV file. If used as decimal separators, please replace '
                    'them with dots')

            if soilveg not in soil_types_soilveg:
                raise ConfigError(
                    'soilveg {} from the data-data1d CSV file does not '
                    'match any soilveg from the data-data1d_soil_types CSV '
                    'file'.format(soilveg)
                )

            soilveg_line = soil_types[np.where(soil_types_soilveg == soilveg)]

            if filtered_soilvegs is not None:
                filtered_soilvegs = np.concatenate((filtered_soilvegs,
                                                    soilveg_line))
            else:
                filtered_soilvegs = soilveg_line

        try:
            soil_types_fields = filtered_soilvegs.dtype.names
        except AttributeError:
            raise ProviderError("Invalid input data. Empty joined dataset.")

        result = append_fields(
            indata,
            filtered_soilvegs.dtype.names,
            [filtered_soilvegs[name] for name in soil_types_fields],
            usemask=False
        )

        return result

    def _load_roff(self):
        """Load configuration data from roff computation procedure.

        :return dict: loaded data
        """
        from smoderp2d.processes import rainfall

        # read input csv files
        try:
            joint_data = self._load_input_data(
                self._config.get('data', 'data1d'),
                self._config.get('data', 'data1d_soil_types')
            )
        except IOError as e:
            raise ProviderError(e)
        except NoOptionError as e:
            raise ConfigError(e)

        # defaults for nogis provider
        #  type of computing =  1 sheet and rill flow
        data = {}
        data['type_of_computing'] = 1
        data['mfda'] = False

        # time settings
        try:
            data['end_time'] = self._config.getfloat('time', 'endtime') * 60.0
            data['maxdt'] = self._config.getfloat('time', 'maxdt')
        except NoSectionError as e:
            raise ConfigError(e)

        # load precipitation input file
        try:
            data['sr'], data['itera'] = rainfall.load_precipitation(
                self._config.get('data', 'rainfall')
            )
        except TypeError:
            raise ProviderError('Invalid rainfall file in [data] section')
        Logger.progress(10)


        # general settings
        # output directory is always set
        # TODO: isn't it already in globals?
        data['outdir'] = self._config.get('output', 'outdir')
        data['temp'] = os.path.join(data['outdir'], 'temp')
        # some self._configs are not in pickle.dump
        data['extraOut'] = self._config.getboolean('output', 'extraout', fallback=False)
        # rainfall data can be saved
        data['prtTimes'] = self._config.get('output', 'printtimes', fallback=None)

        resolution = self._config.getfloat('domain', 'res')
        # TODO: Change stah -> svah (ha ha) after being changed in the CSV
        data['r'] = self._compute_rows(joint_data['vodorovny_prumet_stahu[m]'],
                                       resolution)
        data['c'] = 1

        # set cell sizes
        data['vpix'] = data['spix'] = self._config.getfloat('domain', 'res')
        data['pixel_area'] = data['vpix'] * data['spix']

        # divide joint data slope into rows corresponding with data['r']
        parsed_data = self._divide_joint_data(joint_data, data['r'],
                                              data['vpix'])

        # allocate matrices
        self._alloc_matrices(data)

        # set no data value, likely used in nogis provider
        data['NoDataValue'] = -9999

        # topography
        data['mat_slope'] = self._compute_mat_slope(
            parsed_data['hor_len'], parsed_data['prevyseni[m]'])
        # TODO can be probably removed (?) or stay zero
        # data['mat_boundary'] = np.zeros((data['r'],data['c']), float)
        data['mat_efect_cont'].fill(data['spix']) # x-axis (EW) resolution
        # flow direction is always to the south
        data['mat_fd'].fill(4)

        # set x and y
        data['x'] = parsed_data['x'].reshape((data['r'], data['c']))
        data['y'] = parsed_data['y'].reshape((data['r'], data['c']))

        # set values to parameter matrics
        data['mat_n'] = parsed_data['n'].reshape((data['r'], data['c']))
        data['mat_b'] = parsed_data['b'].reshape((data['r'], data['c']))
        data['mat_a'], data['mat_aa'] = self._get_a(
            data['mat_n'],
            data['x'],
            data['y'],
            data['r'],
            data['c'],
            data['NoDataValue'],
            data['mat_slope'])
        data['mat_hcrit'] = self._get_crit_water(
            data['mat_b'],
            parsed_data['tau'].reshape((data['r'], data['c'])),
            parsed_data['v'].reshape((data['r'], data['c'])),
            data['r'],
            data['c'],
            data['mat_slope'],
            data['NoDataValue'],
            data['mat_aa']
        )

        data['mat_reten'] = parsed_data['ret'].reshape((data['r'], data['c']))
        data['mat_pi'] = parsed_data['pi'].reshape((data['r'], data['c']))
        data['mat_ppl'] = parsed_data['ppl'].reshape((data['r'], data['c']))

        data['mat_nan'] = np.nan
        data['mat_inf_index'].fill(1)  # 1 = philips infiltration

        data['mat_inf_index'], data['combinatIndex'] = \
            self._get_inf_combinat_index(
                data['r'],
                data['c'],
                parsed_data['k'].reshape((data['r'], data['c'])),
                parsed_data['s'].reshape((data['r'], data['c'])))

        data['mat_nan'], data['mat_slope'], data['mat_dem'] = \
            self._get_mat_nan(data['r'], data['c'], data['NoDataValue'],
                              data['mat_dem'], data['mat_slope'])

        data['array_points'], data['points'] = self._set_hydrographs(data['r'] - 1)
        # and other unused variables
        self._set_unused(data)
        data['rr'], data['rc'] = self._get_rr_rc(data['r'], data['c'],
                                                 data['mat_boundary'])

        # keep soilveg in memory - needed for profile.csv
        self.mat_soilveg = np.char.add(parsed_data['puda'], parsed_data['povrch'])
        self.hor_lengths = parsed_data['hor_len']

        return data

    def _compute_rows(self, lengths, resolution):
        """Compute number of pixels the slope will be divided into.

        :param lengths: np array containing all lengths
        :param resolution: intended resolution of one pixel
        :return: number of pixels, must be integer
        """
        nr_of_rows = int(round(np.sum(lengths) / resolution))

        return nr_of_rows

    @staticmethod
    def _compute_slope_length(lengths, heights):
        """Compute the slope length from lengths and heights.

        :param lengths: np array containing horizontal lengths
        :param heights: np array containing heights
        :return: length of slope
        """
        slope_lengths = np.sqrt(np.power(lengths, 2) + np.power(heights, 2))
        slope_length = np.sum(slope_lengths)

        return slope_length

    @staticmethod
    def _compute_mat_slope(lengths, heights):
        height_division = np.ones(heights.shape)
        for seg_height in np.unique(heights):
            seg_height_bool = heights == seg_height
            height_division = np.where(
                seg_height_bool, np.sum(seg_height_bool), height_division)

        pix_heights = heights / height_division

        return pix_heights / lengths

    def _divide_joint_data(self, joint_data, r, res):
        """Divide joint data into corresponding number of rows.

        :param joint_data: np structurred array with the joint data
        :param r: number of rows
        :param res: pixel resolution
        :return: divided, parsed joint data
        """
        from numpy.lib.recfunctions import merge_arrays
        parsed_data = None
        subsegment_unseen = 0

        hor_length = np.sum(joint_data['vodorovny_prumet_stahu[m]'])
        diff = hor_length - (r * res)
        addition = diff / r
        one_pix_len = res + addition

        for slope_segment in joint_data:
            segment_length = np.sum(
                slope_segment['vodorovny_prumet_stahu[m]'])
            seg_r = self._compute_rows(segment_length, one_pix_len)

            seg_hor_len_arr = np.array(
                [one_pix_len],
                dtype=[('hor_len', 'f4')])
            data_entry = merge_arrays(
                (slope_segment, seg_hor_len_arr),
                flatten=True)

            subsegment_unseen += segment_length

            while subsegment_unseen >= (one_pix_len / 2):
                if parsed_data is not None:
                    parsed_data = np.concatenate((parsed_data,
                                                  data_entry[True]))
                else:
                    parsed_data = data_entry[True]

                subsegment_unseen -= one_pix_len

        return parsed_data

    def _alloc_matrices(self, data):
        # TODO: use loop (check base provider)
        # allocate matrices
        data['mat_b'] = np.zeros((data['r'],data['c']), float)
        data['mat_stream_reach'] = np.zeros((data['r'],data['c']), float)
        data['mat_a'] = np.zeros((data['r'],data['c']), float)
        data['mat_slope'] = np.zeros((data['r'],data['c']), float)
        data['mat_n'] = np.zeros((data['r'],data['c']), float)
        # dem is not needed for computation
        data['mat_dem'] = np.zeros((data['r'],data['c']), float)
        data['mat_inf_index'] = np.zeros((data['r'],data['c']), float)
        data['mat_fd'] = np.zeros((data['r'],data['c']), float)
        data['mat_hcrit'] = np.zeros((data['r'],data['c']), float)
        data['mat_aa'] = np.zeros((data['r'],data['c']), float)
        data['mat_reten'] = np.zeros((data['r'],data['c']), float)
        data['mat_nan'] = np.zeros((data['r'],data['c']), float)
        data['mat_efect_cont'] = np.zeros((data['r'],data['c']), float)
        data['mat_pi'] = np.zeros((data['r'],data['c']), float)
        data['mat_boundary'] = np.zeros((data['r'],data['c']), float)
        data['mat_ppl'] = np.zeros((data['r'],data['c']), float)

    def _set_unused(self, data):
        data['cell_stream'] = None
        data['state_cell'] = None
        data['outletCells'] = None
        data['STREAM_RATIO'] = None
        data['bc'] = None
        data['br'] = None
        data['streams_loc'] = None
        data['streams'] = None
        data['poradi'] = None

    def _set_hydrographs(self, max_row):
        """Get array_points and points for the data dictionary.

        These keys are needed to force the run to compute hydrographs.
        Hydrograph is computed only for the last row, therefore preset values.

        :param max_row: index of the last cell
        """
        array_points = np.array([1, max_row, 0, 0, 0]).reshape((1, 5))
        points = 'test'

        return array_points, points

    def postprocessing(self, cumulative, surface_array, stream):
        super().postprocessing(cumulative, surface_array, stream)

        # extra to normal postprocessing - write profile.csv

        slope_width = float(self._config.get('domain', 'slope_width'))

        header = ['length[m]', 'soil_vegFID', 'maximalSurfaceFlow[m3/s]',
                  'totalRunoff[m3]', 'maximalSurfaceRunoffVelocity[m/s]',
                  'maximalTangentialStress[Pa]', 'rillRunoff[Y/N]']
        vals_to_write = (
            self.hor_lengths.flatten(),
            self.mat_soilveg.flatten(),
            cumulative.q_sur_tot.flatten() * slope_width,
            cumulative.vol_rill.flatten() * slope_width,
            cumulative.v_sheet.flatten(),
            cumulative.shear_sheet.flatten(),
            [0 if i.state == 0 else 1 for i in surface_array.flatten()]
        )

        profile_path = os.path.join(Globals.outdir, 'profile.csv')
        with open(profile_path, 'w') as out_csv:
            writer = csv.writer(out_csv)

            writer.writerow(header)
            writer.writerows(zip(*vals_to_write))
