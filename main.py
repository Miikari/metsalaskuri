import geopandas as gpd
import pandas as pd
import requests
from io import BytesIO
from shapely.ops import transform

# --- ASETUKSET ---
API_KEY = "479edcb3-563a-49c8-b100-34cd18325dfe"
MML_URL = "https://avoin-paikkatieto.maanmittauslaitos.fi/kiinteisto-avoin/simple-features/v3/collections/PalstanSijaintitiedot/items"
GPKG_PATH = "MV_Päijät-Häme.gpkg"

'''
Look geodata based on given property code, 
calculate the area based on true coordinates of property in metres 
and calculates the true value of property.
'''
class Metsalaskuri:
    def __init__(self, api_key):
        self.api_key = api_key
        self.hinnat = {'tukki': 78.0, 'kuitu': 32.0, 'maa': 1000.0}

    '''Finds the coordinates of property'''
    def hae_rajat(self, tunnus):
        osat = tunnus.replace(' ', '').split('-')
        if len(osat) == 4:
            puhdas = f"{osat[0].zfill(3)}{osat[1].zfill(3)}{osat[2].zfill(4)}{osat[3].zfill(4)}"
        else:
            puhdas = tunnus.replace('-', '')

        print(f"📡 Haetaan rajat MML:stä ID: {puhdas}...")
        r = requests.get(MML_URL, params={'api-key': self.api_key, 'kiinteistotunnus': puhdas, 'crs': 'http://www.opengis.net/def/crs/EPSG/0/4326'})
        
        if r.status_code == 200:
            gdf = gpd.read_file(BytesIO(r.content))
            if not gdf.empty:
                gdf.set_crs(epsg=4326, allow_override=True, inplace=True)
                gdf.geometry = gdf.geometry.map(lambda poly: transform(lambda x, y: (y, x), poly))
                return gdf.to_crs(epsg=3067)
        return None

    '''Calculates the value of property, not fully functional yet.'''
    def laske_arvo(self, rajat_gdf):
        print(f"🌲 Etsitään kuvioita tiedostosta {GPKG_PATH} sijainnin perusteella...")
        
        try:
            # 1. äR
            stands = gpd.read_file(GPKG_PATH, layer='stand', bbox=tuple(rajat_gdf.total_bounds), engine="pyogrio")
            if stands.empty:
                print("⚠️ Tiedostosta ei löytynyt kuvioita tältä koordinaattialueelta.")
                return

            stands.columns = [c.lower() for c in stands.columns]

            # 2. Reads the tree data
            summary = gpd.read_file(GPKG_PATH, layer='treestandsummary', engine="pyogrio")
            summary_df = pd.DataFrame(summary).drop(columns='geometry', errors='ignore')
            
            summary_df.columns = [c.lower() for c in summary_df.columns]

            # 3. Spatial Join:
            osumat = gpd.sjoin(stands, rajat_gdf, predicate='intersects')
            
            # 4. Merge
            data = osumat.merge(summary_df, on='standid', how='left')

            # 5. Calculations
            for col in ['sawlogvolume', 'pulpwoodvolume', 'area']:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
            
            puu_arvo = (data['sawlogvolume'] * data['area'] * self.hinnat['tukki']).sum() + \
                       (data['pulpwoodvolume'] * data['area'] * self.hinnat['kuitu']).sum()
            
            ala = rajat_gdf.geometry.area.sum() / 10000
            
            print("\n" + "="*40)
            print(f"✅ ANALYYSI VALMIS")
            print(f"📏 Kiinteistön pinta-ala: {ala:.2f} ha")
            print(f"🌲 Löydettyjä metsäkuvioita: {len(data)}")
            print("-" * 40)
            print(f"💰 Puuston arvo: {puu_arvo:,.0f} €")
            print(f"🏗️ Maapohjan arvo: {ala * self.hinnat['maa']:,.0f} €")
            print(f"💎 YHTEENSÄ: {puu_arvo + (ala * self.hinnat['maa']):,.0f} €")
            print("="*40)

        except Exception as e:
            print(f"❌ Virhe laskennassa: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    laskuri = Metsalaskuri(API_KEY)
    tunnus = input("Syötä kiinteistötunnus (kokeile 111-414-2-126): ")
    rajat = laskuri.hae_rajat(tunnus)
    if rajat is not None:
        laskuri.laske_arvo(rajat)
    else:
        print("❌ Kiinteistön rajoja ei saatu haettua.")