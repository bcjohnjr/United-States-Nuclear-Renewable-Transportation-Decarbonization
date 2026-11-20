"""Hand-digitised, simplified outline of the contiguous United States (lon, lat) for schematic maps.

No GIS layers were available in the build environment, so this outline (~170 vertices) and the corridor, basin,
pipeline and lease-area markers below are approximate and for orientation only.  They are not survey-grade and
must not be used for siting.  Replace with Natural Earth / Census TIGER layers for publication maps.
"""
CONUS = [
    (-124.7, 48.4), (-124.1, 46.9), (-124.0, 46.3), (-123.9, 45.5), (-124.1, 44.6), (-124.4, 43.3), (-124.5, 42.8),
    (-124.2, 42.0), (-124.1, 41.0), (-124.4, 40.4), (-123.8, 39.5), (-123.7, 38.9), (-123.0, 38.0), (-122.5, 37.8),
    (-122.4, 37.2), (-121.9, 36.6), (-121.5, 36.0), (-120.9, 35.4), (-120.6, 34.6), (-120.0, 34.45), (-119.2, 34.2),
    (-118.5, 34.0), (-118.4, 33.8), (-117.9, 33.6), (-117.3, 33.1), (-117.1, 32.5),
    (-114.7, 32.7), (-111.0, 31.33), (-108.2, 31.33), (-108.2, 31.78), (-106.5, 31.75), (-104.9, 30.6), (-104.4, 29.6),
    (-103.1, 29.0), (-102.4, 29.8), (-101.4, 29.8), (-100.3, 28.3), (-99.5, 27.5), (-99.1, 26.4), (-97.4, 25.9),
    (-97.2, 26.6), (-97.4, 27.6), (-96.6, 28.4), (-95.3, 28.9), (-94.4, 29.5), (-93.8, 29.7), (-92.3, 29.5),
    (-91.2, 29.2), (-90.2, 29.1), (-89.4, 28.9), (-89.2, 29.4), (-89.6, 30.2), (-88.6, 30.4), (-88.0, 30.3),
    (-87.3, 30.3), (-86.4, 30.4), (-85.4, 29.7), (-84.4, 29.9), (-83.6, 29.7), (-82.8, 28.9), (-82.7, 28.0),
    (-82.3, 26.9), (-81.8, 26.1), (-81.1, 25.2), (-80.4, 25.2), (-80.1, 25.8), (-80.0, 26.7), (-80.6, 28.2),
    (-81.2, 29.6), (-81.4, 30.7), (-81.2, 31.5), (-80.6, 32.3), (-79.9, 32.8), (-79.2, 33.3), (-78.5, 33.9),
    (-77.9, 34.0), (-76.7, 34.7), (-75.5, 35.2), (-75.7, 36.2), (-76.0, 36.9), (-75.7, 37.5), (-75.2, 38.0),
    (-75.05, 38.45), (-75.1, 38.8), (-74.9, 38.95), (-74.4, 39.4), (-74.0, 40.1), (-74.0, 40.5), (-73.9, 40.6),
    (-72.8, 40.75), (-71.9, 41.05), (-72.9, 41.25), (-71.9, 41.3), (-71.4, 41.45), (-70.95, 41.5), (-70.6, 41.55),
    (-70.0, 41.6), (-69.95, 41.9), (-70.3, 41.75), (-70.6, 41.95), (-70.9, 42.4), (-70.6, 42.7), (-70.75, 43.1),
    (-70.2, 43.6), (-69.2, 44.0), (-68.2, 44.4), (-67.0, 44.8),
    (-67.8, 45.7), (-67.8, 47.1), (-69.2, 47.45), (-70.0, 46.7), (-70.3, 45.9), (-71.5, 45.0), (-74.7, 45.0),
    (-76.3, 44.2), (-79.0, 43.4), (-79.0, 42.9), (-82.5, 41.7), (-83.1, 42.1), (-82.4, 43.0), (-82.5, 45.3),
    (-84.1, 46.5), (-88.4, 48.3), (-89.6, 48.0), (-95.15, 49.0), (-123.3, 49.0), (-123.2, 48.3), (-124.7, 48.4),
]
LAKES = {
    "Superior": [(-92.1, 46.7), (-90.4, 46.6), (-88.0, 47.0), (-86.5, 46.5), (-84.6, 46.5), (-84.9, 47.0), (-86.0, 47.9),
                 (-88.4, 48.3), (-89.6, 48.0), (-91.5, 47.2)],
    "Michigan": [(-87.8, 41.65), (-86.8, 41.75), (-86.3, 42.6), (-86.2, 43.6), (-86.5, 44.6), (-85.6, 45.4), (-84.8, 45.8),
                 (-86.0, 45.9), (-87.0, 45.7), (-87.6, 44.8), (-87.9, 43.5), (-87.8, 42.4)],
    "Huron": [(-82.4, 43.0), (-82.6, 44.0), (-83.4, 44.3), (-83.4, 45.0), (-84.4, 45.6), (-84.1, 46.0), (-82.5, 45.3)],
    "Erie": [(-83.4, 41.7), (-82.0, 41.5), (-80.5, 42.0), (-79.0, 42.6), (-79.0, 42.9), (-82.5, 41.75)],
    "Ontario": [(-79.0, 43.4), (-77.6, 43.3), (-76.3, 43.5), (-76.3, 44.2)],
}
CITIES = {
    "Seattle": (-122.3, 47.6), "Portland": (-122.7, 45.5), "Sacramento": (-121.5, 38.6), "San Francisco": (-122.4, 37.8),
    "Los Angeles": (-118.2, 34.05), "San Diego": (-117.15, 32.7), "Phoenix": (-112.1, 33.45), "Las Vegas": (-115.15, 36.2),
    "Salt Lake City": (-111.9, 40.75), "Reno": (-119.8, 39.5), "Boise": (-116.2, 43.6), "Spokane": (-117.4, 47.65),
    "Billings": (-108.5, 45.8), "Denver": (-105.0, 39.75), "Cheyenne": (-104.8, 41.1), "Albuquerque": (-106.65, 35.1),
    "El Paso": (-106.45, 31.8), "Flagstaff": (-111.65, 35.2), "Amarillo": (-101.8, 35.2), "Dallas": (-96.8, 32.8),
    "Houston": (-95.4, 29.75), "San Antonio": (-98.5, 29.4), "Laredo": (-99.5, 27.5), "Oklahoma City": (-97.5, 35.5),
    "Kansas City": (-94.6, 39.1), "Omaha": (-95.95, 41.25), "Des Moines": (-93.6, 41.6), "Minneapolis": (-93.25, 44.95),
    "Sioux Falls": (-96.7, 43.55), "Chicago": (-87.65, 41.85), "St. Louis": (-90.2, 38.6), "Memphis": (-90.05, 35.15),
    "Little Rock": (-92.3, 34.75), "New Orleans": (-90.05, 29.95), "Shreveport": (-93.75, 32.5), "Jackson": (-90.2, 32.3),
    "Birmingham": (-86.8, 33.5), "Atlanta": (-84.4, 33.75), "Nashville": (-86.8, 36.15), "Knoxville": (-83.9, 35.95),
    "Indianapolis": (-86.15, 39.75), "Columbus": (-83.0, 39.95), "Cincinnati": (-84.5, 39.1), "Detroit": (-83.05, 42.35),
    "Toledo": (-83.55, 41.65), "Cleveland": (-81.7, 41.5), "Pittsburgh": (-80.0, 40.45), "Buffalo": (-78.9, 42.9),
    "Albany": (-73.75, 42.65), "Boston": (-71.05, 42.35), "New York": (-74.0, 40.7), "Philadelphia": (-75.15, 39.95),
    "Baltimore": (-76.6, 39.3), "Washington": (-77.05, 38.9), "Richmond": (-77.45, 37.55), "Raleigh": (-78.65, 35.8),
    "Charlotte": (-80.85, 35.2), "Columbia": (-81.05, 34.0), "Savannah": (-81.1, 32.1), "Jacksonville": (-81.65, 30.35),
    "Orlando": (-81.4, 28.55), "Tampa": (-82.45, 27.95), "Miami": (-80.2, 25.8), "Mobile": (-88.05, 30.7),
    "Tallahassee": (-84.3, 30.45), "Wichita": (-97.35, 37.7), "Madison": (-89.4, 43.07), "Portland ME": (-70.25, 43.65),
    "Barstow": (-117.0, 34.9),
}
# Candidate electric-highway (catenary) corridors on the Interstate network (~40,000 route-km in total)
CORRIDORS = {
    "I-5": ["Seattle", "Portland", "Sacramento", "Los Angeles", "San Diego"],
    "I-10": ["Los Angeles", "Phoenix", "El Paso", "San Antonio", "Houston", "New Orleans", "Mobile", "Tallahassee", "Jacksonville"],
    "I-40": ["Barstow", "Flagstaff", "Albuquerque", "Amarillo", "Oklahoma City", "Little Rock", "Memphis", "Nashville", "Knoxville", "Raleigh"],
    "I-80": ["San Francisco", "Sacramento", "Reno", "Salt Lake City", "Cheyenne", "Omaha", "Des Moines", "Chicago", "Toledo", "Cleveland", "New York"],
    "I-90/94": ["Seattle", "Spokane", "Billings", "Sioux Falls", "Madison", "Chicago", "Toledo", "Cleveland", "Buffalo", "Albany", "Boston"],
    "I-95": ["Miami", "Jacksonville", "Savannah", "Richmond", "Washington", "Baltimore", "Philadelphia", "New York", "Boston", "Portland ME"],
    "I-35": ["Laredo", "San Antonio", "Dallas", "Oklahoma City", "Wichita", "Kansas City", "Des Moines", "Minneapolis"],
    "I-70": ["Denver", "Kansas City", "St. Louis", "Indianapolis", "Columbus", "Pittsburgh", "Baltimore"],
    "I-75": ["Miami", "Tampa", "Atlanta", "Knoxville", "Cincinnati", "Toledo", "Detroit"],
    "I-20": ["Dallas", "Shreveport", "Jackson", "Birmingham", "Atlanta", "Columbia"],
    "I-15": ["San Diego", "Las Vegas", "Salt Lake City"],
}
GAS_BASINS = {"Appalachia (Marcellus/Utica)": (-80.2, 40.6), "Permian": (-102.4, 31.9), "Haynesville": (-93.8, 32.1),
              "Eagle Ford": (-98.4, 28.7), "Anadarko": (-98.6, 35.6), "Bakken": (-103.3, 47.9), "Rockies (Green R./DJ)": (-108.2, 41.5)}
