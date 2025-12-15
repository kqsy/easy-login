import os
import re
import sys
import time
import json
import shutil
import ctypes
import urllib3
import requests
import selenium
import zipfile as zf
from selenium import webdriver
from selenium_stealth import stealth

if os.name != "nt": #script is designed for WinOS
    exit()

try:
    usrsys = sys.platform
    token = ""
    useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    api = json.loads(requests.get('https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json', headers={'User-Agent' : useragent}).text)
    refver = "" # referencing to Main()
    response = ""
    dist = "chromedriver"
    scrver = 3 # script version
    ctrl = 0 # incrementer
    current = "" # url to latest version of chromedriver
    instver = "" # new chromedriver installation version
    vcvs = [] # list of valid chromedriver versions
    appname = f"Easy Login V{str(scrver)}" # used for application & Message box Title
except ConnectionError as ConnectionException:
    print(ConnectionException)
    exit()
except OSError as NotPermitted:
    print(NotPermitted)
    exit()
except urllib3.exceptions.MaxRetryError as TimeoutException:
    print(TimeoutException)
    exit()
except urllib3.exceptions.NewConnectionError as NewConnectionException:
    print(NewConnectionException)
    exit()

def Clear():
    os.system('cls')

def Title(text):
    return ctypes.windll.kernel32.SetConsoleTitleW(text)

def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

def chop(cvf): #chromedriver version format
    prefix = '.'.join(cvf.split('.')[:-1])+"."
    return prefix

def getchrome(body, idver):
    global vcvs #list of valid chromedriver versions
    global instver #new chromedriver installation version
    global ctrl #incrementer
    global current
    for key, value in body.items():
        if key == "versions":
            versions = body.get(key)
            for value in versions:
                chromeversion = value["version"]
                if (ctrl == 0):
                    if (chop(chromeversion) == idver):
                        vcvs.append(chromeversion)
                if (ctrl == 1): #manual break function
                    if (chromeversion == instver):
                        tree = value["downloads"].get(dist)
                        systems = 0
                        while (systems < len(tree)):
                            branch = tree[systems]
                            system = branch["platform"]
                            downloads = branch["url"]
                            if system == usrsys:
                                current = str(downloads)
                                return
                            systems += 1

    if vcvs:
        instver = max(vcvs)
        if (instver != None):
            ctrl += 1
    getchrome(body, idver) #indicated full loop has been made

def getlink(body, idver): # refer API variable
    global vcvs # list of valid chromedriver versions
    global instver # new chromedriver installation version
    global ctrl # incrementer
    global current
    for key in body.items():
        channels = body["channels"]
        for key in channels:
            release = channels[key]
            for key in release:
                chromeversion = release["version"]
                if (ctrl == 0):
                    if (chop(chromeversion) == idver):
                        vcvs.append(chromeversion) # after loop finishes, gets latest
                if (ctrl == 1): # manual break function
                    if (chromeversion == instver):
                        tree = release["downloads"].get(dist) # dist = "chromedriver"
                        systems = 0
                        while (systems < len(tree)):
                            branch = tree[systems]
                            system = branch["platform"]
                            downloads = branch["url"]
                            if system == usrsys:
                                current = str(downloads)
                                return
                            # else: 
                                # handle user system not being recognized
                            systems += 1

    if vcvs: # fixes {instver} being a constantly changing var
        instver = max(vcvs)
        if (instver != None):
            ctrl += 1
    getlink(body, idver) # indicated full loop has been made

def delete(archive):
    NotFound = []
    contents = list(archive)
    for item in contents:
        if os.path.exists(item):
            if (item.split('.')[-1] == "zip"):
                os.remove(item) # try os.rmdir
            else:
                shutil.rmtree(item)
        else:
            NotFound.append(item)
    if NotFound:
        if (len(NotFound) > 1):
            lost = ", ".join(NotFound[:-1]) + f", or {NotFound[-1]}"
        else:
            lost = NotFound[0]
        print(f"Could not find {lost}.")

