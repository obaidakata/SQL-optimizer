from SqlOptimizer import SqlOptimizer


class OptimizerUI:
    __optimizer = None
    __numberOfRules = None
    __options = []
    __query = None
    LastAppliedRule = None

    def __init__(self):
        self.__optimizer = SqlOptimizer()

    def show(self):
        self.__options = self.__optimizer.GetOptions()
        self.__numberOfRules = len(self.__options)
        self.__insertQuery()
        userChoice = self.__showStartMenu()
        self.LastAppliedRule = self.__options[userChoice - 1]
        self.__query = self.__optimizer.Optimize(self.LastAppliedRule, self.__query)
        self.__showResult()

    def __isUserChoiceLegal(self, userChoice):
        isLegal = False
        if userChoice.isnumeric():
            userChoiceAsInt = int(userChoice)
            isLegal = userChoiceAsInt >= 1 and userChoiceAsInt <= self.__numberOfRules

        return isLegal

    def __showStartMenu(self):
        while True:
            print("---------SQL Optimizer--------")
            i = 1
            for option in self.__options:
                print("{0}) Implement Rule {1}".format(i, option))
                i = i + 1

            userChoice = input("Please Choose one from the Above:")
            if self.__isUserChoiceLegal(userChoice):
                break
            else:
                print("Error Should be in the range({0},{1})".format(1, self.__numberOfRules))
        return int(userChoice)

    def __insertQuery(self):
        # self.__query = input("Please Type Your SQL query:")
        # "SIGMA[x>5 and y<3]", "JOIN(R, S)"
        self.__query = 'SELECT R.D, S.E FROM R, S WHERE S.B>4 AND R.A=10'

    def __showResult(self):
        print("Result After apply Rule ", self.LastAppliedRule, end=" is ")
        print(self.__query)