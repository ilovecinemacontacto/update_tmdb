import os, requests, re
from supabase import create_client

# Conexión
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_KEY"))
TMDB_KEY = os.environ.get("TMDB_API_KEY")

def limpiar_para_tmdb(titulo):
    # Esto quita los paréntesis como los de 'SEND HELP (ENVIAD AYUDA)'
    return re.sub(r'\s*\(.*?\)', '', titulo).strip()

def main():
    # 1. Buscamos pelis sin ID
    res = supabase.table("peliculas").select("id", "titulo").is_("tmdb_id", "null").execute()
    
    for peli in res.data:
        titulo_busqueda = limpiar_para_tmdb(peli['titulo'])
        print(f"Buscando: {titulo_busqueda}")

        # 2. Consulta a TMDB
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_KEY}&query={titulo_busqueda}&language=es-ES"
        r = requests.get(url).json()

        if r.get('results'):
            # El ID que ves en la URL de tu captura 313b60
            tmdb_id = str(r['results'][0]['id'])
            
            # 3. Guardar en Supabase
            supabase.table("peliculas").update({"tmdb_id": tmdb_id}).eq("id", peli['id']).execute()
            print(f"✅ Guardado ID {tmdb_id} para {peli['titulo']}")
        else:
            # Si sale este error, es que la Key sigue mal o el título es rarísimo
            print(f"❌ Error en {titulo_busqueda}: {r.get('status_message', 'No encontrado')}")

if __name__ == "__main__":
    main()
