from retriever.lib.repository import check_for_updates
from retriever.lib.scripts import SCRIPT_LIST

def check(url):
    print("Ansh")
    check_for_updates()

    script_list = SCRIPT_LIST()

    for script in script_list:
        x=script
        if script == url:
            print("Already in Retriever")
        else:
            print("url does not exist hence you can add the data.")