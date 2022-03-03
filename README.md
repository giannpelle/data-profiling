# Data Profiling
This repository contains the code for the project submitted for the *Data Profiling* course from the Free University of Bozen-Bolzano.

# Project description
We developed the most popular algorithms to discover Primary keys, Foreign keys and Functional dependencies from raw data sets.
For a detailed review of the whole project you can have a look at the documentation available [here](https://github.com/giannpelle/data-profiling/blob/master/data_profiling_report.pdf).

# Algorithms developed

## Frequent item set discovery
The code implementation is available [here](https://github.com/giannpelle/data-profiling/blob/master/frequent_item_set_discovery.py.pdf).

## Unique column combination discovery
The code implementation is available [here](https://github.com/giannpelle/data-profiling/blob/master/UCC_discovery.py).

## Functional dependency discovery
It was developed following the algorithm available in *TANE: An efficient algorithm for discovering functional and approximate dependencies* (Huhtala et al., 1999).
Following a 1-1 translation of the algorithm in python, there were some functional dependencies the algorithm could not detect.
In particular, a very special kind of FDs could not be found: Bigger primary keys -> Smaller primary keys.
The problem was that the pseudocode indicates to prune the Candidate set generation of primary keys, treating them as nodes with empty candidate sets; so, all super-keys containing those keys in the column combination appear to have an empty candidate set, which is incorrect by definition of (super) key. (A (super) key functionally determines all other columns).
I developed my own way to solve this problem: I keep a reference to all discovered Primary keys and when the Candidate set of a column combination X does not exist but X is a super key (contains one of the saved primary keys) then I treat it as it had all other columns in the C(X).

I was then curious how [Metanome](https://hpi.de/naumann/projects/data-profiling-and-analytics/metanome-data-profiling.html) was handling this situation, since it was the tool we used to check the correctness of the algorithm; and there I found the *bug* in the pseudocode.

From the paper cited above, the pseudocode for the pruning is shown in the image below:

<img src="https://github.com/giannpelle/data-profiling/blob/master/images/paper_code.png" width="500">

From the implementation of TANE in Metanome, the code is the following:

<img src="https://github.com/giannpelle/data-profiling/blob/master/images/metanome_code.png" width="700">

<img src="https://github.com/giannpelle/data-profiling/blob/master/images/metanome_code_2.png" width="700">

In the end, I decided to stick with my own solution for 3 reasons:
* because the proposed solution differs in a significant way from the vanilla pseudocode available in the Paper
* because it was not possible to use the same technique Metanome used since I implemented the code with python and I only used lists and simple dictionaries of primitive data types
* it works in all situations with just 3 extra lines of code in the correct place, and a new list of data to store (it is not very efficient but at least it doesn't mess up with the original code of the paper)

The code implementation is available [here](https://github.com/giannpelle/data-profiling/blob/master/FD_discovery.py).

## Approximate functional dependency discovery
It was developed following the algorithm available in *TANE: An efficient algorithm for discovering functional and approximate dependencies* (Huhtala et al., 1999).

The code implementation is available [here](https://github.com/giannpelle/data-profiling/blob/master/FD_approximate_discovery.py).

## Unary inclusion dependency discovery
The code implementation is available [here](https://github.com/giannpelle/data-profiling/blob/master/unary_IND_discovery.py).

## Installation

```bash
cd data-profiling
conda env create -f environment.yml
conda activate data-profiling

python3 frequent_item_set_discovery.py

python3 UCC_discovery.py --dataset=breast-cancer-wisconsin.csv
python3 UCC_discovery.py --dataset=satellites.csv
python3 UCC_discovery.py --dataset=abalone.csv

python3 FD_discovery.py --dataset=breast-cancer-wisconsin.csv
python3 FD_discovery.py --dataset=satellites.csv
python3 FD_discovery.py --dataset=abalone.csv

python3 FD_approximate_discovery.py --dataset=breast-cancer-wisconsin.csv
python3 FD_approximate_discovery.py --dataset=satellites.csv
python3 FD_approximate_discovery.py --dataset=abalone.csv

python3 unary_IND_discovery.py
```

