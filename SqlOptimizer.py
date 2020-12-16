class SqlOptimizer:
    __Schema = {}
    __LegalOperators = []
    _QueryTree = []
    _SquareBrackets = ['[', ']']
    _RoundedBrackets = ['(', ')']
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
        self.__options.append("11b")
        self.__options.append("6")
        self.__options.append("4")
        self.__options.append("4a")
        self.__options.append("5a")

    def GetOptions(self):
        return self.__options

    def __buildTree(self, i_Query):
        fromSubQuery = i_Query.split("FROM")
        subQuery = fromSubQuery[1].split("WHERE")
        subQuery = subQuery[0].strip()
        cartesian = "CARTESIAN({0})".format(subQuery)

        whereSubQuery = i_Query.split("WHERE")
        whereSubQuery = whereSubQuery[1].strip()
        sigma = "SIGMA[{0}]".format(whereSubQuery)

        selectSubQuery = i_Query.split("SELECT")
        selectSubQuery = selectSubQuery[1].split("FROM")
        selectSubQuery = selectSubQuery[0].strip()
        pi = "PI[{0}]".format(selectSubQuery)

        self._QueryTree = [pi, sigma, cartesian]
        return fromSubQuery

    def __getOperatorConditionAndOperand(self, i_OperatorName, i_NextOperatorName):
        toReturn = None
        treeLength = len(self._QueryTree)
        for i in range(treeLength):
            subQuery = self._QueryTree[i]
            if subQuery.startswith(i_OperatorName):
                nextSubQuery = self._QueryTree[i + 1] if (i + 1 < treeLength) else None
                if (nextSubQuery is not None) and (i_NextOperatorName is None) or (
                        nextSubQuery.startswith(i_NextOperatorName)):
                    # Pop the operator and its operands
                    self._QueryTree.pop(i)
                    self._QueryTree.pop(i)
                    condition = self.__getSub(subQuery, self._SquareBrackets)
                    toReturn = [condition, nextSubQuery, i]
                    break

        return toReturn

    def __thetaJoinRule(self):
        res = self.__getOperatorConditionAndOperand("SIGMA", "CARTESIAN")
        if res is not None:
            tables = self.__getSub(res[1], self._RoundedBrackets)
            joinFormat = self._getTheProperJoinFormat(res[0])
            condition = joinFormat.format(res[0], tables)
            self._QueryTree.append(condition)

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

    def __sigmaJoinRule(self):
        res = self.__getOperatorConditionAndOperand("SIGMA", "NJOIN")
        if res is not None:
            condition = res[0]
            tables = self.__getSub(res[1], self._RoundedBrackets)
            tables = tables.split(',')
            fixed = "SIGMA[{0}]({1}),{2}".format(condition, tables[0], tables[1])
            self._QueryTree.append("NJOIN")
            self._QueryTree.append(fixed)

    def __str__(self):
        return self.__toString()

    def __toString(self):
        toReturn = self._QueryTree[0]
        for x in self._QueryTree[1:]:
            toReturn += "("
            toReturn += x

        for _ in self._QueryTree[1:]:
            toReturn += ")"
        return toReturn

    def setQuery(self, i_Query):
        self.__buildTree(i_Query)
        print(self)

    def Optimize(self, i_Rule):
        if i_Rule == self.__options[0]:
            self.__thetaJoinRule()
        elif i_Rule == self.__options[1]:
            self.__sigmaJoinRule()
        elif i_Rule == self.__options[2]:
            self.__rule4()
        elif i_Rule == self.__options[3]:
            self.__rule4a()
        elif i_Rule == self.__options[4]:
            self.__rule5a()
        else:
            print("Error")
        optimizedQuery = self.__toString()
        return optimizedQuery

    def __rule4(self):
        sigmaCondition = None
        queryTreeLen = len(self._QueryTree)
        for i in range(queryTreeLen):
            if self._QueryTree[i].startswith("SIGMA"):
                sigmaCondition = self.__getSub(self._QueryTree[i], self._SquareBrackets)
                if "AND" in sigmaCondition:
                    self._QueryTree.pop(i)
                    break

        if sigmaCondition != None and "AND" in sigmaCondition:
            splitted_sigmaCondition = sigmaCondition.split("AND", 1)
            sec1 = splitted_sigmaCondition[0].strip()
            sec2 = splitted_sigmaCondition[1].strip()
            newSigma1 = "SIGMA[{0}]".format(sec1)
            newSigma2 = "SIGMA[{0}]".format(sec2)
            self._QueryTree.insert(i, newSigma1)
            self._QueryTree.insert(i + 1, newSigma2)

    def __rule4a(self):
        res = self.__getOperatorConditionAndOperand("SIGMA", "SIGMA")
        if res is not None:
            firstSigmaCondition = res[0]
            secondSigmaCondition = self.__getSub(res[1], self._SquareBrackets)
            newSigma1 = "SIGMA[{0}]".format(secondSigmaCondition)
            newSigma2 = "SIGMA[{0}]".format(firstSigmaCondition)
            oldSigmaIndex = res[2]
            self._QueryTree.insert(oldSigmaIndex, newSigma1)
            self._QueryTree.insert(oldSigmaIndex + 1, newSigma2)

    def __rule5a(self):
        res = self.__getOperatorConditionAndOperand("PI", "SIGMA")
        if res is not None:
            piCondition = res[0]
            SigmaCondition = self.__getSub(res[1], self._SquareBrackets)
            sigma = "SIGMA[{0}]".format(SigmaCondition)
            pi = "PI[{0}]".format(piCondition)
            index = res[2]
            self._QueryTree.insert(index, sigma)
            self._QueryTree.insert(index + 1, pi)

