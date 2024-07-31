from seleniumbase import SB
from bs4 import BeautifulSoup



with SB(uc=True, test=True) as sb:
    url = "https://www.avto.net"
    sb.open(url)

    # Čakanje na gumb za piškotke in klik, če se pojavi
    sb.click_if_visible('#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')
    sb.click_if_visible('a.btn.btn-outline-light.btn-block.text-left.border.h-100')
    sb.click_if_visible('a[href="https://www.avto.net/Ads/Search.asp?SID=10000"]')

    #<select id="starost2" name="starost2" size="1" class="custom-select">
    #<option value="999" selected="">kadarkoli</option>
    #<option value="0">danes</option>
    #<option value="1">zadnjih 24 ur</option>
    #<option value="3">zadnjih 3 dni</option>
    #<option value="7">v zadnjem tednu</option>
    #</select>

    #<select id="prodajalec" name="prodajalec" size="1" class="custom-select">
    #<option value="2" selected="">trgovec ali fizična oseba</option>
    # <option value="0">fizična oseba</option>
    # <option value="1">trgovec</option>
    # </select>

    sb.select_option_by_text("#starost2", "danes")
    sb.select_option_by_text("#prodajalec", "fizična oseba")
    sb.select_option_by_text("#zaloga", "prikaži SAMO kar je na zalogi")


    sb.click_if_visible('button[name="B1"]')

    #VČASIH SE POJAVI GOOGLE OGLAS POPUP
    sb.click_if_visible('dismiss-button')

    html_content = sb.get_page_source()

    # Uporabite BeautifulSoup za razčlenjevanje HTML vsebine
    soup = BeautifulSoup(html_content, 'html.parser')

    links = soup.find_all('a', class_='stretched-link')

    ids = []
    for link in links:
        href = link['href']
        if "id=" in href:
            id_value = href.split('id=')[1].split('&')[0]
            ids.append(id_value)

    print(ids)

    # Ne pozabite na koncu zapreti brskalnika
    #sb.quit()


