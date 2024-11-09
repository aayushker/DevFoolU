from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time

# Initialize WebDriver
driver = webdriver.Chrome()
driver.get("https://devfolio.co/search?primary_filter=projects")

# Define lists to store scraped data
project_urls = []
project_names = []
project_descriptions = []
project_tech_stacks = []

# Scroll and collect project URLs
try:
    # Scroll until a sufficient number of projects are loaded (you can adjust this limit as necessary)
    SCROLL_PAUSE_TIME = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)

        # Find project elements and extract URLs
        project_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/projects/')]")
        for project in project_elements:
            url = project.get_attribute("href")
            if url not in project_urls:
                project_urls.append(url)

        # Break when no more new projects are loaded
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        if len(project_urls) >= 20:
            break

finally:
    # Once URLs are collected, move to scraping project details
    print(f"Collected {len(project_urls)} project URLs.")
    driver.quit()

# Open each project URL and extract data
driver = webdriver.Chrome()
for url in project_urls:
    try:
        driver.get(url)
        time.sleep(0.5)  # Allow time for the page to load

        # Extract project name
        project_name = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//h1"))
        ).text

        # Extract project description with updated class name
        try:
            # project_description = driver.find_element(
            #     # By.XPATH, "//div[contains(@class, 'sc-hKMtZM ShowMore__StyledContent-sc-4d42d6d7-0  kZPyny')]"
            #     # By.XPATH, "//*[@id='__next']/html/body/div/div[2]/section[1]/div[1]"
            #     # By.XPATH, "//*[@id='__next'] //section[@class=\"sc-bWijRQ dbnBTD\"]" 
            #     # By.XPATH, "//*[@id='__next']/div[2]/section[1]/div[1]" 
            #     By.XPATH, "//*[@id='__next']/div[2]/section[1]/div[1]/div" 
            # ).text
            project_description_element = driver.find_element(By.XPATH, "//*[@id='__next']/div[2]/section[1]/div[1]/div")
            all_text = [element.text for element in project_description_element.find_elements(By.XPATH, ".//*")]
            project_description = " ".join(all_text)


        except:
            project_description = "No description available"

        # Extract tech stack with updated class name
        tech_stack_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'sc-edUIhV sc-jmnVvD ProjectTechCard__ProjectTechChip-sc-c8650bcd-0 coEGBY dxbIEt BTjHj')]")
        tech_stack = ", ".join([element.text for element in tech_stack_elements])

        # Append data to lists
        project_names.append(project_name)
        project_descriptions.append(project_description)
        project_tech_stacks.append(tech_stack)

    except Exception as e:
        print(f"Failed to load data from {url}: {e}")
        continue

driver.quit()

# Save to CSV
df = pd.DataFrame({
    "Project URL": project_urls,
    "Project Name": project_names,
    "Project Description": project_descriptions,
    "Tech Stack": project_tech_stacks
})
df.to_csv("devfolio_projects.csv", index=False)

print("Data scraping completed and saved to devfolio_projects.csv.")