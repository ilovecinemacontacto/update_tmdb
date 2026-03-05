import os, requests, re
from supabase import create_client

# Conexión con tus Secrets
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_KEY"))
TMDB_KEY = os.environ.get("TMDB_API_KEY")

def limpiar_nombre(titulo):
    # Elimina lo que haya entre paréntesis (ej: " (ENVIAD AYUDA)") para que TMDB encuentre la peli
    return re.sub(r'\s*\(.*?\)', '', titulo).strip()

def main():
    # 1. Traer solo películas con tmdb_id vacío
    res = supabase.table("peliculas").select("id", "titulo").is_("tmdb_id", "null").execute()
    
    if not res.data:
        print("✅ No hay películas pendientes.")
        return

    print(f"🎬 Procesando {len(res.data)} películas...")

    for peli in res.data:
        titulo_limpio = limpiar_nombre(peli['titulo'])
        print(f"Buscando: {titulo_limpio}...")

        # 2. Llamada directa a la búsqueda de TMDB
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_KEY}&query={titulo_limpio}&language=es-ES"
        
        try:
            r = requests.get(url).json()
            if r.get('results'):
                # Extraemos el ID numérico (el mismo de la URL que mostraste)
                tmdb_id = str(r['results'][0]['id'])
                
                # 3. Pegar el ID en tu columna tmdb_id
                supabase.table("peliculas").update({"tmdb_id": tmdb_id}).eq("id", peli['id']).execute()
                print(f"✔️ ID {tmdb_id} guardado para {peli['titulo']}")
            else:
                print(f"❌ No se encontró en TMDB: {titulo_limpio}")
        except Exception as e:
            print(f"⚠️ Error con {peli['titulo']}: {e}")

if __name__ == "__main__":
    main()
