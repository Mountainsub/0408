
import pandas as pd


def keisan():
    temp = pd.HDFStore("./data/sum.hdf5")
    temp2 = temp["testcase"]
    df = temp.tail(1)
    return float(df["total"])

if __name__ =="__main__":

    temp = pd.HDFStore("./data/sum2.hdf5")
    temp2 = temp["testcase"]

    df_hundred = temp2.tail(100)

    names = {}
    count = 0
    for i in df_hundred["total"]:
        names[i] = i 
    keynames =list(names.keys())
    numbers = {}
    for i in keynames:
        for j in df_hundred["total"]:
            if i ==j:
                count+= 1
        numbers[i] = count
        count = 0

            
    max_key = max(numbers, key=numbers.get)

    topix_init = pd.DataFrame({"total":[max_key]})

    store = pd.HDFStore("./data/sum.hdf5")

    store.put("testcase", topix_init)