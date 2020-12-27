#!/usr/bin/python3
#Ať se na to dívá kdokoli, plánuju to předělat celý, je to hrůza a děs
#Novejší verze bude dostupná na https://github.com/CZKikin/MiniRouterProject

def load_dns():
    return_variables=[]
    with open("/etc/dhcp/dhcpd.conf", "r")as file:
        contents = file.read()
        contents = contents.splitlines()


        contents[12] = contents[12].replace("option domain-name-servers ","")
        contents[12] = contents[12].strip(" ;")
        dnsf, dnss = contents[12].split(",")
        dnss = dnss.strip(" ")
        return_variables.append(dnsf)
        return_variables.append(dnss)

        #ip and mask
        contents[5] = contents[5].replace("subnet ","")
        contents[5] = contents[5].replace("netmask ","")
        contents[5] = contents[5].strip("{")
        subnet, mask = contents[5].split(" ")
        return_variables.append(subnet)
        return_variables.append(mask)

        #starting & ending_range
        contents[6] = contents[6].replace("range ","")
        contents[6] = contents[6].strip(";")
        starting, ending = contents[6].split(" ")
        return_variables.append(starting)
        return_variables.append(ending)

        #Broadcast
        contents[7]=contents[7].replace("option broadcast-address ","")
        return_variables.append(contents[7].strip(";"))

        #router ip
        contents[8] = contents[8].replace("option routers ","")
        return_variables.append(contents[9].strip(";"))

        return return_variables

def dns():   #TODO: Merge this with enter_ip()
    entering_dns = True
    while entering_dns:
        try:
            dnsf = input("Enter first dns ip: ")
            dnss = input("Enter second dns ip: ")
            dnsf = dnsf.strip(" ")
            dnss = dnss.strip(" ")
            first, second, third, fourth = dnsf.split(".")
            firsta, seconda, thirda, fourtha = dnss.split(".")

            if (int(first) not in range(0, 256) 
                or int(second) not in range(0, 256)
                or int(third) not in range(0, 256)
                or int(fourth) not in range(0, 256)
               ):
                print("\033[1;31;40mFirst ip is invalid\033[1;37;40m")
                continue
            else:
                print("First ip is OK!")

            if (int(firsta) not in range(0, 256) 
                or int(seconda) not in range(0, 256) 
                or int(thirda) not in range(0, 256) 
                or int(fourtha) not in range(0, 256)
               ):
                print("\033[1;31;40mSecond ip is invalid\033[1;37;40m")
            else:
                print("Second ip is OK!")
                entering_dns = False

        except Exception as err:
            print("\033[1;31;40m{}\033[1;37;40m".format(err))



    return dnsf, dnss

def save_wlan(ip,mask):
    print("SAVE WLAN IS ON TEST :83") 
    with open("/etc/network/interfaces","w") as inter:
        inter_str = "source-directory /etc/network/interfaces.d\nauto "\
"lo\niface lo inet loopback\nallow-hotplug wlan0\niface "\
"wlan0 inet static\n    address "+ip+"\n    "\
"netmask "+mask+"\n"
        inter.write(inter_str)
        print("\033[1;33;40mdhcp saved, to apply changes "
              "restart the device\033[1;37;40m")

def save_dhcp(subnet = None, broadcast=None, mask=None,
                  starting_range=None, ending_range=None,
                  router_ip=None, dns_conf=False
             ):
    global global_dnsf
    global global_dnss
    global global_subnet
    global global_mask
    global global_starting_range
    global global_ending_range
    global global_router_ip
    global global_broadcast

    if dns_conf == False:
        dnsf = global_dnsf
        dnss = global_dnss
    elif dns_conf:
        dnsf, dnss = dns()
        subnet = global_subnet
        broadcast = global_broadcast
        mask = global_mask
        starting_range = global_starting_range
        ending_range = global_ending_range
        router_ip = global_router_ip
    with open("/etc/dhcp/dhcpd.conf", "w")as dhcpd:
        dhcpd_conf = "ddns-update-style none;\ndefault-lease-time 600;"\
