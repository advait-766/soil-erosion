# @package nacteni a uloze hodnot co jsou z data preparation
#  roff, dpre, full se resi  resolve_partial_computin
#  odtud se jen vola tato funkce.


import math
import sys


# get type of computing identifier based on the string
from smoderp2d.tools.tools import comp_type

from smoderp2d.tools.tools import get_argv
import smoderp2d.constants as constants


# Documentation for a class.
#
#  method to compute size of class arrays
class Size:

    # size
    #  @param arrayNBytes <numpy array>.nbytes
    #  @param m value in denominator to get bytes, kilobytes (m=2**10), megabytes (m=2**10+m**10) and so on.

    def size(self, arrayNBytes, m=1.0):
        # arrayNBytes eq self.state.nbytes
        size = (self.n * arrayNBytes) / m
        return size


# Class Globals contains global variables
#
#  from data_preparation, in instance of class needed
#  the data are taken from import of this class
#
class Globals:

    # area of a raster cell in meters
    pixel_area = None
    # number of rows in rasters
    r = None
    # number of columns in rasters
    c = None
    # id of rows in computational domain
    rr = None
    # id of columns in computational domain
    rc = None
    # x coordinate od of left bottom corner of raster
    xllcorner = None
    # y coordinate od of left bottom corner of raster
    yllcorner = None
    # size of raster cell
    dx = None

    # no data value for raster
    NoDataValue = None
    # no data integer value for raster
    NoDataInt = None

    # path to a output directory
    outdir = None
    # path to directory for temporal data storage
    temp = None

    # array containing information of hydrogram points
    array_points = None

    # combinatIndex
    combinatIndex = None

    # raster contains potential interception data
    mat_pi = None
    # raster contains leaf area data
    mat_ppl = None
    # raster contains id of infiltration type
    mat_inf_index = None
    # raster contains critical water level
    mat_hcrit = None
    # raster contains parameter of power law for surface runoff
    mat_aa = None
    # raster contains parameter of power law for surface runoff
    mat_b = None
    # raster contains surface retention data
    mat_reten = None
    # raster contains parameters ...
    mat_a = None
    # raster contains parameters ...
    mat_n = None

    # raster contains flow direction datas
    mat_fd = None
    # raster contains digital elevation model
    mat_dmt = None
    # raster contains efective couterline data
    mat_efect_vrst = None
    # raster contains surface slopes data
    mat_slope = None

    # raster labels not a number cells (MASK)
    mat_nan = None

    # type of computation
    type_of_computing = None
    # bool variable for flow direction algorithm (false=one direction, true multiple flow direction)
    mfda = None

    # list contains the precipitation data
    sr = None
    # counter of precipitation intervals
    itera = None

    # reach information
    toky = None
    # raster contains the reach id data
    mat_reach = None
    # where to store used points for hydrographs
    tokyLoc = None

    # end time of computation
    end_time = None
    # time step
    maxdt = None

    def get_pixel_area(self):
        return self.pixel_area

    def get_rows(self):
        return self.r

    def get_cols(self):
        return self.c

    def get_rrows(self):
        return self.rr

    def get_rcols(self):
        return self.rc

    def get_xllcorner(self):
        return self.xllcorner

    def get_yllcorner(self):
        return self.yllcorner

    def get_NoDataValue(self):
        return self.NoDataValue

    def get_NoDataInt(self):
        return self.NoDataInt

    def get_dx(self):
        return self.dx

    def get_type_of_computing(self):
        return self.type_of_computing

    def get_outdir(self):
        return self.outdir

    def get_array_points(self):
        return self.array_points

    def get_combinatIndex(self):
        return self.combinatIndex

    def get_mat_pi(self):
        return self.mat_pi

    def get_mat_ppl(self):
        return self.mat_ppl

    def get_mat_inf_index(self):
        return self.mat_inf_index

    def get_mat_hcrit(self):
        return self._mat_hcrit

    def get_mat_aa(self):
        return self.mat_aa

    def get_mat_b(self):
        return self.mat_b

    def get_mat_reten(self):
        return self.mat_reten

    def get_mat_fd(self):
        return self.mat_fd

    def get_mat_dmt(self):
        return self.mat_dmt

    def get_mat_efect_vrst(self):
        return self.mat_efect_vrst

    def get_mat_slope(self, i, j):
        return self.mat_slope[i][j]

    def get_mat_nan(self):
        return self.mat_nan

    def get_mat_a(self):
        return self.mat_a

    def get_mat_n(self, i, j):
        return self.mat_n[i][j]

    def get_end_tim(self):
        return self.end_time

    def get_temp(self):
        return self.temp

    def get_mfda(self):
        return self.mfda

    def get_sr(self):
        return self.sr

    def get_itera(self):
        return self.itera

    def get_toky(self):
        return self.toky

    def get_mat_reach(self, i, j):
        return self.mat_reach[i][j]

    def get_tokyLoc(self):
        return self.tokyLoc


