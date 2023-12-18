from git import Repo
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LogInFailure(Exception):
    pass

def GetRemoteURL(repoNames, id, pw):
    repoURLDict = {}

    #---------- remote repository -----------
    # set webdriver options
    url = "https://github.com"

    user_agent = "baidu"

    options = webdriver.ChromeOptions()
    options.add_argument("use-agent=" + user_agent)

    # create new webdriver
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(time_to_wait=5)

    # ---------- github.com/login ----------
    driver.get(url + "/login")
    time.sleep(1)
    loginInput = driver.find_element(By.ID, "login_field")
    loginInput.send_keys(id)

    passwordInput = driver.find_element(By.ID, "password")
    passwordInput.send_keys(pw)

    submitButton = driver.find_element(By.CLASS_NAME, "js-sign-in-button")
    submitButton.click()
    
    try:
        WebDriverWait(driver, 5).until(EC.url_changes(url + "/session"))
    except:
        driver.close()
        raise LogInFailure()

    for remoteRepositoryName in repoNames:
        # ---------- github.com/new ----------
        driver.get(url + "/new")
        repoNameInput = driver.find_element(By.ID, ":r3:")
        repoNameInput.send_keys(remoteRepositoryName)

        privateRadioButton = driver.find_elements(By.NAME, "visibilityGroup")[1]
        privateRadioButton.click()

        READMECheckBox = driver.find_element(By.ID, ":r9:")
        READMECheckBox.click()

        createRepositoryButton_XPATH = "/html/body/div[1]/div[6]/main/react-app/div/form/div[5]/button"

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        createRepositoryButton = driver.find_element(By.XPATH, createRepositoryButton_XPATH)
        createRepositoryButton.click()
        time.sleep(1)

        try:
            WebDriverWait(driver, 5).until(EC.url_changes(url + "/" + id + "/" + remoteRepositoryName))
        except:
            repoURLDict[remoteRepositoryName] = None
        finally:
            # ---------- github.com/REPONAME ----------
            driver.get(url + "/" + id + "/" + remoteRepositoryName)
            codeButton = driver.find_element(By.ID, ":r5:")
            codeButton.click()

            remoteUrl_XPATH = '//*[@id="__primerPortalRoot__"]/div/div/div/ul/div[2]/div/div[2]/div/input'
            remoteUrl = driver.find_element(By.XPATH, remoteUrl_XPATH).get_attribute("value")
            
            repoURLDict[remoteRepositoryName] = remoteUrl

    driver.close()
    
    return repoURLDict

def CommitFolders(repoNames, repoPathDict, repoURLDict):
    #---------- local repository ----------
    for repoName in repoNames:
        directoryPath = repoPathDict[repoName]
        remoteUrl = repoURLDict[repoName]
        
        if remoteUrl == None:
            continue
        
        try:
            repo = Repo(directoryPath)
        except:
            repo = Repo.init(directoryPath)

        origin = repo.create_remote("origin", remoteUrl)
        origin.pull(refspec="master")

        commitList = repo.untracked_files + [d.a_path for d in repo.index.diff()]

        repo.index.add(commitList)
        repo.index.commit("Commit for backup to " + repoName)
        origin.push(refspec="master")