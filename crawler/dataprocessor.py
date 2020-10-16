import pandas as pd
import matplotlib.pyplot as plt


def runGraphTime(threads):
    df = pd.read_csv("data.txt", header=None)
    data = [max(df[df[0] == x][1]) for x in threads]
    plt.plot(threads, data, '-ok')
    df = pd.DataFrame(data={'Num': threads, 'Time': data})
    print(df)

