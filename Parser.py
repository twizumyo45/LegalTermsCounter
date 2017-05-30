import os
import glob
import csv
import re
import collections

class Parser:
    # Change these to your actual input/output folder names
    inputFolderName = "/Users/rogerlau/LawsuitParserFolder/"
    outputFolderName = "/Users/rogerlau/LawsuitParserFolderOutput/"

    def parse(self):
        """ 
        The method which opens the input files, and counts the terms/headers. It will then write a csv file which
        contains all counts of terms divided by the number of headers. 
        """
        with open(self.outputFolderName + "OutPut.csv", 'w') as outputCsv:
            orderedLawTermsDict = self.createOrderedLawTermsDict()

            # Create the output file and write to it the title row
            outputCsvWriter = csv.writer(outputCsv)
            outputCsvWriter.writerow(self.createTitleRowArray(orderedLawTermsDict.keys()))

            # Process each .txt file in the input folder
            for fileName in glob.glob(os.path.join(self.inputFolderName, '*.txt')):
                with open(fileName, 'r') as file:
                    #convert the file into a list of strings with the newlines stripped from the end of them
                    fileLines = [line.rstrip('\n') for line in file]

                    isFederal, isState = self.checkIfFileIsFederalOrState(fileLines)
                    fileSize = os.path.getsize(fileName)

                    orderedTermCountsDict = self.createOrderedTermCountsDict(fileLines, orderedLawTermsDict)

                    rowArray = [os.path.basename(fileName), str(isFederal), str(isState), str(fileSize)]
                    rowArray.extend(orderedTermCountsDict.values())

                    outputCsvWriter.writerow(rowArray)


    def createOrderedLawTermsDict(self):
        """ Create a dictionary of the law abbreviations to terms. """

        orderedLawTermsDict = collections.OrderedDict()
        with open(os.path.join(self.inputFolderName, 'input.csv')) as lawTermsFile:
            for rowStr in lawTermsFile:
                rowList = rowStr.split(',')
                orderedLawTermsDict[''.join(rowList[0].split())] = ''.join(rowList[1].split())
        return orderedLawTermsDict


    def createTitleRowArray(self, lawTermAbbreviations):
        """ 
        Create the title row of the output CSV file. 
        The title row consists of file name, fed, state, and all the law term abbreviations. 
        """
        titleRowArray = ["FILENAME", "FED", "STATE", "FILESIZE(bytes)"]
        titleRowArray.extend(lawTermAbbreviations)
        return titleRowArray


    def checkIfFileIsFederalOrState(self, fileLines):
        """ Returns two booleans. isFederal is true if it is a federal suit, isState is true if it is a state suit. """
        firstTenLinesStr = ' '.join(fileLines[:10]).lower()
        isFederal = 'District Court'.lower() in firstTenLinesStr
        isState = 'Superior Court'.lower() in firstTenLinesStr
        return isFederal, isState


    def createOrderedTermCountsDict(self, fileLines, orderedLawTermsDict):
        """ Return a dictionary that contains legal-term : (legal-term count/number-of-headers) pairs. """

        numHeaders = self.countTheNumberOfHeaders(fileLines)

        # Count the number of occurances for each term
        fileStr = ' '.join(fileLines).lower()
        orderedTermCountsDict = collections.OrderedDict()
        for term in orderedLawTermsDict.keys():
            searchTermRegex = orderedLawTermsDict[term]
            orderedTermCountsDict[term] = len(re.findall(searchTermRegex, fileStr)) / float(numHeaders)
        return orderedTermCountsDict


    def countTheNumberOfHeaders(self, fileLines):
        numHeaders = 0
        seenBlankLine = False
        seenHeader = False
        noWhiteSpaceLines = [line.strip('\t') for line in fileLines]
        noWhiteSpaceLines = [line.strip(' ') for line in noWhiteSpaceLines]
        for noWhiteSpaceLine in noWhiteSpaceLines:
            if noWhiteSpaceLine == '' or not noWhiteSpaceLine[0].isalnum():  # not isalnum cos there's some mystery blank char
                seenBlankLine = True
            elif ('CAUSE OF ACTION' in noWhiteSpaceLine or 'CLAIM FOR RELIEF' in noWhiteSpaceLine) and seenBlankLine:
                seenHeader = True
            elif noWhiteSpaceLine[0].isdigit() and seenBlankLine and seenHeader:
                numHeaders += 1
                seenBlankLine = False
                seenHeader = False

        if numHeaders == 0:
            numHeaders = 1  # avoid division by zero errors
        return numHeaders


if __name__ == "__main__":
    Parser().parse()