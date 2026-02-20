import requests
from dotenv import MESTA_API_KEY

API_KEY = MESTA_API_KEY
KIINTEISTOTUNNUS = "43441500010226"

url = f"https://avoin-paikkatieto.maanmittauslaitos.fi/kiinteisto-avoin/simple-features/v3/collections/PalstanSijaintitiedot/items?api-key={API_KEY}&kiinteistotunnus={KIINTEISTOTUNNUS}"

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    palstat = data.get("features", [])
    
    print(f"--- Kiinteistön {KIINTEISTOTUNNUS} palstat ({len(palstat)} kpl) ---\n")

    for i, f in enumerate(palstat, 1):
        pid = f.get("id")
        
        coords = f.get("properties", {}).get("kiinteistotunnuksenSijainti", {}).get("coordinates", [])
        
        if coords:
            lon, lat = coords
            maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            
            print(f"PALSTA {i} (ID: {pid})")
            print(f"📍 Sijainti kartalla: {maps_link}")
            print("-" * 40)

except Exception as e:
    print(f"Virhe haussa: {e}")