class Schema:

    def __init__(self):
        self.__name = None
        self.__columns = {}
        self.__columnsSize = {}
        self.__rowCount = 0
        self.__rowSize = None

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
    def ColumnsSize(self):
        return self.__columnsSize

    @ColumnsSize.setter
    def ColumnsSize(self, i_ColumnsSize):
        self.__columnsSize = i_ColumnsSize

    @property
    def RowCount(self):
        return self.__rowCount

    @RowCount.setter
    def RowCount(self, i_RowCount):
        self.__rowCount = i_RowCount

    @property
    def RowSize(self):
        if self.__rowSize is None:
            self.__rowSize = 0
            for columnSize in self.__columnsSize.items():
                self.__rowSize += columnSize[1]
        return self.__rowSize