"\nmax-lease-time 7200;\nauthoritative;\nlog-facility "\
"local7;\nsubnet "+ subnet +" netmask "+ mask + "{\nrange"\
" "+starting_range+" "+ending_range+";\noption broadcast-a"\
"ddress "+broadcast+";\noption routers "+ router_ip + ";\n"\
"default-lease-time 21600;\nmax-lease-time 43200;\noption "\
"domain-name \"local\";\noption domain-name-servers "\
+ dnsf +", " + dnss +";\n}"
        dhcpd.write(dhcpd_conf)

    loaded_data = load_dns()
    global_subnet = loaded_data[0]
    global_mask = loaded_data[1]
    global_starting_range = loaded_data[2]
    global_ending_range = loaded_data[3]
    global_broadcast = loaded_data[4]
    global_router_ip = loaded_data[5]

def enter_ip():
    entering_subnet = True
    while entering_subnet:
                try:
                    subnet = input("Enter subnet: ")  #Entering IP which is stripped to 4 pieces
                    subnet = subnet.strip(" ")
                    first, second, third, fourth = subnet.split(".")
                    first, second, third, fourth = int(first), int(
                        second), int(third), int(fourth)
                except:
                    print("\033[1;31;40mEnter subnet IP!!! eg.: "\
"192.168.1.0\033[1;37;40m")
                try:
                    if (first not in range(0, 256) 
      or second not in range(0, 256) 
      or third not in range(0, 256) 
                        or fourth not in range(0, 256)
                       ):
                        print("\033[1;31;40mInvalid IP\033[1;37;40m")
                    else:
                        entering_subnet = False
                except:
                    print("\033[1;31;40mCannot calculate ip!!\033[1;37;40m")

    return first, second, third, fourth 

def enter_mask():
    entering_mask = True
    mask_octets = [0, 128, 192, 224, 240, 248, 252, 254, 255]
    while entering_mask:
        try:
            mask = input("Enter mask: ")
            mask = mask.strip(" ")
            first_m, second_m, third_m, fourth_m = mask.split(".");
            first_m, second_m, third_m, fourth_m = int(first_m), int(second_m),\
 int(third_m), int(fourth_m)
            if (first_m not in mask_octets or second_m not in mask_octets 
                or third_m not in mask_octets or fourth_m not in mask_octets
               ):
                print("\033[1;31;40mInvalid mask!!!\033[1;37;40m")
                continue
            else:
                if first_m != 255:
                    if second_m != 0 and third_m != 0 and fourth_m !=0:
                        print("\033[1;33;40mYour fist octet isn't full, "\
"setting your mask to {}.0.0.0\033[1;37;40m".format(first_m))
                        second_m, third_m, fourth_m = 0, 0, 0
                        mask = clearstr(mask)
                        mask += first_m + "." + second_m + "." + third_m +\
"." + fourth_m
                        entering_mask = False
                    elif second_m != 255:
                        if third_m != 0 and fourth_m !=0:
                            print("\033[1;33;40mYour second octet isn't full, "\
"setting your mask to {}.{}.0.0\033[1;37;40m".format(first_m,second_m))
                            third_m, fourth_m = 0, 0
                            mask = clearstr(mask)
                            mask += first_m + "." + second_m + "." + third_m +\
"." + fourth_m
                            entering_mask = False
                    elif third_m != 255:
                        if fourth_m !=0:
                            print("\033[1;33;40mYour third octet isn't full, "\
"setting your mask to {}.{}.{}.0\033[1;37;40m".format(first_m,second_m,third_m))
                            fourth_m = 0
                            mask = clearstr(mask)
                            mask += first_m + "." + second_m + "." + third_m +\
"." + fourth_m
                            entering_mask = False
                    else:
                        entering_mask = False
        except ValueError:
            print("\033[1;31;40mYou have entered bad ip format!\033[1;37;40m")
        except TypeError:
            print("\033[1;31;40mEnter numbers!\033[1;37;40m")
        except Exception as err_msg:
            print("\033[1;31;40m{}!!\033[1;37;40m".format(err_msg))

    return first_m, second_m, third_m, fourth_m

