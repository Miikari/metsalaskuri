import geopandas as gpd

file_path = "MV_Päijät-Häme.gpkg"

def tarkista_sisalto():
    print(f"--- Tarkistetaan tiedosto: {file_path} ---")
    
    # Luetaan vain 5 riviä geometrioiden kanssa
    df = gpd.read_file(file_path, rows=5, engine="pyogrio")
    
    print("\n1. Koordinaattijärjestelmä (CRS):")
    print(df.crs)

    print("\n2. Esimerkkikoordinaatteja (Geometry):")
    print(df.geometry.head())

    # Lasketaan koko aineiston rajat (tämä kertoo missä päin Suomea data on)
    # Huom: jos tiedosto on jättimäinen, tämä voi kestää hetken
    print("\n3. Koko tiedoston maantieteellinen laajuus (Bounds):")
    full_bounds = gpd.read_file(file_path, engine="pyogrio").total_bounds
    print(full_bounds)
    
    print("\n4. Sarakkeet:")
    print(df.columns.tolist())

if __name__ == "__main__":
    tarkista_sisalto()