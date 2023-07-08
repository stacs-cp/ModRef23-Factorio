# Factorio Blueprint Optimiser
To run an instance, a parameter file is needed <br>
Samples are stored in /param <br>
<br>
Run with:
<br>
`python factorio_opt.py --param [path to param file] (--max_recipes [n]) (--max-bpp [n]) (--keep-files) (--save-log)` <br>
<br>
NB: Savile Row must be in $PATH <br>
<br>
`--param`       (required): The parameter file to use <br>
`--max_recipes` (optional): How many attempts are allowed of the recipe stage (default 100) <br>
`--max_bpp`     (optional): How many attempts are allowed of the bin-packing stage per recipe stage attempt (default 100) <br>
`--keep-files`  (optional): Whether to keep non-solution Savile Row output (default False) <br>
`--save-log`    (optional): Whether to store the error log in the output folder (default False) <br>
<br>
Output is stored in /out in a folder named for the parameter file and time