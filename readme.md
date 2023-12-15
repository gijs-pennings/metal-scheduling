# 2MMR10 Metal scheduling OMP Case

## Introduction

For the modeling week component of course 2MMR10 Professional portfolio we got our project case from OMP. The problem description and report on our solution can be found [in this document](#TODO) and presentation slides [here](#TODO).

This it the software implementation for our algorithm. It is written in Python. Specifically, we used Python 3.10(.4) for development. Requirements can be found in `requirements.txt` and can be installed by

    pip install -r requirements.txt


## Data sets and format
OMP gave us an example data set [`TUEdatav1.xlsx`](data/input/TUEdatav1.xlsx) including an initial solution. In our software we do not use the  problem format as used in this file (with a seperate tab for the runs and the steps), instead we combine these internally in one `csv` file. The script [`clean.py`](data/input/clean.py) can be used to transform the problem from the excel into our structure. For `TUEdatav1.xlsx`, the result of the problem is in [`data.csv`](data/input/data.csv). Once in our own format, it can be loaded using `read_problem` from [`data_structures.py`](data_structures.py).

For solutions, we do use the same structure as in the file, this can be loaded from the excel using `parse_solution` from [`data_structures.py`](data_structures.py), or directly from a `csv` file to a Pandas dataframe and then using `parse_solution`.

Details on the data formats and data structures we use, and functions to read/write them, can be found in [`data_structures.py`](data_structures.py).

In [`TestData.py`](data/input/TestData.py) is functionality to create 'random' datasets, i.e. random but still satisfying the assumptions of our algorithm.

## Running the algorithm
Our algorithm is implemented in [`greedy_partitioner.py`](greedy_partitioner.py), see the details there. Example code to run the solver is the following:

    from greedy_partitioner import *
    from data_structures import *

    problem = read_problem("data/input/data.csv")

    solution = solve(problem)
    print(solution.cost())
    print(feasibility(solution))

    write_solution(solution, "data/output/solution.csv")

## Visualizing a solution
The script [`schedule_visualisation.py`](schedule_visualisation.py) can be used to visualize a solution given a solution and problem. The following lines may need to be changed to your problem and solution file.

    ...
    problem_csv = "data/input/random_data.csv"
    solution_csv = "data/output/solution.csv"
    ...

Running `python schedule_visualisation.py` will open a visualization in the browser.