def dhcp_config():   #TODO: Separate this to more functions
    dhcp_config_change_subnet_run = True
    while dhcp_config_change_subnet_run:
        first, second, third, fourth = enter_ip() 
        first_m, second_m, third_m, fourth_m = enter_mask() 
        
        subnet_calculation = []; subnet_calculation.append(first&first_m)
        subnet_calculation.append(second&second_m)
        subnet_calculation.append(third&third_m)
        subnet_calculation.append(fourth&fourth_m)

        not_negated_mask = []; not_negated_mask.append(first_m)
        not_negated_mask.append(second_m), not_negated_mask.append(third_m),\
not_negated_mask.append(fourth_m)
        not_negated_mask = ip_list_to_str(not_negated_mask)

        #negation of mask
        first_m = 255-first_m; second_m = 255 - second_m
        third_m = 255 - third_m; fourth_m = 255 - fourth_m
        broadcast = []; broadcast.append(subnet_calculation[0]|first_m)
        broadcast.append(subnet_calculation[1]|second_m)
        broadcast.append(subnet_calculation[2]|third_m)
        broadcast.append(subnet_calculation[3]|fourth_m)
        broadcast_str = ip_list_to_str(broadcast)

        #setting end range ip
        ending_range = broadcast; ending_range[3] -= 2
        ending_range_str = ip_list_to_str(ending_range)

        #converting list to str
        subnet_control = ip_list_to_str(subnet_calculation)

        #ip of router
        router_ip = ending_range; router_ip[3] += 1
        router_ip_str = ip_list_to_str(router_ip)

        #setting starting ip
        starting_range = subnet_calculation
        starting_range[3] += 1
        starting_range_str = ip_list_to_str(starting_range)

        if subnet_control != subnet:
            print("\033[1;33;40mCalculation resulted in network {}"\
" setting subnet to this network!\033[1;37;40m".format(subnet_control))
            dhcp_config_change_subnet_run = False
            print("Writing down Subnet {},Range start {}, Range end {}, "\
"Broadcast {}, Ip of router {}".format(subnet_control,starting_range_str,
ending_range_str,broadcast_str,router_ip_str))
            save_dhcp(subnet_control, broadcast_str, mask, starting_range_str, 
ending_range_str, router_ip_str)

            #dhcp config saved
            save_wlan(router_ip_str, not_negated_mask)
        elif subnet_control == subnet:
            dhcp_config_change_subnet_run = False
            print("Writing down Subnet {},Range start {}, Range end {},"\
"Broadcast {}, Ip of router {}".format(subnet,starting_range_str,
ending_range_str,broadcast_str,router_ip_str))
            save_dhcp(subnet, broadcast_str, mask, starting_range_str,
ending_range_str, router_ip_str)

            #dhcp config saved
            save_wlan(router_ip_str,not_negated_mask)
        else:
            print("Error at calculating dhcp subnet")

def check_channels():
    free = []
    print("""\n-----------------------------
Looking for free channels...
-----------------------------""")
    sub.call("sudo iwlist wlan0 scan | grep Channel: > chan.txt",shell=True)
    atleast = True
    with open("chan.txt","r")as file:
        chan = file.readlines()
        a={"1":0, "2":0, "3":0, "4":0, "5":0, "6":0, "7":0, "8":0, "9":0,
"10":0, "11":0, "12":0, "13":0}
        for i in chan:
            i = i.strip()
            i = i.replace("Channel:","")
            for x in range(1,14):
                if x == int(i):
                    a[i]+=1
        for i in a:
            if a[i]==0:
                free.append(int(i))
                atleast = False
        print("\033[1;33;40mFree channels: "\
"{}\033[1;37;40m\n".format(sorted(free)))
        if atleast:
            print("\033[1;31;40mNo free channels, here is list of channels"\
" and number of hotspots.\n{}\033[1;37;40m".format(a))

def save_hostapd(ssid,channel,wpa_passphrase):
    try:   #TODO: Use str.format method to save files
        with open("/etc/hostapd/hostapd.conf","w") as file:
            hostapd_config="interface=wlan0\n"+"#driver=rtl871xdrv\n"+"ssid="+\
