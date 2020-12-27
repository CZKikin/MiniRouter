#!/usr/bin/python3
import subprocess as sub
import sys

class Color:
    RESET = "\033[0m"
    GREEN = "\033[1;32m"
    RED = "\033[1;31m"
    YELLOW = "\033[1;33m"

def getCmd(confDict):
    if confDict["change"]:
        cmd = input(f"{Color.YELLOW}{confDict['ssid']}{Color.RESET}>!> ")
    else:
        cmd = input(f"{Color.GREEN}{confDict['ssid']}{Color.RESET}>>> ")
    return cmd.strip().lower()

def runCmd(cmd):
    if cmd in cmdsDict:
        return cmdsDict[cmd]()
    else:
        print(f"{Color.YELLOW}Unrecognized command '{cmd}'{Color.RESET}")
    return False 

def save(confDict):
    saveIfaceConf(confDict)
    dhcpWrite(confDict)
    hostapdWrite(confDict)
    confDict["change"] = False

def saveIfaceConf(confDict):
    with open("/etc/network/interfaces","w") as f:
        f.write(f"""source-directory /etc/network/interfaces.d
auto lo
iface lo inet loopback
allow-hotplug {confDict["iface"]}
iface {confDict["iface"]} inet static
    address {confDict["ip"]}
    netmask {confDict["mask"]}
""")

def calcSubnet(ip, mask):
    subnet = []
    for i,j in zip(ip, mask):
        subnet.append(int(i)&int(j))
    return subnet

def calcBroadcast(ip, mask):
    bcast = [] 
    for i,j in zip(ip, mask):
        bcast.append(int(i)|(255-int(j))) 
    return bcast

def formatIp(confDict, asWhat, ipArr):
    confDict[asWhat] = f"{ipArr[0]}.{ipArr[1]}.{ipArr[2]}.{ipArr[3]}" 

def calcRange(confDict):
    formatIp(confDict, "subnet", calcSubnet(confDict["ip"].split("."),\
            confDict["mask"].split(".")))

    formatIp(confDict, "broadcast", calcBroadcast(confDict["ip"].split("."),\
            confDict["mask"].split(".")))
    
    confDict["ip"] = confDict["subnet"][:-1]\
            + str(int(confDict["subnet"][-1]) + 1)

    confDict["rangeStart"] = confDict["ip"][:-1]\
            + str(int(confDict["ip"][-1]) + 1)

    confDict["rangeEnd"] = confDict["broadcast"][:-1]\
            + str(int(confDict["broadcast"][-1]) - 1)
    
def dhcpWrite(confDict):
    calcRange(confDict)
    with open("/etc/dhcp/dhcpd.conf", "w") as f:
        f.write(f"""ddns-update-style none;
default-lease-time 600;
max-lease-time 7200;
authoritative;
log-faility local7;
subnet {confDict["subnet"]} netmask {confDict["mask"]} {{
range {confDict["rangeStart"]} {confDict["rangeEnd"]};
option broadcast-address {confDict["broadcast"]}
option routers {confDict["ip"]};
default-lease-time 21600;
max-lease-time 43200;
option domain-name "local";
option domain-name-servers {confDict["dns1"]}, {confDict["dns2"]};
}}""")

def dhcpLoad(confDict):
    try:
        with open("/etc/dhcp/dhcpd.conf", "r")as file:
            contents = file.readlines()

            confDict["dns1"], confDict["dns2"] = contents[12]\
                    .replace("option domain-name-servers ","").replace(";","")\
                    .strip().split(",")

            confDict["subnet"], confDict["mask"] = contents[5]\
                    .replace("subnet ","").replace("netmask ","")\
                    .replace("{","").strip().split(" ")

            confDict["ip"] = confDict["subnet"][:-1] + str(int(confDict["subnet"][-1]) + 1)

            confDict["rangeStart"], confDict["rangeEnd"] = contents[6]\
                    .replace("range ","").replace(";","").strip().split(" ")

        return True
    except FileNotFoundError:
        print(f"{Color.RED}No configuration found!{Color.RESET}")
    except Exception as e:
        print(f"{Color.RED}Unexpected error in dhcpLoad.\n{e}{Color.RESET}") 
    return False

