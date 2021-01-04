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
        self.__showStartMenu()

    def __isUserChoiceLegal(self, userChoice, minValue, maxValue):
        isLegal = False
        if userChoice.isnumeric():
            userChoiceAsInt = int(userChoice)
            isLegal = userChoiceAsInt >= minValue and userChoiceAsInt <= maxValue

        return isLegal

    def __getQueryFromUser(self):
        # self.__query = input("Please Type Your SQL query:")
        self.__query = 'SELECT R.D, S.E FROM R, S WHERE S.D=4 AND R.A=10'
        # only equal
        # self.__query = 'SELECT R.A, S.D FROM R, S WHERE ((((R.A=4 AND (R.B=9 OR R.C=8))) AND R.C=7))'
        self.__showStartMenu()

    def __showResult(self, result):
        print("Result After apply Rule is {0}".format(result))

    def __getLegalChoice(self, firstIndex, secondIndex):
        while True:
            userChoice = input("Please Choose one from the Above:")
            if self.__isUserChoiceLegal(userChoice, firstIndex, secondIndex):
                break
            else:
                print("Error Should be in the range({0},{1})".format(firstIndex, secondIndex))
        return int(userChoice)

    def __showStartMenu(self):
        numberOfParts = len(self.__parts)
        print("---------SQL Optimizer--------")

        if self.__query is None:
            print("Set query: ")
            self.__getQueryFromUser()
        else:
            print("{0}) Change query".format(0))
            for part in self.__parts:
                print("{0}) launch part".format(part))

            userChoice = self.__getLegalChoice(0, numberOfParts)
            if userChoice == 0:
                self.__getQueryFromUser()
            elif userChoice == 1:
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
            userChoice = self.__getLegalChoice(1, numberOfOption)
            if userChoice == self.__back:
                break
            else:
                optimizerResult = optimizer.Optimize(self.__rules[userChoice -1])
                self.__showResult(optimizerResult)

        self.__showStartMenu()

    def __showPart2(self):
        numberOfOptimizers = 50
        numberOfRandomRulesToApply = 10
        optimizers = self.__getOptimizers(numberOfOptimizers)
        results = self.__runRules(optimizers, numberOfRandomRulesToApply)
        for i in range(len(results)):
            print("{0}----------------{1}".format(i, results[i]))
        input("Press any key to return to menu")
        self.__showStartMenu()

    def __showPart3(self):
        numberOfOptimizers = 1000
        numberOfRandomRulesToApply = 50
        optimizers = self.__getOptimizers(numberOfOptimizers)
        self.__runRules(optimizers, numberOfRandomRulesToApply)
        for optimizer in optimizers:
            optimizer.getSizeEstimation()
            # if res
            # print("{0} size = {1}".format(result, resultSize))


        input("Press any key to return to menu")
        self.__showStartMenu()

    def __SetOptimizer(self, i_Optimizer):
        i_Optimizer.setSchema(self.__fileParser.getFirstSchema(), self.__fileParser.getSecondSchema())
        i_Optimizer.setQuery(self.__query)

    def __getOptimizers(self, numberOfOptimizers):
        optimizers = []
        for i in range(numberOfOptimizers):
            optimizer = SqlOptimizer()
            self.__SetOptimizer(optimizer)
            optimizers.append(optimizer)
        return optimizers

    def __runRules(self, optimizers, numberOfRandomRulesToApply):
        results = []
        numberOfRules = len(self.__rules) - 2  # Back is not allowed
        for optimizer in optimizers:
            for _ in range(numberOfRandomRulesToApply):
                randomNumber = random.randint(0, numberOfRules)
                randomRule = self.__rules[randomNumber]
                results.append(optimizer.Optimize(randomRule))
        return results