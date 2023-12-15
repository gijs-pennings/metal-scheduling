import time
import plotly.express as px
import pandas as pd
import datetime as dt
import plotly.graph_objects as go

problem_csv = "data/input/random_data.csv"
solution_csv = "greedy_solution.csv"

df_solution = pd.read_csv(solution_csv)
df_problem = pd.read_csv(problem_csv)

df_problem["metal"] = df_problem["metal"].astype(str)

df_steps = []
for i in range(1,4):
   df_step_i = df_problem[[f"step{i}", f"len{i}", "metal", "due"]].copy()
   df_step_i.columns = ["StepId", "length", "metal", "due"]
   df_steps.append(df_step_i)
df_step = pd.concat(df_steps)

df_solution = df_solution.join(df_step.set_index("StepId"), on="StepId")

start_date = pd.to_datetime("2023-11-06")
df_solution["Start"] = start_date + pd.to_timedelta(df_solution['StartDate_Seconds'], unit='s')
df_solution["End"] = start_date + pd.to_timedelta(df_solution['EndDate_Seconds'], unit='s')
df_solution["Machine"] = df_solution["StepId"].str.get(0)

mask_setup_times = df_solution["SetupTime_Hours"] > 0

#DataFrame for just the setup times
df_setup_times = df_solution[mask_setup_times].copy()
df_setup_times["End"] = df_setup_times["Start"] + pd.to_timedelta(df_setup_times["SetupTime_Hours"], unit='h')

#Shorten the "Step" into its actual Step time (excluding setup time_
df_solution["Start"] = df_solution["Start"] + pd.to_timedelta(df_solution["SetupTime_Hours"], unit='h')

actual_start_time = df_solution["Start"].min()

df_solution_ontime = df_solution[df_solution["TooLate_Weeks"] == 0].copy()
df_solution_late = df_solution[df_solution["TooLate_Weeks"] != 0].copy()

fig_ontime = px.timeline(df_solution_ontime,
                  x_start="Start",
                  x_end="End",
                  y="Machine",
                  color = "metal",
                  color_discrete_map={"0": '#ff0000', "1": '#4467C4', "2": '#1fc600'},
                  hover_data=["StepId", "TooLate_Weeks", "SetupTime_Hours", "StartDate_Seconds", "StartDate_Seconds", "due"],
                  range_x=(actual_start_time, actual_start_time + pd.to_timedelta(3600*24, unit='s')))
fig_ontime.update_yaxes(autorange="reversed", fixedrange=True)

fig_late = px.timeline(df_solution_late,
                  x_start="Start",
                  x_end="End",
                  y="Machine",
                  color = "metal",
                  color_discrete_map={"0": '#b10000', "1": '#00008C', "2": '#0a5d00'},
                  hover_data=["StepId", "TooLate_Weeks", "SetupTime_Hours", "StartDate_Seconds", "StartDate_Seconds"]
                       )

fig_setup = px.timeline(df_setup_times,
                        x_start="Start",
                        x_end="End",
                        y="Machine",
                        color="metal",
                        hover_data=["StepId", "TooLate_Weeks", "SetupTime_Hours"],
                        color_discrete_map={metal_type: "silver" for metal_type in df_setup_times["metal"].unique()})

# df_solution_lines = df_solution.copy()
# df_solution_lines["Duration"] = (df_solution_lines["End"] - df_solution_lines["Start"]).dt.seconds
# df_solution_lines["X"] = df_solution_lines["Start"] + pd.to_timedelta(df_solution_lines["Duration"]/2.0, unit='s')
#
# fig_lines = px.line(df_solution_lines,
#                     x="X",
#                     y="Machine",
#                     color="RunId",
#                     color_discrete_map={x: "black" for x in df_solution_lines["RunId"].unique()})


new_fig = go.Figure(data=fig_ontime.data + fig_late.data + fig_setup.data, layout=fig_ontime.layout)
new_fig.update_layout(title=f"Schedule {solution_csv}")
for due_date_seconds in df_solution["due"].unique():
    new_fig.add_vline(start_date + pd.to_timedelta(due_date_seconds, unit='s'))

new_fig.show("browser")
