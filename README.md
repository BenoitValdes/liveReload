Live reload allow to launch in a subprocess an app. It also detect if a tracked file is edited.
If so, the app is relaunched. To avoid any frustration, the live reload stop when the app is ended (by the user or if the app close by itself)

# TODOLIT:
- Use argparse system to handle the file to launch
- setup a main function to allow to unittest in a better way

# CHANGELOG:
## 0.1.0
- Creation of the live reload system
- Allow to launch a python file or a config file that give more options to the user
- Add a tag in the print to let the user know if the messages come from the live reload app or the app he is working on
