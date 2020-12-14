from SqlOptimizer import SqlOptimizer


def main():
    optimizer = SqlOptimizer()
    optimizedQuery = optimizer.Optimize('SELECT R.D, S.E FROM R, S WHERE S.B>4 AND R.A=10')
    # optimizer.Print()
    # print(optimizer)

if __name__ == '__main__':
    main()
