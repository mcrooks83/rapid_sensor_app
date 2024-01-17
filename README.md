## install
pip3 install -r requirements.txt

## run
python / python3 gui.py

## Fixes


FIXED : “Acceleration Magnitude (g)” where the values should range from 0 to roughly 400. So the scaling factor currently looks to be off by a factor of 10x.
Previous code acc_y = acc_y / params.get_parameter('acc_gain') where acc_gain = 10

FIXED: After selecting “Mark as Labeled” the “Deployments” drop-down often reverts back to Test No 0.

THIS SEEM TO WORK: The Plot Scenario Results do not allow for a scenario to be selected (drop-down remains empty after labelling all deployments) and does not yet display the plots.

FIXED: After selecting an ROI in zoom mode, the plot should not zoom back out to full size. This allows the user to see that the location marked is correct.

Also now the plot will remove previous labels if re labelling points


FIXED “Pressure” and “Acceleration Magnitude” legends should allow for the user to turn the plots off / on for each.

cannot use legends so add checkboxes

FIXED: In the console, it would be nice to have the total number of files for the current run and the % status reported while the user is waiting for the scenario to load.

FIXED: call load import raw data 

FIXED: When scenario is fully labelled need to add to the compare scenario drop down boxes

FIXED: compare runs within a scenario that are completed -> need at least 1 complete run to do it with

FIXED: - check the accleration - due to wrong start offset in finding max accel mag in window

FIXED: - removed async portion from api

CANT REPRO: After the user has selected a faulty deployment and clicks on “Next” the “Undo Faulty” button is still displayed, even if the current deployment is “not labeled”.

FIXED: Acceleration magnitude and pressure labels need to be swapped: “Pressure (mbar)” on the right vertical axis, “Acceleration Magnitude (g)” on the left vertical axis.

The units of acceleration remain incorrect. At rest (e.g. the beginning and end of the datasets), the values should be around 1 g, which denotes the gravitational acceleration. Also as a reference, the maximum acceleration of the sensors should be around 400 g.


# attention
add functions to (to a class) to retrieve individual deployments from a scenario
need a better represenation of the data model to allow for easier read / write operations
places where functions should be produced

# packaging 