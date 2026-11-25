# Missing empirical data for Science V9.9

The current document **does not claim county-level BT23 data are loaded**. The national feedstock allocation, logistics, soil carbon and plant nutrient availability retain unverified analyst parameters.

## Mandatory DOE/ORNL county residue-price supply

Official portal: https://bioenergykdf.ornl.gov/bt23-agricultural-download

The portal lets anyone view but requires an account to download CSV. Obtain/log into an ORNL BioEnergy KDF account. Select Agriculture → Agricultural residues, mature-market medium scenario, all U.S. counties/states, and **all offered farmgate-price levels**. Export complete original CSV(s) including columns `resource`, `fips`, `state_name`, `scenario_name`, `Price Offered`, `Production`, and `Production Unit`. Do not remove `dt` units or edit CSV rows. Include corn stover, wheat straw, rice straw, oats/barley, soybean, sorghum and cotton where the portal provides them. A complete agriculture export may contain >100,000 rows across scenarios; the V9.9 importer filters the named scenario and acceptable field resources.

Extract this flat ZIP into a Windows folder. Double-click `RUN_DOWNLOAD_OFFICIAL_BT23_DATA.bat`. It opens the official site when source exports are absent. Save exported CSV/ZIP files in the new `BT23_EXPORTS` subfolder. Double-click the same BAT **again**. The tool then validates missing units, duplicated county/resource/price records, nonmonotone offered-price cumulative supply, and minimum U.S. coverage before creating `BT23_USDA_COUNTY_DATA_FOR_V99.zip`. **Upload that ZIP to ChatGPT.** Do not save an HTML page renamed as CSV.

BT23 corn stover may already contain leaves and cobs. Do not add distinct corn-cob/husk quantities that duplicate the same field material. Official agricultural processing and municipal wastes must be evaluated as separate, independent resource inventories.

## Recommended USDA crop-area cross-check

Register for a *free separate* USDA NASS Quick Stats API key: https://quickstats.nass.usda.gov/api. Double-click `RUN_USDA_COUNTY_DATA.bat`, supply the key interactively (it is not saved), and the script downloads county-level crop-area observations from 2022/2023 for eight crops. It creates `USDA_QUICKSTATS_COUNTY_V99.zip`, which you can attach here. Data gaps are reported rather than guessed.

USDA harvested crop acres alone are **not** sustainable removable biomass, and cannot substitute for county-price residue supply, soil erosivity, nutrient contents or competing feedstock uses.

## Empirical studies still required

Literature- or experiment-supported HTL yields by feedstock and N/P/K element, treated water plant availability and contaminants, residual soil nitrogen/soil organic carbon outcomes, residue logistics and soil carbon saturation. Software cannot manufacture those measurements. The V9.9 manuscript therefore reports explicitly conditional sensitivity results.

## Never omit the Grid Harvester

`FigS1_grid_harvester.tif`, `FigS22_GridHarvester_Energy_Efficiency.tif`, `grid_harvester.py` and `us91_grid_harvester_efficiency.csv` are **required** in each version. The V9.9 validator checks those exact files, their data values, and the actual embedded S1 and S22 images in the supplement.
