##########################################################################
#                                                                        #
# Copyright (C) 2015 Carsten Fortmann-Grote                              #
# Contact: Carsten Fortmann-Grote <carsten.grote@xfel.eu>                #
#                                                                        #
# This file is part of simex_platform.                                   #
# simex_platform is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# simex_platform is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
# Include needed directories in sys.path.                                #
#                                                                        #
##########################################################################

""" Module that holds the XMDYNDemoPhotonMatterInteractor class.

    @author : CFG
    @institution : XFEL
    @creation 20151215

"""
import os
import subprocess


from pmi_demo import PMIDemo
import pmi_script

from SimEx.Calculators.AbstractPhotonInteractor import AbstractPhotonInteractor
from TestUtilities.TestUtilities import generateTestFilePath


class XMDYNDemoPhotonMatterInteractor(AbstractPhotonInteractor):
    """
    Class representing a x-ray free electron laser photon propagator.
    """

    def __init__(self,  parameters=None, input_path=None, output_path=None, sample_path=None):
        """
        Constructor for the xfel photon propagator.

        @param parameters : Parameters that govern the PMI calculation.
        @type : dict

        @param input_path : Location of data needed by the PMI calculation (Laser source wavefront data).
        @type : string

        @param output_path : Where to store the data generated by the PMI calculation.
        @type : string

        @param sample_path : Location of the sample specification file.
        @type : string
        """

        # Initialize base class.
        super(XMDYNDemoPhotonMatterInteractor, self).__init__(parameters,input_path,output_path)

        self.__sample_path = sample_path

        self.__provided_data = ['/data/snp_<7 digit index>/ff',
                                '/data/snp_<7 digit index>/halfQ',
                                '/data/snp_<7 digit index>/Nph',
                                '/data/snp_<7 digit index>/r',
                                '/data/snp_<7 digit index>/T',
                                '/data/snp_<7 digit index>/Z',
                                '/data/snp_<7 digit index>/xyz',
                                '/data/snp_<7 digit index>/Sq_halfQ',
                                '/data/snp_<7 digit index>/Sq_bound',
                                '/data/snp_<7 digit index>/Sq_free',
                                '/history/parent/detail',
                                '/history/parent/parent',
                                '/info/package_version',
                                '/info/contact',
                                '/info/data_description',
                                '/info/method_description',
                                '/version']

        self.__expected_data = ['/data/arrEhor',
                                '/data/arrEver',
                                '/params/Mesh/nSlices',
                                '/params/Mesh/nx',
                                '/params/Mesh/ny',
                                '/params/Mesh/qxMax',
                                '/params/Mesh/qxMin',
                                '/params/Mesh/qyMax',
                                '/params/Mesh/qyMin',
                                '/params/Mesh/sliceMax',
                                '/params/Mesh/sliceMin',
                                '/params/Mesh/xMax',
                                '/params/xMin',
                                '/params/yMax',
                                '/params/yMin',
                                '/params/zCoord',
                                '/params/beamline/printout',
                                '/params/Rx',
                                '/params/Ry',
                                '/params/dRx',
                                '/params/dRy',
                                '/params/nval',
                                '/params/photonEnergy',
                                '/params/wDomain',
                                '/params/wEFieldUnit',
                                '/params/wFloatType',
                                '/params/wSpace',
                                '/params/xCentre',
                                '/params/yCentre',
                                '/info/package_version',
                                '/info/contact',
                                '/info/data_description',
                                '/info/method_description',
                                '/misc/xFWHM',
                                '/misc/yFWHM',
                                '/version',
                                ]

        if (self.parameters is None) or ('number_of_trajectories' not in self.parameters.keys()):
            self.parameters = {'number_of_trajectories' : 1,
                    }
        if self.parameters['number_of_trajectories'] != 1:
            print "\n WARNING: Number of trajectories != 1 not supported for this demo version of the PMI module. Falling back to 1 trajectory.\n"
            self.parameters['number_of_trajectories'] = 1

    def expectedData(self):
        """ Query for the data expected by the Interactor. """
        return self.__expected_data

    def providedData(self):
        """ Query for the data provided by the Interactor. """
        return self.__provided_data

    def backengine(self):
        """ This method drives the backengine code."""
        status = 0
        input_files = []
        if os.path.isfile(self.input_path):
            input_files = [self.input_path]

        elif os.path.isdir(self.input_path):
            input_files = [ os.path.join( self.input_path, f) for f in os.listdir( self.input_path ) ]
            input_files.sort()

        else:
            raise IOError("Input file %s does not exist or cannot be read." % (self.input_path) )

        # Create output directory if not existing yet.
        if not os.path.isdir( self.output_path ):
            os.mkdir( self.output_path )
        elif os.path.isfile( self.output_path ):
            raise IOError( "Output file %s already exists, cowardly refusing to overwrite." % (self.output_path) )

        # Generate formatted output files (i.e. attach history to output file).
        for i,input_file in enumerate(input_files):
            tail = input_file.split( 'prop' )[-1]
            output_file = os.path.join( self.output_path , 'pmi_out_%07d.h5' % (i+1) )
            pmi_script.f_h5_out2in( input_file, output_file)

            # Get the backengine calculator.
            pmi_demo = PMIDemo()

            # Transfer some parameters.
            pmi_demo.g_s2e['prj'] = ''
            pmi_demo.g_s2e['id'] = tail.split('_')[-1].split('.')[0]
            pmi_demo.g_s2e['prop_out'] = input_file
            pmi_demo.g_s2e['setup'] = dict()
            pmi_demo.g_s2e['sys'] = dict()
            pmi_demo.g_s2e['setup']['num_digits'] = 7

            if 'number_of_steps' in self.parameters.keys():
                pmi_demo.g_s2e['steps'] = self.parameters['number_of_steps']
            else:
                pmi_demo.g_s2e['steps'] = 100

            pmi_demo.g_s2e['maxZ'] = 100


            pmi_demo.g_s2e['setup']['pmi_out'] = output_file
            # Setup the database.
            pmi_demo.f_dbase_setup()

            # Go through the pmi workflow.
            pmi_demo.f_init_random()
            pmi_demo.f_save_info()
            pmi_demo.f_load_pulse( pmi_demo.g_s2e['prop_out'] )
            pmi_demo.f_load_sample(self.__sample_path)
            pmi_demo.f_rotate_sample()
            pmi_demo.f_system_setup()

            # Perform the trajectories for this pulse and orientation.
            for traj in range( self.parameters['number_of_trajectories'] ):
                pmi_demo.f_time_evolution()

        return status

    @property
    def data(self):
        """ Query for the field data. """
        return self.__data

    def _readH5(self):
        """ """
        """ Private method for reading the hdf5 input and extracting the parameters and data relevant to initialize the object. """
        pass # Nothing to be done since IO happens in backengine.

    def saveH5(self):
        """ """
        """
        Private method to save the object to a file.

        @param output_path : The file where to save the object's data.
        @type : string
        @default : None
        """
        pass # No action required since output is written in backengine.
