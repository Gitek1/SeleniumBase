import time
import random
import json
import concurrent.futures
from seleniumbase import SB
from bs4 import BeautifulSoup

def random_delay(min_ms, max_ms):
    """Naključni zamik med min in max milisekundami."""
    delay = random.uniform(min_ms / 1000.0, max_ms / 1000.0)
    time.sleep(delay)

def parse_basic_car_details(html):
    """Razčleni osnovne podatke vozila iz tabele z naslovom 'Osnovni podatki'."""
    soup = BeautifulSoup(html, 'html.parser')
    car_details = {}
    target_table = None
    for th in soup.find_all('th'):
        if "Osnovni podatki" in th.get_text():
            target_table = th.find_parent('table')
            break
    if target_table:
        for row in target_table.find_all('tr'):
            key_elem = row.find('th', class_="font-weight-normal")
            value_elem = row.find('td')
            if key_elem and value_elem:
                key = key_elem.get_text(strip=True)
                value = value_elem.get_text(strip=True)
                if key and value:
                    car_details[key] = value
    return car_details

def parse_fuel_consumption_and_emissions(html):
    """Razčleni podatke o porabi goriva in emisijah (NEDC) iz tabele."""
    soup = BeautifulSoup(html, 'html.parser')
    fuel_emissions_details = {}
    target_table = None
    for th in soup.find_all('th'):
        if "Poraba goriva in emisije (NEDC)" in th.get_text():
            target_table = th.find_parent('table')
            break
    if target_table:
        for row in target_table.find_all('tr'):
            key_elem = row.find('th', class_="font-weight-normal")
            value_elem = row.find('td')
            if key_elem and value_elem:
                key = key_elem.get_text(strip=True)
                value = value_elem.get_text(strip=True)
                if key and value:
                    fuel_emissions_details[key] = value
    return fuel_emissions_details

def parse_equipment_details(html):
    """Razčleni opremo in ostale podatke o ponudbi iz tabele."""
    soup = BeautifulSoup(html, 'html.parser')
    equipment_details = {}
    target_table = None
    for th in soup.find_all('th'):
        if "Oprema in ostali podatki o ponudbi" in th.get_text():
            target_table = th.find_parent('table')
            break
    if target_table:
        current_section = ''
        for row in target_table.find_all('tr'):
            header = row.find('th', class_="font-weight-bold")
            if header:
                current_section = header.get_text(strip=True)
                equipment_details[current_section] = []
            else:
                if current_section:
                    ul = row.find('ul', class_="list")
                    if ul:
                        items = [li.get_text(strip=True) for li in ul.find_all('li')]
                        if items:
                            equipment_details[current_section] = items
    return equipment_details

def extract_value_from_html(html, key_word):
    """Izlušči vrednost za podani ključ (npr. 'Prva registracija', 'Prevoženih', ...)"""
    soup = BeautifulSoup(html, 'html.parser')
    value = ""
    divs = soup.find_all('div', class_="col-6 col-md-4 p-0")
    for div in divs:
        media = div.find('div', class_="media")
        if media:
            media_body = media.find('div', class_="media-body")
            if media_body:
                span_elem = media_body.find('span')
                if span_elem and span_elem.get_text(strip=True) == key_word:
                    h5 = media_body.find('h5')
                    if h5:
                        value = h5.get_text(strip=True)
                        break
    return value