# Canada -> U.S. gas import points (existing) and illustrative new-pipeline corridors
CANADA_ENTRY = {"Sumas WA": (-122.27, 49.0), "Eastport/Kingsgate ID": (-116.2, 49.0), "Port of Morgan MT": (-107.8, 49.0),
                "Emerson MN/ND": (-97.2, 49.0), "St. Clair MI": (-82.4, 42.9), "Niagara NY": (-79.05, 43.1), "Waddington NY": (-75.2, 44.9)}
NEW_PIPES = [[(-116.2, 49.0), (-114.5, 45.0), (-111.9, 40.75)],             # Montney/WCSB -> Intermountain West
             [(-107.8, 49.0), (-104.0, 45.0), (-100.0, 41.0), (-97.5, 36.0)],   # Alberta -> Midcontinent hub
             [(-97.2, 49.0), (-94.0, 45.5), (-88.0, 42.0)]]                    # Manitoba border -> Chicago
# HTGR cascade hubs: (name, lon, lat, rationale)
HUBS = [("Seadrift / Coastal Bend TX", -96.7, 28.4, "Long Mott Xe-100 site; petrochemicals; Gulf gas"),
        ("Lake Charles / Port Arthur", -93.6, 30.0, "refineries -> biocrude upgrading; LNG corridor"),
        ("Baton Rouge / Mississippi River", -91.2, 30.5, "refining; seaweed from Mississippi plume"),
        ("Shreveport (Haynesville)", -93.75, 32.5, "gas at wellhead; forest residues"),
        ("Permian (Midland-Odessa)", -102.1, 31.95, "associated gas; desalinated water for local use"),
        ("Oklahoma / Anadarko", -97.6, 35.8, "gas; wind; crop drying"),
        ("Appalachia (SW PA / WV)", -80.4, 39.9, "Marcellus gas; graphite & carbon-black plants"),
        ("Central Iowa / Nebraska", -94.5, 41.6, "ethanol plants; corn drying; residue biocrude"),
        ("Illinois / Indiana", -88.0, 40.5, "ethanol, refineries (Whiting), crop drying"),
        ("Central Valley CA", -120.5, 36.8, "greenhouses; crop drying; brackish-water distillation"),
        ("Columbia Basin WA/OR", -119.3, 46.2, "forest/ag residues; potatoes & crop drying"),
        ("Southern New England port", -70.95, 41.65, "kelp landing, drying, fertiliser"),
        ("Gulf of Maine port", -70.25, 43.65, "kelp landing, drying, fertiliser"),
        ("Chesapeake / Hampton Roads", -76.3, 36.9, "kelp landing; seafood farms"),
        ("Humboldt / Coos Bay", -124.15, 40.8, "Pacific kelp landing"),
        ("Morro Bay / Port San Luis", -120.85, 35.37, "Pacific kelp landing")]