# Init fills the Globals class with values from preprocessing
#
def initLinux():

    # get_indata is method which reads the input data
    from smoderp2d.tools.resolve_partial_computing import get_indata_lin
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('typecomp', help='type of computation',
                        type=str, choices=['full', 'dpre', 'roff'])
    parser.add_argument('--indata', help='file with input data', type=str)
    args = parser.parse_args()
    partial_comp = args.typecomp

    if (partial_comp == 'roff'):

        boundaryRows, boundaryCols, \
            mat_boundary, rrows, rcols, outletCells, \
            x_coordinate, y_coordinate,\
            NoDataValue, array_points, \
            cols, rows, combinatIndex, delta_t,  \
            mat_pi, mat_ppl, \
            surface_retention, mat_inf_index, mat_hcrit, mat_aa, mat_b, mat_reten,\
            mat_fd, mat_dmt, mat_efect_vrst, mat_slope, mat_nan, \
            mat_a,   \
            mat_n,   \
            output, pixel_area, points, poradi,  end_time, spix, state_cell, \
            temp, type_of_computing, vpix, mfda, sr, itera, \
            toky, cell_stream, mat_reach, STREAM_RATIO, tokyLoc, extraOut, prtTimes, \
            maxdt = get_indata_lin(partial_comp, args)

        # geometry information
        Globals.pixel_area = pixel_area
        Globals.r = rows
        Globals.c = cols
        Globals.rr = rrows
        Globals.rc = rcols
        Globals.xllcorner = x_coordinate
        Globals.yllcorner = y_coordinate
        Globals.dx = math.sqrt(pixel_area)

        # NoDataValue definition
        Globals.NoDataValue = NoDataValue
        Globals.NoDataInt = int(-9999)

        # output directories
        Globals.outdir = output
        Globals.temp = temp

        # points of hydrpgraphs
        Globals.array_points = array_points

        # infiltration set
        Globals.combinatIndex = combinatIndex

        # matrices with parameters
        Globals.mat_pi = mat_pi
        Globals.mat_ppl = mat_ppl
        Globals.mat_inf_index = mat_inf_index
        Globals.mat_hcrit = mat_hcrit
        Globals.mat_aa = mat_aa
        Globals.mat_b = mat_b
        Globals.mat_reten = -mat_reten/1000.
        Globals.mat_a = mat_a
        Globals.mat_n = mat_n

        # DMT inferred parameters
        Globals.mat_fd = mat_fd
        Globals.mat_dmt = mat_dmt
        Globals.mat_efect_vrst = mat_efect_vrst
        Globals.mat_slope = mat_slope

        # maks delineation array
        Globals.mat_nan = mat_nan

        # definition of solved processes
        Globals.type_of_computing = type_of_computing
        Globals.mfda = mfda
        Globals.diffuse = comp_type(type_of_computing, 'diffuse')
        Globals.subflow = comp_type(type_of_computing, 'subflow')
        Globals.isRill = comp_type(type_of_computing, 'rill')
        Globals.isStream = comp_type(type_of_computing, 'stream')

        # rainfall information
        Globals.sr = sr
        Globals.itera = itera

        # reaches information
        Globals.toky = toky
        Globals.tokyLoc = tokyLoc
        Globals.mat_reach = mat_reach

        # I/O parametrs
        Globals.extraOut = extraOut
        Globals.arcgis = False
        Globals.prtTimes = prtTimes

        # time step information
        Globals.end_time = end_time
        Globals.maxdt = maxdt

        return True

    else:
        print 'for Linux only roff'
        return False


