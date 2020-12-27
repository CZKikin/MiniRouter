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
#"config": config,
#"showcfg": showcfg,
#"ping": ping,
#"tracert": tracert,
"showdhcpls":(lambda: sub.call("cat /var/lib/dhcp/dhcpd.leases | more", shell=True))
}

def getCmd():
        cmd = input(f"{ssid}>>> ")
        return cmd.lower()

def runCmd(cmd):
    if cmd in cmdsDict:
        return cmdsDict[cmd]()
    else:
        print(f"{Color.YELLOW}Unrecognized command{Color.RESET}")
    return False 

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

def hostapdWrite(configDict):
    with open("/etc/hostapd/hostapd.conf", "w") as f:
        f.write("""interface={configDict["iface"]}
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
            confDict["iface"] = contents[1].replace("interface=","")
            confDict["ssid"] = contents[2].replace("ssid=",""),
            confDict["passphrase"] = contents[10].replace("wpa_passphrase=",""),
            confDict["channel"] = contents[5].replace("channel=","")
        return True
    except FileNotFoundError:
        print(f"{Color.RED}No configuration found!{Color.RESET}")
    except Exception as e:
        print(f"{Color.RED}Unexpected error in hostapdLoad.{color.RESET}") 
    finally:
        return False

if __name__=="__main__":
    runningConf = {}
    if not hostapdLoad(runningConf):
       sys.exit(f"{Color.RED}Failed to load AP config!{Color.RESET}") 

    quitFlag = False 
    while not quitFlag:
        cmd = getCmd()
        if cmd != "":
            quitFlag = runCmd(cmd)
