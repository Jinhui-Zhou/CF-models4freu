# CF-models4freu
Characterization factors (CFs) models for freshwater eutrophication
This Python 3.7 script implements a model for simulating the characterization factors (CFs) of phosphorus (P) and nitrogen (N) emissions from human activities on freshwater fish biodiversity, as described in Zhou et al. (2024).
The model integrates regionalized nutrient fate and their ecological impacts on freshwater fish species richness across global freshwater systems at a spatial resolution of 0.5° × 0.5°.

*Structure
The model is composed of the following scripts and modules:

1. CF_main.py
The main script that coordinates the calculation of CFs for phosphorus and nitrogen.

2. ascrastergrid.py
Contains utility functions for processing raster data, including reading and writing rasters, and determining cell indices (i, j).

3. CF_calculation.py
Calculates CFs by tracing nutrient transport along river networks and aggregating their fate downstream.

4. dir_accuflux.py
Handles flow direction data and identifies downstream cells for nutrient accumulation using flow direction rasters.

5. residence_time.py
Adjusts water body residence times based on outputs from IMAGE and PCR-GLOBWB models.

6. dominant_process.py
Maps the dominant eutrophication-related impact pathways (e.g., addvection of river discharge, retention of nutrients, or water consumption) affecting biodiversity on a global scale.

7. NPlimit.py
Determines phosphorus and nitrogen limitation based on nutrient concentrations modeled by IMAGE-GNM.

8. soil_CF_X.py
Calculates CFs for diffuse and erosion-driven nutrient sources from soil. The suffix X refers to either P or N (i.e., soil_CF_P.py or soil_CF_N.py).

citation: Zhou, J., Mogollón, J. M., van Bodegom, P. M., Beusen, A. H. W., & Scherer, L. (2024). Global regionalized characterization factors for phosphorus and nitrogen impacts on freshwater fish biodiversity. Sci Total Environ. doi: 10.1016/j.scitotenv.2023.169108.