from SqlOptimizer import SqlOptimizer
from FileParser import FileParser
import random

class OptimizerUI:
    __rules = []
    __parts = []
    __query = None
    LastAppliedRule = None
    __optimizer = None
    __fileParser = None

    def __init__(self):
        self.__parts = ["1", "2", "3"]
        self.__optimizer = SqlOptimizer()
        self.__rules = self.__optimizer.GetOptions()
        self.__back = len(self.__rules) + 1
        self.__fileParser = FileParser()
        self.__fileParser.Parse("statistics.txt")

    def show(self):
        self.__getQueryFromUser()
        self.__showStartMenu()

    def __isUserChoiceLegal(self, userChoice, maxValue):
        isLegal = False
        if userChoice.isnumeric():
            userChoiceAsInt = int(userChoice)
            isLegal = userChoiceAsInt >= 1 and userChoiceAsInt <= maxValue

        return isLegal

    def __getQueryFromUser(self):
        # self.__query = input("Please Type Your SQL query:")
        # self.__query = 'SELECT R.D, S.E FROM R, S WHERE S.B>4 AND R.A=10 AND R.A=9'
        # only equal
        return 'SELECT R.A, S.D FROM R, S WHERE R.B=4 AND R.A=9 AND R.A=10 '

    def __showResult(self, result):
        print("Result After apply Rule is {0}".format(result))

    def __getLegalChoice(self, numberOfOptions):
        while True:
            userChoice = input("Please Choose one from the Above:")
            if self.__isUserChoiceLegal(userChoice, numberOfOptions):
                break
            else:
                print("Error Should be in the range({0},{1})".format(1, numberOfOptions))
        return int(userChoice)

    def __showStartMenu(self):
        numberOfParts = len(self.__parts)
        print("---------SQL Optimizer--------")
        i = 1
        for part in self.__parts:
            print("{0}) launch part".format(i))
            i = i + 1

        userChoice = self.__getLegalChoice(numberOfParts)
        if userChoice == 1:
            self.__showPart1()
        elif userChoice == 2:
            self.__showPart2()
        elif userChoice == 3:
            self.__showPart3()

    def __showPart1(self):
        numberOfOption = len(self.__rules) +1
        print("---------SQL Optimizer--------")
        i = 1
        for option in self.__rules:
            if option is not self.__back:
                print("{0}) Implement Rule {1}".format(i, option))
                i = i + 1
        print("{0}) Back".format(i))


        optimizer = SqlOptimizer()
        self.__SetOptimizer(optimizer)
        print(optimizer)
        while True:
            userChoice = self.__getLegalChoice(numberOfOption)
            if userChoice == self.__back:
                break
            else:
                optimizerResult = optimizer.Optimize(self.__rules[userChoice -1])
                self.__showResult(optimizerResult)

        self.__showStartMenu()

    def __showPart2(self):
        numberOfRules = len(self.__rules) -2 # Back is not allowed
        results = []
        optimizers = []
        numberOfOptimizers = 1000
        for i in range(numberOfOptimizers):
            results.append("Empty")
            optimizers.append(SqlOptimizer())
            self.__SetOptimizer(optimizers[i])

        numberOfRandomRulesToApply = 50
        for i in range(numberOfOptimizers):
            for _ in range(numberOfRandomRulesToApply):
                randomNumber = random.randint(0, numberOfRules)
                randomRule = self.__rules[randomNumber]
                results[i] = optimizers[i].Optimize(randomRule)

        uniqeResults = list(set(results))
        for i in range(len(uniqeResults)):
            print("{0}----------------{1}".format(i, uniqeResults[i]))
        input("Press any key to return to menu")
        self.__showStartMenu()

    def __showPart3(self):
        print("In progress")
        input("Press any key to return to menu")
        self.__showStartMenu()

    def __SetOptimizer(self, i_Optimizer):
        i_Optimizer.setSchema(self.__fileParser.getFirstSchema(), self.__fileParser.getSecondSchema())
        userQuery = self.__getQueryFromUser()
        i_Optimizer.setQuery(userQuery)