def download(link):
    # downloads ZIP file
    # web request, get data
    global usrsys
    try: # compressed ZIP file, containing Chromedriver.exe
        comp = [f"chromedriver_{usrsys}.zip", [f"chromedriver-{usrsys}", ["THIRD_PARTY_NOTICES.chromedriver", "LICENSE.chromedriver", "chromedriver.exe"]]]
        subfile = comp[1][1][2] # subfile(s) of compressed ZIP file, where Chromedriver.exe is stored
        compfile = comp[0]
        subfolder = comp[1][0]
        filepath = subfolder + '/'

        r = requests.get(link, allow_redirects=True)
        open(compfile, 'wb').write(r.content)

        with zf.ZipFile(compfile, 'r') as zip_ref:
            for subpath in zip_ref.infolist():
                if subpath.filename.startswith(filepath+subfile):
                    zip_ref.extract(member=subpath)
        shutil.move(src=os.path.join(filepath, subfile), dst=os.path.join('./', subfile))
        delete([subfolder, compfile])
    except Exception as error:
        print(error)
        exit()

def update():
    # tasks: download file(s), extract ZIP, replace 'chromedriver.exe'
    try:
        Clear()
        print("Restarting")
        refver = chop(response) #ideal referred chromedriver version
        getlink(api, refver)
        download(current)
        Mbox(appname, "Chromedriver is up-to-date", 0+0x10)
        Main()
    except:
        pass

def login():
    global response
    global token
    try:
        chromeloc = './chromedriver.exe' # alternative: 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
        Clear()
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--guest') # alternative: '--profile-directory=Profile 0' or other number
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'user-agent={useragent}')
        options.add_experimental_option('detach', True)
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])

        if os.path.exists(chromeloc):
            driver = webdriver.Chrome(chromeloc, options=options)
        else:
            print("No set Chromedriver location")
            exit()
        stealth(driver,
            languages=['en-US', 'en'],
            vendor='Google Inc.',
            platform='Win32',
            webgl_vendor='Intel Inc.',
            renderer='Intel Iris OpenGL Engine',
            fix_hairline=True,
            )
        script = """
                function login(token) {
                setInterval(() => {
                document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"`
                }, 50);
                setTimeout(() => {
                location.reload();
                }, 2500);
                }
                """
        driver.get('https://discord.com/login')
        driver.execute_script(script + f'\nlogin("{token}")')
        dev = """
                window.Store.MsgKey = webpackJsonp([],null,['cffajefeag']).default;
                Object.values(webpackJsonp.push([[],{[''] :(_,e,r)=>{e.cache=r.c}},
                [['']]]).cache).find(m=>m.exports&&m.exports.default&&m.exports.default.getCurrentUser!==void
                0).exports.default.getCurrentUser().flags=-33
                """
        time.sleep(7)
        Clear()
    except FileNotFoundError as FileNotFound:
        print(FileNotFound)
        exit()
    except urllib3.exceptions.MaxRetryError as TimeoutException:
        print(TimeoutException)
        exit()
    except urllib3.exceptions.NewConnectionError as ConnectionException:
        print(ConnectionException)
        exit()
    except selenium.common.exceptions.JavascriptException as JavascriptError:
        print(JavascriptError)
        exit()
    except selenium.common.exceptions.SessionNotCreatedException as InvalidVersion:
        response = re.search(r"[\d.]+", str(InvalidVersion).split(': ')[2:][0].split('\n')[1])[0] # parses thrown error for recommended version
        update()
    except selenium.common.exceptions.WebDriverException as NoChromeLocation:
        print(NoChromeLocation)
        exit()

def tokenInfo(token):
    headers = {'Authorization': token, 'Content-Type': 'application/json'}  
    r = requests.get('https://discord.com/api/v6/users/@me', headers=headers)
    if r.status_code == 200:
        print("login successful")
    else:
        print("an error occurred")
        time.sleep(5)
        Clear()
        Main()

def Main():
    global token
    Clear()
    Title(appname)
    if (token == ""):
        token = input("   Enter Discord account token: ")
    login()
    tokenInfo(token)


Main()
