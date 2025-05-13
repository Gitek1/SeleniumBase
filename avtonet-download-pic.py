from seleniumbase import SB
import os
import time
import re

def save_image_from_tab(sb, url, folder):
    # Odpri novo okno in naloži URL slike
    sb.open_new_window()
    sb.open(url)
    time.sleep(1)  # Počakaj, da se slika naloži

    filename = url.split("/")[-1]
    file_path = os.path.join(folder, filename)
    sb.save_screenshot(file_path)  # Shrani zaslonsko sliko, ki naj vsebuje samo sliko

    print(f"Image saved: {file_path}")
    # Zapri trenutno okno prek WebDriverja
    sb.driver.close()
    sb.switch_to_window(0)  # Preklopi nazaj na glavno okno

with SB(uc=True, test=True) as sb:
    url = "https://www.avto.net/Ads/details.asp?id=20830127&display=Audi%20A4%20Avant"
    sb.open(url)
    time.sleep(10)  # Počakaj, da se dinamična vsebina naloži

    folder = "downloaded_images"
    os.makedirs(folder, exist_ok=True)

    # Poišči vse <img> elemente znotraj elementov z razredom GO-OglasThumb
    thumb_elements = sb.find_elements(".GO-OglasThumb img")
    print(f"Found {len(thumb_elements)} thumbnail images")

    for thumb in thumb_elements:
        onclick_attr = thumb.get_attribute("onclick")
        print(f"Onclick attribute: {onclick_attr}")
        if onclick_attr:
            # Izvleči URL iz onclick atributa, kjer je oblika:
            # document.getElementById('BigPhoto').src='https://...jpg'
            match = re.search(r"src=['\"](https://\S+\.(?:jpg|jpeg|png))['\"]", onclick_attr, re.IGNORECASE)
            if match:
                image_url = match.group(1)
                print(f"Found image URL: {image_url}")
                save_image_from_tab(sb, image_url, folder)
            else:
                print("No matching URL found in onclick attribute")
        else:
            print("No onclick attribute found")
