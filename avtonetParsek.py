import time
import random
import json
from seleniumbase import SB
from bs4 import BeautifulSoup

def random_delay(min_ms, max_ms):
    """Naključni zamik med min in max milisekundami."""
    delay = random.uniform(min_ms/1000.0, max_ms/1000.0)
    time.sleep(delay)

def parse_basic_car_details(html):
    """Razčleni osnovne podatke vozila iz tabele z naslovom 'Osnovni podatki'."""
    soup = BeautifulSoup(html, 'html.parser')
    car_details = {}
    target_table = None
    # Poišči <th> element, ki vsebuje besedilo "Osnovni podatki" in dobite pripadajočo tabelo
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
    """Izlušči vrednost za podani ključ (npr. 'Prva registracija', 'Prevoženih', ...)
       iz strukture, kjer se išče div z določenimi razredi."""
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

def main():
    all_car_info = []
    # Uporabimo SB brez disable_images in nato dodamo chrome argument za onemogočanje slik
    with SB(uc=True, test=True, headless=True) as sb:
        try:
            sb.driver.execute_cdp_cmd("Network.enable", {})
            sb.driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp"]})
        except Exception as e:
            print("Napaka pri nastavitvi blokiranja slik:", e)

            # Odprava webdriver lastnosti
        sb.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

        # Odpri osnovno stran in obravnavaj popup-e/piškotke
        base_url = "https://www.avto.net"
        sb.open(base_url)
        sb.click_if_visible('#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')
        sb.click_if_visible('a.btn.btn-outline-light.btn-block.text-left.border.h-100')
        sb.click_if_visible('a[href="https://www.avto.net/Ads/Search.asp?SID=10000"]')

        # Nastavi iskalne filtre: starost, prodajalec, zaloga
        sb.select_option_by_text("#starost2", "danes")
        sb.select_option_by_text("#prodajalec", "fizična oseba")
        sb.select_option_by_text("#zaloga", "prikaži SAMO kar je na zalogi")

        # Zaženi iskanje
        sb.click_if_visible('button[name="B1"]')

        # Če se pojavi Google oglasni popup, ga zapri
        sb.click_if_visible('dismiss-button')

        # Počakaj, da se stran naloži
        #time.sleep(1)

        # Pridobi HTML iskalnih rezultatov
        html_content = sb.get_page_source()
        soup = BeautifulSoup(html_content, 'html.parser')

        # Poišči vse povezave oglasov, ki se začnejo z "../Ads/details.asp?id="
        car_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith("../Ads/details.asp?id=") and "display" not in href:
                modified_href = href.replace("..", "https://avto.net")
                car_links.append(modified_href)

        # Če povezav ni najdenih, uporabi alternativo (npr. povezave z razredom "stretched-link")
        if not car_links:
            links = soup.find_all('a', class_='stretched-link')
            for link in links:
                href = link.get('href')
                if href and "id=" in href:
                    if not href.startswith("http"):
                        href = base_url + (href if href.startswith("/") else "/" + href)
                    car_links.append(href)

        print(f"Najdenih je {len(car_links)} oglasov.")

        # Za vsak oglas pridobi podatke
        for url in car_links:
            sb.open(url)
            # Naključni zamik med 5 in 8 sekundami
            #random_delay(1000, 2000)
            # Preklopi na zadnji odprti zavihek (če jih je več)
            handles = sb.driver.window_handles
            if handles:
                sb.switch_to_window(handles[-1])
            try:
                current_html = sb.get_page_source()
            except Exception as e:
                print(f"Napaka pri pridobivanju HTML-ja za {url}: {e}")
                continue

            current_soup = BeautifulSoup(current_html, 'html.parser')

            # Pridobi ceno: poišči <p> element s class "h2 font-weight-bold"
            price_text = ""
            price_elem = current_soup.find('p', class_="h2 font-weight-bold")
            if price_elem:
                price_text = price_elem.get_text(strip=True).replace("€", "").strip()

            # Pridobi število lastnikov: poišči prvi <span> z "Lastnikov" in naslednji <h5>
            number_of_owners = ""
            for span in current_soup.find_all('span'):
                if "Lastnikov" in span.get_text():
                    h5 = span.find_next('h5')
                    if h5:
                        number_of_owners = h5.get_text(strip=True)
                    break

            # Pridobi opombe (če obstajajo) iz elementa z id "StareOpombe"
            opombe_elem = current_soup.find(id="StareOpombe")
            opombe = opombe_elem.decode_contents() if opombe_elem else ""

            # Izlušči dodatne podatke iz tabele
            car_details = parse_basic_car_details(current_html)
            fuel_emissions_data = parse_fuel_consumption_and_emissions(current_html)
            equipment_data = parse_equipment_details(current_html)

            # Dodatni podatki (npr. Prva registracija, Prevoženih, Lastnikov, Vrsta goriva, Moč motorja, Menjalnik)
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
            all_car_info.append(car_info)
            print(f"Obdelan oglas: {url}")

        # Shrani zbrane podatke v JSON datoteko
        with open("allCarInfo.json", "w", encoding="utf-8") as f:
            json.dump(all_car_info, f, indent=4, ensure_ascii=False)
        print("Vsi podatki so shranjeni v allCarInfo.json")

        # Opcijsko: shrani screenshot zadnje strani ali HTML vsebino
        # sb.save_screenshot("screenshot.png")
        # with open("pageContent.html", "w", encoding="utf-8") as f:
        #     f.write(current_html)

if __name__ == "__main__":
    main()
