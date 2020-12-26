from Schema import Schema
class SqlOptimizer:
    __Schema = {}
    __SchemaSize = {}
    __LegalOperators = []
    __QueryTree = []
    __SquareBrackets = ['[', ']']
    __RoundedBrackets = ['(', ')']
    __options = []
    __logNumber = 1
    __sc = {}
    def __init__(self):
        self.__InitLegalOperators()
        self.__initOptions()

    def setSchema(self, i_FirstSchema, i_SecondSchema):
        self.__Schema[i_FirstSchema.Name] = i_FirstSchema.Columns
        self.__Schema[i_SecondSchema.Name] = i_SecondSchema.Columns
        self.__SchemaSize[i_FirstSchema.Name] = i_FirstSchema.RowSize
        self.__SchemaSize[i_SecondSchema.Name] = i_SecondSchema.RowSize
        self.__sc[i_FirstSchema.Name] = i_FirstSchema
        self.__sc[i_SecondSchema.Name] = i_SecondSchema

    def __InitLegalOperators(self):
        self.__LegalOperators = ["<=", ">=", "<>", "<", ">", "="]

    def __initOptions(self):
        self.__options = ["11b", "4", "4a", "5a", "6 with Cartesian", "6a with Cartesian", "6 with NJOIN",
                          "6a with NJOIN"]

    def Optimize(self, i_Rule):
        if i_Rule == self.__options[0]:
            self.__rule11b()
        elif i_Rule == self.__options[1]:
            self.__rule4()
        elif i_Rule == self.__options[2]:
            self.__rule4a()
        elif i_Rule == self.__options[3]:
            self.__rule5a()
        elif i_Rule == self.__options[4]:
            self.__rule6WithCartesian()
        elif i_Rule == self.__options[5]:
            self.__rule6AWithCartesian()
        elif i_Rule == self.__options[6]:
            self.__rule6WithNjoin()
        elif i_Rule == self.__options[7]:
            self.__rule6AWithNjoin()
        else:
            print("Error {0} is not rule ".format(i_Rule))
        optimizedQuery = self.__toString(self.__QueryTree)
        self.__printSizeEstimation()
        return optimizedQuery

    def GetOptions(self):
        return self.__options

    def __buildTree(self, i_Query):
        fromSubQuery = i_Query.split("FROM")
        subQuery = fromSubQuery[1].split("WHERE")
        subQuery = subQuery[0].strip()
        tmpTables = subQuery.split(',')
        tables = []
        for table in tmpTables:
            tables.append(table.strip())
        cartesian = "CARTESIAN"

        whereSubQuery = i_Query.split("WHERE")
        whereSubQuery = whereSubQuery[1].strip()
        sigma = "SIGMA[{0}]".format(whereSubQuery)
        sigma = ' '.join(sigma.split())

        selectSubQuery = i_Query.split("SELECT")
        selectSubQuery = selectSubQuery[1].split("FROM")
        selectSubQuery = selectSubQuery[0].strip()
        pi = "PI[{0}]".format(selectSubQuery)
        pi = ' '.join(pi.split())

        self.__QueryTree = [pi, sigma, cartesian, tables]

    def __getSub(self, i_Sub, i_Parenthesis):
        start = i_Sub.find(i_Parenthesis[0])
        end = i_Sub.rfind(i_Parenthesis[1])
        toReturn = None
        if start != -1 and end != -1:
            toReturn = i_Sub[start + 1:end]
            toReturn = toReturn.strip()
        return toReturn

    def __str__(self):
        return self.__toString(self.__QueryTree)

    def __toString(self, listToPrint):
        toReturn = ""
        close = 0
        listLen = len(listToPrint)
        for i in range(listLen):
            toPrint = listToPrint[i]
            if isinstance(toPrint, str):
                toPrint = toPrint.strip()
                toReturn += toPrint
                if self.__isOperator(toPrint):
                    toReturn += "("
                    close = close + 1
                elif i < listLen - 1:
                    toReturn += ", "
            elif i < listLen - 1:
                toReturn += self.__toString(toPrint) + ', '
            else:
                toReturn += self.__toString(toPrint)

        for _ in range(close):
            toReturn += ")"
        return toReturn

    def __isOperator(self, stirngToCheck):
        if isinstance(stirngToCheck, str):
            res = stirngToCheck.startswith("PI")
            res = res or stirngToCheck.startswith("SIGMA")
            res = res or stirngToCheck.startswith("CARTESIAN")
            res = res or stirngToCheck.startswith("NJOIN")
            return res
        return False

    def setQuery(self, i_Query):
        self.__buildTree(i_Query)

    def __rule11b(self):
        sigmaIndex = self.__getOperatorConditionAndOperand(self.__QueryTree, "SIGMA", "CARTESIAN")
        if sigmaIndex is not None:
            cartesianIndex = sigmaIndex.copy()  # self.__getNextOperatorIndex(sigmaIndex)
            cartesianIndex[-1] = cartesianIndex[-1] + 1
            sigma = self.__getNestedElement(self.__QueryTree, sigmaIndex)
            self.__replaseNestedElement(self.__QueryTree, sigmaIndex, "NJOIN")
            self.__replaseNestedElement(self.__QueryTree, cartesianIndex, None)
        else:
            self.__log("rule 11b - No SIGMA(CARTESIAN()) found")

    def __rule6WithCartesian(self):
        res = self.__getOperatorConditionAndOperand(self.__QueryTree, "SIGMA", "CARTESIAN")
        if res is not None:
            sigma = self.__getNestedElement(self.__QueryTree, res)
            condition = self.__getSub(sigma, self.__SquareBrackets)
            cartesianIndex = res[-1] + 1
            cartesianTablesIndex = cartesianIndex + 1
            cartesiainTables = self.__QueryTree[cartesianTablesIndex]
            # if self.checkIfConditionContainsOnlySharedColomns(cartesiainTables[0], condition):
            toInsert = ["CARTESIAN", [[sigma, cartesiainTables[0]], cartesiainTables[1]]]
            self.__QueryTree.pop(cartesianIndex)
            self.__QueryTree.pop(cartesianIndex)  # Pop out catisian tables
            toInsert.reverse()
            self.__QueryTree = self.insertIntoNestedArray(self.__QueryTree, res, toInsert)
            # else:
            #     print("Columns aren't in the table.")
        else:
            self.__log("rule 6 With Cartesian- No SIGMA(CARTESIAN()) found")

    def __rule6AWithCartesian(self):
        res = self.__getOperatorConditionAndOperand(self.__QueryTree, "SIGMA", "CARTESIAN")
        if res is not None:
            sigma = self.__getNestedElement(self.__QueryTree, res)
            condition = self.__getSub(sigma, self.__SquareBrackets)
            cartesianIndex = res[-1] + 1
            cartesianTablesIndex = cartesianIndex + 1
            cartesiainTables = self.__QueryTree[cartesianTablesIndex]
            # if self.checkIfConditionContainsOnlySharedColomns(cartesiainTables[0], condition):
            toInsert = ["CARTESIAN", [cartesiainTables[0], [sigma, cartesiainTables[1]]]]
            self.__QueryTree.pop(cartesianIndex)
            self.__QueryTree.pop(cartesianIndex)  # Pop out catisian tables
            toInsert.reverse()
            self.__QueryTree = self.insertIntoNestedArray(self.__QueryTree, res, toInsert)
            # else:
            #     print("Columns aren't in the table.")
        else:
            self.__log("rule 6a With Cartesian- No SIGMA(CARTESIAN()) found")

    def __removeDuplicatesFromList(self, i_list):
        mylist = list(dict.fromkeys(i_list))
        return mylist

    def __getColumn(self, condition):
        dotSides = condition.split(".")
        return dotSides[1]

    def checkIfConditionContainsOnlySharedColomns(self, table, sigma_condition):
        splitted_cond = self.__splitSigmaCond(sigma_condition)
        splitted_cond = self.__removeDuplicatesFromList(splitted_cond)
        # check if there are more than one table in the condition.
        for i in range(len(splitted_cond)):
            if table not in splitted_cond[i]:
                return False
        # check if all the columns in the condition belongs to the same table.
        for i in range(len(splitted_cond)):
            rightDot = self.__getColumn(splitted_cond[i])
            if not self.__checkIfColumnInTable(str(table), rightDot):
                return False
        return True

    def __rule6WithNjoin(self):
        res = self.__getOperatorConditionAndOperand(self.__QueryTree, "SIGMA", "NJOIN")
        if res is not None:
            sigma = self.__getNestedElement(self.__QueryTree, res)
            condition = self.__getSub(sigma, self.__SquareBrackets)
            nJoinIndex = res[-1] + 1
            nJoinTablesIndex = nJoinIndex + 1
            nJoinTables = self.__QueryTree[nJoinTablesIndex]
            # if self.checkIfConditionContainsOnlySharedColomns(nJoinTables[0], condition):
            toInsert = ["NJOIN", [[sigma, nJoinTables[0]], nJoinTables[1]]]
            self.__QueryTree.pop(nJoinIndex)
            self.__QueryTree.pop(nJoinIndex)  # Pop out nJoin tables
            toInsert.reverse()
            self.__QueryTree = self.insertIntoNestedArray(self.__QueryTree, res, toInsert)
            # else:
            #     print("Columns aren't in the table.")
        else:
            self.__log("rule 6 With Njoin- No SIGMA(NJOIN()) found")

    def __rule6AWithNjoin(self):
        res = self.__getOperatorConditionAndOperand(self.__QueryTree, "SIGMA", "NJOIN")
        if res is not None:
            sigma = self.__getNestedElement(self.__QueryTree, res)
            condition = self.__getSub(sigma, self.__SquareBrackets)
            nJoinIndex = res[-1] + 1
            nJoinTablesIndex = nJoinIndex + 1
            nJoinTables = self.__QueryTree[nJoinTablesIndex]
            # if self.checkIfConditionContainsOnlySharedColomns(nJoinTables[1], condition):
            toInsert = ["CARTESIAN", [nJoinTables[0], [sigma, nJoinTables[1]]]]
            self.__QueryTree.pop(nJoinIndex)
            self.__QueryTree.pop(nJoinIndex)  # Pop out nJoin tables
            toInsert.reverse()
            self.__QueryTree = self.insertIntoNestedArray(self.__QueryTree, res, toInsert)
            # else:
            #     print("Columns aren't in the table.")
        else:
            self.__log("rule 6 With Njoin - No SIGMA(NJOIN()) found")

    def __rule4(self):
        res = self.__findSigmaWithAndCondition(self.__QueryTree)
        if res is not None:
            tempArray = self.__QueryTree
            for i in res:
                tempArray = tempArray[i]
            sigma = tempArray
            sigmaCondition = self.__getSub(sigma, self.__SquareBrackets)
            if sigmaCondition is not None and "AND" in sigmaCondition:
                splitted_sigmaCondition = sigmaCondition.split("AND", 1)
                sec1 = splitted_sigmaCondition[0].strip()
                sec2 = splitted_sigmaCondition[1].strip()
                newSigma1 = "SIGMA[{0}]".format(sec1)
                newSigma2 = "SIGMA[{0}]".format(sec2)
                toInsert = [newSigma2, newSigma1]
                self.__QueryTree = self.insertIntoNestedArray(self.__QueryTree, res, toInsert)
            else:
                self.__log("Rule 4 no AND found")
        else:
            self.__log("rule 4 - No digma with and")

    def __rule4a(self):
        sigmaIndex = self.__getOperatorConditionAndOperand(self.__QueryTree, "SIGMA", "SIGMA")
        if sigmaIndex is not None:
            firstSigma = self.__getNestedElement(self.__QueryTree, sigmaIndex)
            secondSigmaIndex = self.__getNextOperatorIndex(sigmaIndex)
            secondSigma = self.__getNestedElement(self.__QueryTree, secondSigmaIndex)
            # Swap the to sigma
            self.__replaseNestedElement(self.__QueryTree, sigmaIndex, secondSigma)
            self.__replaseNestedElement(self.__QueryTree, secondSigmaIndex, firstSigma)
        else:
            self.__log("Error in rule 4a - NO SIGMA(SIGMA()) found")

    def __rule5a(self):
        piIndex = self.__getOperatorConditionAndOperand(self.__QueryTree, "PI", "SIGMA")
        if piIndex is not None:
            pi = self.__getNestedElement(self.__QueryTree, piIndex)
            sigmaIndex = self.__getNextOperatorIndex(piIndex)
            sigma = self.__getNestedElement(self.__QueryTree, sigmaIndex)
            sigmaCondition = self.__getSub(sigma, self.__SquareBrackets)
            piCondition = self.__getSub(pi, self.__SquareBrackets)
            if self.__checkPIAndSigmaConds(sigmaCondition, piCondition):
                sigma = "SIGMA[{0}]".format(piCondition)
                pi = "PI[{0}]".format(sigmaCondition)
                self.__replaseNestedElement(self.__QueryTree, sigmaIndex, pi)
                self.__replaseNestedElement(self.__QueryTree, piIndex, sigma)
            else:
                self.__log("Failed in checking condition ")
        else:
            self.__log("Error in rule 5a - PI(SIGMA)")

    def __findSigmaWithAndCondition(self, arrayToLookFor):
        res = None
        arrayLen = len(arrayToLookFor)
        for i in range(arrayLen):
            subQuery = arrayToLookFor[i]
            if isinstance(subQuery, str):
                if subQuery.startswith("SIGMA"):
                    sigmaCondition = self.__getSub(subQuery, self.__SquareBrackets)
                    if "AND" in sigmaCondition:
                        res = [i]
                        break
            else:
                pathTail = self.__findSigmaWithAndCondition(subQuery)
                if pathTail is not None:
                    res = [i] + pathTail
        return res

    def __getOperatorConditionAndOperand(self, arrayToLookFor, i_OperatorName, i_NextOperatorName):
        toReturn = None
        arrayLen = len(arrayToLookFor)
        for i in range(arrayLen):
            subQuery = arrayToLookFor[i]
            if isinstance(subQuery, str):
                if subQuery.startswith(i_OperatorName):
                    nextSubQuery = arrayToLookFor[i + 1] if (i + 1 < arrayLen) else None
                    if nextSubQuery is not None:
                        if isinstance(nextSubQuery, str) and nextSubQuery.startswith(i_NextOperatorName):
                            # return i_OperatorName index
                            toReturn = [i]
                            break
                        elif isinstance(nextSubQuery[0], str) and nextSubQuery[0].startswith(i_NextOperatorName):
                            toReturn = [i]
                            break

            else:
                # return full path of nested i_OperatorName
                pathTail = self.__getOperatorConditionAndOperand(subQuery, i_OperatorName, i_NextOperatorName)
                if pathTail is not None:
                    toReturn = [i] + pathTail

        return toReturn

    def __getNestedElement(self, arrayToLookFor, indexs):
        tempArray = arrayToLookFor
        for i in indexs:
            tempArray = tempArray[i]
        return tempArray

    def __replaseNestedElement(self, arrayToLookFor, indexs, newElement=None):
        numberOfIndexes = len(indexs)
        temp = arrayToLookFor
        for i in range(numberOfIndexes):
            if i == numberOfIndexes - 1:
                temp.pop(indexs[i])
                if newElement is not None:
                    temp.insert(indexs[i], newElement)
                break
            else:
                temp = temp[indexs[i]]

    def __getNextOperatorIndex(self, indexes):
        nextIndexes = indexes.copy()
        nextIndexes[-1] = nextIndexes[-1] + 1
        nextElement = self.__getNestedElement(self.__QueryTree, nextIndexes)
        if not isinstance(nextElement, str):
            nextIndexes.append(0)
        return nextIndexes

    def insertIntoNestedArray(self, nestedArray, indexs, toInsert):
        newArray = nestedArray
        for i in indexs:
            if isinstance(newArray[i], str):
                newArray.pop(i)
                for y in toInsert:
                    newArray.insert(i, y)
            else:
                indexs.pop(0)
                subArray = self.insertIntoNestedArray(newArray[i], indexs, toInsert)
                newArray[i] = subArray
        return newArray

    def __splitAndOr(self, condition):
        if "AND" in condition and not "OR" in condition:
            splitRes = condition.split("AND")
        elif "OR" in condition and not "AND" in condition:
            splitRes = condition.split("AND")
        else:
            splittedAnd = condition.split("AND")
            splitRes = "".join(splittedAnd).split("OR")
        return splitRes

    def __splitOfOperators(self, condition):

        for i in range(len(self.__LegalOperators)):
            if self.__LegalOperators[i] in condition:
                splitRes3 = condition.split(self.__LegalOperators[i])
                condition = "".join(splitRes3)
        return splitRes3

    def __splitSigmaCond(self, sigmaCond):
        splitRes = self.__splitAndOr(sigmaCond)
        splitedRes2 = "".join(splitRes)
        splitResOp = self.__splitOfOperators(splitedRes2)
        s = ''.join(splitResOp)
        s1 = " ".join(s.split())
        result = ''.join([i for i in s1 if not i.isdigit()]).split(" ")
        return result

    def __checkPIAndSigmaConds(self, sigmaCondition, piCondition):
        result = self.__splitSigmaCond(sigmaCondition)
        result2 = piCondition.split(",")
        result2 = [x.strip(' ') for x in result2]
        for i in range(len(result)):
            dotSides = result[i].split(".")
            if result[i] in result2:
                continue;
            elif dotSides[0] not in result2:
                return False
        return True

    def __checkIfColumnInTable(self, table, column):
        if column not in self.__Schema[table]:
            return False
        return True

    def __log(self, toLog):
        # print("{0}) ---------------- {1} ---------------------".format(self.__logNumber, toLog), self)
        self.__logNumber = self.__logNumber + 1

    def __printSizeEstimation(self):
        firstElement = self.__QueryTree[0]
        if self.__isOperator(firstElement):
            innerTable = self.__buildInnerSchema(self.__QueryTree[1], [1])
            res = self.__calculateOperatorSize(firstElement, innerTable)

    def __calculateOperatorSize(self, operator, schemas):
        if self.__isOperator(operator):
            if operator.startswith("SIGMA"):
                res = Schema.applySigma(schemas)
            elif operator.startswith("PI"):
                res = Schema.applyPi(schemas)
            elif operator.startswith("CARTESIAN"):
                res = Schema.applyCartesian(schemas[0], schemas[1])
            elif operator.startswith("NJOIN"):
                res = Schema.applyJoin(schemas[0], schemas[1])
            print("Apply {0} on {1} table -> table size {2}".format(operator, res.Name, res.RowCount))
            return res
        return None

    def __buildInnerSchema(self, i_ToCalculate, i_operatorIndex):
        innerSchema = None
        if self.__isOperator(i_ToCalculate):
            # calculate operand size
            if i_ToCalculate.startswith("SIGMA") or i_ToCalculate.startswith("PI"):
                operandIndex = self.__getNextOperatorIndex(i_operatorIndex)
                operand = self.__getNestedElement(self.__QueryTree, operandIndex)
                operand = self.__buildInnerSchema(operand, operandIndex)
                innerSchema = self.__calculateOperatorSize(i_ToCalculate, operand)
            elif i_ToCalculate.startswith("CARTESIAN") or i_ToCalculate.startswith("NJOIN"):
                schems = []
                firstOperandIndex = self.__getNextOperatorIndex(i_operatorIndex)
                firstOperand = self.__getNestedElement(self.__QueryTree, firstOperandIndex)
                schems.append(self.__buildInnerSchema(firstOperand, firstOperandIndex))

                secondOperandIndex = firstOperandIndex
                secondOperandIndex[-1] = secondOperandIndex[-1] + 1
                secondOperand = self.__getNestedElement(self.__QueryTree, secondOperandIndex)
                schems.append(self.__buildInnerSchema(secondOperand, secondOperandIndex))

                innerSchema = self.__calculateOperatorSize(i_ToCalculate, schems)

        elif isinstance(i_ToCalculate, list):
            elementIndex = i_operatorIndex.copy()
            elementIndex.append(0)
            operand = self.__getNestedElement(self.__QueryTree, elementIndex)
            innerSchema = self.__buildInnerSchema(operand, elementIndex)
        else :
            innerSchema = self.__sc[str(i_ToCalculate)]

        return innerSchema