import pandas as pd

"""
This script 'cleans' an input dataset (such as the one given in our case): it combines all relevant data
into a single csv file.
"""


dfs = pd.read_excel("TUEdatav1.xlsx", sheet_name=["Steps", "Runs"])
df_steps = dfs["Steps"]
df_runs = dfs["Runs"]

metals = set(df_steps.loc[:, "MetalType"])
print(metals)

metals = {
    304: 0,
    316: 1,
    430: 2
}

data = []
for index, row in df_runs.iterrows():
    step1 = row["Step1"]
    step2 = row["Step2"]
    step3 = row["Step3"]

    row_step1 = df_steps.loc[df_steps["StepId"] == step1]
    row_step2 = df_steps.loc[df_steps["StepId"] == step2]
    row_step3 = df_steps.loc[df_steps["StepId"] == step3]

    assert len(row_step1) == 1
    assert len(row_step2) == 1
    assert len(row_step3) == 1

    row_step1 = row_step1.iloc[0]
    row_step2 = row_step2.iloc[0]
    row_step3 = row_step3.iloc[0]

    metal = row_step1["MetalType"]
    assert metal == row_step2["MetalType"] and metal == row_step3["MetalType"]

    data.append([
        step1,
        row_step1["Length_Seconds"],
        step2,
        row_step2["Length_Seconds"],
        step3,
        row_step3["Length_Seconds"],
        metals[metal],
        row["DueDate_Seconds"]
    ])

df = pd.DataFrame(
    data,
    columns=["step1", "len1", "step2", "len2", "step3", "len3", "metal", "due"]
)

print(df)
df.to_csv("data.csv", index=False)
