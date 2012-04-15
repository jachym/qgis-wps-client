from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.core.SextanteLog import SextanteLog
from sextante.outputs.OutputFactory import OutputFactory
from sextante.parameters.ParameterFactory import ParameterFactory
import time,  inspect

from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgswpstools import *


class WpsAlgorithm(GeoAlgorithm):
    '''This is an example algorithm that takes a vector layer and creates
    a new one just with just those features of the input layer that are
    selected.
    It is meant to be used as an example of how to create your own SEXTANTE
    algorithms and explain methods and variables used to do it.
    An algorithm like this will be available in all SEXTANTE elements, and
    there is not need for additional work.

    All SEXTANTE algorithms should extend the GeoAlgorithm class'''

    #constants used to refer to parameters and outputs.
    #They will be used when calling the algorithm from another algorithm,
    #or when calling SEXTANTE from the QGIS console.
    OUTPUT_LAYER = "OUTPUT_LAYER"
    INPUT_LAYER = "INPUT_LAYER"

    def __init__(self, descriptionfile):
        GeoAlgorithm.__init__(self)
#        QMessageBox.information(None, 'in alg',  descriptionfile)
        self.descriptionFile = descriptionfile
        self.defineCharacteristicsFromFile()
        self.numExportedLayers = 0
        
    def defineCharacteristicsFromFile(self):
        lines = open(self.descriptionFile)
        line = lines.readline().strip("\n").strip()
        self.name = line
        line = lines.readline().strip("\n").strip()
        self.group = line
        while line != "":
            try:
                    line = line.strip("\n").strip()
                    if line.startswith("Parameter"):
                        self.addParameter(ParameterFactory.getFromString(line))
                    else:
                        self.addOutput(OutputFactory.getFromString(line))
                    line = lines.readline().strip("\n").strip()
            except Exception,e:
                SextanteLog.addToLog(SextanteLog.LOG_ERROR, "Could not open WPS algorithm: " + self.descriptionFile + "\n" + line)
                raise e
        lines.close()

    def processAlgorithm(self, progress):
        '''Here is where the processing itself takes place'''

        #the first thing to do is retrieve the values of the parameters
        #entered by the user
        inputFilename = self.getParameterValue(self.INPUT_LAYER)
        output = self.getOutputValue(self.OUTPUT_LAYER)

        #input layers values are always a string with its location.
        #That string can be converted into a QGIS object (a QgsVectorLayer in this case))
        #using the Sextante.getObject() method
        vectorLayer = Sextante.getObject(inputFilename)

        #And now we can process

        #First we create the output layer.
        #The output value entered by the user is a string containing a filename,
        #so we can use it directly
        settings = QSettings()
        systemEncoding = settings.value( "/UI/encoding", "System" ).toString()
        provider = vectorLayer.dataProvider()
        writer = QgsVectorFileWriter( output, systemEncoding,provider.fields(), provider.geometryType(), provider.crs() )

        #Now we take the selected features and add them to the output layer
        selection = vectorLayer.selectedFeatures()
        for feat in selection:
            writer.addFeature(feat)
        del writer

        #There is nothing more to do here. We do not have to open the layer that we have created.
        #SEXTANTE will take care of that, or will handle it if this algorithm is executed within
        #a complex model