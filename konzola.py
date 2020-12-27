#!/usr/bin/python3
import subprocess as sub
import sys

class Color:
    RESET = "\033[0m"
    GREEN = "\033[1;32m"
    RED = "\033[1;31m"
    YELLOW = "\033[1;33m"

cmdsDict = {
"cls": lambda: sub.call("clear", shell=True),
"help": lambda: print(*cmdsDict),
"exit": lambda: True,
"reboot": lambda: sub.call("reboot",shell=True), 
"save": save,
#"change-ssid"
#"change-dns"
#"change-ip"
"showcfg": lambda: print(runningConf),
"showdhcpls": lambda: sub.call("cat /var/lib/dhcp/dhcpd.leases | more", shell=True)
}

def getCmd(confDict):
    if confDict["change"]:
        cmd = input(f"{Color.YELLOW}{confDict['ssid']}{Color.reset}>!> ")
    else:
        cmd = input(f"{Color.GREEN}{confDict['ssid']}{Color.reset}>>> ")
    return cmd.lower()

def runCmd(cmd):
    if cmd in cmdsDict:
        return cmdsDict[cmd]()
    else:
        print(f"{Color.YELLOW}Unrecognized command{Color.RESET}")
    return False 

def save(configDict):
    saveIfaceConf(configDict)
    dhcpWrite(configDict)
    hostapdWrite(configDict)

def saveIfaceConf(configDict):
    with open("/etc/network/interfaces","w") as f:
        f.write(f"""source-directory /etc/network/interfaces.d
auto lo
iface lo inet loopback
allow-hotplug {configDict["iface"]}
iface {configDict["iface"]} inet static
    address {configDict["ip"]}
    netmask {configDict["mask"]}
""")

def dhcpWrite(configDict):
    broadcast = configDict["rangeEnd"]
    broadcast = broadcast[:-1] + str(int(broadcast[-1]) + 1)
    with open("/etc/dhcp/dhcpd.conf", "w") as f:
        f.write(f"""ddns-update-style none;
default-lease-time 600;
max-lease-time 7200;
authoritative;
log-faility local7;
subnet {configDict["subnet"]} netmask {configDict["mask"]} {{
range {configDict["rangeStart"]} {configDict["rangeEnd"]};
option broadcast-address {broadcast}
option routers {configDict["ip"]};
default-lease-time 21600;
max-lease-time 43200;
option domain-name "local";
option domain-name-servers {configDict["dns1"]}, {configDict["dns2"]};
}}""")

def dhcpLoad(configDict):
    try:
        with open("/etc/dhcp/dhcpd.conf", "r")as file:
            contents = file.readlines()
            
            #DNS IP
            contents[12] = contents[12].replace("option domain-name-servers ","").strip(" ;")
            configDict["dns1"], configDict["dns2"] = contents[12].split(",")
            configDict["dns1"] = configDict["dns1"].strip()
            configDict["dns2"] = configDict["dns2"].strip()

            #Device IP
            contents[5] = contents[5].replace("subnet ","")
            contents[5] = contents[5].replace("netmask ","")
            contents[5] = contents[5].strip("{")
            configDict["subnet"], configDict["mask"] = contents[5].split(" ")
            configDict["ip"] = str(int(configDict["subnet"][:-1]) + 1)

            #Dhcp range
            contents[6] = contents[6].replace("range ","")
            contents[6] = contents[6].strip(";")
            configDict["rangeStart"], configDict["rangeEnd"] = contents[6].split(" ")
        return True
    except FileNotFoundError:
        print(f"{Color.RED}No configuration found!{Color.RESET}")
    except Exception as e:
        print(f"{Color.RED}Unexpected error in dhcpLoad.\n{e}{color.RESET}") 
    return False

def hostapdWrite(configDict):
    with open("/etc/hostapd/hostapd.conf", "w") as f:
        f.write(f"""interface={configDict["iface"]}
ssid={configDict["ssid"]}
country_code=US
hw_mode=g
channel={configDict["channel"]}
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={configDict["passphrase"]}
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

if __name__=="__main__":
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
