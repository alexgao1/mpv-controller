import json
from pathlib import Path
import subprocess

PROG_CONF = "mpvControl.json"
MPV_PATH = ""

mpvMedia = []

activePage = 0

# https://stackoverflow.com/a/3744524
def getrows_byslice(seq, rowlen):
    for start in range(0, len(seq), rowlen):
        yield seq[start:start+rowlen]
        
def genArgs(args):
    #Naive slicing assuming all arguments start with -- which isn't always the case
    return ", ".join([arg[2::] for arg in args])
    
def createMediaEntry(name, url, args):
    return {"name": name, "url": url, "arguments": args}
        
def displayMediaPage(data, page):
    if len(data) < 1:
        return
    for index, entry in enumerate(data[page], start=1):
        print(f"{index} - {entry['name']}: {genArgs(entry['arguments'])}")

def checkPageLimits(direction, curPage, pages):
    if (direction == "n"):
        return (not ((curPage + 1) >= pages))
    elif (direction == "p"):
        return (not ((curPage - 1) < 0))
    return True
    
def parseConfig():
    with open(PROG_CONF, "r") as config:
        data = json.load(config)
        return data["media_links"]
  
def createConfig():
    f = open(PROG_CONF, "w")
    f.write(json.dumps({
        "media_links": []
    }, indent=4))
    f.close()

def saveConfig():
    with open(PROG_CONF, "w") as config:
        config.write(json.dumps({
            "media_links": mpvMedia
        }, indent=4))

conf = Path(PROG_CONF)
if conf.is_file():
    mpvMedia = parseConfig()
else:
    createConfig()
    
# Main
while True:
    paginatedRes = list(getrows_byslice(mpvMedia, 10))
    paginatedLen = len(paginatedRes)
    displayMediaPage(paginatedRes, activePage)
    print(f"Current Page: {activePage + 1} of {paginatedLen if paginatedLen > 0 else 1}")
    uInput = input("Make a selection, '0' to add new media, 'x' to quit, 'n' or 'p' to go to the next or previous page.")
    if uInput == "0":
        newName = input("Name of New Media?")
        newUrl = input("URL of New Media?")
        newArgs = input("MPV Arguments of New Media?")
        newArgs = newArgs.split(" ")
        mpvMedia.append(createMediaEntry(newName, newUrl, newArgs))
        saveConfig()
        continue
    elif uInput == "n":
        if (checkPageLimits(uInput, activePage, paginatedLen)):
            # True to advance pages
            activePage += 1
        continue
    elif uInput == "p":
        if (checkPageLimits(uInput, activePage, paginatedLen)):
            # True to go back a page
            activePage -= 1
        continue
    elif uInput == "x":
        break
    try:
        int(uInput)
        uInput = int(uInput) - 1
        # Launch mpv
        fullCommand = [MPV_PATH, paginatedRes[activePage][uInput]['url']] + paginatedRes[activePage][uInput]['arguments']
        #Do not capture output or provide input to not wait
        subprocess.Popen(fullCommand, stdin=None, stdout=None, stderr=None)
    except ValueError:
        continue