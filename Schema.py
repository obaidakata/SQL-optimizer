import math


class Schema:

    def __init__(self):
        self.__name = None
        self.__columns = {}
        self.__columnsSize = {}
        self.__rowCount = 0
        self.__rowSize = 0

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
        toAdd = 0
        for columnType in self.__columns.values():
            if columnType == "INTEGER":
                toAdd = 4
            self.__rowSize += toAdd

    @property
    def RowSize(self):
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
        condition = schemaToReturn.__removeAllTablesNames(condition)
        schemaToReturn.__applyCondition(condition)
        schemaToReturn.__calculateRowSize()

        return schemaToReturn

    def __removeAllTablesNames(self, condition):
        elements = condition.split(" ")
        toReturn = ""
        for element in elements:
            if element.startswith("AND") or element.startswith("OR"):
                toReturn += element + " "
            elif "=" in element:
                toReturn += self.__getColumnFromOperand(element) + " "
        return  toReturn

    def __applyCondition(self, condition):
        if "(" in condition:
            # Deal with complex condition
            x = 3
        else:
            elements = condition.split(" ")
            for element in elements:
                element = element.strip()
                if "AND" in element:
                    x = 3
                elif "OR" in element:
                    x = 4
                elif "=" in element:
                    column = self.__getColumnFromOperand(element)
                    x = 3

    def __getColumnFromOperand(self, operand):
        if "=" in operand:
            operand = operand.split("=")
            operand = operand[0].strip()
            column = operand.split(".")
            column = column[1].strip()
            return  column
        else:
            return None

    def __getAllOperatorsIndexes(self, operator):
        items = operator.split(' ')
        toReturn = {}
        for i in range(len(items)):
            items[i] = items[i].strip()
            if items[i] in "AND":
                toReturn[i] = "AND"
            elif items[i] in "OR":
                toReturn[i] = "OR"
        return toReturn

    def __isConditionLegal(self, i_Condition):
        stack = []
        for char in i_Condition:
            if char == "(":
                stack.append(char)
            else:
                if char == ")":
                    if not stack:  # check if stack is empty.
                        return False
                    stack.pop()

        # Check Empty Stack
        if stack:
            return False
        return True

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
        self.ColumnsNumberOfUniqueValues = self.mergeDictionary(firstSchema.ColumnsNumberOfUniqueValues, secondSchema.ColumnsNumberOfUniqueValues)
        for key in firstSchema.ColumnsNumberOfUniqueValues.keys():
            if key in secondSchema.ColumnsNumberOfUniqueValues.keys():
                firstProbability = 1 / firstSchema.ColumnsNumberOfUniqueValues[key]
                secondProbability = 1 / secondSchema.ColumnsNumberOfUniqueValues[key]
                totalProbability = firstProbability * secondProbability
                self.ColumnsNumberOfUniqueValues[key] = math.ceil(self.RowCount * totalProbability)

    def __str__(self):
        return "Table Size: |{0}| = {1}".format(self.Name, self.RowCount)
