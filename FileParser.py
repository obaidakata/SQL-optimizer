import os.path
import sys

from Schema import Schema


class FileParser:
    __Schemas = []

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
        newSchema = Schema()
        schema = i_scheme[0]
        newSchema.Name = schema[0:schema.find('(')]
        variables = schema[schema.find("(")+1:schema.find(")")].split(",")
        for variable in variables:
            variableParts = variable.split(":")
            variableName = variableParts[0]
            variableType = variableParts[1]
            newSchema.Columns[variableName] = variableType

        vaiablesData = i_scheme[1:]
        for data in vaiablesData:
            parts = data.split('=')
            if parts[0] in "n_" + newSchema.Name:
                newSchema.RowCount = parts[1]
            elif parts[0].startswith("V"):
                columnName = parts[0]
                columnName = columnName[columnName.find("(")+1:columnName.find(")")]
                newSchema.ColumnsNumberOfUniqueValues[columnName] = int(parts[1])

        self.__Schemas.append(newSchema)

    def getFirstSchema(self):
        return self.__Schemas[0]

    def getSecondSchema(self):
        return self.__Schemas[1]