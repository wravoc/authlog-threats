#!/usr/local/bin/python3

""" Get attacking IP addresses from authlog
and add them to pf mapped file for uptake for
OpenBSD 7.3, Python 3.10.10 
Usable on FreeBSD 13.2, Unix, and Linux

Copyright (C) Quadhelion Engineering
* All Rights Reserved
* Propreitary and Confidential
Unauthorized sharing of this proprietary Software script via any 
medium is strictly prohibited. No Warranty or Liability provided.

QHE License Permissions (QHELP-OCE-NC-NAI)
Grant only to Obtain, Customize, Execute (OCE-NC-NAI):
* Obtain original copy from github.com/wravoc or quadhelion.engineering
* Customize the USER MODIFIABLE section
* Execute this script on Non-Commercial Systems via Human Implementation
"""

__author__ = "Elias Christopher Griffin"
__copyright__ = "Copyright 2023, Quadhelion Engineering"
__url__ = "https://www.quadhelion.engineering/qhelp-license.html"
__license__ = "QHELP-OCE-NC-NAI"
__version__ = "1.0"
__date__ = "2023/05/05"
__email__ = "elias@quadhelion.engineering"
__status__ = "Production"



from pathlib import Path
from datetime import datetime, date
import os, re, time, sys, subprocess

