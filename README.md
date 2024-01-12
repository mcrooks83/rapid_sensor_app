## install
pip3 install -r requirements.txt

## run
python / python3 gui.py

## Fixes


FIXED : “Acceleration Magnitude (g)” where the values should range from 0 to roughly 400. So the scaling factor currently looks to be off by a factor of 10x.
Previous code acc_y = acc_y / params.get_parameter('acc_gain') where acc_gain = 10

FIXED: After selecting “Mark as Labeled” the “Deployments” drop-down often reverts back to Test No 0.

THIS SEEM TO WORK: The Plot Scenario Results do not allow for a scenario to be selected (drop-down remains empty after labelling all deployments) and does not yet display the plots.



“Pressure” and “Acceleration Magnitude” legends should allow for the user to turn the plots off / on for each.

After selecting an ROI in zoom mode, the plot should not zoom back out to full size. This allows the user to see that the location marked is correct.

In the console, it would be nice to have the total number of files for the current run and the % status reported while the user is waiting for the scenario to load.




# attention
add functions to (to a class) to retrieve individual deployments from a scenario
need a better represenation of the data model to allow for easier read / write operations
places where functions should be produced

# packaging 