import requests
from bs4 import BeautifulSoup
import re
import time

def get_total_pages(soup):
    # Sabemos que hay 92 artículos en total y 32 por página
    total_products = 92
    products_per_page = 32
    return (total_products + products_per_page - 1) // products_per_page

def extract_price_and_volume(text):
    # Extraer precio y volumen usando expresiones regulares
    price_match = re.search(r'(\d+,\d+)\s*€\s*(\d+)\s*ml', text)
    if price_match:
        price_str = price_match.group(1).replace(',', '.')
        volume = float(price_match.group(2))
        price = float(price_str)
        price_per_ml = round(price / volume, 3)
        return f"{text}\t{price_per_ml:.3f} €/ml"
    return text

def extract_articles():
    # URL base de la página web
    base_url = "https://www.essenciales.com/aceites-esenciales/"
    all_articles = []
    
    try:
        total_pages = get_total_pages(None)  # No necesitamos soup aquí
        
        # Iterar sobre todas las páginas
        for page in range(1, total_pages + 1):
            # Añadir un retraso para no sobrecargar el servidor
            time.sleep(1)
            
            # Construir la URL con el parámetro page correcto
            url = f"{base_url}?page={page}" if page > 1 else base_url
            print(f"Procesando página {page} de {total_pages}...")
            
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Encontrar todos los elementos article en la página actual
            articles = soup.find_all('article')
            if articles:
                all_articles.extend(articles)
                print(f"Encontrados {len(articles)} artículos en la página {page}")
            else:
                print(f"No se encontraron artículos en la página {page}")
        
        # Crear el archivo articles.txt
        with open('articles.txt', 'w', encoding='utf-8') as f:
            for article in all_articles:
                texto = article.get_text()
                texto = '\t'.join(filter(None, texto.split('\n')))
                texto = re.sub(r'[\t\s]*Comprar[\t\s]*', '', texto)
                texto = re.sub(r'[\t\s]*Cantidad[\t\s]*', '', texto)
                texto = extract_price_and_volume(texto)  # Añadir precio por ml
                f.write(texto)
                f.write('\n')
                
        print(f"Se han extraído {len(all_articles)} artículos y guardado en articles.txt")
        
    except requests.RequestException as e:
        print(f"Error al acceder a la página web: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    extract_articles() 