if __name__ == "__main__":

    ######################## CUSTOMIZE #########################
    #########################  SET PATHS #############################
    whitelist = Path("/etc/whitelist")
    authlog = Path("/var/log/authlog")
    threats_list = Path("/etc/bruteforce")
    threats_added = Path("/var/log/threats/threats_added")
    ##################################################################
    ###################### CUSTOMIZE ###########################


    ## script arguements
    #  test, pf, or backup

    ## Mode "test"
    #  Print to stdout without writing to /etc/threats
    #  authlog_threats.py test


    ## Mode  "pf"
    #  Add new threats to file and reload pf with them
    #  authlog_threats.py pf
    pf_reload_rules_cmd = "pfctl -t " + threats_list.name + " -T replace -f " + str(threats_list)
    pf_stats_cmd = "pfctl -vsi"


    ## Mode "backup"
    #  Nothing but backup copies of whitelist, threatlist, and authlog


    ## Script arguements 
    sysarg = sys.argv


    if "test" in sysarg:
        pf_mode, test_mode, backup_mode = False, True, False
        print(f"\n*********************\033[38;5;75m Test Mode \033[0;0m***********************")
        print(f"\033[38;5;208m No writes \033[0;0m")
        print(f"*******************************************************\n")
    elif "pf" in sysarg:
        pf_mode, test_mode, backup_mode = True, False, False
        print(f"\n********************\033[38;5;75m pf Mode \033[0;0m*************************")
        print(f"\033[38;5;208m {pf_reload_rules_cmd} \033[0;0m")
        print(f"*******************************************************\n")
    elif "backup" in sysarg:
        test_mode, backup_mode = False, True
        print(f"\n********************\033[38;5;75m Backup Mode \033[0;0m**********************")
        print(f"Backing up whitelist, threatlist, and authlog")
        print(f"*******************************************************\n")
    else:
        pf_mode, test_mode, backup_mode = False, False, False
        print(f"\n********************\033[38;5;75m Base Mode \033[0;0m**********************")
        print(f"Available modes \033[38;5;208mtest\033[0;0m or \033[38;5;208mbackup\033[0;0m or \033[38;5;208mpf\033[0;0m")
        print(f"*******************************************************\n")


    ## Backup mode ## copies whitelist, threatlist, and authlog
    if backup_mode:
        backup_date = date.today()
        backup_suffix = ".backup" + "-" + backup_date.strftime("%B") + "-" + backup_date.strftime("%d")
        whitelist_backup = whitelist.with_suffix(backup_suffix)
        threatslist_backup = threats_list.with_suffix(backup_suffix)
        authlog_backup = authlog.with_suffix(backup_suffix)
        try:
            whitelist_backup.write_bytes(whitelist.read_bytes())
            threatslist_backup.write_bytes(threats_list.read_bytes())
            authlog_backup.write_bytes(authlog.read_bytes())
        except FileNotFoundError as e:
            error_path = Path(e.filename)
            print(f"\n******************\033[38;5;1m File Not Found \033[0;0m*********************")
            print(f"Filename: {error_path.name}")
            print(f"Directories used: {error_path.parts}\n")
            print("*******************************************************\n")
        except PermissionError as e:
            print(f"\n******************\033[38;5;1m Permissions \033[0;0m************************\n")
            print(f"Insufficient permissions {e}")
            print(f"{os.stat(threats_added)}{os.linesep}")
            print(f"*******************************************************\n")
        except OSError as e:
            print(f"\n********************\033[38;5;1m Locked \033[0;0m**************************\n")
            print(f"Perhaps file is busy, locked, process blocked, or raced:\n") 
            print(f"{e}")
            print(f"*******************************************************\n")
        else:
            print(f"\n*********************\033[38;5;76m Success \033[0;0m*************************")
            print(f"Backups created:\n")
            print(f"{whitelist_backup}")
            print(f"{threatslist_backup}")
            print(f"{authlog_backup}")
            print(f"*******************************************************\n")
            sys.exit()


    ## Check for directory to write script logs to
    script_log_directory = threats_added.parent
    if not script_log_directory.exists():
        print(f"\n****************\033[38;5;1m No directory exists \033[0;0m******************")
        print(f"At {threats_added.parent} to create log")
        print(f"*******************************************************\n")
        sys.exit()
    else:
        print(f"\n*******************************************************")
        print(f"Log directory: \033[38;5;75m{script_log_directory}\033[0;0m ")
        print(f"*******************************************************\n")
        

    ## Allow user to see log directory as the
    ## IP Address list to stdout will send this output off-screen
    time.sleep(0.7)


    ## Handle system files
    try:
        whitelist_content = whitelist.read_text(encoding="utf-8")
        authlog_content = authlog.read_text(encoding="utf-8")
        threat = open(threats_list, "a")
        threat_content = threats_list.read_text(encoding="utf-8")
        threats_added.touch()
    except FileNotFoundError as e:
        error_path = Path(e.filename)
        print(f"\n*******************\033[38;5;1m File Not Found \033[0;0m********************")
        print(f"Filename: {error_path.name}")
        print(f"Directories used: {error_path.parts}\n")
        print("*******************************************************\n")
    except PermissionError as e:
        print(f"\n******************\033[38;5;1m Permissions \033[0;0m************************\n")
        print(f"Permission to read/append {e}")
        print(f"{os.stat(authlog)}{os.linesep}")
        print(f"{os.stat(threats_list)}{os.linesep}")
        print(f"{os.stat(threats_added)}{os.linesep}")
        print(f"*******************************************************\n")
    else:
        print(
            f"{os.linesep}*********************\033[38;5;75m Running \033[0;0m*************************{os.linesep}"
            f"{Path.cwd()}/authlog-threats.py{os.linesep}"
            f"*******************************************************{os.linesep}"
        )
    finally:
        print(f"\n*******************\033[38;5;75m Files Mapped \033[0;0m*********************")
        print(f"Loaded system files for read/append\n")
        print(f"{authlog}")
        print(f"{threats_list}")
        print(f"*******************************************************\n")


    ## Allow user to see script status as the
    ## IP Address list to stdout will send this output off-screen
    time.sleep(0.7)
    

    ## Initialize loop elements
    ## Blackhole IP address 198.51.100.0/24 https://datatracker.ietf.org/doc/html/rfc5737
    ip_set = [] 
    ip_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    # Loop through each line, collecting IP Addresses not already present
    for line in authlog_content.splitlines():  
        logline = re.search(ip_pattern, line)
        if logline is not None:
            if (logline.group(0) not in threat_content) and (logline.group(0) not in whitelist_content) and (logline.group(0) != "0.0.0.0"):
                if test_mode:
                    ip_set.append(logline.group())
                else:
                    ip_set.append(logline.group())
                    threat.writelines(logline.group() + "\n")
            else:
                continue
        else:
            continue
            

    ## Remove duplicates, count new additions, format single column	list
    ip_set = [*set(ip_set)]
    threat_count = len(ip_set)
    ip_string = "\n".join([str(elem) for elem in ip_set])


    ## Count out threats in existing file during test
    if test_mode: 
        try:
            threat_count_reader = open(threats_list, "r")
            threat_count_original = len(threat_count_reader.readlines())
        except OSError as e:
            print(f"\n********************\033[38;5;1m Locked \033[0;0m**************************\n")
            print(f"Perhaps file is busy, locked, process blocked, or raced:\n") 
            print(f"{e}")
            print(f"*******************************************************\n")
        else:
            print(f"\n*********************\033[38;5;75m Catalog \033[0;0m*************************")
            print(f"\033[38;5;208m{threat_count_original}\033[0;0m existing threats counted")
            print(f"*******************************************************\n")


    ## Create log file of discovered IP addresses in seperate timestamped file
    try:
        timestamp = datetime.now().isoformat()
        threats_timestamp = threats_added.name + "-" + timestamp
        threats_added_timestamped = threats_added.with_name(threats_timestamp)
        threats_added.replace(threats_added_timestamped)
        threats_added_timestamped.write_text(ip_string)
    ## Reload packet filter rules with new threats if command given
        if pf_mode:
            pf_reloaded = subprocess.run([pf_reload_rules_cmd], shell=True, timeout=1.7)
    except subprocess.CalledProcessError as e:
        print(f"\n*********************\033[38;5;1m Shell Error \033[0;0m*********************")
        print(f"Command {e.args[1]} failed")
        print("*******************************************************\n")
    except FileNotFoundError as e:
        error_path = Path(e.filename)
        print(f"\n******************\033[38;5;1m File Not Found \033[0;0m*********************")
        print(f"Filename: {error_path.name}")
        print(f"Directories used: {error_path.parts}\n")
        print("*******************************************************\n")
    except PermissionError as e:
        print(f"\n******************\033[38;5;1m Permissions \033[0;0m************************\n")
        print(f"Insufficient permissions {e}")
        print(f"{os.stat(threats_added)}{os.linesep}")
        print(f"*******************************************************\n")
    except OSError as e:
        print(f"\n********************\033[38;5;1m Locked \033[0;0m**************************\n")
        print(f"Perhaps file is busy, locked, process blocked, or raced:\n") 
        print(f"{e}")
        print(f"*******************************************************\n")
    else:
        print(f"\n*********************\033[38;5;76m Success \033[0;0m*************************")
        print(f"\033[38;5;208mThreats:\033[0;0m{os.linesep}{os.linesep.join(map(str, ip_set))}\n\n")
        print(f"{threat_count} new threats added")
        print(f"Log at {threats_added_timestamped.name}")
        print(f"*******************************************************\n")
        print(f"*******************************************************\n")
        if pf_mode and pf_reloaded.returncode == 0:
            print(f"\n*******************\033[38;5;75m pf reloaded \033[0;0m*********************")
            print(f"{subprocess.run([pf_stats_cmd], shell=True, timeout=1.7)}")
            print(f"*******************************************************\n")
            print(f"*******************************************************\n")
        