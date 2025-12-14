# BSD Layout Routing Project

This project implements layout routing for a Binary Decision Diagram (BDD) represented in a BSD file format. The main goal is to optimize the layout of transistors based on a decision tree structure using a simulated annealing algorithm.

## BSD File Format

BSD 文件为文本格式，描述决策树的每一层节点及其连接关系。示例：

```
[(0,1)]
[(0,1),(-1,2)]
[(-2,0),(0,1),(2,3)]
[0,2,1]
```
最后一行为输入变量顺序。

## Project Structure

```
bsd-layout-routing
├── src
│   ├── __init__.py          # Marks the src directory as a Python package
│   ├── bdd.py               # Contains the BDD class for constructing and traversing BDDs
│   ├── decision_tree.py      # Defines the DecisionTree class for modeling decision trees
│   ├── layout.py            # Implements the Layout class for handling transistor layouts
│   ├── simulated_annealing.py # Contains the SimulatedAnnealing class for layout optimization
│   └── utils.py             # Provides utility functions for parsing and layout generation
├── tests
│   ├── __init__.py          # Marks the tests directory as a Python package
│   ├── test_bdd.py          # Unit tests for the BDD class
│   ├── test_decision_tree.py # Unit tests for the DecisionTree class
│   ├── test_layout.py       # Unit tests for the Layout class
│   └── test_simulated_annealing.py # Unit tests for the SimulatedAnnealing class
├── requirements.txt          # Lists project dependencies
├── .gitignore                # Specifies files to ignore in version control
└── README.md                 # Project documentation
```

## Usage Instructions

   Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```



