from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_navitrends_dynamic():
    print("Démarrage du scraping dynamique...", flush=True)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("🔄 Navigateur initialisé avec succès", flush=True)

    urls = [
        "https://navitrends.com/",
        "https://navitrends.com/a-propos/",
        "https://navitrends.com/services/",
        "https://navitrends.com/contact/",
        "https://navitrends.com/devis/"
    ]

    all_texts = []

    for url in urls:
        print(f"🌐 Accès à l'URL : {url}", flush=True)
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "p"))
            )
            print("✅ Contenu chargé avec succès", flush=True)
        except:
            print("⚠️ Le contenu n'a pas pu être chargé à temps", flush=True)
            continue

        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        headings = driver.find_elements(By.XPATH, "//h1 | //h2 | //h3")
        list_items = driver.find_elements(By.TAG_NAME, "li")

        texts = [el.text for el in paragraphs + headings + list_items]

        if "contact" in url:
            try:
                contact_elements = driver.find_elements(By.XPATH, "//a[contains(@href,'mailto')]|//a[contains(@href,'tel')]")
                contact_texts = []
                for el in contact_elements:
                    href = el.get_attribute("href")
                    if href.startswith("mailto:"):
                        contact_texts.append(href.replace("mailto:", "Email: "))
                    elif href.startswith("tel:"):
                        contact_texts.append(href.replace("tel:", "Téléphone: "))
                if contact_texts:
                    print("📞 Coordonnées trouvées :", contact_texts, flush=True)
                    texts.extend(contact_texts)
            except:
                print("⚠️ Coordonnées non trouvées", flush=True)

        print(f"ℹ️ {len(texts)} éléments extraits de cette page", flush=True)
        print("Exemples :", texts[:5], flush=True)

        all_texts.extend(texts)

    driver.quit()
    print("✅ Scraping terminé", flush=True)
    print(f"📄 Total de caractères récupérés : {len(all_texts)}", flush=True)

    return "\n".join(all_texts)

if __name__ == "__main__":
    contenu = scrape_navitrends_dynamic()
