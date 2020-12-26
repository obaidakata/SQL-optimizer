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
    def ColumnsSize(self):
        return self.__columnsSize

    @ColumnsSize.setter
    def ColumnsSize(self, i_ColumnsSize):
        self.__columnsSize = i_ColumnsSize

    @property
    def RowCount(self):
        return self.__rowCount

    @RowCount.setter
    def RowCount(self, i_RowCount):
        self.__rowCount = int(i_RowCount)

    @property
    def RowSize(self):
        if self.__rowSize is None:
            self.__rowSize = 0
            for columnSize in self.__columnsSize.items():
                self.__rowSize += columnSize[1]
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
        schemaToReturn.ColumnsSize = Schema.mergeDictionary(firstSchema.ColumnsSize, secondSchema.ColumnsSize)
        return schemaToReturn

    @staticmethod
    def applyPi(schema):
        schemaToReturn = Schema()
        schemaToReturn.Name = "PI({0})".format(schema.Name)
        schemaToReturn.RowSize = schema.RowSize
        schemaToReturn.RowCount = schema.RowCount + 3
        schemaToReturn.Columns = schema.Columns
        schemaToReturn.ColumnsSize = schema.ColumnsSize
        return schemaToReturn

    @staticmethod
    def applySigma(schema):
        schemaToReturn = Schema()
        schemaToReturn.Name = "SIGMA({0})".format(schema.Name)
        schemaToReturn.RowSize = schema.RowSize
        schemaToReturn.RowCount = schema.RowCount + 5
        schemaToReturn.Columns = schema.Columns
        schemaToReturn.ColumnsSize = schema.ColumnsSize
        return schemaToReturn

    @staticmethod
    def applyJoin(firstSchema, secondSchema):
        schemaToReturn = Schema()
        schemaToReturn.Name = "NJOIN({0}, {1})".format(firstSchema.Name, secondSchema.Name)
        schemaToReturn.RowSize = firstSchema.RowSize + secondSchema.RowSize
        schemaToReturn.RowCount = firstSchema.RowCount + 7
        schemaToReturn.Columns = Schema.mergeDictionary(firstSchema.Columns, secondSchema.Columns)
        schemaToReturn.ColumnsSize = Schema.mergeDictionary(firstSchema.ColumnsSize, secondSchema.ColumnsSize)
        return schemaToReturn
