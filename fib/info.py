# CFIS-horaris, a timetable generator for CFIS students
#     Copyright (C) {year}  {name of author}
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

import requests
import assignatura
import classe
import grup
from colorama import Fore, Style

class Info:
    """Classe per a obtenir horaris del grau en enginyeria informàtica
    des de l'api del racó."""
    def __init__(self):
        self.llista = self.llistaAssignatures()
        self.name = "Enginyeria Informàtica [FIB]"

    def llistaAssignatures(self):
        r = requests.get("https://raco.fib.upc.edu/api/horaris/assignatures-titulacio.txt?codi=GRAU")
        return r.text.split()

    def selecciona(self):
        print("A continuació tens una llista d'assignatures, selecciona la que desitjis:")
        print()
        for x in range(0,len(self.llista)):
            print(x+1,":",self.llista[x])

        print()
        i = input("escriu el numero de l'assignatura desitjada: ")
        num = int(i)
        conf = input("Has seleccionat " + self.llista[num-1] + "? (s/n) :")
        if conf != "s":
            return selecciona()
        else:
            codi = self.llista[num-1]
            a = assignatura.Assignatura(self.llista[num-1], codi,Fore.YELLOW+"F"+Style.RESET_ALL)
            return a



    def obteHorari(self, assig):
        base = "https://raco.fib.upc.edu/api/horaris/horari-assignatures.txt?assignatures="
        base += assig.codi
        print("Buscant horaris per a",assig.nom,"...")
        r = requests.get(base)
        ls = r.text.split('\n')
        lis = []
        for el in ls:
            if len(el) > 0:
                lis.append(el.split('\t'))
        def gkey(i):
            return int(i[1])
        horari = sorted(lis, key=gkey)

        lastg = 0
        isGroup = True
        gcal = [[False for x in range(0,5)] for y in range(0,14)]
        for cl in horari:
            act = int(cl[1])
            if act != lastg:
                if not isGroup: # Venim de l'ultim subgrup del grup anterior
                    self.parseCal(scal,lastg,assig)
                elif isGroup and lastg!=0 and act==lastg+10: #només hi ha grups
                    self.parseCal(gcal,lastg,assig)
                if act%10 == 0:
                    # print("Grup",act)
                    isGroup = True
                    gcal = [[False for x in range(0,5)] for y in range(0,14)]
                else:
                    # print("  subgrup",act)
                    isGroup = False
                    scal = [row[:] for row in gcal]
                lastg = act
            h = int(cl[3].split(':')[0]) - 8
            d = int(cl[2])-1
            if isGroup:
                gcal[h][d] = True
            else:
                scal[h][d] = True
        if isGroup:
            self.parseCal(gcal,lastg,assig)
        else:
            self.parseCal(scal,lastg,assig)


    def parseCal(self,cal, grupo, assig):
        started = False
        g = grup.Grup(grupo)
        start = -1
        for d in range(0,5):
            for f in range(0,14):
                if cal[f][d]:
                    if not started:
                        start = f + 8
                        started = True
                else:
                    if started:
                        g.afegeixClasse(classe.Classe(start, f+8,d))
                    started = False
            if started:
                g.afegeixClasse(classe.Classe(start, f+8,d))
        assig.afegeixGrup(g)
        #grupo += 10




    def creaAssignatura(self):
        a = self.selecciona()
        self.obteHorari(a)
        print("Assignatura",a.nom,"creada!")
        return a
