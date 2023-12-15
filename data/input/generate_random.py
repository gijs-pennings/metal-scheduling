import numpy as np
import pandas as pd


"""

This file is an old script to generate 'random' datasets. Use TestData.py instead

"""

# parameters
num_runs = 200
num_machines = 3
means = [2500, 10000, 30000]

lengths3 = np.concatenate([
    np.random.normal(m, 500, size=num_runs // len(means)).round() for m in means
])
lengths3 = lengths3.astype(int)

due = (lengths3.sum() + 172800) // 8

rows = []
for i, len3 in enumerate(lengths3):
    rows.append([
        "A" + str(i),
        2000,
        "B" + str(i),
        2000,
        "C" + str(i),
        len3,
        np.random.randint(0, num_machines),
        due
    ])

df = pd.DataFrame(rows, columns=["step1", "len1", "step2", "len2", "step3", "len3", "metal", "due"])
df.to_csv("./data/input/random_data_int.csv", index=False)
