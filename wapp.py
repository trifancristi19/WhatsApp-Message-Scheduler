from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import schedule
import logging
import os
import datetime
import pytz

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def setup_driver():
    # Setup Chrome WebDriver with improved options
    options = webdriver.ChromeOptions()
    
    # Create chrome-data directory if it doesn't exist
    chrome_data_dir = os.path.join(os.getcwd(), "chrome-data")
    if not os.path.exists(chrome_data_dir):
        os.makedirs(chrome_data_dir)
    
    options.add_argument(f"--user-data-dir={chrome_data_dir}")  # Saves WhatsApp session
    options.add_argument("--start-maximized")  # Start with maximized browser
    
    # Disable logging
    options.add_argument("--log-level=3")
    options.add_argument("--silent")
    
    # Disable unnecessary features
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    # Disable automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        return None

def is_logged_in(driver, timeout=30):
    """Check if already logged in to WhatsApp Web"""
    try:
        # Wait for either the QR code or the main chat interface
        wait = WebDriverWait(driver, timeout)
        
        # Try to find elements that indicate we're logged in
        try:
            # Look for the search box or side panel which appears when logged in
            wait.until(EC.presence_of_element_located((
                By.XPATH, 
                '//div[@role="textbox"][@title="Search input textbox"] | //div[@contenteditable="true"][@data-tab="3"]'
            )))
            logger.info("Already logged in to WhatsApp Web")
            return True
        except:
            # Look for QR code which appears when not logged in
            try:
                wait.until(EC.presence_of_element_located((
                    By.XPATH, '//div[contains(@class, "landing-wrapper")]//canvas'
                )))
                logger.info("QR code detected - need to scan to log in")
                return False
            except:
                logger.warning("Could not determine login status")
                return False
    except Exception as e:
        logger.error(f"Error checking login status: {e}")
        return False

def wait_for_login(driver, max_wait_time=120):
    """Wait for user to scan QR code and log in"""
    logger.info("Waiting for QR code scan...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        if is_logged_in(driver, timeout=5):
            logger.info("Successfully logged in!")
            return True
        time.sleep(2)
    
    logger.error(f"Login timed out after {max_wait_time} seconds")
    return False

def send_whatsapp_message(driver, contact_name, message):
    try:
        # Check if we need to navigate to WhatsApp Web
        if "web.whatsapp.com" not in driver.current_url:
            driver.get("https://web.whatsapp.com/")
            logger.info("Navigating to WhatsApp Web...")
            
            # Wait for WhatsApp to load and check login status
            if not is_logged_in(driver, timeout=30):
                if not wait_for_login(driver):
                    logger.error("Failed to log in to WhatsApp Web")
                    return False
        
        # Wait for the page to load completely - look for the search box
        wait = WebDriverWait(driver, 60)  # Increased timeout to 60 seconds
        
        # Try different XPath selectors for the search box
        try:
            search_box = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
            ))
        except:
            # Alternative selector
            search_box = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[@role="textbox"][@title="Search input textbox"]')
            ))
        
        # Clear any existing text and search for contact
        search_box.clear()
        search_box.send_keys(contact_name)
        logger.info(f"Searching for contact: {contact_name}")
        time.sleep(3)  # Wait for search results
        
        # Click on the contact - try different selectors
        try:
            contact = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f'//span[@title="{contact_name}"]')
            ))
            contact.click()
        except:
            try:
                # Alternative selector
                contact = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, f'//span[contains(@title,"{contact_name}")]')
                ))
                contact.click()
            except Exception as e:
                logger.error(f"Could not find contact {contact_name}: {e}")
                return False
                
        logger.info(f"Contact {contact_name} found and clicked")
        
        # Wait for the chat to load
        time.sleep(3)
        
        # Find message input and send message - try different selectors
        try:
            message_box = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
            ))
        except:
            try:
                # Alternative selector
                message_box = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//div[@role="textbox"][@title="Type a message"]')
                ))
            except Exception as e:
                logger.error(f"Could not find message input box: {e}")
                return False
        
        message_box.clear()
        message_box.send_keys(message)
        time.sleep(1)
        message_box.send_keys(Keys.ENTER)
        
        # Get current time in Dutch timezone
        dutch_tz = pytz.timezone('Europe/Amsterdam')
        current_time = datetime.datetime.now(dutch_tz).strftime('%H:%M:%S')
        
        logger.info(f"✅ Message sent to '{contact_name}': '{message}' at {current_time} Dutch time")
        return True
    
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

def scheduled_message_task():
    contact_name = ""  # Replace with your contact name
    message = ""      # Replace with your message
    
    # Get current time in Dutch timezone
    dutch_tz = pytz.timezone('Europe/Amsterdam')
    current_time = datetime.datetime.now(dutch_tz)
    
    logger.info(f"Attempting to send scheduled message to {contact_name} at {current_time.strftime('%H:%M:%S')} Dutch time")
    success = send_whatsapp_message(driver, contact_name, message)
    
    if not success:
        logger.warning("Message sending failed, will retry next scheduled time")

# Initialize the driver
driver = setup_driver()
if not driver:
    logger.critical("Could not initialize WebDriver. Exiting.")
    exit(1)

# Initial setup - Open WhatsApp Web and check login status
logger.info("Opening WhatsApp Web for initial setup...")
driver.get("https://web.whatsapp.com/")

# Check if already logged in, if not wait for QR code scan
if not is_logged_in(driver):
    logger.info("Please scan the QR code to log in to WhatsApp Web")
    if not wait_for_login(driver):
        logger.critical("Login failed. Exiting.")
        driver.quit()
        exit(1)

# Get Dutch timezone
dutch_tz = pytz.timezone('Europe/Amsterdam')
now = datetime.datetime.now(dutch_tz)

# Calculate time until 5:00 AM Dutch time
target_time = now.replace(hour=5, minute=0, second=0, microsecond=0)
if now > target_time:
    # If it's already past 5:00 AM today, schedule for tomorrow
    target_time = target_time + datetime.timedelta(days=1)

time_diff = (target_time - now).total_seconds()
hours, remainder = divmod(time_diff, 3600)
minutes, seconds = divmod(remainder, 60)

logger.info(f"Current Dutch time: {now.strftime('%H:%M:%S')}")
logger.info(f"Scheduled to send message at: {target_time.strftime('%H:%M:%S')} Dutch time")
logger.info(f"Waiting for {int(hours)} hours, {int(minutes)} minutes, and {int(seconds)} seconds")

# Schedule the message at 5:00 AM Dutch time
schedule.every().day.at("05:00").do(scheduled_message_task)

try:
    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 seconds
except KeyboardInterrupt:
    logger.info("Script stopped by user")
finally:
    logger.info("Closing WebDriver")
    driver.quit()