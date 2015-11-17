""" Test module for the AbstractPhotonPropagator module.

    @author : CFG
    @institution : XFEL
    @creation 20151006

"""
import os

import paths
import unittest


# Import the class to test.
from SimEx.Calculators.AbstractPhotonPropagator import AbstractPhotonPropagator
from SimEx.Calculators.AbstractBaseCalculator import AbstractBaseCalculator

from TestUtilities import TestUtilities

class TestPhotonPropagator(AbstractPhotonPropagator):

            def __init__(self):
                input_path = TestUtilities.generateTestFilePath('FELsource_out.h5')
                super(TestPhotonPropagator, self).__init__(parameters=None, input_path=input_path, output_path='test_out.h5')

            def backengine(self):
                pass

            def _readH5(self): pass
            def saveH5(self): pass



class AbstractPhotonPropagatorTest(unittest.TestCase):
    """
    Test class for the AbstractPhotonPropagator.
    """

    @classmethod
    def setUpClass(cls):
        """ Setting up the test class. """

    @classmethod
    def tearDownClass(cls):
        """ Tearing down the test class. """

    def setUp(self):
        """ Setting up a test. """
        self.test_class = TestPhotonPropagator()

    def tearDown(self):
        """ Tearing down a test. """
        del self.test_class

    def testConstruction(self):
        """ Testing the default construction of the class. """

        self.assertRaises(TypeError, AbstractPhotonPropagator )

    def testConstructionDerived(self):
        """ Test that we can construct a derived class and it has the correct inheritance. """
        test_source = self.test_class

        self.assertIsInstance( test_source, TestPhotonPropagator )
        self.assertIsInstance( test_source, object )
        self.assertIsInstance( test_source, AbstractBaseCalculator )
        self.assertIsInstance( test_source, AbstractPhotonPropagator )

    def testDataInterfaceQueries(self):
        """ Check that the data interface queries work. """

        # Get test instance.
        test_propagator = self.test_class

        # Get expected and provided data descriptors.
        expected_data = test_propagator.expectedData()
        provided_data = test_propagator.providedData()

        # Check types are correct.
        self.assertIsInstance(expected_data, list)
        self.assertIsInstance(provided_data, list)
        for d in expected_data:
            self.assertIsInstance(d, str)
            self.assertEqual(d[0], '/')
        for d in provided_data:
            self.assertIsInstance(d, str)
            self.assertEqual(d[0], '/')

    def testDefaultPaths(self):
        """ Check that default pathnames are chosen correctly. """

        # Attempt to setup without input path.
        class Propagator(AbstractPhotonPropagator):
            def __init__(self):
                super (Propagator, self).__init__(parameters=None, input_path=None, output_path=None)
            def backengine(self):
                pass
            def _readH5(self):
                pass
            def saveH5(self):
                pass

        # Construct with no paths given.
        propagator = Propagator()

        self.assertEqual(propagator.output_path, os.path.abspath('propagation_out.h5'))
        self.assertEqual(propagator.input_path, os.path.abspath('source_out.h5'))




if __name__ == '__main__':
    unittest.main()
