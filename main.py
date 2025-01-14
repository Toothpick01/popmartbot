from gologin import GoLogin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# GoLogin profile configuration
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Nzg2MWZjOWQ2NDc1ZGZlMzZmMmZjYTMiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2Nzg2MjE5NTNiMDViNjgzZGJkMjE2MDQifQ._WmMUpkTsGOZGvcO_uuMhHb6rWM3gyS702K90x4GdUM"
PROFILE_ID = "67861fcad6475dfe36f2fd47"  

# Set up GoLogin
gl = GoLogin({
    "token": TOKEN,
    "profile_id": PROFILE_ID,
})

# Launch the browser with GoLogin
debugger_address = gl.start()
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", debugger_address)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# Open the product page
url = "https://m.popmart.com/es/products/1194/THE-MONSTERS---Have-a-Seat-Vinyl-Plush-Blind-Box"
driver.get(url)

def monitor_and_purchase():
    try:
        # Click the "Notify Me" element
        try:
            notify_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="__next"]/div/div/div[2]/div[1]/div[2]/div[2]/div/div[2]/div[2]/div[2]')
            ))
            notify_button.click()
            print("Clicked 'Notify Me' button.")
        except TimeoutException:
            print("'Notify Me' button not found. Continuing...")

        while True:
            # Monitor for the "BUY NOW" button
            try:
                buy_now_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'index_euBtn__7NmZ6') and contains(text(), 'BUY NOW')]")
                ))
                print("Product is available! Clicking 'BUY NOW'...")
                buy_now_button.click()

                # Proceed to the payment page
                payment_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'index_placeOrderBtn__E2dbt') and contains(text(), 'PROCEED TO PAY')]")
                ))
                payment_button.click()
                print("Clicked 'PROCEED TO PAY'. Order process initiated.")
                break

            except TimeoutException:
                print("'BUY NOW' button not found yet. Retrying...")
            except NoSuchElementException:
                print("Unexpected issue locating elements. Retrying...")

            # Pause between checks (no need if auto-refresher is active)
            time.sleep(5)

    finally:
        driver.quit()

# Start monitoring
try:
    monitor_and_purchase()
finally:
    # Stop GoLogin profile
    gl.stop()