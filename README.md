CS 143 Network Simulator 
===========================

Authors
----------------

* John Li

* Jonathan Joo

* Matthew Jin

* Albert Ge

Prerequisites
-------------------

* Python

* matplotlib

Usage
----------------

To run the program:
```bash
python src/runSimulation.py -j [json_file] [--Reno | --FAST] [-m [--more --less --avg] [-l [links]] [-f [flows]]] [-v]
```

To display graphs of link rate, flow rate, link buffer occupancy, etc, use -m, followed by the necessary subarguments. 

Example:
```bash
python src/runSimulation.py -j --FAST src/test1.json -m --avg -l L1 L2 -f F1
```

Help:
```bash
python src/runSimulation.py -h
```

