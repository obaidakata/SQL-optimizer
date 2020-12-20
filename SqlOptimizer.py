class SqlOptimizer:
    __Schema = {}
    __LegalOperators = []
    __QueryTree = []
    __SquareBrackets = ['[', ']']
    __RoundedBrackets = ['(', ')']
    __options = []

    def __init__(self):
        self.__initSchema()
        self.__InitLegalOperators()
        self.__initOptions()

    def __initSchema(self):
        self.__Schema["R"] = {"A": "int", "B": "int", "C": "int", "D": "int", "E": "int"}
        self.__Schema["S"] = {"D": "int", "E": "int", "F": "int", "H": "int", "I": "int"}

    def __InitLegalOperators(self):
        self.__LegalOperators = ["<=", ">=", "<>", "<", ">", "="]

    def __initOptions(self):
        self.__options = ["11b", "6", "4", "4a", "5a"]

    def GetOptions(self):
        return self.__options

    def __buildTree(self, i_Query):
        fromSubQuery = i_Query.split("FROM")
        subQuery = fromSubQuery[1].split("WHERE")
        subQuery = subQuery[0].strip()
        tables = subQuery.split(',')
        cartesian = "CARTESIAN"

        whereSubQuery = i_Query.split("WHERE")
        whereSubQuery = whereSubQuery[1].strip()
        sigma = "SIGMA[{0}]".format(whereSubQuery)

        selectSubQuery = i_Query.split("SELECT")
        selectSubQuery = selectSubQuery[1].split("FROM")
        selectSubQuery = selectSubQuery[0].strip()
        pi = "PI[{0}]".format(selectSubQuery)

        self.__QueryTree = [pi, sigma, cartesian, tables]
        return fromSubQuery

    # def __getOperatorConditionAndOperand(self, i_OperatorName, i_NextOperatorName):
    #     if i_NextOperatorName == "CARTESIAN":
    #         res = self.__getOperatorConditionAndOperand2(i_OperatorName, i_NextOperatorName)
    #         tablesIndex = res[2]
    #         res[1] = self.__QueryTree[tablesIndex]
    #         self.__QueryTree.pop()
    #         return res
    #     else:
    #         return self.__getOperatorConditionAndOperand2(i_OperatorName, i_NextOperatorName)


    # def __getOperatorConditionAndOperand2(self, i_OperatorName, i_NextOperatorName):
    #     toReturn = None
    #     treeLength = len(self.__QueryTree)
    #     for i in range(treeLength):
    #         subQuery = self.__QueryTree[i]
    #         if isinstance(subQuery, str) and subQuery.startswith(i_OperatorName):
    #             nextSubQuery = self.__QueryTree[i + 1] if (i + 1 < treeLength) else None
    #             if (nextSubQuery is not None) and (i_NextOperatorName is None) or (
    #                     nextSubQuery.startswith(i_NextOperatorName)):
    #                 # Pop the operator and its operands
    #                 self.__QueryTree.pop(i)
    #                 self.__QueryTree.pop(i)
    #                 condition = self.__getSub(subQuery, self.__SquareBrackets)
    #                 toReturn = [condition, nextSubQuery, i]
    #                 break
    #
    #     return toReturn

    def _getTheProperJoinFormat(self, i_Condition):
        format = "TJOIN[{0}]({1})"
        andExist = "AND" in i_Condition
        orExist = "OR" in i_Condition
        if not andExist and not orExist and "=" in i_Condition:
            format = "NJOIN[{0}]({1})"

        return format

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
        for x in listToPrint:
            if isinstance(x, str):
                toReturn += x
                if self.__isOperator(x):
                    toReturn += "("
                    close = close + 1
            else:
                inside = self.__toString(x)
                toReturn += inside


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
        print(self)

    def Optimize(self, i_Rule):
        if i_Rule == self.__options[0]:
            self.__rule11b()
        elif i_Rule == self.__options[1]:
            self.__rule6()
        elif i_Rule == self.__options[2]:
            self.__rule42()
        elif i_Rule == self.__options[3]:
            self.__rule4a()
        elif i_Rule == self.__options[4]:
            self.__rule5a()
        else:
            print("Error")
        optimizedQuery = self.__toString(self.__QueryTree)
        return optimizedQuery

    def __rule11b(self):
        #TODO: FIX
        res = self.__getOperatorConditionAndOperand(self.__QueryTree, "SIGMA", "CARTESIAN")
        if res is not None:
            tables = res[1]
            joinFormat = self._getTheProperJoinFormat(res[0])
            condition = joinFormat.format(res[0], tables)
            self.__QueryTree.append(condition)

    def __rule6(self):
        res = self.__getOperatorConditionAndOperand(self.__QueryTree, "SIGMA", "CARTESIAN")
        if res is not None:
            tempArray = self.__QueryTree
            for i in res:
                tempArray = tempArray[i]
            sigma = tempArray
            cartisianIndex = res[-1] + 1
            cartisianTablesIndex = cartisianIndex + 1
            cartisiainTables = self.__QueryTree[cartisianTablesIndex]
            toInsert = ["CARTESIAN", [[sigma, cartisiainTables[0]], cartisiainTables[1]]]
            self.__QueryTree.pop(cartisianIndex)
            self.__QueryTree.pop(cartisianIndex) # Pop out catisian tables
            toInsert.reverse()
            self.__QueryTree = self.insertIntoNestedArray(self.__QueryTree, res, toInsert)



    def __rule42(self):
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


    def __rule4(self):
        sigmaCondition = None
        queryTreeLen = len(self.__QueryTree)
        for i in range(queryTreeLen):
            if self.__QueryTree[i].startswith("SIGMA"):
                sigmaCondition = self.__getSub(self.__QueryTree[i], self.__SquareBrackets)
                if "AND" in sigmaCondition:
                    self.__QueryTree.pop(i)
                    break

        if sigmaCondition is not None and "AND" in sigmaCondition:
            splitted_sigmaCondition = sigmaCondition.split("AND", 1)
            sec1 = splitted_sigmaCondition[0].strip()
            sec2 = splitted_sigmaCondition[1].strip()
            newSigma1 = "SIGMA[{0}]".format(sec1)
            newSigma2 = "SIGMA[{0}]".format(sec2)
            self.__QueryTree.insert(i, newSigma1)
            self.__QueryTree.insert(i + 1, newSigma2)

    def __rule4a2(self):
        # TODO: What if there are 3 sigma witch one i should swap
        res = self.__getOperatorConditionAndOperand(self.__QueryTree, "SIGMA", "SIGMA")
        if res is not None:
            firstSigmaCondition = res[0]
            secondSigmaCondition = self.__getSub(res[1], self.__SquareBrackets)
            newSigma1 = "SIGMA[{0}]".format(secondSigmaCondition)
            newSigma2 = "SIGMA[{0}]".format(firstSigmaCondition)
            oldSigmaIndex = res[2]
            self.__QueryTree.insert(oldSigmaIndex, newSigma1)
            self.__QueryTree.insert(oldSigmaIndex + 1, newSigma2)

    def __rule4a(self):
        sigmaIndex = self.__getOperatorConditionAndOperand(self.__QueryTree, "SIGMA", "SIGMA")
        if sigmaIndex is not None:
            firstSigma = self.__getNestedElement(self.__QueryTree, sigmaIndex)
            secondSigmaIndex = self.__getNextOperatorIndex(sigmaIndex)
            secondSigma = self.__getNestedElement(self.__QueryTree, secondSigmaIndex)
            # Swap the to sigma
            self.__replaseNestedElement(self.__QueryTree, sigmaIndex, secondSigma)
            self.__replaseNestedElement(self.__QueryTree, secondSigmaIndex, firstSigma)






    def __rule5a(self):
        res = self.__getOperatorConditionAndOperand(self.__QueryTree, "PI", "SIGMA")
        if res is not None:
            piCondition = res[0]
            SigmaCondition = self.__getSub(res[1], self.__SquareBrackets)
            sigma = "SIGMA[{0}]".format(SigmaCondition)
            pi = "PI[{0}]".format(piCondition)
            index = res[2]
            self.__QueryTree.insert(index, sigma)
            self.__QueryTree.insert(index + 1, pi)

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
                res = [i] + self.__findSigmaWithAndCondition(subQuery)
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

    def __replaseNestedElement(self, arrayToLookFor, indexs, newElement):
        numberOfIndexes = len(indexs)
        temp = arrayToLookFor
        for i in range(numberOfIndexes):
            if i == numberOfIndexes -1:
                temp.pop(indexs[i])
                temp.insert(indexs[i], newElement)
                break
            else:
                temp = temp[indexs[i]]

    def __getNextOperatorIndex(self, indexes):
        numberOfIndexes = len(indexes)
        temp = self.__QueryTree
        nextOperatorIndex = indexes.copy()
        for i in range(numberOfIndexes):
            if i == numberOfIndexes - 1:
                if isinstance(temp[i -1], str):
                    nextOperatorIndex[-1] = nextOperatorIndex[-1] + 1
                else:
                    nextOperatorIndex[-1] = nextOperatorIndex[-1] + 1
                    nextOperatorIndex.append(0)
            else:
                temp = temp[indexes[i]]
        return nextOperatorIndex