import math


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
        if self.__rowSize is None:
            toAdd = 0
            self.__rowSize = 0
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
        self.__calculateRowSize()

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
        schemaToReturn.__multipleUniqueValues(firstSchema, secondSchema)
        return schemaToReturn

    def __multipleUniqueValues(self, firstSchema, secondSchema):
        self.ColumnsNumberOfUniqueValues = {}
        for key in firstSchema.ColumnsNumberOfUniqueValues.keys():
            if not key in secondSchema.ColumnsNumberOfUniqueValues.keys():
                valueInFirstSchema = firstSchema.ColumnsNumberOfUniqueValues[key]
                self.ColumnsNumberOfUniqueValues[key] = valueInFirstSchema
            else:
                # TODO: check if ok
                valueInFirstSchema = firstSchema.ColumnsNumberOfUniqueValues[key]
                valueInSecondSchema = secondSchema.ColumnsNumberOfUniqueValues[key]
                self.ColumnsNumberOfUniqueValues[key] = max(valueInFirstSchema, valueInSecondSchema)

        for key in secondSchema.ColumnsNumberOfUniqueValues.keys():
            if not key in firstSchema.ColumnsNumberOfUniqueValues.keys():
                valueInSecondSchema = secondSchema.ColumnsNumberOfUniqueValues[key]
                self.ColumnsNumberOfUniqueValues[key] = valueInSecondSchema

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
        schemaToReturn.RowCount = schema.RowCount
        schemaToReturn.ColumnsNumberOfUniqueValues = schema.ColumnsNumberOfUniqueValues
        schemaToReturn.__applyCondition(condition)
        schemaToReturn.__calculateRowSize()

        return schemaToReturn

    def __applyCondition(self, condition):
        conditionAsMath = ""
        condition = condition.replace("(", "( ")
        condition = condition.replace(")", " )")
        conditionParts = condition.split(" ")
        for element in conditionParts:
            if "AND" in element:
                conditionAsMath += "*"
            elif "OR" in element:
                conditionAsMath += "+"
            elif "." in element:
                calculatedProbably = self.__calculateProbability(element)
                if calculatedProbably is not None:
                    calculatedProbably = str(calculatedProbably)
                    conditionAsMath += calculatedProbably
            elif "(" in element or ")" in element:
                conditionAsMath += element

        try:
            if conditionAsMath is not "":
                result = eval(conditionAsMath)
                self.RowCount = math.ceil(result * self.RowCount)
        except SyntaxError:
            print("Can't calculate Condition")

    def __calculateProbability(self, operand):
        toReturn = None
        if "=" in operand:
            splitOperand = operand.split("=")
            column = self.__getColumnFromOperand(splitOperand[0])
            if column is not None and column in self.ColumnsNumberOfUniqueValues:
                if splitOperand[1].isdecimal():
                    toReturn = 1 / self.ColumnsNumberOfUniqueValues[column]
                else:
                    secondColumn = self.__getColumnFromOperand(splitOperand[1])
                    toReturn = 1 / self.ColumnsNumberOfUniqueValues[secondColumn]
        return toReturn

    def __getColumnFromOperand(self, operand):
        if "." in operand:
            column = operand.split(".")
            column = column[1].strip()
            return column
        else:
            return None

    @staticmethod
    def applyJoin(firstSchema, secondSchema):
        schemaToReturn = Schema()
        schemaToReturn.Name = "NJOIN({0}, {1})".format(firstSchema.Name, secondSchema.Name)
        schemaToReturn.Columns = Schema.mergeDictionary(firstSchema.Columns, secondSchema.Columns)
        schemaToReturn.RowCount = firstSchema.RowCount * secondSchema.RowCount
        schemaToReturn.__calculateRowSize()
        schemaToReturn.__calculateNumberOfUniqueValues(firstSchema, secondSchema)
        return schemaToReturn

    def __calculateNumberOfUniqueValues(self, firstSchema, secondSchema):
        self.ColumnsNumberOfUniqueValues = self.mergeDictionary(firstSchema.ColumnsNumberOfUniqueValues,
                                                                secondSchema.ColumnsNumberOfUniqueValues)
        for key in firstSchema.ColumnsNumberOfUniqueValues.keys():
            if key in secondSchema.ColumnsNumberOfUniqueValues.keys():
                firstProbability = 1 / firstSchema.ColumnsNumberOfUniqueValues[key]
                secondProbability = 1 / secondSchema.ColumnsNumberOfUniqueValues[key]
                totalProbability = firstProbability * secondProbability
                self.ColumnsNumberOfUniqueValues[key] = math.ceil(self.RowCount * totalProbability)

    def __str__(self):
        return "n_{0} = {1}, R_{0} = {2}".format(self.Name, self.RowCount, self.RowSize)