# offshore-wind + seaweed co-location zones (schematic boxes: lon0, lat0, width, height)
OSW_BOXES = {"gom": (-70.2, 42.6, 1.6, 0.8), "sne": (-71.4, 40.6, 1.4, 0.55), "nyb": (-74.0, 39.4, 1.3, 0.8),
             "midatl": (-75.4, 36.6, 1.0, 1.6), "pac_n": (-125.6, 40.4, 0.7, 3.2), "pac_c": (-122.2, 34.9, 0.8, 1.2),
             "gulf": (-93.6, 27.9, 4.3, 0.75)}

# ---------------------------------------------------------------------------------------------- v2 additions
# Approximate interior state boundaries (hand-digitised polylines; rivers simplified).  Schematic only.
STATE_LINES = [
    [(-124.0, 46.25), (-123.0, 46.15), (-122.0, 45.6), (-121.0, 45.65), (-119.0, 45.95), (-116.92, 46.0)],          # WA/OR
    [(-117.04, 49.0), (-117.04, 46.4), (-116.92, 46.0), (-116.5, 45.5), (-117.0, 44.3), (-117.03, 42.0)],             # WA-OR/ID
    [(-124.2, 42.0), (-111.05, 42.0)],                                                                                # 42nd parallel
    [(-120.0, 42.0), (-120.0, 39.0), (-114.6, 35.0), (-114.4, 34.3), (-114.7, 33.4), (-114.7, 32.7)],                # CA/NV, CA/AZ
    [(-114.05, 42.0), (-114.05, 36.2), (-114.6, 35.0)],                                                              # NV/UT, NV/AZ
    [(-116.05, 49.0), (-116.05, 47.95), (-115.7, 47.4), (-114.4, 46.6), (-114.5, 45.6), (-113.4, 44.8), (-112.8, 44.4), (-111.05, 44.5)],  # ID/MT
    [(-111.05, 45.0), (-111.05, 41.0), (-109.05, 41.0)],                                                             # ID/WY, UT/WY
    [(-114.05, 37.0), (-102.05, 37.0)], [(-109.05, 41.0), (-109.05, 31.33)],                                          # 37th; UT-AZ/CO-NM
    [(-111.05, 45.0), (-104.05, 45.0)], [(-109.05, 41.0), (-102.05, 41.0)], [(-104.05, 49.0), (-104.05, 41.0)],      # MT/WY; WY/CO-NE; Dakotas/MT-WY
    [(-102.05, 41.0), (-102.05, 37.0)], [(-102.05, 40.0), (-95.3, 40.0)],                                            # CO/KS; NE/KS
    [(-103.05, 37.0), (-103.05, 32.0), (-106.6, 32.0)], [(-103.05, 36.5), (-100.0, 36.5), (-100.0, 34.6), (-98.0, 34.1), (-96.0, 33.8), (-94.5, 33.6)],  # NM/TX; TX/OK
    [(-102.05, 37.0), (-94.6, 37.0)],                                                                                 # OK/KS
    [(-104.05, 45.94), (-96.56, 45.94)], [(-104.05, 43.0), (-98.5, 43.0), (-97.0, 42.8), (-96.6, 42.5)],               # ND/SD; SD/NE
    [(-97.2, 49.0), (-96.6, 46.0), (-96.56, 45.3), (-96.45, 43.5), (-96.6, 42.5)],                                    # MN/Dakotas, SD/IA
    [(-96.45, 43.5), (-91.2, 43.5)], [(-91.2, 43.5), (-92.8, 44.7), (-92.8, 45.6), (-92.3, 46.65)],                    # MN/IA; MN/WI
    [(-96.6, 42.5), (-96.0, 41.0), (-95.3, 40.0), (-94.9, 39.1), (-94.6, 39.1), (-94.6, 36.5)],                        # NE/IA, MO/KS
    [(-95.8, 40.6), (-91.4, 40.6)], [(-94.6, 36.5), (-90.15, 36.5), (-90.1, 36.0), (-89.7, 36.0)],                    # IA/MO; MO/AR
    [(-91.2, 43.5), (-90.6, 42.5), (-90.6, 41.5), (-91.4, 40.6), (-91.0, 39.5), (-90.2, 38.6), (-89.5, 37.0), (-89.5, 36.5),
     (-90.3, 35.0), (-91.1, 33.0), (-91.6, 31.0)],                                                                    # Mississippi River
    [(-90.6, 42.5), (-87.8, 42.5)], [(-90.4, 46.6), (-88.1, 45.9), (-87.6, 45.1)],                                     # WI/IL; WI/MI
    [(-87.0, 41.7), (-84.8, 41.7), (-83.5, 41.7)], [(-87.5, 41.7), (-87.5, 39.0), (-88.0, 37.8)],                     # MI/IN-OH; IN/IL
    [(-84.8, 41.7), (-84.8, 39.1)],                                                                                   # IN/OH
    [(-89.2, 37.0), (-88.0, 37.8), (-87.0, 37.9), (-86.0, 38.0), (-85.5, 38.4), (-84.8, 39.1), (-83.7, 38.6), (-82.6, 38.4),
     (-81.0, 39.5), (-80.52, 40.6)],                                                                                  # Ohio River
    [(-89.5, 36.6), (-81.7, 36.6)], [(-82.6, 38.4), (-82.0, 37.5), (-83.7, 36.6)],                                    # KY/TN; KY/WV-VA
    [(-80.52, 42.0), (-80.52, 39.72)], [(-80.52, 42.0), (-75.3, 42.0), (-74.7, 41.35)],                                # OH/PA; PA/NY
    [(-74.7, 41.35), (-75.1, 40.0), (-75.5, 39.8)], [(-80.52, 39.72), (-75.8, 39.72)],                                 # PA/NJ; Mason-Dixon
    [(-79.5, 39.72), (-79.5, 39.2), (-78.4, 39.6), (-77.7, 39.3), (-78.3, 38.8), (-79.5, 38.4), (-80.3, 37.5), (-81.7, 37.2), (-82.0, 37.5)],  # WV
    [(-77.7, 39.3), (-77.0, 38.8), (-76.3, 38.0)], [(-75.8, 39.72), (-75.8, 38.45), (-75.05, 38.45)],                  # Potomac; DE/MD
    [(-83.7, 36.6), (-75.9, 36.55)], [(-81.7, 36.6), (-82.6, 36.0), (-84.3, 35.0)],                                    # VA/NC; TN/NC
    [(-84.3, 35.0), (-90.3, 35.0)], [(-94.04, 33.6), (-94.04, 33.0), (-91.1, 33.0)],                                   # TN south; AR/LA
    [(-94.04, 33.0), (-94.04, 32.0), (-93.8, 30.0), (-93.8, 29.7)], [(-91.6, 31.0), (-89.75, 31.0), (-89.6, 30.2)],     # LA/TX; LA/MS
    [(-88.2, 35.0), (-88.4, 30.4)], [(-85.6, 35.0), (-85.0, 32.3), (-85.0, 31.0)], [(-87.6, 31.0), (-85.0, 31.0)],     # MS/AL; AL/GA; AL/FL
    [(-87.6, 31.0), (-87.5, 30.3)], [(-85.0, 31.0), (-84.9, 30.7), (-82.0, 30.6), (-81.5, 30.7)],                      # Perdido; GA/FL
    [(-83.1, 34.9), (-82.2, 33.6), (-81.1, 32.1)], [(-84.3, 35.0), (-83.1, 35.0), (-82.4, 35.2), (-81.0, 35.1), (-80.9, 34.8), (-79.7, 34.8), (-78.6, 33.9)],  # GA/SC; NC/SC
    [(-73.35, 45.0), (-73.3, 43.6), (-73.25, 42.75)], [(-71.5, 45.0), (-72.0, 44.3), (-72.5, 42.73)],                  # NY/VT; VT/NH
    [(-73.25, 42.73), (-70.9, 42.85)], [(-71.08, 45.3), (-70.95, 43.1), (-70.7, 43.08)],                               # MA north; NH/ME
    [(-73.5, 42.75), (-73.5, 41.1)], [(-73.5, 42.03), (-71.4, 42.03)], [(-71.8, 42.03), (-71.8, 41.3)], [(-71.4, 42.03), (-71.2, 41.5)],
    [(-74.7, 41.35), (-73.9, 41.0)],
]
STATE_LABELS = {"WA": (-120.5, 47.4), "OR": (-120.5, 43.9), "CA": (-119.6, 37.2), "NV": (-116.8, 39.3), "ID": (-114.6, 43.6),
                "MT": (-109.6, 47.0), "WY": (-107.5, 43.0), "UT": (-111.7, 39.3), "AZ": (-111.7, 34.3), "CO": (-105.6, 39.0),
                "NM": (-106.1, 34.4), "ND": (-100.5, 47.5), "SD": (-100.3, 44.4), "NE": (-99.8, 41.5), "KS": (-98.4, 38.5),
                "OK": (-97.5, 35.6), "TX": (-99.0, 31.3), "MN": (-94.4, 46.3), "IA": (-93.5, 42.0), "MO": (-92.5, 38.4),
                "AR": (-92.4, 34.9), "LA": (-92.3, 31.0), "WI": (-89.8, 44.6), "IL": (-89.2, 40.0), "MI": (-84.7, 43.6),
                "IN": (-86.3, 39.9), "OH": (-82.8, 40.3), "KY": (-85.3, 37.5), "TN": (-86.3, 35.8), "MS": (-89.7, 32.7),
                "AL": (-86.8, 32.7), "GA": (-83.4, 32.7), "FL": (-81.6, 28.3), "SC": (-80.9, 33.9), "NC": (-79.3, 35.5),
                "VA": (-78.6, 37.5), "WV": (-80.6, 38.6), "PA": (-77.7, 40.9), "NY": (-75.5, 42.9), "VT": (-72.7, 44.0),
                "NH": (-71.6, 43.7), "ME": (-69.2, 45.3), "MA": (-72.0, 42.35), "CT": (-72.7, 41.6), "NJ": (-74.5, 40.1),
                "MD": (-76.8, 39.1), "DE": (-75.5, 38.95)}
