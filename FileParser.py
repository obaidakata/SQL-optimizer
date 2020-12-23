import os.path
import sys
from os import path

class FileParser:
    __lines = []
    __Schema = {}
    __SchemaData = {}
    __SchemaSize = {}
    def __init__(self):
        pass

    def Parse(self, filePath):
        filePath = os.path.join(sys.path[0], filePath)
        with open(filePath, 'r') as file:
            schemes = []
            schemeAsLines = []

            for i in range(2):
                isNewScheme = True
                for line in file:
                    if line.startswith("Scheme") and not isNewScheme:
                        break
                    if line.startswith("Scheme") and isNewScheme:
                        isNewScheme = False
                    elif line is not "\n":
                        if '\n' in line:
                            line = line[:-1]
                        schemeAsLines.append(line)
                schemes.append(schemeAsLines.copy())
                schemeAsLines.clear()

        for scheme in schemes:
            self.__createSchemas(scheme)


    def __createSchemas(self, i_scheme):
        schema = i_scheme[0]
        schemaParts = schema.split("(")
        schemaName = schemaParts[0]
        schemavariables = schemaParts[1]
        schemavariables =  schemavariables[:-1]# Delete the ) at the end
        variables = schemavariables.split(",")
        variablesDictionary = {}
        for variable in variables:
            variableParts = variable.split(":")
            variableName = variableParts[0]
            variableType = variableParts[1]
            variablesDictionary[variableName] = variableType

        vaiableDataDictionary = {}
        vaiablesData = i_scheme[2:]
        i = 0
        for variableName in variablesDictionary.keys():
            parts = vaiablesData[i].split('=')
            i = i + 1
            vaiableDataDictionary[variableName] = parts[1]

        parts = i_scheme[1].split('=')
        self.__Schema[schemaName] = variablesDictionary
        self.__SchemaData[schemaName] = vaiableDataDictionary
        self.__SchemaSize[schemaName] = parts[1]

    def getSchema(self):
        return self.__Schema

    def getSchemaData(self):
        return self.__SchemaData

    def getSchemaSize(self):
        return self.__SchemaSize