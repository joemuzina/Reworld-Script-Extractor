import os
import sys
from pathlib import Path
from shutil import copyfile, copy

PROJECT_NAME = "0G Racer"
REMOVE_EMPTY_DIRECTORIES = True

ENGINE_DIR = "C:\\Users\\" + os.getlogin() + "\\AppData\\LocalLow\\CodeView\\Reworld Engine"
PROJECT_DIR = ENGINE_DIR + "\\Scene_MyGame\\" + PROJECT_NAME
toolDir = "extractedScripts"
scriptsDir = toolDir + "\\scripts"
ignoreDir = toolDir + "\\temp"
pathDelim = "RW_SE_path"

filesIgnored = []
filesAdded = {}
filesPruned = []

def validateInstallLocation():
    os.chdir(PROJECT_DIR)
    if not os.path.isdir(toolDir):
        os.mkdir(toolDir)
    if not os.path.isdir(ignoreDir):
       os.mkdir(ignoreDir)
    if not os.path.isdir(scriptsDir):
        os.mkdir(scriptsDir)

def remove_empty_dir(path):
    try:
        os.rmdir(path)
    except OSError:
        pass

def removeEmptyDirs():
    os.chdir(ENGINE_DIR)
    for root, dirnames, filenames in os.walk(ENGINE_DIR, topdown=False):
        for dirname in dirnames:
            remove_empty_dir(os.path.realpath(os.path.join(root, dirname)))

def printAdded():
    print("--------------Files Copied--------------")
    for file in filesAdded:
        print(file)
    print("\n")

def printIgnored():
    print("--------------Files Ignored--------------")
    for file in filesIgnored:
        print(file)
    print("\n")

def printPruned():
    print("--------------Old Files Pruned--------------")
    for file in filesPruned:
        print(file)
    print("\n")

def outputResult():
    printAdded()
    printPruned()
    printIgnored()

def shouldReplaceCopy(attempt, existing):
    attempt = Path(attempt)
    existing = Path(existing)

    existing_modifyTime = existing.stat().st_mtime
    attempt_modifyTime = attempt.stat().st_mtime
                        
    return (existing_modifyTime < attempt_modifyTime)


def getLuaFiles():
    for path in Path('../../').rglob('*.lua'):
        path = str(path)
        slashPos = path.rfind("\\")
        fileName = path[slashPos:].replace("\\", '')

        try:
            copyfile(path, ignoreDir + "/" + fileName)
        except:
            pass

        tempPath = ignoreDir + "/" + fileName
        scriptPath = scriptsDir + "/" + fileName

        fileIgnored = os.system("git check-ignore " + fileName)

        if fileIgnored == 1 and not ' ' in fileName:
            with open(tempPath) as script:
                scriptText = script.read()
                pathLoc = scriptText.find(pathDelim)
                if pathLoc != -1:
                    pathStart = pathLoc + len(pathDelim) + 1
                    pathEnd = scriptText.find("\n", pathStart)

                    rwPath = scriptText[pathStart:pathEnd]
                    subDirectories = rwPath.split("/")

                    checkDir = scriptsDir + "/"

                    for dir in subDirectories:
                        checkDir = checkDir + dir
                        if not os.path.isdir(checkDir):
                            os.mkdir(checkDir)
                        checkDir = checkDir + "/"

                    checkDir = checkDir[:-1]

                    copyDir = checkDir + "/" + fileName

                    if copyDir in filesAdded.keys():
                        if not shouldReplaceCopy(path, filesAdded[copyDir]):
                            try:
                                os.remove(tempPath)
                                os.remove(path)
                            except:
                                pass
                            filesPruned.append(path)
                            continue

                    copyfile(tempPath, copyDir)
                    filesAdded[copyDir] = path
        else:
            filesIgnored.append(path)
        try:  
            os.remove(tempPath)
        except:
            pass
    try:
        os.rmdir(PROJECT_DIR + "/" + toolDir + "/temp")
    except:
        pass



validateInstallLocation()
getLuaFiles()
outputResult()

if REMOVE_EMPTY_DIRECTORIES:
    removeEmptyDirs()