# Init fills the Globals class with values from preprocessing
#
def initWin():

        # get_indata is method which reads the input data
    from smoderp2d.tools.resolve_partial_computing import get_indata_win

    partial_comp = get_argv(constants.PARAMETER_PARTIAL_COMPUTING)

    if (partial_comp == 'roff') | (partial_comp == 'full'):

        boundaryRows, boundaryCols, \
            mat_boundary, rrows, rcols, outletCells, \
            x_coordinate, y_coordinate,\
            NoDataValue, array_points, \
            cols, rows, combinatIndex, delta_t,  \
            mat_pi, mat_ppl, \
            surface_retention, mat_inf_index, mat_hcrit, mat_aa, mat_b, mat_reten,\
            mat_fd, mat_dmt, mat_efect_vrst, mat_slope, mat_nan, \
            mat_a,   \
            mat_n,   \
            output, pixel_area, points, poradi,  end_time, spix, state_cell, \
            temp, type_of_computing, vpix, mfda, sr, itera, \
            toky, cell_stream, mat_tok_reach, STREAM_RATIO, tokyLoc = get_indata_win(
                partial_comp, sys.argv)

        sys.argv.append(type_of_computing)

        Globals.pixel_area = pixel_area
        Globals.r = rows
        Globals.c = cols
        Globals.rr = rrows
        Globals.rc = rcols
        Globals.br = boundaryRows
        Globals.bc = boundaryCols
        Globals.xllcorner = x_coordinate
        Globals.yllcorner = y_coordinate
        Globals.NoDataValue = NoDataValue
        Globals.NoDataInt = int(-9999)
        Globals.dx = math.sqrt(pixel_area)
        Globals.dy = Globals.dx
        Globals.type_of_computing = type_of_computing
        Globals.outdir = output
        Globals.mat_boundary = mat_boundary
        Globals.outletCells = outletCells
        Globals.array_points = array_points
        Globals.combinatIndex = combinatIndex
        Globals.mat_pi = mat_pi
        Globals.mat_ppl = mat_ppl
        Globals.surface_retention = surface_retention
        Globals.mat_inf_index = mat_inf_index
        Globals.mat_hcrit = mat_hcrit
        Globals.mat_aa = mat_aa
        Globals.mat_b = mat_b
        Globals.mat_reten = -mat_reten / 1000.
        Globals.mat_fd = mat_fd
        Globals.mat_dmt = mat_dmt
        Globals.mat_efect_vrst = mat_efect_vrst
        Globals.mat_slope = mat_slope
        Globals.mat_nan = mat_nan
        Globals.mat_a = mat_a
        Globals.mat_n = mat_n
        Globals.points = points
        Globals.poradi = poradi
        Globals.end_time = end_time
        Globals.spix = spix
        Globals.state_cell = state_cell
        Globals.temp = temp
        Globals.vpix = vpix
        Globals.mfda = mfda
        Globals.sr = sr
        Globals.itera = itera
        Globals.toky = toky
        Globals.cell_stream = cell_stream
        Globals.mat_tok_reach = mat_tok_reach
        Globals.STREAM_RATIO = STREAM_RATIO
        Globals.tokyLoc = tokyLoc
        Globals.diffuse = comp_type('diffuse')
        Globals.subflow = comp_type('subflow')

        return True

    elif (partial_comp == 'dpre'):
        stop = get_indata_win(partial_comp, sys.argv)
        return stop


def initNone():
    print "Unsupported platform."
    print "Exiting smoderp 2d..."
    return False
