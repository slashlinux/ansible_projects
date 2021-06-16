#!/usr/bin/env python
import subprocess
import socket, subprocess,sys
import os 
from datetime import datetime

def print_menu():
	print 30 * "-", "MENU", 30 * "-"
	print "1. Create playbook-ansible-certificates file"
	print "2. Create certificates name"
	print "3. Show the playbook-ansible-certificates"
	print "4. Deploy the playbook-ansible-certificates"
	print "5. Check OpenSSL verify for the csr generated"
	print "6. Add permission centos to pem files and archive"
	print "7. SCP the csr archive"
	print "8. Show disabled certificates OCSP"
	print "9. Clear the screen"
	print "10. Exit"
	print 67 * "-"

now = datetime.now()
date_time = now.strftime("%m%d%Y")
loop=True
while loop:
	print_menu()
	try:
		choice = input("Enter your choice[1-10]:")

		if choice==1:
			region=raw_input("\t Type Region EU/China/JP/KR : ")
			env=raw_input("\t Type environment name Test/QA/PROD : ")
			server_name=raw_input("\t Type server name from your ssh config : ")

			try:

				with open('playbook-csr.yml','w') as f:
						f.write('---\n')
						f.write('- hosts: '+server_name+' \n')
						f.write('  become: yes \n')
						f.write('  become_user: ocsp \n')
						f.write('  tasks:  \n')
						f.write('   - name: Create directory  \n')
						f.write('     file: path=/tmp/my_csr state=directory \n\n')


			except KeyboardInterrupt:
       				print "You stop this "

		elif choice==2:
			token_creation_name=raw_input("\t Type crypto-token creation name eg. name_2017 : ")
			ocsp_name = raw_input("\t Type ocsp name for crypto-token generation key : ")
			cn = raw_input("\t Type CN Name for CSR : ")

			try:
				create_crypto_token = ('cryptotoken create OCSP_CryptoToken_'+token_creation_name+'_'+date_time+' ocsp true SoftCryptoToken true')
				generate_key_crypto_token =('cryptotoken generatekey OCSP_CryptoToken_'+token_creation_name+'_'+date_time+' "ocsp '+ocsp_name+ '" RSA2048')
				create_keybind=('keybind create OCSP_KeyBinding_'+token_creation_name+'_'+date_time+' OcspKeyBinding DISABLED null OCSP_CryptoToken_'+token_creation_name+'_'+date_time+' "ocsp '+ocsp_name+ '" SHA256WithRSA -nonexistingisgood=false -includesigncert=true')
				generate_keybind_csr=('keybind gencsr --name OCSP_KeyBinding_'+token_creation_name+'_'+date_time+' --subjectdn "'+cn+'"')

				with open('playbook-csr.yml','a') as f:
        				f.write('   - name: Create crypto-token for '+token_creation_name+'_'+date_time+'  \n')
        				f.write('     shell: /opt/ocsp/ejbca/bin/ejbca.sh ' +create_crypto_token+ ' >> /tmp/csrs/csr_'+token_creation_name+'.log \n\n')
        				f.write('   - name: Generate crypto-token key for '+token_creation_name+'_'+date_time+' \n')
        				f.write('     shell: /opt/ocsp/ejbca/bin/ejbca.sh ' +generate_key_crypto_token+ ' >>  /tmp/csrs/csr_'+token_creation_name+'.log \n\n')
        				f.write('   - name: Create keybind ejbc for '+token_creation_name+'_'+date_time+'  \n')
        				f.write('     shell: /opt/ocsp/ejbca/bin/ejbca.sh  '+create_keybind+ ' >>  /tmp/csrs/csr_'+token_creation_name+'.log \n\n')
        				f.write('   - name: Generate CSR keybind ejbc for '+token_creation_name+'_'+date_time+' \n')
        				f.write('     shell: /opt/ocsp/ejbca/bin/ejbca.sh  '+generate_keybind_csr+ ' -f /tmp/my_csr/csr_'+token_creation_name+'.pem >>  /tmp/csrs/csr_'+token_creation_name+'.log \n\n')
        				f.write('   - name: Show kb certificates for '+token_creation_name+'_'+date_time+'  \n')
        				f.write('     shell: \'/bin/bash -i -c   \"kb | grep -i  '+token_creation_name+'\" \' \n')
        				f.write('     register: results \n\n')
        				f.write('   - debug: msg=\"{{ results.stdout_lines | regex_replace(\'\[93m\' , \'-\') | regex_replace(\'\ED\' , \'ED-\') | regex_replace(\'\[93m\' , \'-\') }}" \n')


			except KeyboardInterrupt:
       				print "You stop this "

		elif choice==3:
			cmd = 'cat playbook-csr.yml'
			subprocess.Popen(cmd, shell=True)

		elif choice==4:
			cmd = 'ansible-playbook playbook-csr.yml'
			subprocess.Popen(cmd, shell=True)

		elif choice==5:
			try:
				with open('playbook-csr-2.yml','w') as f:
						f.write('---\n')
						f.write('- hosts: '+server_name+' \n')
						f.write('  become: yes \n')
						f.write('  become_user: ocsp \n')
						f.write('  tasks:  \n')
						f.write('   - name: Check OpenSSL for all csr.pem generated  \n')
						f.write('     shell: | \n')
						f.write('         for i in /tmp/my_csr/*.pem;do \n')
						f.write('         echo $i; \n')
						f.write('         openssl req -verify -noout -text -in $i; \n')
						f.write('         done \n')
						f.write('     args: \n')
						f.write('      executable: /bin/bash \n')
						f.write('     register: results \n')
						f.write('   - debug: msg="{{ results.stderr_lines }}" \n')
				
				
				cmd = 'ansible-playbook playbook-csr-2.yml'
				subprocess.Popen(cmd, shell=True)

			except KeyboardInterrupt:
       				print "You stop this "

		elif choice==6:
			
			try:

				with open('playbook-csr-3.yml','w') as f:
						f.write('---\n')
						f.write('- hosts: '+server_name+' \n')
						f.write('  become: yes \n')
						f.write('  become_user: root \n')
						f.write('  tasks:  \n')
						f.write('   - name: Set user centos permission for pem csr  \n')
						f.write('     shell: chown -R centos.centos /tmp/my_csr/*.pem \n\n')

						f.write('   - name: Archive csr.pem  \n')
						f.write('     shell: tar -czvf /tmp/my_csr/archive_'+region+'_'+env+'.tar.gz /tmp/my_csr/*.pem \n\n')

						f.write('   - name: Set user centos permission for csr archive \n')
						f.write('     shell: chown -R centos.centos /tmp/my_csr/*.tar.gz \n\n')

						f.write('   - name: Remove csr pem \n')
						f.write('     shell: rm -rf /tmp/my_csr/*.pem  \n')


				cmd = 'ansible-playbook playbook-csr-3.yml'
				subprocess.Popen(cmd, shell=True)

			except KeyboardInterrupt:
       				print "You stop this "


		elif choice==7:
			cmd = 'scp -r '+server_name+':/tmp/my_csr/archive_'+region+'_'+env+'.tar.gz .'
			subprocess.Popen(cmd, shell=True)

		elif choice==8:
			region=raw_input("\t Type Region EU/China/JP/KR : ")
			env=raw_input("\t Type environment name Test/QA/PROD : ")
			server_name=raw_input("\t Type server name from ssh your ssh config : ")

			try:

				with open('playbook-csr-4.yml','w') as f:
						f.write('---\n')
						f.write('- hosts: '+server_name+' \n')
						f.write('  become: yes \n')
						f.write('  become_user: ocsp \n')
						f.write('  tasks:  \n')
						f.write('   - name: Show disabled certificates  \n')
						f.write('     shell: \'/bin/bash -i -c \"kb | grep -i disabled "\' \n')
						f.write('     register: results \n')
						f.write('   - debug: msg=\"{{ results.stdout_lines | regex_replace(\'\[32m\' , \'-\')  | regex_replace(\'\[93m\' , \'-\') | regex_replace(\'\ED\' , \'ED-\') | regex_replace(\'\[93m\' , \'-\') }}" \n')

				cmd = 'ansible-playbook playbook-csr-4.yml'
				subprocess.Popen(cmd, shell=True)

			except KeyboardInterrupt:
       				print "You stop this "

		elif choice==9:
			os.system('clear')

		elif choice==10:
			cmd = 'rm -f playbook-csr*.yml'
			subprocess.Popen(cmd, shell=True)
			print "Bye .."
			loop=False
	except :
		print "try again"
