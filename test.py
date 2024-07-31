from seleniumbase import SB

with SB(uc=True, test=True) as sb:
    url = "https://www.avto.net"
    sb.open(url)

    # Čakanje na gumb za piškotke in klik, če se pojavi
    sb.click_if_visible('#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')

    #cookie_button_selector = "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"

    # Uporabimo wait_for_element, če želimo počakati, da se element pojavi
   # if sb.is_element_present(cookie_button_selector):
    #    sb.click(cookie_button_selector)

    sb.click_if_visible('a.btn.btn-outline-light.btn-block.text-left.border.h-100')

    # Čakanje na gumb za napredno iskanje in klik
    #napredno_iskanje_btn = 'a.btn.btn-outline-light.btn-block.text-left.border.h-100'
    #sb.wait_for_element(napredno_iskanje_btn)
    #sb.click(napredno_iskanje_btn)

    #sb.sleep(8)
    sb.click_if_visible('a[href="https://www.avto.net/Ads/Search.asp?SID=10000"]')


    sb.click_if_visible('button[name="B1"]')

    #gumb_selector = 'button[name="B1"]'
    #sb.click(gumb_selector)


    #sb.click_if_visible('a[https://www.avto.net/Ads/search_category.asp?SID=60000&head=1"]')

   # moto_btn = 'a[https://www.avto.net/Ads/search_category.asp?SID=60000&head=1"]'
   # sb.wait_for_element(moto_btn)
    #sb.click(moto_btn)










    # Čakamo na gumb za napredno iskanje in kliknite nanj
    #napredno_iskanje_link = 'a[href="https://www.avto.net/Ads/Search.asp?SID=10000"]'
    #sb.wait_for_element(napredno_iskanje_link)
    #sb.click(napredno_iskanje_link)

    #sb.sleep(3)  # Čakajte 5 sekund; prilagodite glede na potrebe

    #sb.execute_script("document.getElementById('starost2').value = '0';")


#<select id="starost2" name="starost2" size="1" class="custom-select">
    #<option value="999" selected="">kadarkoli</option>
    #<option value="0">danes</option>
    #<option value="1">zadnjih 24 ur</option>
    #<option value="3">zadnjih 3 dni</option>
    #<option value="7">v zadnjem tednu</option>
#</select>


    sb.click_if_visible('#starost2')

    # Čakamo na element spustnega seznama in nato izberemo "danes"
    #select_oglas_objavljen_id = "starost2"  # ID spustnega seznama
    #option_oglas_objavljen_value = "0"  # Vrednost za "danes"

    #TIMEOUT NE SMEMO UPORABIT KER CLOUDFLARE ZAZNA BOTA
    #sb.wait_for_element(select_oglas_objavljen_id, timeout=5)
    #sb.wait_for_element(select_oglas_objavljen_id)
    #sb.select_option_by_value(select_oglas_objavljen_id, option_oglas_objavljen_value)


#<select id="prodajalec" name="prodajalec" size="1" class="custom-select">
    #<option value="2" selected="">trgovec ali fizična oseba</option>
    # <option value="0">fizična oseba</option>
    # <option value="1">trgovec</option>
# </select>


    # Čakamo na element spustnega seznama in nato izberemo "danes"
    #select_prodajalec_je_lahko_id = "prodajalec"  # ID spustnega seznama
    #option_select_prodajalec_je_lahko_id_value = "0"  # Vrednost za "danes"
   # sb.wait_for_element(select_prodajalec_je_lahko_id)
    #sb.select_option_by_value(select_prodajalec_je_lahko_id, option_select_prodajalec_je_lahko_id_value)
