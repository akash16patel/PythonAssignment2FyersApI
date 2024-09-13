from fyers_apiv3 import fyersModel as FM
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import pyotp as tp

client_id = 'FK9E8YPI2C-100'
secret_key = '4Z24S0WRKI'
redirect_uri = 'https://www.google.com/'
user_name="YA31758"
totpkey="RCDORYYRBSGMVIHUDGDRGN7DKO7SI3TV"
pin1,pin2,pin3,pin4="1","9","9","8"
response_type = "code"
grant_type = "authorization_code"
session = FM.SessionModel(client_id=client_id, secret_key=secret_key, redirect_uri=redirect_uri,
                          response_type=response_type, grant_type=grant_type)
response=session.generate_authcode()
link=response

# driver = webdriver.Chrome()
options=webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver=webdriver.Chrome(options=options)
driver.get(link)
time.sleep(2)
login_with_client_id='//*[@id="login_client_id"]'
elem=driver.find_element(By.XPATH,login_with_client_id)
elem.click()
time.sleep(1)
client_id_input_x_path='//*[@id="fy_client_id"]'
elem2 = driver.find_element(By.XPATH, client_id_input_x_path)
elem2.send_keys("YA31758")
elem2.send_keys(Keys.RETURN)
time.sleep(5)
t=tp.TOTP(totpkey).now()
print(t)
time.sleep(5)
try:
    # Wait for the first element to be visible and interactable, then send the first digit
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="first"]')))
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="first"]'))).send_keys(t[0])

    # Repeat for the other input fields
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="second"]'))).send_keys(t[1])
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="third"]'))).send_keys(t[2])
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="fourth"]'))).send_keys(t[3])
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="fifth"]'))).send_keys(t[4])
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sixth"]'))).send_keys(t[5])

    # Wait for the checkbox and click it (assuming the checkbox has an id or XPath you can use)
    checkbox = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="checkbox_id"]')))  # Replace with actual checkbox XPath or ID
    checkbox.click()  # This clicks the checkbox to check it

except Exception as e:
    print(f"Error encountered: {e}")
time.sleep(1)

driver.find_element(By.ID,"verifyPinForm").find_element(By.ID,"first").send_keys(pin1)
driver.find_element(By.ID,"verifyPinForm").find_element(By.ID,"second").send_keys(pin2)
driver.find_element(By.ID,"verifyPinForm").find_element(By.ID,"third").send_keys(pin3)
driver.find_element(By.ID,"verifyPinForm").find_element(By.ID,"fourth").send_keys(pin4)

driver.find_element(By.XPATH,'//*[@id="verifyPinSubmit"]').click()
time.sleep(1)
newurl = driver.current_url
print(newurl)
auth_code = newurl[newurl.index('auth_code=')+10:newurl.index('&state')]
print(auth_code)
session = FM.SessionModel(client_id=client_id, secret_key=secret_key, redirect_uri=redirect_uri,
                          response_type=response_type, grant_type=grant_type)
# Set the authorization code in the session object
session.set_token(auth_code)

# Generate the access token using the authorization code
response = session.generate_token()

# Print the response, which should contain the access token and other details
print(response)

access_token=response['access_token']
with open('accessT.txt','w') as k:
    k.write(access_token)


