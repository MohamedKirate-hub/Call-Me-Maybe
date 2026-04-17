import pandas as pd

file1 = '/home/mkirate/goinfre/Call_Me_Maybe/timings1.csv'
file2 = '/home/mkirate/goinfre/Call_Me_Maybe/timings2.csv'
file3 = '/home/mkirate/goinfre/Call_Me_Maybe/timings3.csv'
pd.set_option('display.max_columns', None)
for file in [file1, file2, file3]:
    df = pd.read_csv(file)
    print(df.head())
