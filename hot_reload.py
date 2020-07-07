######################################################################
"""
Live reload allow to launch in a subprocess an app. It also detect if a tracked file is edited.
If so, the app is relaunched. To avoid any frustration, the live reload stop when the app is ended (by the user or if the app close by itself)

TODOLIT:
- Use argparse system to handle the file to launch
- setup a main function to allow to unittest in a better way

CHANGELOG:
# 0.1.0
- Creation of the live reload system
- Allow to launch a python file or a config file that give more options to the user
- Add a tag in the print to let the user know if the messages come from the live reload app or the app he is working on
"""

__author__ = "Benoit Valdes"
__version__ = "0.1.0"
__maintainer__ = "Benoit Valdes"
__status__ = "Beta"
######################################################################

from PySide2 import QtWidgets
import threading, sys, os, subprocess

def display(*argv):
    """Override the print() to add a tag before and help the user to know that
    these message don't come from the app they are testing     
    """
    print("[LIVE RELOAD]", *argv)

def tracker(trackedFiles, subprocessComThread):
    """This function track the files and end when a tracked file has been edited (last modif time has changed)
    or if the thread given as argument ended.
    It has been designed to be launched in a Thread.

    Args:
        trackedFiles (list): List of the paths of the files to track
        subprocessComThread (threading.Thread): The thread thaat contain the subprocess.comunicate().
                                                If this thread is not aline that mean that the suprocess ended
    """
    latestEditDict = {}
    for file in trackedFiles:
        latestEditDict[file] = os.path.getmtime(file)

    while True:
        broken = False
        for file in latestEditDict.keys():
            if latestEditDict[file] < os.path.getmtime(file):
                broken = True
                break
        if broken is True:
            break
        if subprocessComThread.is_alive() is False:
            break


def subprocessEnded(subprocess):
    """Hack to be able to know that the subprocess ended on his own.
    When this function end, we will know that the subprocess finish.
    It has been designed to be launched in a Thread.

    Args:
        subprocess (subprocess.Popen): The subprocess object
    """
    p.communicate()

def pythonExec():
    """Find the python executable used to run the current python instance

    Returns:
        string: The python executable path or "python"
    """
    import sys
    pythonExec = os.path.join(os.path.dirname(sys.path[1]), "python.exe")
    if os.path.exists(pythonExec):
        return pythonExec
    else:
        return "python"

if __name__ == "__main__":
    # Can be commented for debug purpose
    if sys.argv[-1] == __file__:
        display("You have to specify a file as argument")
        sys.exit()

    appFile = sys.argv[-1] # You can replace the content of the variable by the path of the file if you want to test it directely
    trackFolder = False
    trackedFiles = []
    excludeFiles = []
    # If the given file is a config file (see the documentation), the data have to the extracted from it
    if appFile.endswith("json"):
        import json
        content = json.load(open(appFile, "r"))        
        appFile = content.get('appFile') or appFile
        trackFolder = content.get('trackFolder') or trackFolder
        excludeFiles = content.get('excludeFiles') or excludeFiles
        trackedFiles += content.get('extraIncludeFiles') or []

    # fill the tracked file list (for example if trackFolder is set to True)
    if trackFolder:
        for root, dirs, files in os.walk(os.path.dirname(appFile)):
            for file in files:
                file = os.path.join(root, file).replace("\\", '/')
                trackedFiles.append(file)

    # Avoid to double track the main file to launch (if the user add it to the extraIncludeFiles for example)
    if not appFile in trackedFiles:
        trackedFiles.append(appFile)

    # remove the exclude files from the trackedFiles list:
    toRemove = []
    for file in trackedFiles:
        for excludeFile in excludeFiles:
            if excludeFile in file:
                toRemove.append(file)
    for file in toRemove:
        trackedFiles.remove(file)

    # Main loop of the live reload
    while True:
        p = subprocess.Popen(r'{} "{}"'.format(pythonExec(), appFile))

        pCommunicate = threading.Thread(target=subprocessEnded, args=[p], daemon=True)
        pCommunicate.start()


        t = threading.Thread(target=tracker, args=[trackedFiles, pCommunicate], daemon=True)
        t.start()
        t.join()

        if pCommunicate.is_alive():        
            display("A tracked file has been edited. The app has been reloaded successfully")
            os.kill(p.pid, 9)
        else:
            display("App closed by the user. The live reload is disabled")
            sys.exit()

