import os, requests
from supabase import create_client

# Configuración
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_KEY"))
TMDB_KEY = os.environ.get("TMDB_API_KEY")

def main():
    # 1. Leer títulos de tu tabla (solo los que no tienen ID aún)
    res = supabase.table("peliculas").select("id", "titulo").is_("tmdb_id", "null").execute()
    
    if not TMDB_KEY:
        print("❌ ERROR: No se encuentra la TMDB_API_KEY en los Secrets de GitHub.")
        return

    for peli in res.data:
        titulo = peli['titulo']
        print(f"Buscando ID para: {titulo}...")

        # 2. Buscar en TMDB de la forma más simple posible
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_KEY}&query={titulo}&language=es-ES"
        
        try:
            r = requests.get(url).json()
            if r.get('results'):
                # Extraemos el ID (el mismo que ves en la URL de tu captura 313b60)
                tmdb_id = str(r['results'][0]['id'])
                
                # 3. Pegar el ID en la columna tmdb_id de Supabase
                supabase.table("peliculas").update({"tmdb_id": tmdb_id}).eq("id", peli['id']).execute()
                print(f"✅ ID {tmdb_id} guardado para {titulo}")
            else:
                print(f"⚠️ No se encontró ID en TMDB para '{titulo}'")
        except Exception as e:
            print(f"❌ Error técnico con {titulo}: {e}")

if __name__ == "__main__":
    main()