def process_car_link(url):
    """Obdelaj posamezen URL in vrni zbrane podatke."""
    current_html = None  # Inicializiramo spremenljivko
    try:
        with SB(uc=True, test=True, headless=True) as sb:
            try:
                sb.driver.execute_cdp_cmd("Network.enable", {})
                sb.driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp"]})
            except Exception as e:
                print("Napaka pri nastavitvi blokiranja slik:", e)
            # Poskus redefiniranja navigator.webdriver z dodajanjem configurable: true
            try:
                sb.execute_script(
                    "try {"
                    "   Object.defineProperty(navigator, 'webdriver', { get: function() { return undefined; }, configurable: true });"
                    "} catch(e) { console.log(e); }"
                )
            except Exception as e:
                print(f"Opozorilo: redefiniranje navigator.webdriver ni uspelo za {url}: {e}")
            sb.open(url)
            random_delay(1000, 2000)
            handles = sb.driver.window_handles
            if handles:
                sb.switch_to_window(handles[-1])
            current_html = sb.get_page_source()
    except Exception as e:
        print(f"Napaka pri obdelavi {url}: {e}")
        return None

    if not current_html:
        print(f"Ni uspelo pridobiti HTML-ja za {url}")
        return None

    current_soup = BeautifulSoup(current_html, 'html.parser')

    price_text = ""
    price_elem = current_soup.find('p', class_="h2 font-weight-bold")
    if price_elem:
        price_text = price_elem.get_text(strip=True).replace("€", "").strip()

    number_of_owners = ""
    for span in current_soup.find_all('span'):
        if "Lastnikov" in span.get_text():
            h5 = span.find_next('h5')
            if h5:
                number_of_owners = h5.get_text(strip=True)
            break

    opombe_elem = current_soup.find(id="StareOpombe")
    opombe = opombe_elem.decode_contents() if opombe_elem else ""

    car_details = parse_basic_car_details(current_html)
    fuel_emissions_data = parse_fuel_consumption_and_emissions(current_html)
    equipment_data = parse_equipment_details(current_html)

    additional_data = {
        "first_registration": extract_value_from_html(current_html, "Prva registracija"),
        "mileage": extract_value_from_html(current_html, "Prevoženih"),
        "owners": extract_value_from_html(current_html, "Lastnikov"),
        "fuel_type": extract_value_from_html(current_html, "Vrsta goriva"),
        "engine_power": extract_value_from_html(current_html, "Moč motorja"),
        "transmission": extract_value_from_html(current_html, "Menjalnik")
    }

    car_info = {
        "url": url,
        "priceText": price_text,
        "numberOfOwners": number_of_owners,
        "opombe": opombe,
        "carDetails": car_details,
        "fuelEmissionsData": fuel_emissions_data,
        "equipmentData": equipment_data,
        "additionalData": additional_data
    }
    print(f"Obdelan oglas: {url}")
    return car_info


def main():
    all_car_info = []
    # Pridobitev URL-jev oglasov z eno SB instanco
    with SB(uc=True, test=True, headless=True) as sb:
        try:
            sb.driver.execute_cdp_cmd("Network.enable", {})
            sb.driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp"]})
        except Exception as e:
            print("Napaka pri nastavitvi blokiranja slik:", e)
        sb.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        base_url = "https://www.avto.net"
        sb.open(base_url)
        sb.click_if_visible('#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')
        sb.click_if_visible('a.btn.btn-outline-light.btn-block.text-left.border.h-100')
        sb.click_if_visible('a[href="https://www.avto.net/Ads/Search.asp?SID=10000"]')
        sb.select_option_by_text("#starost2", "danes")
        sb.select_option_by_text("#prodajalec", "fizična oseba")
        sb.select_option_by_text("#zaloga", "prikaži SAMO kar je na zalogi")
        sb.click_if_visible('button[name="B1"]')
        sb.click_if_visible('dismiss-button')
        time.sleep(1)
        html_content = sb.get_page_source()
        soup = BeautifulSoup(html_content, 'html.parser')

        car_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith("../Ads/details.asp?id=") and "display" not in href:
                modified_href = href.replace("..", "https://avto.net")
                car_links.append(modified_href)
        if not car_links:
            links = soup.find_all('a', class_='stretched-link')
            for link in links:
                href = link.get('href')
                if href and "id=" in href:
                    if not href.startswith("http"):
                        href = base_url + (href if href.startswith("/") else "/" + href)
                    car_links.append(href)
        print(f"Najdenih je {len(car_links)} oglasov.")

    # Vzporedna obdelava URL-jev z uporabo ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(process_car_link, url) for url in car_links]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is not None:
                all_car_info.append(result)

    with open("allCarInfo.json", "w", encoding="utf-8") as f:
        json.dump(all_car_info, f, indent=4, ensure_ascii=False)
    print("Vsi podatki so shranjeni v allCarInfo-1.json")

if __name__ == "__main__":
    main()
