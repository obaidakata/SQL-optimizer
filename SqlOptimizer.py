class SqlOptimizer:
    m_Schema = {}
    m_LegalOperators = []
    m_QueryTree = []

    def __init__(self):
        self.InitSchema()

    def InitSchema(self):
        self.m_Schema["R"] = {"A": "int", "B": "int", "C": "int", "D": "int", "E": "int"}
        self.m_Schema["S"] = {"D": "int", "E": "int", "F": "int", "H": "int", "I": "int"}

    def InitLegalOperators(self):
        self.m_LegalOperators = ["<=", ">=", "<>", "<", ">", "="]

    def Print(self):
        print(self.m_QueryTree[0], end="")
        for x in self.m_QueryTree[1:]:
            print("(", x, sep="", end="")

        for i in self.m_QueryTree[1:]:
            print(")", sep="", end="")

    def Optimize(self, i_Query):
        m_QueryTree = self.buildTree(i_Query)
        return m_QueryTree

    def buildTree(self, i_Query):
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

        self.m_QueryTree = [pi, sigma, cartesian]

        return fromSubQuery


