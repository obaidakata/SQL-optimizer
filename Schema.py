class Schema:

    def __init__(self):
        self.__name = None
        self.__columns = {}
        self.__columnsSize = {}
        self.__rowCount = 0
        self.__rowSize = None

    @property
    def Name(self):
        return self.__name

    @Name.setter
    def Name(self, i_Name):
        self.__name = i_Name

    @property
    def Columns(self):
        return self.__columns

    @Columns.setter
    def Columns(self, i_Columns):
        self.__columns = i_Columns

    @property
    def ColumnsNumberOfUniqueValues(self):
        return self.__columnsSize

    @ColumnsNumberOfUniqueValues.setter
    def ColumnsNumberOfUniqueValues(self, i_ColumnsSize):
        self.__columnsSize = i_ColumnsSize

    @property
    def RowCount(self):
        return self.__rowCount

    @RowCount.setter
    def RowCount(self, i_RowCount):
        self.__rowCount = int(i_RowCount)

    def __calculateRowSize(self):
        self.__rowSize = 0
        toAdd = 0
        for columnType in self.__columns.values():
            if columnType == "INTEGER":
                toAdd = 4
            self.__rowSize += toAdd

    @property
    def RowSize(self):
        if self.__rowSize is None:
            self.__calculateRowSize()
        return self.__rowSize

    @RowSize.setter
    def RowSize(self, i_RowSize):
        self.__rowSize = i_RowSize


    @staticmethod
    def mergeDictionary(firstDictionary, secondDictionary):
        toReturn = firstDictionary.copy()
        toReturn.update(secondDictionary)
        return toReturn

    @staticmethod
    def applyCartesian(firstSchema, secondSchema):
        schemaToReturn = Schema()
        schemaToReturn.Name = "CARTESIAN({0}, {1})".format(firstSchema.Name, secondSchema.Name)
        schemaToReturn.RowSize = firstSchema.RowSize + secondSchema.RowSize
        schemaToReturn.RowCount = firstSchema.RowCount * secondSchema.RowCount
        schemaToReturn.Columns = Schema.mergeDictionary(firstSchema.Columns, secondSchema.Columns)
        schemaToReturn.ColumnsNumberOfUniqueValues = Schema.mergeDictionary(firstSchema.ColumnsNumberOfUniqueValues, secondSchema.ColumnsNumberOfUniqueValues)
        return schemaToReturn

    @staticmethod
    def applyPi(schema, columnsToKeep):
        schemaToReturn = Schema()
        schemaToReturn.Name = "PI({0})".format(schema.Name)
        schemaToReturn.RowCount = schema.RowCount
        schema.__keepColumns(columnsToKeep, schemaToReturn)
        schemaToReturn.__calculateRowSize()
        return schemaToReturn

    def __keepColumns(self, columnsToKeep, schemaToReturn):
        for column in columnsToKeep:
            if column in self.Columns:
                schemaToReturn.Columns[column] = self.Columns[column]
                schemaToReturn.ColumnsNumberOfUniqueValues[column] = self.ColumnsNumberOfUniqueValues[column]


    @staticmethod
    def applySigma(schema):
        schemaToReturn = Schema()
        schemaToReturn.Name = "SIGMA({0})".format(schema.Name)
        schemaToReturn.RowSize = schema.RowSize
        schemaToReturn.RowCount = schema.RowCount + 5
        schemaToReturn.Columns = schema.Columns
        schemaToReturn.ColumnsNumberOfUniqueValues = schema.ColumnsNumberOfUniqueValues
        return schemaToReturn

    @staticmethod
    def applyJoin(firstSchema, secondSchema):
        schemaToReturn = Schema()
        schemaToReturn.Name = "NJOIN({0}, {1})".format(firstSchema.Name, secondSchema.Name)
        schemaToReturn.RowSize = firstSchema.RowSize + secondSchema.RowSize
        schemaToReturn.RowCount = firstSchema.RowCount + 7
        schemaToReturn.Columns = Schema.mergeDictionary(firstSchema.Columns, secondSchema.Columns)
        schemaToReturn.ColumnsNumberOfUniqueValues = Schema.mergeDictionary(firstSchema.ColumnsNumberOfUniqueValues, secondSchema.ColumnsNumberOfUniqueValues)
        return schemaToReturn
