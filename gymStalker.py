#!/usr/bin/env python3

import requests, sys, signal, time, colorama, os, re, random, pdb
from bs4 import BeautifulSoup
from colorama import *

init()

def sig_handler(sig, frame):
	print(Fore.RED + "\n\n[!] Saliendo...\n")
	sys.exit(0)

def cleanScreen():
	if sys.platform.startswith('win'):
		os.system('cls')
	else:
		os.system('clear')

signal.signal(signal.SIGINT, sig_handler)

#Variables globales

login_url = "https://intranet.upv.es/pls/soalu/est_aute.intraalucomp"
sports_url = "https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?p_campus=V&p_tipoact=6690&p_codacti=21229&p_vista=intranet&p_idioma=c&p_solo_matricula_sn=&p_anc=filtro_actividad"

def booking(urlFreeGroups,freeGroups,session,number) :
	for url_group, group in zip(urlFreeGroups,freeGroups):
		link_group = f"https://intranet.upv.es/pls/soalu/{url_group}"
		session.get(link_group)
		with open('groups.txt', 'r') as file:
			lines = file.readlines()
		line = lines[number].replace(group,"")
		lines[number]=line
		with open('groups.txt','w') as file:
			file.writelines(lines)

def foundFreeGroups(session,groups) :
	result = session.get(sports_url)
	soup = BeautifulSoup(result.text, 'html.parser')
	urlFreeGroups=[]
	freeGroups=[]
	links = soup.find_all('a', href=True)
	for link in links:
		if "p_codgrupo_mat" in link.get('href') :
			for group in groups:
				if f"MUS0{group}" in link.get_text() :
					urlFreeGroup = link.get('href')
					urlFreeGroups.append(urlFreeGroup)
					freeGroups.append(group)
	return urlFreeGroups,freeGroups

def login(dni,password):
	session = requests.Session()
	payload = { 'dni' : dni, 'clau' : password }
	result = session.post(login_url, data=payload, timeout=5)
	return result.text,session

#MAIN

if __name__ == "__main__":
	with open("credentials.txt", 'r') as credsFile:
		credsLines = credsFile.readlines()
	with open("groups.txt", 'r') as groupsFile:
		groupsLines = groupsFile.readlines()
	accounts=[]
	number=0
	if len(groupsLines) == 0  or groupsLines[0] == " " or len(credsLines) == 0  or credsLines[0] == " " :
		cleanScreen()
		print(Fore.YELLOW + f"\n[!] Porfavor lee el README antes de ejecutar el programa{Style.RESET_ALL}")
		sig_handler(None,None)
	for credLine,groupLine in zip(credsLines,groupsLines):
		groups= groupLine.strip().split(' ')
		parts = credLine.split(' ')
		name = parts[0].strip()
		dni = parts[1].strip()
		password = parts[2].strip()
		result,session=login(dni,password)
		if "Alta socios de deportes" in result :
			print(Fore.GREEN + f"[+] Login Correcto para {name}")
			account=(number,name,dni,password,session,groups)
			accounts.append(account)
			number+=1
			time.sleep(1)
		else:
			print(Fore.RED + f"\n[!] Login Incorrecto para {name}")
			sig_handler(None, None)

#EN ESCUCHA
while True:
	cleanScreen()
	print(f"{Fore.YELLOW}\n[+] Comprobando ... {Style.RESET_ALL}\n")
	time.sleep(1)
	for account in accounts:
		if len(account[5]) != 0 :
			urlFreeGroups,freeGroups = foundFreeGroups(*account[-2:])
			if len(urlFreeGroups) != 0 :
				booking(urlFreeGroups,freeGroups,account[4],account[0])
				for freeGroup in freeGroups:
					account[5].remove(freeGroup)
	cleanScreen()
	finished=0
	for account in accounts:
		if len(account[5]) == 0 :
			print(Fore.GREEN + f"\n[⋆] Todos los grupos reservados con éxito para {Style.BRIGHT}{account[1]}{Style.RESET_ALL}")
			finished+=1
		else:
			print(f"{Fore.YELLOW}\n[!] Quedan los grupos {', '.join(account[5])} por reservar para {Style.BRIGHT}{account[1]}{Style.RESET_ALL}")
	if finished == len(accounts):
		sig_handler(None,None)
	random_time = random.randint(30, 60)
	time.sleep(random_time)
