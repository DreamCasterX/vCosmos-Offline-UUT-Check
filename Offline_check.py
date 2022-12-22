import os
import subprocess
import socket
import urllib.request
import psutil
import urllib.request
import webbrowser
import time


# UPDATED on 10/31/2022

# CHECK UUT REGISTRATION
register = "C:\\TestAutomation\\vCosmos-2\\registration.json"
if os.path.isfile(register) == True:
    print("\n* This UUT was registered *")
else:
    print("\n* This UUT has not been registered *")


# CHECK LAST JOB
testrun = "C:\\TestAutomation\\TestJobs"
if os.path.isdir(testrun) == True and len(os.listdir(testrun)) != 0:
    lists = os.listdir(testrun)
    folders = sorted(lists, key=lambda x:os.path.getmtime(os.path.join(testrun, x))) # Sort Parent directory list by time order
    new_folder = str(testrun + "\\" + folders[-1])

    lists2 = os.listdir(new_folder)
    folders2 = sorted(lists2, key=lambda y:os.path.getmtime(os.path.join(new_folder, y))) # Sort Child directory list by time order
    new_folder2 = str(folders[-1] + "\\" + folders2[-1])

    folder_path = str(new_folder + "\\" + folders2[-1])
    modified_time = os.path.getmtime(folder_path)
    convert_time = time.ctime(modified_time)
    print("Last test job: " + new_folder2 + " (" + convert_time + ")")
else:
    print("Last test job: N/A")    


# CHECK FIREWALL
print("\n\n(1) Fetching firewall status...")
firewall = subprocess.check_call("netsh advfirewall show allprofiles state")


# CHECK AC SLEEP AFTER
print("\n(2) Checking current AC power setting for S3...")
scheme_guid = str(subprocess.check_output(["powercfg", "-getactivescheme"]))
current_scheme_guid = scheme_guid[scheme_guid.index("GUID: "):][6:42]
# current_scheme_guid = scheme_guid[-49:-13]
# print(scheme_guid)
# print(current_scheme_guid)
sub_guid = str(subprocess.check_output(["powercfg", "-aliases"]))
sleep_guid = sub_guid[:sub_guid.index("  SUB_SLEEP")][-36:]
# print(sleep_guid)
output = str(subprocess.check_output(["powercfg", "-query", current_scheme_guid, sleep_guid]))
# print(output)
ac_output = output[output.index("STANDBYIDLE"):][202:244]
# print(ac_output)

if ac_output == "Current AC Power Setting Index: 0x00000000":
    print('>>> Sleep after on AC is set to Never\n\n')
else:
    print('>>> Sleep after on AC is NOT set to "Never"!!\n\n')


# CHECK NETWORK AND IP
google = "http://google.com"
host = "15.37.192.65"
port = 8093
print("(3) Checking UUT's network capability...")
# check Internet connection
def connect():
    try:
        urllib.request.urlopen(google) 
        return True
    except:
        return False
print(">>> Network connection is available" if connect() else ">>> No network connection!!")
time.sleep(1.5)
# connect to production site and get UUT IP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((host, port))
print(">>> IP = " + "[" + s.getsockname()[0] + "]")
s.close()


# CHECK SSHD
print("\n\n(4) Checking SSHD service state...")

# Judge by checking sshd & sshg-gui process (support both pkg v6.1.1 and v6.2.0) 
def checkIfProcessRunning(processName): # Check if there is any running process that contains the given name processName.
    for proc in psutil.process_iter():  # Iterate over the all the running process
        try:
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

if checkIfProcessRunning("sshd") or checkIfProcessRunning("sshd-gui"):
    print(">>> sshd service is running")
else:
    print(">>> sshd service is NOT running!!")


# Judge by checking "sshd.service" (no longer support pkg v6.2.0) 
"""
def get_service(name):
    service = None
    try:
        service = psutil.win_service_get(name)
        service = service.as_dict()
    except Exception as ex:
        print(str(ex))
    return service
service = get_service("sshd")
if service:
    print(">>> Service found")
    # print("service found: ", service)
else:
    print(">>> Service not found!!")

if service and service['status'] == 'running':
    print(">>> sshd service is running")
else: 
    print(">>> sshd service is NOT running!!")
"""

# CONNECT TO URL
print("\n\n(5) Opening URL to check isSshAlive & isSshEnable...")
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((host, port))
UUTip = s.getsockname()[0]
s.close()
site = "https://15.37.192.65/agent/api/scanUut?ip=" + str(UUTip)
print(">>> Connecting to " + site)
time.sleep(3)
webbrowser.get("windows-default").open_new(site)

print(input(""))



