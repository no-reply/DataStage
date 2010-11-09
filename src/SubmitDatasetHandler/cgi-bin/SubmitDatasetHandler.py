#!/usr/bin/python
#
# Coypyright (C) 2010, University of Oxford
#
# Licensed under the MIT License.  You may obtain a copy of the License at:
#
#     http://www.opensource.org/licenses/mit-license.php
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# $Id: $

"""
Main CGI handler program for submitting data files from ADMIRAL to to stored as
an RDF Databank dataset.
"""
__author__ = "Bhavana Ananda"
__version__ = "0.1"

import cgi, sys, re, logging, os, os.path
sys.path.append("..")
sys.path.append("../..")

import SubmitDatasetUtils
from MiscLib import TestUtils
ZipMimeType      =  "application/zip"
FilePat          =  re.compile("^.*$(?<!\.zip)")
logger           =  logging.getLogger("processDatasetSubmissionForm")
ERROR_MESSAGE    =  None

def processDatasetSubmissionForm(formdata, outputstr):
    """
    Process form data, and print (to stdout) a new HTML page reflecting
    the outcome of the request.
    
    formdata    is a dictionary containing parameters from the dataset submission form
    """
    siloName= "admiral-test"
    save_stdout = sys.stdout
    #print repr(formdata)
    if outputstr:
        sys.stdout = outputstr
  
    try:
        datasetName  = formdata["datId"].value   
        dirName      = formdata["datDir"].value

        datIDPattern = re.compile("^[a-zA-Z0-9._:-]+$")
        matchedString = datIDPattern.match(datasetName)
        
        if matchedString==None:
            raise new SubmitDatasetUtils.SubmitDatasetError(
                "INPUT ERROR",
                None,
                "Not a valid Dataset ID: '"+datasetName+"' supplied")
            
            ERROR_MESSAGE = "Not a valid Dataset ID: '"+datasetName+"' supplied"
        assert matchedString!= None, ERROR_MESSAGE

        if dirName.endswith('/'):
            ERROR_MESSAGE = "Expecting no trailing '/' on directory name: '"+dirName+"' supplied"    
        assert not dirName.endswith('/'), "Expecting no trailing '/' on directory name: "+dirName+" supplied"
          
        zipFileName = os.path.basename(dirName) +".zip"
        zipFilePath = "/tmp/" + zipFileName
        logger.debug("datasetName %s, dirName %s, zipFileName %s"%(datasetName,dirName,zipFileName))

        # Creating a dataset
        SubmitDatasetUtils.createDataset(siloName, datasetName)
        # Zip the selected Directory
        SubmitDatasetUtils.zipLocalDirectory(dirName, FilePat, zipFilePath)
        # Submit zip file to dataset
        try:
            SubmitDatasetUtils.submitFileToDataset(siloName, datasetName, zipFilePath, ZipMimeType, zipFileName)
        finally:
            SubmitDatasetUtils.deleteLocalFile(zipFilePath)

        # Unzip the contents into a new dataset
        SubmitDatasetUtils.unzipRemoteFileToNewDataset(siloName, datasetName, zipFileName)
        print "Content-type: text/html"
        print                               # end of MIME headers

        print "<h2>Form parameters supplied</h2>"
        # print "<h3>Printing form dqata: " + str(formdata)+"</h3>"
        print "<dl>"
        print "<dt></dt><dd></dd>"
        for k in formdata:
            print "  <dt>%s</dt><dd>%s</dd>"%(k, formdata[k].value)
        print "</dl>"
    
        print "Dataset submission handler to be implemented here"

    finally:
        sys.stdout = save_stdout
        if ERROR_MESSAGE != None:
            SubmitDatasetUtils.generateErrorResponsePage(SubmitDatasetUtils.INPUT_ERROR,None,ERROR_MESSAGE)

    return


if __name__ == "__main__":
    form = cgi.FieldStorage() #parse the query
    processDatasetSubmissionForm(form, sys.stdout)

# End.
