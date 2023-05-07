# Add new authlog threats to pf

This functionless easy-to-read-is-security simple script with under a 100 lines of working code (minus comments and printing) is meant to provide the OpenBSD administrator with a tool to parse the authlog and insert threatening IP addresses into pf (packer filter) firewall to block those threats with logging and automatic pf table reload recognition to be used optionally in crontab.

Even though this is my first Python script ever, I'm approaching a security area and so I tried to employ as much logging, safety, and error checking as I could but **you are required read this whole README.md before deploying this script into production.**



## Scope:

* IPv4 addresses only

* Python 3.10 (OpenBSD default)

* ksh (OpenBSD default)

* OpenBSD 7.3 default targeted, throughly tested, production ready

  * Will probably work on FreeBSD 13.2
    
    

  
  


## Requirements:

* An authlog that does not log IP addresses that cannot be either in the whitelist or the blacklist, XOR.
  * e.g. 127.0.0.1, IPv6 Multicast, etc.
  * 0.0.0.0 is specifically excluded from parsing in the script as this does rarely happen and would be disastrous to either whitelist or blacklist

* A pf.conf with at least 2 tables, one a whitelist and one for "badhosts"/"blacklist"
  * **You must have a whitelist with all your own IP Addresses used to authenticate or you will block yourself from logging in**
  * pf understands CIDR notation and ranges but the script does not, single IP in whitelist
  * The following is a common pf.conf pattern

```sh
## Whitelist
table <whitelist> persist file "/etc/whitelist"
pass in quick from <whitelist> 


## Badhosts
table <badhosts> persist file "/etc/badhosts"
block in quick from <badhosts>
```

See also [this example](https://github.com/sinner-/ansible-freebsdvps/blob/master/roles/pf/templates/pf.conf.j2) and [this example](https://blog.thechases.com/posts/bsd/aggressive-pf-config-for-ssh-protection/).

* A new directory made by the Licensee for the script to write the log of threats added by the script for the admin to easily track for inspection and auditing
  * Assumes directory `/var/log/threats/` 



## Script Modes/Arguements:

This script has 3 modes all singular, not combinable, and **should be run in this order**:

1. backup `authlog-threats.py backup`

   1. Makes a `.backup` file of the authlog`/var/log/authlog.backup-Month-Day`, "badhosts" `/etc/badhosts.backup-Month-Day`, and whitelist `/etc/whitelist.backup-Month-Day` 
   2. Safely remove old backups with command `rm *.backup-*`
   3. I scripted this so you can also crontab the backup mode alternate to the additions schedule just in case

2. test `authlog-threats.py test`

   1. **If you do not do this you can lock yourself out of your own system!**
   2. Reads out the count of IP addresses in the existing file
   3. Does not actually write to "badhosts" file but writes entires out to stdout
   4. Manually review this list to make sure no unwanted IP addresses are in there

3. No arguments

   1. Will not backup, run tests, or reload pf, but simply write to "badhosts" file for manual
      inspection and manual reload of pf upon approval.

4. pf `authlog-threats.py pf`

   1. After writing to, for example,  `/etc/badhosts`  pf mode will reload the pf.conf persist table from file with the new entries. If there have been new insertions into that pf table other than from "badhosts" as in manually running for example `pfctl -t badhosts -T add 162.142.125.0/24` this script will flush those entires if they are not also in the `/etc/badhosts`

      1. Any runtime packet filtering will be flushed when rules are reloaded

      2. Flushing rules does not influence or impact any already existing stateful connections
   
   2. Uses the command, with example "badhosts"
   
      `pfctl -t badhosts -T replace -f /etc/badhosts`



## Customization

Licensees are allowed only to customize the shebang for proper execution in your environment and also system paths inside of the CUSTOMIZE block at script head. If you're on OpenBSD 7.3, `mkdir /var/log/threats` and match up pf.conf table persist file names below.

```sh
    ######################## CUSTOMIZE #########################
    #########################  SET PATHS #############################
    whitelist = Path("/etc/whitelist")
    authlog = Path("/var/log/authlog")
    threats_list = Path("/etc/badhosts")
    threats_added = Path("/var/log/threats/threats_added")
    ##################################################################
    ###################### CUSTOMIZE ###########################
```



## Execution:

```sh
chmod 750 authlog-threats.py
./authlog-threats.py backup
./authlog-threats.py test
./authlog-threats.py
./authlog-threats.py pf
```



## Installation:

```sh
# Crontab with no output, no email, running at 1AM nigthly
crontab -e
0 1 * * * /path/to/authlog-threats.py > /dev/null 2>&1

# Crontab with output, running at 1AM nightly
0 1 * * * /path/to/authlog-threats.py >> /home/$USER/authlog-threats-output.log

# Crontab with backups every third day
45 0 1-28/3 * * /path/to/authlog-threats.py backup
```



## Statement of Security: 

**Risk** - Low
**Impact** - Low

This script has no networking, accesses no sockets, changes nor sets permissions, only peforms one file operation per system file per mode, and does not access any system files in [full] "write" mode. It appends only to a single system file and will terminate under any error.
