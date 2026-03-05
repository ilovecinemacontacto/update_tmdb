import os, requests
from supabase import create_client

# Diagnóstico de conexión
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_KEY")
TMDB = os.environ.get("TMDB_API_KEY")

print(f"--- DIAGNÓSTICO ---")
print(f"¿Hay URL de Supabase?: {'SÍ' if URL else 'NO'}")
print(f"¿Hay API Key de TMDB?: {'SÍ' if TMDB else 'NO'}")

supabase = create_client(URL, KEY)

def main():
    # 1. Obtenemos solo UNA película para probar
    res = supabase.table("peliculas").select("id", "titulo").is_("tmdb_id", "null").limit(1).execute()
    
    if not res.data:
        print("No hay pelis vacías.")
        return

    peli = res.data[0]
    titulo = peli['titulo'].split('(')[0].strip() # Quitamos el paréntesis si lo hay
    
    print(f"Probando con: {titulo}")
    
    # 2. Buscamos en TMDB
    url_tmdb = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB}&query={titulo}&language=es-ES"
    r = requests.get(url_tmdb).json()
    
    if r.get('results'):
        tmdb_id = str(r['results'][0]['id'])
        print(f"✅ ¡ÉXITO! ID encontrado: {tmdb_id}")
        
        # 3. Intentamos escribir
        try:
            supabase.table("peliculas").update({"tmdb_id": tmdb_id}).eq("id", peli['id']).execute()
            print("✅ ID guardado en Supabase correctamente.")
        except Exception as e:
            print(f"❌ Error al escribir en Supabase: {e}")
    else:
        print(f"❌ TMDB no devolvió resultados para '{titulo}'. Respuesta: {r}")

if __name__ == "__main__":
    main()
