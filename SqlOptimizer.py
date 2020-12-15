class SqlOptimizer:
    _Schema = {}
    _LegalOperators = []
    _QueryTree = []
    _SquareBrackets = ['[', ']']
    _RoundedBrackets = ['(', ')']

    def __init__(self):
        self.__initSchema()
        self.__InitLegalOperators()

    def __initSchema(self):
        self._Schema["R"] = {"A": "int", "B": "int", "C": "int", "D": "int", "E": "int"}
        self._Schema["S"] = {"D": "int", "E": "int", "F": "int", "H": "int", "I": "int"}

    def __InitLegalOperators(self):
        self._LegalOperators = ["<=", ">=", "<>", "<", ">", "="]

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

    def __getSigmaOfCartesian(self):
        toReturn = None
        treeLength = len(self._QueryTree)
        for i in range(treeLength):
            subQuery = self._QueryTree[i]
            if subQuery.startswith("SIGMA"):
                nextSubQuery = self._QueryTree[i + 1] if (i + 1 < treeLength) else None
                if nextSubQuery is not None and nextSubQuery.startswith("CARTESIAN"):
                    # Pop the Sigma and Cartesian from query
                    self._QueryTree.pop(i)
                    self._QueryTree.pop(i)
                    condition = self.__getSub(subQuery, self._SquareBrackets)
                    tables = self.__getSub(nextSubQuery, self._RoundedBrackets)
                    toReturn = [condition, tables]
                    break

        return toReturn

    def __getOperatorConditionAndOperand(self, i_OperatorName, i_NextOperatorName):
        # TODO: What if there is operands after the current operand that the code delete
        toReturn = None
        treeLength = len(self._QueryTree)
        for i in range(treeLength):
            subQuery = self._QueryTree[i]
            if subQuery.startswith(i_OperatorName):
                nextSubQuery = self._QueryTree[i + 1] if (i + 1 < treeLength) else None
                if nextSubQuery is not None and nextSubQuery.startswith(i_NextOperatorName):
                    # Pop the operator and its operands
                    self._QueryTree.pop(i)
                    self._QueryTree.pop(i)
                    condition = self.__getSub(subQuery, self._SquareBrackets)
                    operand = self.__getSub(nextSubQuery, self._RoundedBrackets)
                    toReturn = [condition, operand]
                    break

        return toReturn

    def __thetaJoinRule(self):
        res = self.__getOperatorConditionAndOperand("SIGMA", "CARTESIAN")
        if res is not None:
            condition = "THETAJOIN[{0}]".format(res[0])
            tables = res[1]
            self._QueryTree.append(condition)
            self._QueryTree.append(tables)

    def __getSub(self, i_Sub, i_Parenthesis):
        start = i_Sub.find(i_Parenthesis[0])
        end = i_Sub.rfind(i_Parenthesis[1])
        toReturn = None
        if start != -1 and end != -1:
            toReturn = i_Sub[start + 1:end]
            toReturn = toReturn.strip()
        return toReturn

    def __sigmaJoinRule(self):
        res = self.__getOperatorConditionAndOperand("SIGMA", "JOIN")
        if res is not None:
            condition = res[0]
            tables = res[1]
            fixed = "SIGMA[{0}]({1})".format(condition, tables)
            self._QueryTree.append("JOIN")
            self._QueryTree.append(fixed)

    def Print(self):
        print(self)

    def __str__(self):
        return self._toString()

    def _toString(self):
        toReturn = self._QueryTree[0]
        for x in self._QueryTree[1:]:
            toReturn += "("
            toReturn += x

        for _ in self._QueryTree[1:]:
            toReturn += ")"
        return toReturn

    def Optimize(self, i_Query):
        self.__buildTree(i_Query)
        print("Original: ", self)
        self.__thetaJoinRule()
        print("After thetaJoinRule: ", self)
        # just for example
        self._QueryTree = ["SIGMA[x>5 and y<3]", "JOIN(R, S)"]
        print("Original: ", self)
        self.__sigmaJoinRule()
        print("After sigmaJoinRule: : ", self)
        optimizedQuery = ''.join(self._QueryTree)
        return optimizedQuery
