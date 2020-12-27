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
    def applyPi(operator, schema, columnsToKeep):
        schemaToReturn = Schema()
        schemaToReturn.Name = "{0}({1})".format(operator, schema.Name)
        schemaToReturn.RowCount = schema.RowCount
        schema.__keepColumns(columnsToKeep, schemaToReturn)
        schemaToReturn.__calculateRowSize()
        return schemaToReturn

    def __keepColumns(self, columnsToKeep, schemaToReturn):
        for column in columnsToKeep:
            if column in self.Columns:
                schemaToReturn.Columns[column] = self.Columns[column]
                if column in self.ColumnsNumberOfUniqueValues:
                    schemaToReturn.ColumnsNumberOfUniqueValues[column] = self.ColumnsNumberOfUniqueValues[column]
                else:
                    print("Error in __keepColumns")


    @staticmethod
    def applySigma(operator, condition, schema):
        schemaToReturn = Schema()
        schemaToReturn.Name = "{0}({1})".format(operator, schema.Name)
        schemaToReturn.RowSize = schema.RowSize
        schemaToReturn.Columns = schema.Columns
        schemaToReturn.RowCount = schema.RowCount + 5
        schemaToReturn.ColumnsNumberOfUniqueValues = schema.ColumnsNumberOfUniqueValues
        schemaToReturn.__applyCondition(condition)
        schemaToReturn.__calculateRowSize()

        return schemaToReturn

    def __applyCondition(self, condition):
        # firstLogicalOperator = self.__getFirstLogicalOperator(condition)
        # if firstLogicalOperator is None:
        #      return condition
        # elif firstLogicalOperator in "AND":
        #     andIndex = condition.rfind("AND")
        #     leftOperand = condition[0:andIndex +1]
        #     rightOperand = condition[andIndex:]
        #     def
        # else:
        #     orIndex = condition.rfind("OR")
        x = 5

    def __getFirstLogicalOperator(self, condition):
        andIndex = condition.rfind("AND")
        orIndex = condition.rfind("OR")
        if andIndex is not -1 and andIndex <= orIndex :
            return "AND"
        elif orIndex is not -1 and orIndex <= andIndex:
            return "OR"
        else:
            return None

    @staticmethod
    def applyJoin(firstSchema, secondSchema):
        schemaToReturn = Schema()
        schemaToReturn.Name = "NJOIN({0}, {1})".format(firstSchema.Name, secondSchema.Name)
        schemaToReturn.Columns = firstSchema.__applyIntersectionOnColumns(secondSchema.Columns)
        schemaToReturn.RowCount = firstSchema.RowCount
        schemaToReturn.__calculateRowSize()
        schemaToReturn.ColumnsNumberOfUniqueValues = Schema.mergeDictionary(firstSchema.ColumnsNumberOfUniqueValues, secondSchema.ColumnsNumberOfUniqueValues)
        return schemaToReturn

    def __applyIntersectionOnColumns(self, secondSchemaColumns):
        intersectionOfColumns = self.Columns.copy()
        intersectionOfColumns.update(secondSchemaColumns)
        return intersectionOfColumns

    def __str__(self):
        return "Table Size: |{0}| = {1}".format(self.Name, self.RowCount)
