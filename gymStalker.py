#!/usr/bin/env python3

import requests, sys, signal, time, colorama, os, re, random
from colorama import Fore, Style, init
from bs4 import BeautifulSoup

init()

def sig_handler(sig, frame):
	print(Fore.RED + "\n\n[!] Saliendo...\n")
	sys.exit(0)

signal.signal(signal.SIGINT, sig_handler)

#Variables globales

login_url = "https://intranet.upv.es/pls/soalu/est_aute.intraalucomp"
sports_url = "https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?p_campus=V&p_tipoact=6690&p_codacti=21229&p_vista=intranet&p_idioma=c&p_solo_matricula_sn=&p_anc=filtro_actividad"

def booking(urlFreeGroups,freeGroups) :
	for url_group, group in zip(urlFreeGroups,freeGroups):
		link_group = f"https://intranet.upv.es/pls/soalu/{url_group}"
		session.get(link_group)
		print(f"{Fore.GREEN}[+] Grupo {group} reservado con éxito\n{Style.RESET_ALL}")
		with open('groups.txt','r+') as file :
			content=file.read() #Leemos el archivo, lo guardamos en content
			content_modified=content.replace(group,'')  # guardamos el contenido modificado
			file.seek(0) #Volvemos al inicio del archivo
			file.write(content_modified) #Sobreescribimos el archivo con el contenido modificado
			file.truncate() #El puntero se encuentra abajo, truncamos desde el puntero hasta abajo (aunque no hay nada en este caso)

def foundFreeGroups() :
	result = session.get(sports_url)
	soup = BeautifulSoup(result.text, 'html.parser')
	urlFreeGroups=[]
	freeGroups=[]
	links = soup.find_all('a', href=True)
	for link in links:
		if "p_codgrupo_mat" in link.get('href') :
			with open('groups.txt', 'r') as file:
				line = file.readline().strip()
				groups = line.split()
				for i, group in enumerate(groups):
					if f"MUS0{group}" in link.get_text() :
						urlFreeGroup = link.get('href')
						urlFreeGroups.append(urlFreeGroup)
						freeGroups.append(group)
	return urlFreeGroups,freeGroups

#LOGIN

with open('credentials.txt', 'r') as file:
    line = file.readline().strip()
    parts = line.split(':')
    name = parts[0].strip()
    dni = parts[1].strip()
    password = parts[2].strip()

session = requests.Session()
payload = { 'dni' : dni, 'clau' : password }
result = session.post(login_url, data=payload, timeout=5)
if "Alta socios de deportes" in result.text :
	print(Fore.GREEN + "\n[+] Login Correcto ")
	time.sleep(1)
	os.system('clear')

	#EN ESCUCHA

	while True:
		print(f"{Fore.GREEN}\n[+] Comprobando ... {Style.RESET_ALL}\n")
		urlFreeGroups,freeGroups = foundFreeGroups()
		time.sleep(1)
		if len(urlFreeGroups) != 0 :
			booking(urlFreeGroups,freeGroups)
		with open('groups.txt','r+') as file :
			content=file.read().strip()
		if not content :
			print(Fore.GREEN + "\n[⋆] Todos los grupos reservados con éxito")
			sig_handler(None, None)
		else :
			os.system('clear')
			print(f"{Fore.YELLOW}\n[!] Quedan los grupos {content} por reservar{Style.RESET_ALL}")
			random_time = random.randint(30, 60)
			time.sleep(random_time)
else:
    print(Fore.RED + "\n[!] Login Incorrecto")
    sig_handler(None, None)






