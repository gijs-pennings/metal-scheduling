from random import random
from typing import List
import random
from sklearn.cluster import KMeans
from sklearn.exceptions import ConvergenceWarning
from sklearn.utils._testing import ignore_warnings

from data_structures import *
import numpy as np
import matplotlib.pyplot as plt
import pandas


@ignore_warnings(category=ConvergenceWarning)
def cluster_steps_by_length(steps: List[Step], k: int) -> List[List[Step]]:
    """ Given a List of Steps, partition into k clusters based on length (step.length)
    Uses (one dimensional) KMeans clustering algorithm to find the clusters

    Args:
        steps: List of steps
        k: number of clusters

    Returns: List of k clusters (each cluster being a List of Steps). No particular cluster order is guaranteed, nor is the order of Steps within any cluster.

    """
    assert k >= 1, "k must be at least 1"
    lengths = np.array([step.length for step in steps])
    kmeans = KMeans(n_clusters=k, n_init="auto")
    kmeans.fit(lengths.reshape(-1, 1))
    labels = kmeans.labels_
    clusters = [[] for i in range(k)]
    for i_step, label in enumerate(labels):
        clusters[label].append(steps[i_step])
    return clusters


def cluster_step_classes_by_length_then_sort(classes: List[List[Step]], number_of_clusters: List[int]) -> List[List[Step]]:
    """
    For each class of steps, say the i-th class, cluster into number_of_clusters[i] clusters based on step length
    Sort each cluster by ascending step length (so in each clusters the shorter steps go first)
    Then sort the clusters based on mean step length in that cluster

    Args:
        classes: List of Classes (each being a List of Steps)
        number_of_clusters: a List of integers specifying the number of clusters for class 1,2,3,... respectively

    Returns: List of clusters (each being a list of steps), where the clusters are of ascending mean step length, and each cluster has steps of ascending length

    """
    # For each step class (i.e. metal type),
    # generate clusters (how many is given by number_of_clusters),
    # putting them all in one pile
    clusters = []
    for step_class, k in zip(classes, number_of_clusters):
        clusters.extend(cluster_steps_by_length(step_class, k))

    clusters = [c for c in clusters if len(c) > 0]

    def mean_length_in_cluster(cluster: List[Step]):
        return sum([step.length for step in cluster]) / len(cluster)

    # In each cluster, sort based on step length
    for cluster in clusters:
        cluster.sort(key=lambda step: step.length)

    # Sort all clusters based on mean step length within the cluster.
    clusters_sorted = sorted(clusters, key=lambda c: mean_length_in_cluster(c))

    return clusters_sorted

#
# n_classes = 3
# classes = []
# for i_class in range(n_classes):
#     n_steps = 10
#     steps = [Step(i_class, f"C{i_class}", 1000 + round(random.expovariate(1.0/random.randint(1000, 2000)))) for i in range(100)]
#     classes.append(steps)
#
# nr_clusters = [3 for _ in range(n_classes)]
# print(nr_clusters)
# clusters = cluster_step_classes_by_length_then_sort(classes, nr_clusters)
# mean_lengths = [sum([step.length for step in cluster]) / len(cluster) for cluster in clusters]
# # print(mean_lengths)
# data = []
# for cluster in clusters:
#     for step in cluster:
#         # print(f"{step.name}:{step.length}   ", end="")
#         data.append(dict({"Class": step.index, "Length": step.length}))
#     # print()
#
# df = pd.DataFrame(data).reset_index()
# df.plot(kind="scatter", x="index", y="Length", ylim=(0, 4000), c="Class", cmap="copper")
# plt.show()
# # print(df)
