import geopandas as gpd

path = "MV_Päijät-Häme.gpkg"

def syvaluotaus():
    print(f"--- Tutkitaan tiedostoa: {path} ---")
    # Luetaan 100 riviä, jotta löydetään varmasti jotain
    df = gpd.read_file(path, layer='stand', rows=100, engine="pyogrio")
    
    print("\n1. Sarakkeiden nimet (varmistetaan sarakkeet):")
    print(df.columns.tolist())

    print("\n2. Ensimmäiset 5 riviä (Tunnukset):")
    # Näytetään standid, realestateid ja parcelid
    cols = [c for c in ['standid', 'realestateid', 'parcelid', 'standnumber'] if c in df.columns]
    print(df[cols].head(10))

    print("\n3. Missä nämä kuviot sijaitsevat (Sentroidit):")
    print(df.geometry.centroid.head(5))

if __name__ == "__main__":
    syvaluotaus()