National Wet Waste Inventory (NWWI)

Prepared By: Pacific Northwest National Laboratory (PNNL-SA-154308)
Revision Date: July 10, 2020
Publish Date: July 10, 2020

## DESCRIPTION ##
The National Wet Waste Inventory is a point based spatial dataset containing >56,000 modeled sources of municipal
wastewater sludge; confined animal manure; industrial, institutional, and commercial (IIC) food waste; and fats, 
oils, and greases (FOG).  These wastes are priority organic feedstocks for waste-to-energy conversion.

While the dataset is spatially explicit to enable geospatial analysis, the point locations and the
associated waste magnitudes are considered representative and are intended to be used for national scale
resource assessment modeling and may not reflect current on the ground conditions at a given location.

## DATA SOURCES ##
NWWI integrates several national resource assessment datasets which are based on data ranging from 2012-2016
  * Municipal sludge: Seiple et al., 2020 (https://doi.org/10.1016/j.jenvman.2020.110852)
  * Confined manure: Milbrandt et al., 2017 (https://doi.org/10.1016/j.resconrec.2018.05.023)
  * Food waste: Milbrandt et al., 2017 (https://doi.org/10.1016/j.resconrec.2018.05.023)
  * Fats, oils & grease (FOG): Milbrandt et al., 2017 (https://doi.org/10.1016/j.resconrec.2018.05.023)

## DATA PROCESSING ##
Source data were obtained from the authors referenced above or downloaded as supplemental data as available
All estimates were converted to kg/y dry solids basis
  * Recoverable sludge estimates were already modeled as dry solids
  * Recoverable manure estimates were already modeled as dry solids
  * Recoverable FOG is assumed to be dry solids due to low volatile matter content
  * Recoverable food waste is assumed to contain 75% moisture

Source data were estimated at various spatial scales ranging from facility to county level.  Municipal sludge
was modeled on a site-specific basis at wastewater treatment plants.  Manure was modeled on a site-specific basis
at confined animal operations.  FOG was estimated for urban centers.  Food waste was estimated at the county level.
For additional details pleaser refer to the publications referenced above.

To normalize the spatial scale of the data, food waste estimates were spatially downscaled from the county level to 
representative point locations, where possible.  A national landfill dataset was prepared using 2017 Waste Business 
Journal (WBJ) and May 2017 EPA Greenhouse Gas Reporting Program (GHGRP) landfill data. WBJ sites were prioritized over 
GHGRP sites because they had better spatial validation. GHGRP sites were only used in counties with no WBJ sites.  
If no landfills were present in a given county, the county’s centroid was used. The following summarizes the 
landfill downscaling process.
  1. WBJ: Select * where Group <> 'TS' AND "AnyMSW" = 'Y' AND "TOTAL_WASTE" > 0 (all WBJ sites assumed to be active; any site accepting MSW was considered)
  2. GHGRP: Select all active landfills
  3. Assign remaining waste to county centroids

## DATA PACKAGE ##
The NWWI data package contains the following files
README.txt - DOS formatted text file describing the dataset
NWWI.xlsx - NWWI dataset as Microsoft Excel format
NWWI.txt - NWWI dataset as DOS formatted text file
NWWI_wgs84.shp - NWWI dataset as ESRI shapefile in WGS84 GCS (minor value differences may occur due to rounding or truncation)

The NWWI point dataset contains the following attributes
ROWID		Unique row identifier that is also a foreign key to the shapefile ROWID
dd_LAT		WGS84 latitude in decimal degrees
dd_LONG		WGS84 longitude in decimal degrees
FEEDSTOCK	Primary feedstock category
SUBGROUP	Secondary feedstock category
DRY_KG_YR	Feedstock estimate in kilograms per year
DRY_TONS_YR	Feedstock estimate in short tons per year