str(ssid)+"\n"+"country_code=US\n"+"hw_mode=g\n"+"channel="+\
str(channel)+"\n"+"macaddr_acl=0\n"+"auth_algs=1\n"+"ignore_broadcast_ssid=0\n"\
+"wpa=2"+"\n"+"wpa_passphrase="+str(wpa_passphrase)+"\n"+\
"wpa_key_mgmt=WPA-PSK\n"+"wpa_pairwise=CCMP\n"+"wpa_group_rekey=86400\n"+\
"ieee80211n=1\n"+"wme_enabled=1"
            file.write(hostapd_config)
    except Exception as err:
        print(err)
    print("Wlan conf was saved, to apply changes restart the device")

def load_hostapd():
    with open("/etc/hostapd/hostapd.conf","r") as file:
        contents = file.read()
        contents = contents.splitlines()
        ssid = contents[2].replace("ssid=","")
        passphrase = contents[10].replace("wpa_passphrase=","")
        channel = contents[5].replace("channel=","")
    return ssid, passphrase, channel

def change_ssid():
    ch_ssid_run = True
    while ch_ssid_run:
        ssid = input("ssid: ")
    if ssid == "" or ssid == " " or len(ssid)<3:
        print("Ssid has to be at least 3 characters long!!!")
    else:
        return ssid

def wlan_config():   #TODO: Separate this to more functions
    global channel
    global passphrase
    global ssid
    wlan_config_run = True
    cmds = ["ssid","passphrase","channel","help","exit","save","cls"]
    change_made=False
    while wlan_config_run:
        cmd = inputline(ssid, "config>wlan")
        if cmd in cmds:
            if cmd == "cls":
                cls()
            if cmd == "save":
                save_hostapd(ssid,channel,passphrase)
                change_made = False
            if cmd == "exit":
                while change_made:
                    print("\033[1;33;40mYou have unsaved changes.\033[1;37;40m")
                    let = input("Do yo want to exit without saving?[y/n]: ")
                    if let == "y":
                        change_made=False
                        wlan_config_run = False
                    elif let == "n":
                        save_hostapd(ssid,channel,passphrase)
                        change_made=False
                    else:
                        print("y\033[1;33;40mY/n !!\033[1;37;40mY")
                else:
                    wlan_config_run = False
            if cmd == "help":
                print(*cmds)
            if cmd == "ssid":
                ssid = change_ssid()
                change_made=True
            if cmd == "passphrase":
                change_in_progress = True
                while change_in_progress:
                    passphrase = getp.getpass("Enter your password: ")
                    passphrase_check = getp.getpass("Re-enter your password: ")
                    if passphrase != passphrase_check or len(passphrase)<8:
                        print("\033[1;31;40mPassword is too short (less than 8"\
" characters) or passwords do not match\033[1;37;40m")
                    else:
                        change_in_progress = False
                        change_made=True

            if cmd == "channel":
                channel_change = True
                while channel_change:
                    check_channels()
                    try:
                        channel = int(input("What channel you want to use?"\
" 1-11: "))
                        if channel <1 or channel >11:
                            print("\033[1;31;40mEnter a nuber from 1 to 11"\
" (AP mode does not support channels 12 and 13)!!! \033[1;37;40m")
                        else:
                            channel_change = False
                            change_made=True
                    except:
                        print("\033[1;31;40mEnter a nummber from 1 to "\
"11!!! \033[1;37;40m")
        elif cmd == "" or cmd == " ":
            pass
        else:
            print("\033[1;33;40mUnrecognized command \033[1;37;40m")

