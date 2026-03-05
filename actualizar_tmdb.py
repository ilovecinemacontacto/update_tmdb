import os
import requests
import re
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
TMDB_KEY = os.environ.get("TMDB_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def limpiar_titulo(titulo):
    # 1. Quitamos todo lo que esté entre paréntesis o guiones
    titulo = re.sub(r'\(.*\)', '', titulo)
    titulo = titulo.split(':')[0].split('-')[0]
    # 2. Quitamos palabras de formato que SensaCine añade
    basura = ["4K", "VOSE", "ESTRENO", "DIGITAL", "3D"]
    for palabra in basura:
        titulo = titulo.replace(palabra, "")
    return titulo.strip()

def buscar_en_tmdb(titulo):
    query = limpiar_titulo(titulo)
    print(f"🔍 Buscando como: '{query}'") # Verás esto en los logs de GitHub
    
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_KEY}&query={query}&language=es-ES"
    
    try:
        r = requests.get(url, timeout=10).json()
        if r.get('results'):
            return str(r['results'][0]['id'])
    except Exception as e:
        print(f"❌ Error API: {e}")
    return None

def main():
    res = supabase.table("peliculas").select("id", "titulo").is_("tmdb_id", "null").execute()
    
    if not res.data:
        print("✅ Todo al día.")
        return

    for peli in res.data:
        tmdb_id = buscar_en_tmdb(peli['titulo'])
        if tmdb_id:
            supabase.table("peliculas").update({"tmdb_id": tmdb_id}).eq("id", peli['id']).execute()
            print(f"✔️ {peli['titulo']} -> ID: {tmdb_id}")
        else:
            print(f"⚠️ Fallo: {peli['titulo']}")

if __name__ == "__main__":
    main()
