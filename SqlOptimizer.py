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

    def __thetaJoinRule(self):
        # TODO: verify that QueryTree[1] is what it should be
        condition = self.__getSub(self._QueryTree[1], self._SquareBrackets)
        tables = self.__getSub(self._QueryTree[2], self._RoundedBrackets)

        if condition is not None and tables is not None:
            self._QueryTree.pop(1)
            self._QueryTree.pop(1)
            thetaJoin = "THETAJOIN[{0}]({1})".format(condition, tables)
            self._QueryTree.append(thetaJoin)

    def __getSub(self, i_Sub, parenthesis):
        start = i_Sub.find(parenthesis[0])
        end = i_Sub.rfind(parenthesis[1])
        toReturn = None
        if start != -1 and end != -1:
            toReturn = i_Sub[start+1:end]
        return toReturn

    def __sigmaJoinRule(self):
        #TODO: verify that the string contain sigma(join)
        example = "SIGMA[x>5 and y<3](JOIN(R, S))"
        condition = self.__getSub(example, self._SquareBrackets)
        join = self.__getSub(example, self._RoundedBrackets)
        tables = self.__getSub(join, self._RoundedBrackets)
        if condition is not None and tables is not None:
            tables = tables.split(',')
            firstTable = tables[0].strip()
            secondTable = tables[1].strip()
            fixed = "JOIN(SIGMA[{0}]({1}), {2})".format(condition, firstTable, secondTable)
            print(fixed)

    def Print(self):
        print(self._QueryTree[0], end="")
        for x in self._QueryTree[1:]:
            print("(", x, sep="", end="")

        for i in self._QueryTree[1:]:
            print(")", sep="", end="")

    def Optimize(self, i_Query):
        m_QueryTree = self.__buildTree(i_Query)
        self.__thetaJoinRule()
        self.__sigmaJoinRule()
        return m_QueryTree
