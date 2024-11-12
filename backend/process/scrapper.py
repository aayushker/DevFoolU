from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrapper(projectURL):
    driver = webdriver.Chrome()
    driver.get(projectURL)

    project_name = ""
    project_description = ""
    tech_stack = ""

    try:
        project_name = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//h1"))
        ).text

        try:
            project_description_element = driver.find_element(By.XPATH, "//*[@id='__next']/div[2]/section[1]/div[1]/div")
            all_text = [element.text for element in project_description_element.find_elements(By.XPATH, ".//*")]
            project_description = " ".join(all_text)
        except:
            project_description = "No description available"

        tech_stack_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'sc-edUIhV sc-jmnVvD ProjectTechCard__ProjectTechChip-sc-c8650bcd-0 coEGBY dxbIEt BTjHj')]")
        tech_stack = ", ".join([element.text for element in tech_stack_elements])

    except Exception as e:
        print(f"Failed to load data from {projectURL}: {e}")

    finally:
        driver.quit()

    data = {
        "Project URL": projectURL,
        "projectName": project_name,
        "projectDescription": project_description,
        "Tech Stack": tech_stack
    }

    return data