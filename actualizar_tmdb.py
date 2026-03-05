import os
import requests
from supabase import create_client

# Configuración
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_KEY"))
TMDB_KEY = os.environ.get("TMDB_API_KEY")

def buscar_id_en_tmdb(titulo):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_KEY}&query={titulo}&language=es-ES"
    try:
        r = requests.get(url).json()
        if r.get('results'):
            # Devolvemos el ID de la primera coincidencia
            return str(r['results'][0]['id'])
    except Exception as e:
        print(f"Error buscando {titulo}: {e}")
    return None

def main():
    # 1. Traer películas que NO tengan tmdb_id
    res = supabase.table("peliculas").select("id", "titulo").is_("tmdb_id", "null").execute()
    peliculas_sin_id = res.data

    if not peliculas_sin_id:
        print("✅ Todas las películas tienen ya su tmdb_id.")
        return

    print(f"🔍 Encontradas {len(peliculas_sin_id)} películas sin ID. Procesando...")

    for peli in peliculas_sin_id:
        nuevo_id = buscar_id_en_tmdb(peli['titulo'])
        
        if nuevo_id:
            # 2. Actualizar solo esa fila en Supabase
            supabase.table("peliculas").update({"tmdb_id": nuevo_id}).eq("id", peli['id']).execute()
            print(f"✔️ {peli['titulo']} -> TMDB ID: {nuevo_id}")
        else:
            print(f"❌ No se encontró ID para: {peli['titulo']}")

if __name__ == "__main__":
    main()
