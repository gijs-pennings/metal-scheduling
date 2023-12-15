from operator import itemgetter
import pandas as pd


class Step:
    """
    A class representing a step in the process

    Attributes:
        index: int
            A unique index for each step
        name: str
            The name of each step as provided in the data
        length: int
            The time a step takes on its machine
        run: Run
            Gives the run in which the step appears
    """

    def __init__(self, index: int, name: str, length: int):
        self.index: int = index
        self.name: str = name
        self.length: int = length           # in seconds
        self.run: Run = None                # will be initialized later

    def phase(self) -> int:
        """Returns the machine that this step is performed on. For example, the step C023 has phase 2."""
        return ord(self.name[0]) - 65


class Run:
    """
    A class representing a run in the process

    Attributes:
        metal: int
            Gives the metal type of the run
        steps: list[step]
            Gives a list of the steps of the run
        due: int
            Gives the due date of the run in seconds
    """

    def __init__(self, metal: int, steps: list[Step], due: int):
        self.metal: int = metal             # metal type
        self.steps: list[Step] = steps
        self.due: int = due                 # due date in seconds


class Problem:
    """
    A class representing a problem instance.

    Attributes:
        step_indices: dict[str, int]
            A data structure to find a step's index given its name
        steps: list[Step]
            A collection of all steps
        runs: list[Runs]
            A collection of all runs
    """

    def __init__(self):
        self.step_indices: dict[str, int] = {}
        self.steps: list[Step] = []
        self.runs: list[Run] = []

    def get_step(self, name) -> Step:
        """Returns the step object given its name."""
        return self.steps[self.step_indices[name]]


def read_problem(filename: str = "./data/input/data.csv") -> Problem:
    """
    Reads a csv file given by `filename` and parses it into a Problem object.
    """

    df = pd.read_csv(filename)
    prob = Problem()

    # create steps
    df_steps1 = df[["step1", "len1"]]; df_steps1.columns = ["step", "len"]
    df_steps2 = df[["step2", "len2"]]; df_steps2.columns = ["step", "len"]
    df_steps3 = df[["step3", "len3"]]; df_steps3.columns = ["step", "len"]
    df_steps = pd.concat([df_steps1, df_steps2, df_steps3])
    df_steps.sort_values(by="step", inplace=True)
    df_steps.reset_index(drop=True, inplace=True)
    for i, r in df_steps.iterrows():
        step = Step(i, r["step"], r["len"])
        prob.step_indices[step.name] = step.index
        prob.steps.append(step)

    # create runs
    for _, r in df.iterrows():
        run = Run(
            r["metal"],
            [prob.get_step(r["step1"]), prob.get_step(r["step2"]), prob.get_step(r["step3"])],
            r["due"]
        )
        prob.runs.append(run)
        # link steps to run as well
        for s in run.steps:
            s.run = run
    prob.runs.sort(key=lambda x: x.due)

    return prob


class Solution:
    """
    A class representing a solution for a problem instance.

    Attributes:
        problem: gives the problem instance
        start: gives a list of the start times
    """

    def __init__(self, problem: Problem | None = None):
        self.problem: Problem = problem
        # start time for each step, indexed by `step.index`
        self.start: list[int | None] = [] if problem is None else [None] * len(problem.steps)

    def get_end(self, run: Run) -> int | None:
        """Returns the time when `run` finishes, or `None` if it's not scheduled."""
        step = run.steps[-1]
        start = self.start[step.index]
        return None if start is None else start + step.length

    def get_last_run(self) -> Run | None:
        """Get the run that finishes last in this schedule, or `None` if no run is scheduled."""
        run: Run | None = None
        end: int | None = None
        for r in self.problem.runs:
            e = self.get_end(r)
            if (e is not None) and (end is None or e > end):
                run = r
                end = e
        return run

    def is_late(self, run: Run) -> bool:
        """Returns whether `run` is late in this schedule."""
        step3 = run.steps[-1]
        return self.start[step3.index] + step3.length > run.due

    def cost(self, runs: list[Run] | None = None) -> float:
        """
        Compute the total cost (i.e., lateness plus setup time) of the solution.
        Optionally, you can specify a subset of runs and ignore all others in the computation. It is assumed the last
        steps of `runs` are adjacent. Note that potential setup time before the first run is not considered.
        """

        if runs is None: runs = self.problem.runs
        assert all(r is not None for r in runs)

        # tuple runs with end time
        # then sort from first to last finished
        runs = [(r, self.get_end(r)) for r in runs]
        runs.sort(key=itemgetter(1))

        # compute lateness: sum "TooLate" for each run and rescale from seconds to weeks
        lateness = sum(max(0, end - run.due) for run, end in runs) / (7 * 24 * 3600)

        # compute setup time: add one hour each time adjacent metals are different
        setup_time = sum(r1.metal != r2.metal for (r1, _), (r2, _) in zip(runs, runs[1:]))

        return lateness + setup_time

    def copy(self) -> "Solution":
        """
        Returns a copy of this solution. The `start` array is deep-copied, but the `problem` is copied by reference
        (since it's considered read-only).
        """
        c = Solution()
        c.problem = self.problem
        c.start = self.start.copy()
        return c