def completer(text, state):
    options = [i for i in commands if i.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

def tracert():
    ip = input("Enter host: ")
    try:
        sub.call("traceroute {} -m 20".format(ip),shell=True)
    except Exception as err:
        print(err)

def ping():
    ip = input("Enter host: ")
    try:
        sub.call("ping {} -c 4".format(ip),shell=True)
    except Exception as err:
        print(err)

def showcfg():
        with open("/etc/hostapd/hostapd.conf","r") as file:
            contents = file.read()
            contents = contents.splitlines()
            channel_sh, pass_sh = contents[5], contents[10]
        with open("/etc/dhcp/dhcpd.conf", "r")as file:
            contents = file.read()
            contents = contents.splitlines()
            contents[8] = contents[8].replace("option routers","router ip: ")
            contents[12] = contents[12].replace("option domain-name-servers ",
"")
            print("""\033[1;37;40m
--------------------------------------------
{}\n{}\n{}\n{}\n{}\n{}
--------------------------------------------\n\033[1;37;40m""".format(
channel_sh, pass_sh, contents[6].strip("{"),contents[7].strip(";"),
contents[8].strip(" ;"),contents[12].strip(" ;")))

def clearstr(string):
    for i in string:
        string = string.strip(i)
    return string

def ip_list_to_str(list):
    turn=0
    ret_str = ""
    for i in list:
        if turn != 3:
            ret_str += str(i) + "."
            turn += 1
        else:
            ret_str += str(i)
    return ret_str

def inputline(name, func = False):
    ok = False
    while not ok:
        if not func:
            try:
                cmd = input(name + ">")
                ok = True
                return cmd.lower()
            except UnicodeError:
                print("\033[1;31;40mYou have propably typed UTF-8 character, "
                      "that this console cannot encode/decode!\033[1;37;40m")
            except Exception as err:
                print(err)
        else:
            try:
                cmd = input(name + ">" + func + "#")
                ok = True
                return cmd.lower()
            except Exception as err:
                print(err)

def config():
    config_run = True
    cmds={
    "wlan": wlan_config,
    "passwd": lambda: sub.call("passwd minirouter",shell=True),
    "dhcp": dhcp_config,
    "dns": lambda: save_dhcp(dns_conf=True),
    "help": lambda: print(*cmds),   #TODO: Change some commands to be global and use some global dictionary
    "cls": cls}

    while config_run:
        cmd = inputline(ssid, "config")
        config_run = run_command(cmd, cmds)

def cls():
  sub.call("clear", shell=True)

def run_command(command, command_dict):
    if command in command_dict:
        command_dict[command]()
    elif command == "":
        pass
    elif command == "exit":
        return False
    else:
        print("\033[1;33;40mUnrecognized command \033[1;37;40m")
    return True

import subprocess as sub, getpass as getp, sys, time as t, readline
print("\033[1;32;40m ")
cls()
print("""
                    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                    @                                      @
                    @     |\\\\  /||  ||  |\\\\    ||  ||      @
                    @     ||\\\\//||  ||  ||\\\\   ||  ||      @
                    @     ||    || ROUTER  \\\\  ||  ||      @
                    @     ||    ||  ||  ||  \\\\ ||  ||      @
                    @     ||    ||  ||  ||   \\\\||  ||      @
                    @                                      @
                    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

\033[1;37;40m""")

cmds = {
"config": config,
"cls": cls,
"help": (lambda: print(*cmds)),
"reboot": (lambda: sub.call("sudo reboot",shell=True)), 
"showcfg": showcfg,
"ping": ping,
"tracert": tracert,
"showdhcpls":(lambda: sub.call("cat /var/lib/dhcp/dhcpd.leases | more", 
shell=True))}

print("TESTING.... TESTING ... TESTING ::::")
ssid="TESTING - REMOVE ALL TESTING LINES"

run = True
#readline.parse_and_bind("tab: complete")
#readline.set_completer(completer)
#commands = ["config","cls","help","reboot","showcfg","ping","tracert","dhcp",
#            "dns","wlan","ssid","passphrase","channel","save",
#            "showdhcpls","passwd"]
#ssid, passphrase, channel= load_hostapd()

loaded_data = load_dns()
global_subnet = loaded_data[0]
global_mask = loaded_data[1]
global_starting_range = loaded_data[2]
global_ending_range = loaded_data[3]
global_broadcast = loaded_data[4]
global_router_ip = loaded_data[5]

while run:
    cmd = inputline(ssid)
    run = run_command(cmd, cmds)
print("\033[0m")
cls()