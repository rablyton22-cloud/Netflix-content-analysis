"""Country name → ISO-3166 alpha-3 mapping for choropleth rendering."""
from __future__ import annotations

ISO3 = {
    "United States": "USA", "India": "IND", "United Kingdom": "GBR",
    "Canada": "CAN", "France": "FRA", "Japan": "JPN", "Spain": "ESP",
    "South Korea": "KOR", "Germany": "DEU", "Mexico": "MEX", "China": "CHN",
    "Australia": "AUS", "Egypt": "EGY", "Turkey": "TUR", "Hong Kong": "HKG",
    "Nigeria": "NGA", "Italy": "ITA", "Brazil": "BRA", "Argentina": "ARG",
    "Belgium": "BEL", "Indonesia": "IDN", "Taiwan": "TWN", "Philippines": "PHL",
    "Thailand": "THA", "South Africa": "ZAF", "Colombia": "COL",
    "Netherlands": "NLD", "Denmark": "DNK", "Ireland": "IRL", "Sweden": "SWE",
    "Singapore": "SGP", "Poland": "POL", "United Arab Emirates": "ARE",
    "New Zealand": "NZL", "Lebanon": "LBN", "Israel": "ISR", "Norway": "NOR",
    "Chile": "CHL", "Russia": "RUS", "Malaysia": "MYS", "Pakistan": "PAK",
    "Czech Republic": "CZE", "Switzerland": "CHE", "Romania": "ROU",
    "Uruguay": "URY", "Saudi Arabia": "SAU", "Austria": "AUT",
    "Luxembourg": "LUX", "Finland": "FIN", "Greece": "GRC", "Hungary": "HUN",
    "Iceland": "ISL", "Bulgaria": "BGR", "Qatar": "QAT", "Peru": "PER",
    "Jordan": "JOR", "Kuwait": "KWT", "Vietnam": "VNM", "Serbia": "SRB",
    "Kenya": "KEN", "Cambodia": "KHM", "Portugal": "PRT", "Morocco": "MAR",
    "Ghana": "GHA", "Venezuela": "VEN", "Bangladesh": "BGD", "Croatia": "HRV",
    "Iran": "IRN", "Algeria": "DZA", "Syria": "SYR", "Senegal": "SEN",
    "Malta": "MLT", "Zimbabwe": "ZWE", "Ukraine": "UKR", "Slovenia": "SVN",
    "Nepal": "NPL", "Mauritius": "MUS", "Cayman Islands": "CYM",
    "Namibia": "NAM", "Guatemala": "GTM", "Iraq": "IRQ", "Georgia": "GEO",
    "Burkina Faso": "BFA", "Ethiopia": "ETH", "Cameroon": "CMR",
    "Palestine": "PSE", "Angola": "AGO", "Mozambique": "MOZ", "Belarus": "BLR",
    "Puerto Rico": "PRI", "Cyprus": "CYP", "Malawi": "MWI", "Paraguay": "PRY",
    "Albania": "ALB", "Slovakia": "SVK", "Bermuda": "BMU", "Ecuador": "ECU",
    "Armenia": "ARM", "Mongolia": "MNG", "Bahamas": "BHS", "Sri Lanka": "LKA",
    "Latvia": "LVA", "Liechtenstein": "LIE", "Cuba": "CUB", "Nicaragua": "NIC",
    "Dominican Republic": "DOM", "Samoa": "WSM", "Azerbaijan": "AZE",
    "Botswana": "BWA", "Vatican City": "VAT", "Jamaica": "JAM",
    "Kazakhstan": "KAZ", "Lithuania": "LTU", "Afghanistan": "AFG",
    "Somalia": "SOM", "Sudan": "SDN", "Panama": "PAN", "Uganda": "UGA",
    "Montenegro": "MNE", "United States Virgin Islands": "VIR",
    "West Germany": None, "East Germany": None, "Soviet Union": None,
    "Not Available": None,
}


def iso3(country: str) -> str | None:
    return ISO3.get(country)