def parse_solution(prob: Problem, df_solution: pd.DataFrame | None = None) -> Solution:
    """
    Given a problem and a dataframe containing the information of a solution, transforms it into an instance of the class Solution

    Input:
        prob: Problem instance
        df_solution: Dataframe containing a solution
    Output:
        sol: Object of class Solution
    """
    if df_solution is None:
        # by default read the example solution
        df_solution = pd.read_excel("./data/input/TUEdatav1.xlsx", sheet_name="InitialSolution")

    sol = Solution(prob)
    for _, r in df_solution.iterrows():
        i = prob.step_indices[r["StepId"]]
        sol.start[i] = r["StartDate_Seconds"] + r["SetupTime_Hours"] * 3600

    return sol


def feasibility(sol: Solution) -> bool:
    """
    For a given solution checks whether the solution is feasible

    Args:
        sol: object from class Solution

    Returns:
        bool: Returns True if the solution is feasible and False when it is not
    """
    #Initialize lists
    Astart = []
    Bstart = []
    Cstart = []
    for run in sol.problem.runs:
        #get steps of one run
        step1 = run.steps[0]
        step2 = run.steps[1]
        step3 = run.steps[2]
        #get length of the steps
        len1 = step1.length
        len2 = step2.length
        len3 = step3.length
        #get start time of steps from solution
        start1 = sol.start[step1.index]
        start2 = sol.start[step2.index]
        start3 = sol.start[step3.index]
        #get end times of the steps from the solutions
        end1 = start1 + len1
        end2 = start2 + len2
        end3 = start3 + len3

        if start1 > start2 or start2 > start3:
            print('Infeasible, run goes to machines in wrong order')
            return False

        if start1 < 0 or start2 < 0 or start3 < 0:
            print('Infeasible, negative start times')
            return False

        if end1 > 2000000 or end2 > 2000000 or end3 > 2000000:
            print('Infeasible, end times out of bound')
            return False

        if start2 < end1 or start3 < end2:
            print('Infeasible, overlapping end and start times for one run')
            return False

        if end3 < 172800:
            print('Infeasible, Machine under maintenance')
            return False
        #Add steps on machine A,B and C to the respective lists
        Astart.append([step1.index, sol.start[step1.index]])
        Bstart.append([step2.index, sol.start[step2.index]])
        Cstart.append([step3.index, sol.start[step3.index]])
    #Sort lists by starting times
    Astart = sorted(Astart, key=lambda x: x[1])
    Bstart = sorted(Bstart, key=lambda x: x[1])
    Cstart = sorted(Cstart, key=lambda x: x[1])
    #Check for overlap on machine A
    for i in range(len(Astart)-1):
        start2 = Astart[i+1][1]
        ind1 = Astart[i][0]
        len1 = sol.problem.steps[ind1].length
        end1 = Astart[i][1] + len1

        if end1 > start2:
            print('infeasible, overlap on machine A')
            return False
    #Check for overlap on machine B
    for i in range(len(Bstart)-1):
        start2 = Bstart[i+1][1]
        ind1 = Bstart[i][0]
        len1 = sol.problem.steps[ind1].length
        end1 = Bstart[i][1] + len1

        if end1 > start2:
            print('infeasible, overlap on machine B')
            return False
    #Check for overlap on machine C as well as whether the setup times are correct
    for i in range(len(Cstart)-1):
        start2 = Cstart[i+1][1]
        ind1 = Cstart[i][0]
        ind2 = Cstart[i+1][0]
        len1 = sol.problem.steps[ind1].length
        end1 = Cstart[i][1] + len1

        if end1 > start2:
            print('infeasible, overlap on machine C')
            return False

        for run in sol.problem.runs:
            if sol.problem.steps[ind1] in run.steps:
                metal1 = run.metal
            if sol.problem.steps[ind2] in run.steps:
                metal2 = run.metal

        if metal1 != metal2:
            if end1 > start2 - 3600:
                print('infeasible , no setup time')
                return False
    return True

def write_solution(sol: Solution, filename: str) -> None:
    """
    Given an instance of the solution class and a filename transforms it into a cvs file

    Input:
        sol: Solution instance
        filename: name of the file
    Output:
        None
    """
    prob = sol.problem
    runs = sorted(prob.runs, key=lambda r: sol.get_end(r))  # list of runs sorted by time of finishing

    result = []

    for i, r in enumerate(runs):
        for step in r.steps:
            row = {}
            row["StepId"] = step.name
            row["StartDate_Seconds"] = sol.start[step.index]
            endTime = sol.start[step.index] + step.length
            row["EndDate_Seconds"] = endTime
            row["TooLate_Weeks"] = 0
            row["SetupTime_Hours"] = 0

            if step.phase() == 2:
                # step on machine C
                previousRun = runs[max(0,i-1)]
                if previousRun.metal != r.metal:
                    # setup necessary
                    row["StartDate_Seconds"] -= 3600
                    endTime += 3600
                    row["SetupTime_Hours"] = 1
                row["EndDate_Seconds"] = endTime
                lateness = max(0, endTime - r.due)
                if lateness > 0:
                    # run is late
                    row["TooLate_Weeks"] = lateness / 7 / 24 / 3600

            result.append(row)

    pd.DataFrame(result).to_csv(filename)
