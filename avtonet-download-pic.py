from seleniumbase import SB
import os
import time

def save_image_from_tab(sb, url, folder):
    sb.open_new_window()  # Open a new window
    sb.open(url)  # Open the image URL
    time.sleep(1)  # Wait for the image to load

    filename = url.split("/")[-1]
    file_path = os.path.join(folder, filename)
    sb.save_screenshot(file_path)  # Save screenshot of the page, which should only contain the image

    print(f"Image saved: {file_path}")
    sb.switch_to_default_content()  # Switch back to the original tab

with SB(uc=True, test=True) as sb:
    url = "https://www.avto.net/Ads/details.asp?id=19538828&display=%8Akoda%20Superb"
    sb.open(url)
    time.sleep(10)  # Allow time for any dynamic content to load

    folder = "downloaded_images"
    os.makedirs(folder, exist_ok=True)

    img_elements = sb.find_elements("img[src], p[data-src]")
    for img in img_elements:
        src = img.get_attribute("src") or img.get_attribute("data-src")
        if src and src.split(".")[-1] in ["png", "jpg", "jpeg"]:
            save_image_from_tab(sb, src, folder)