# Land-use regions (schematic polygons)
REGIONS = {
    "onshore_wind": [  # Great Plains wind belt
        [(-104.0, 48.5), (-97.0, 48.5), (-96.5, 43.5), (-94.0, 43.3), (-94.5, 40.5), (-97.0, 37.0), (-97.5, 33.0),
         (-101.5, 31.5), (-103.0, 33.5), (-104.5, 37.0), (-105.0, 41.0), (-106.5, 42.5), (-104.0, 45.0)]],
    "solar": [  # desert Southwest + south Texas + Southeast
        [(-119.0, 37.5), (-114.5, 37.6), (-111.0, 36.8), (-104.5, 35.5), (-103.0, 31.5), (-106.6, 31.8), (-111.0, 31.4), (-114.7, 32.7), (-117.5, 33.8)],
        [(-100.5, 30.5), (-97.0, 30.0), (-97.6, 27.0), (-99.3, 26.6), (-100.5, 28.5)],
        [(-84.5, 33.5), (-80.5, 33.2), (-81.2, 29.5), (-82.5, 28.0), (-82.8, 29.5), (-84.5, 30.5)]],
    "bamboo": [  # clumping bamboo: Florida peninsula, Gulf Coast plain, coastal GA/SC, lower Rio Grande
        [(-82.6, 29.6), (-80.9, 29.4), (-80.3, 26.6), (-81.6, 26.2), (-82.4, 27.4)],
        [(-97.6, 29.2), (-94.0, 30.2), (-91.0, 30.5), (-88.2, 30.9), (-88.2, 30.4), (-89.6, 30.2), (-91.2, 29.5), (-93.8, 29.75), (-95.3, 29.0), (-96.8, 28.2)],
        [(-81.9, 32.5), (-80.6, 32.6), (-81.2, 31.4), (-81.5, 30.8), (-82.2, 31.3)],
        [(-98.8, 26.7), (-97.6, 26.9), (-97.4, 26.1), (-98.5, 26.2)]],
    "hemp": [  # Northern Plains & Upper Midwest, Kentucky, Colorado/Nebraska
        [(-104.0, 48.8), (-96.8, 48.8), (-96.6, 45.9), (-100.5, 45.9), (-103.0, 46.5), (-104.0, 47.5)],
        [(-96.4, 47.5), (-92.3, 46.8), (-90.0, 45.0), (-91.5, 43.6), (-95.6, 43.8), (-96.4, 45.0)],
        [(-89.0, 37.6), (-84.0, 38.3), (-83.3, 37.0), (-88.0, 36.4)],
        [(-105.0, 40.8), (-100.5, 40.8), (-100.5, 39.0), (-105.0, 38.8)]],
    "corn_ethanol": [  # Corn Belt ethanol plants
        [(-100.0, 43.2), (-93.5, 44.6), (-89.0, 43.2), (-85.5, 41.6), (-85.0, 39.5), (-89.0, 38.6), (-94.2, 39.6), (-98.5, 40.0)]],
    "residues": [  # Southeastern pine forests (forest residues) and Corn Belt stover overlap
        [(-95.3, 33.5), (-91.0, 33.7), (-86.0, 34.8), (-81.0, 35.5), (-77.5, 36.0), (-79.5, 33.8), (-81.8, 31.6), (-84.8, 31.2), (-88.8, 31.4), (-94.0, 31.0)],
        [(-124.0, 46.0), (-121.5, 46.5), (-121.8, 42.5), (-123.8, 42.2)]],
}
# HTGR hub sites: (name, lon, lat, weight, role).  The model's hub count is split by weight (largest remainder).
HUB_SITES = [
    ("Seadrift / Coastal Bend TX", -96.7, 28.4, 7, "H2, petrochemicals, Gulf seaweed"), ("Houston Ship Channel", -95.1, 29.7, 9, "H2, refineries->biofuels"),
    ("Port Arthur / Lake Charles", -93.6, 30.0, 8, "refineries, bamboo HTL"), ("Baton Rouge / St. James LA", -91.0, 30.3, 7, "refining, Mississippi-plume seaweed"),
    ("Mobile / Pascagoula", -88.3, 30.6, 4, "bamboo and forest-residue HTL"), ("Shreveport (Haynesville)", -93.75, 32.5, 5, "gas, forest residues"),
    ("Permian (Midland-Odessa)", -102.1, 31.95, 5, "associated gas, eHighway I-10/I-20 power"), ("Oklahoma City / Anadarko", -97.6, 35.5, 5, "gas, wind, crop drying"),
    ("Appalachia SW PA / WV", -80.4, 39.9, 8, "Marcellus gas, carbon fibre & graphite"), ("Ohio River (Ohio/Kentucky)", -84.0, 38.7, 4, "hemp, carbon products"),
    ("Central Iowa", -93.6, 41.9, 6, "ethanol-to-jet, crop drying, greenhouses"), ("Nebraska / Kansas", -97.0, 40.6, 4, "ethanol, hemp, crop drying"),
    ("Illinois / Indiana", -88.0, 40.5, 6, "ethanol, Whiting refinery, crop drying"), ("Minneapolis region", -93.6, 45.2, 3, "hemp, greenhouses"),
    ("North Dakota (Bakken)", -102.0, 47.9, 3, "gas, hemp oil & stalks"), ("Central Valley CA", -120.5, 36.8, 5, "greenhouses, crop drying, Pacific seaweed"),
    ("Columbia Basin WA/OR", -119.3, 46.2, 4, "forest residues, crop drying"), ("Humboldt / Coos Bay", -124.1, 41.5, 3, "Pacific giant-kelp landing"),
    ("Grays Harbor WA", -123.8, 46.95, 2, "Washington kelp landing"), ("Morro Bay / Long Beach", -120.0, 34.6, 3, "Southern CA kelp, ports"),
    ("Gulf of Maine (Portland ME)", -70.3, 43.7, 3, "kelp landing, drying, fertiliser"), ("Southern New England / New Bedford", -71.0, 41.7, 3, "kelp landing"),
    ("NY/NJ Harbor", -74.1, 40.6, 4, "kelp landing, eHighway I-95 power, greenhouses"), ("Hampton Roads VA", -76.3, 36.9, 3, "seaweed, seafood farms"),
    ("Savannah / Brunswick GA", -81.3, 31.9, 3, "bamboo, Gracilaria landing"), ("Florida (Tampa)", -82.4, 27.9, 3, "bamboo, greenhouses"),
    ("Denver / Front Range", -104.8, 39.9, 2, "eHighway I-70/I-25 power"), ("Salt Lake City", -112.0, 40.8, 2, "eHighway I-15/I-80 power"),
    ("Phoenix", -112.1, 33.4, 2, "eHighway I-10 power, desert solar firming"), ("Atlanta", -84.4, 33.6, 3, "eHighway I-75/I-85 power"),
]
CORRIDOR_KM = {"I-5": 2200, "I-10": 3960, "I-15": 1150, "I-20": 2500, "I-35": 2540, "I-40": 4100, "I-70": 3480, "I-75": 2850,
               "I-80": 4650, "I-90/94": 5000, "I-95": 3050}
