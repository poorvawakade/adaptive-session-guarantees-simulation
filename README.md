# Adaptive Session Guarantees in Partially Replicated Distributed Storage

This repository contains a simulation study of adaptive session guarantees in partially replicated distributed storage.

## Contents

- `simulator.py` – simulator for nodes, clients and replicas  
- `run_experiment.py` – single-configuration experiment runner  
- `run_experiments_multi.py` – multi-configuration experiment runner  
- `plot_results.py` – script to generate comparison plots  
- `results/` – CSV files and plots

## How to run

```bash
python run_experiments_multi.py
python plot_results.py
```

Results are saved in the `results/` folder.
