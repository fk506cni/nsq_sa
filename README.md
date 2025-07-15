# NSP/SA
Nurse Scheduling Problem using simulated annealing.

## About: 
Here are the modules developed for research and the notebooks used for optimization. The xlsx files that contain the actual nurses' capabilities and holiday preferences are not included here because they contain a lot of personal information.

## nlp_assist:
several classes to achive NSP using SA.

1. nlp_connect
    parser for condition xlsx files.
1. nlp_limiter
    dummy variable generator and qubo generator
1. nsp_expressions
    nsp expression class
1. p_solver
    parralel solver
1. res_parser
    result parser and error checker

## notes
several process notebook and Rmd file for visualization

## requirement
### major packages
1. dwave-neal 0.6.0
1. pandas 1.5.2
1. openpyxl 3.0.10
1. optuna 3.1.0
1. optuna-dashboard 0.8.1
1. jupyter 1.0.0 

whole Python: condalist.txt
whole R: installed_packages.csv

## License
Our code is licensed under GPLv3.