def hostapdWrite(confDict):
    with open("/etc/hostapd/hostapd.conf", "w") as f:
        f.write(f"""interface={confDict["iface"]}
ssid={confDict["ssid"]}
country_code=US
hw_mode=g
channel={confDict["channel"]}
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={confDict["passphrase"]}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
wpa_group_rekey=86400
ieee80211n=1
wme_enabled=1""")

def hostapdLoad(confDict):
    try:
        with open("/etc/hostapd/hostapd.conf","r") as file:
            contents = file.read()
            contents = contents.splitlines()
            confDict["iface"] = contents[0].replace("interface=","")
            confDict["ssid"] = contents[1].replace("ssid=","")
            confDict["passphrase"] = contents[9].replace("wpa_passphrase=","")
            confDict["channel"] = contents[4].replace("channel=","")
        return True
    except FileNotFoundError:
        print(f"{Color.RED}No configuration found!{Color.RESET}")
    except Exception as e:
        print(f"{Color.RED}Unexpected error in hostapdLoad.\n{e}{color.RESET}") 
    return False

def changeSsid(confDict):
    ssid = str(input("Enter Ssid: "))
    if len(ssid < 2) or len(ssid > 32):
        print("{Color.RED}SSID has to be at least 3 characters LONG!{Color.RESET}")
        return

    confDict["ssid"] = ssid
    confDict["change"] = True

def isIp(ipStr):
    ipStr = ipStr.split(".")
    if len(ipStr) != 4:
        return False

    try:
        for i in ipStr:
            if int(i)<0 or int(i)>255:
                return False
    except Exception as e:
        print(f"{Color.RED}Input is not a valid IP!{Color.RESET}")
        return False

    return True

def isMask(ipStr):
    if not isIp(ipStr):
        return False
    maskValues = [0,128,192,224,240,248,252,254,255]

    shouldBeZero = False
    for i in ipStr.split("."):
        if shouldBeZero:
            if int(i) != 0:
                return False

        if int(i) not in maskValues:
            return False

        if int(i) != 255:
            shouldBeZero = True

    if int(ipStr.split(".")[3]) in [254,255]:
        print(f"{Color.YELLOW}This subnet is too small!{Color.RESET}")
        return False
    return True

def changeDns(confDict):
    dns = str(input("Enter dns1 ip: "))
    if isIp(dns):
        confDict["dns1"] = dns
        confDict["change"] = True
    else:
        print("{Color.YELLOW}Entered ip is not valid!{Color.RESET}")
    
    dns = str(input(f"Enter dns2 ip, leave blank for {confDict['dns2']}: "))
    if dns != "":
        if isIp(dns):
            confDict["dns2"] = dns
        else:
            print("{Color.YELLOW}Entered ip is not valid!{Color.RESET}")

def changeSubnet(confDict):
    ip = str(input("Enter subnet ip: "))
    if not isIp(ip):
        print("{Color.YELLOW}Entered ip is not valid!{Color.RESET}")
        return;

    mask = str(input("Enter mask: "))
    if not isMask(ip):
        print("{Color.YELLOW}Entered mask is not valid!{Color.RESET}")
        return;
    
    confDict["ip"] = ip
    confDict["mask"] = mask 
    confDict["change"] = True

if __name__=="__main__":
    cmdsDict = {
        "cls": lambda: sub.call("clear", shell=True),
        "help": lambda: print(*cmdsDict),
        "exit": lambda: True,
        "reboot": lambda: sub.call("reboot",shell=True), 
        "save": lambda: save(runningConf),
        "change-ssid": lambda: changeSsid(runningConf),
        "change-dns": lambda: changeDns(runningConf),
        "change-subnet": lambda: changeSubnet(runningConf),
        "showcfg": lambda: print(runningConf),
        "showdhcpls": lambda: sub.call("cat /var/lib/dhcp/dhcpd.leases | more", shell=True)
    }

    runningConf = {"change": False}
    if not hostapdLoad(runningConf):
       sys.exit(f"{Color.RED}Failed to load AP config!{Color.RESET}") 
    if not dhcpLoad(runningConf):
       sys.exit(f"{Color.RED}Failed to load DHCP config!{Color.RESET}") 

    quitFlag = False 
    while not quitFlag:
        cmd = getCmd(runningConf)
        if cmd != "":
            quitFlag = runCmd(cmd)
