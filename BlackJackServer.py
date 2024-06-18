#BlackJack-Server

#Libraries 
import socket #Für die Client Server verbindung
import time #Für senden der Nachrichten da zur verarbeitung der empfangenen Nachricten eine gewisse Zeit benötigt wird
import threading #Für mehrere Clients
import random #Zum shufflen des Decks
#Listen für Anzahl der Clients und wie viele Bereit sind sowie für das senden an alle Clients
client_list=[]
client_ready=[]
#clients={}
#Lock und Event um Wartelobby zu erstellen
lock= threading.Lock()
alle_bereit=threading.Event()
#classes
class Player: #Player Klasse
    def __init__(self, name, kontostand=100): #Initalisierung des Players
        self.name=name #Name des Players
        self.kontostand=kontostand #Kontostand des Players
        self.karten = [] #Hand des Players
    def begruessung(self): #Begrüsung des Spielers
        return f"Hallo {self.name}"
    def guthaben_info(self): #Gibt dem Spiler die Information wie viel Guthaben er hat
        return f"{self.name} dein Guthaben beträgt {self.kontostand}"
    def einsatz(self, betrag): #Funktion die überprüft ob die Menge die der Player setztn möchte möglich ist
        if betrag > self.kontostand: #Bedingung wenn der Player mehr setzten möchte als er hat
            return False, f"{self.name} du hast zu wenig Guthaben, dein Guthaben beträgt nur {self.kontostand}" # False startet die im Programm weiter unten stehende while-Schleife neu um die Frage erneut zu senden wie viel de Player setzen möchte
        else:
            self.kontostand -= betrag #Bedingung wenn es möglich ist den Betrag zu setzen
            return True, f"{self.name} dein neuer Kontostand ist {self.kontostand}" #Ture lässt die im Programm weiter unten stehende while-Schleife weiter laufen
    def karten_zeigen(self): #Gibt die Karten des Players aus
        return [karte.karte() for karte in self.karten]
    def handwert_berechnen(self):#Hier wird der Wert der Hand berechnet
        wert=0 #Wert der Hand
        asse=0 #Anzahl der Asse
        for karte in self.karten:
            if karte.wert in ["Bube","Dame","König"]: #Bedingung wenn eine dieser Karten auf der Hand ist bekommt sie den Wert 10
                wert+=10
            elif karte.wert == "Ass": #Bedingung wenn eine der Karten auf der Hand ein Ass ist 
                asse +=1
                wert+=11
            else: #bedingung wenn eine andere Karte auf der Hand ist wird der String der den Wert der Karte beinhaltet in ein Integer umgewandelt
                wert+=int(karte.wert)
        while wert > 21 and asse: #Überprüft ob die Hand einen Wert über 21 hat und ein Ass auf der Hand ist wenn dies der Fall ist zählt das Ass nur 1
            wert-=10
            asse-=1
        return wert #Wert wird wieder zurück gegeben
class Dealer: #Dealer Klasse
    def __init__(self,kontostanddealer=0): #Initialisierung des Dealers
        self.kontostanddealer=kontostanddealer #Kontostand des Dealers
        self.deck=None #Leeres Deck des Dealers wird im weiteren Verlauf zugewiesen
        self.clients=[] #Liste der Clients
    def kontostand(self): #Funktion zum ausgeben des Kontostandes des Dealers
        return f"Dealer hat {self.kontostanddealer}"
    def deck_erhalten(self,deck): #Funktion in dem der Dealer sein Deck bekommt
        self.deck=deck
    def clients_hinzufügen(self,client): #Funktion mit der die Clients der Cientliste hinzugefügt werden
        self.clients.append(client)
    def karten_austeilen(self): #Funktion die den Spielern und dem Dealern die Karten austeilt
        self.karten=[self.deck.deck.pop() for _ in range(2)] #Karten des Dealers
        for client in self.clients:
            client.karten=[self.deck.deck.pop() for _ in range(2)] #Karten werden der jeweiligen Clients
    def erste_karte_dealer(self): #Funktion welche die erste Karte des Dealers ausgibt
        return self.karten[0].karte() 
    def deck(self): #Funktion um das Deck zu verwenden
        return [karte.karte for karte in self.deck.deck]
    def karte_ziehen(self,player): #Funktion die eine Karte zum Dealer oder Playerdeck hinzufügt player dient hier nur als platzhalter
        player.karten.append(self.deck.deck.pop())
    def berechne_handwert(self): #Funktionsweise wie bei der Berechnung des Handwertes des Players
        wert=0
        asse=0
        for karte in self.karten:
            if karte.wert in ["Bube","Dame","König"]:
                wert+=10
            elif karte.wert=="Ass":
                asse+=1
                wert+=11
            else:
                wert+=int(karte.wert)
        while wert > 21 and asse:
            wert-=10
            asse-=1
        return wert
    def karten_zeigen(self): #Gibt die Karten des Dealers aus
        return [karte.karte() for karte in self.karten]
class Karte: #Karten Klasse
    def __init__(self,zeichen,wert): #Karte wird Initialisiert
        self.zeichen=zeichen #Der Karte wird ein Zeichen übergeben
        self.wert=wert #Der Karte wird ein Wert übergeben
    def karte(self): #Funktion zur ausgabe der Karte
        return f"{self.zeichen}{self.wert}"
class Deck: #Deck Klasse
    def __init__(self): #Deck wird initialisiert
        self.zeichen=["Herz","Karo","Pick","Kreuz"] #Liste der Zeichen der Karten
        self.wert=["2","3","4","5","6","7","8","9","10","Bube","Dame","König","Ass"] #Liste der Werte der Karten
        self.deck=[Karte(zeichen,wert) for zeichen in self.zeichen for wert in self.wert] #Deck wird zusammengestellt
        random.shuffle(self.deck) #Deck wird gemischelt
    #def kartendeck(self):
        #return [karte.karte() for karte in self.deck]

#Funktion für Threads für die Clients
def thread_funktion(conn,address):
    print(f"Verbindung von {address}") #Gibt aus 
    #Nachrichten an Client senden
    willkommens_message="Willkommen bei BlackJack"
    conn.send(willkommens_message.encode('utf-8'))
    time.sleep(1)
    bereit_message="Sind Sie bereit?"
    conn.send(bereit_message.encode('utf-8'))
    time.sleep(1)
    b_message=conn.recv(1024).decode('utf-8')
    #Überprüfen ob alle Clients die Verbunden sind auch Bereit sind um das Spiel zu starten
    with lock:
        client_ready.append(b_message)
        if len(client_list)==len(client_ready):
            alle_bereit.set()
    alle_bereit.wait()
    time.sleep(1)
    alle_bereit_message="Alle Spieler sind bereit"
    conn.send(alle_bereit_message.encode('utf-8'))
    time.sleep(1)
    name_eingeben_message="Geben Sie Ihren Namen ein"
    conn.send(name_eingeben_message.encode('utf-8'))
    name_message=conn.recv(1024).decode('utf-8')
    p1=Player(name_message)
    begruessungs_message=p1.begruessung()
    conn.send(begruessungs_message.encode('utf-8'))
    time.sleep(1)
    while True:
        guthaben_message=p1.guthaben_info()
        conn.send(guthaben_message.encode('utf-8'))
        while True:
            betrag=int(conn.recv(1024).decode('utf-8'))
            erfolg,einsatz_spieler=p1.einsatz(betrag)
            conn.send(einsatz_spieler.encode('utf-8'))
            if erfolg:
                break
        d1=Dealer()
        d1.deck_erhalten(Deck())
        print(d1.deck_erhalten(Deck()))
        karten_dealen_message="Karten werden nun gedealt\n"
        conn.send(karten_dealen_message.encode('utf-8'))
        d1.clients_hinzufügen(p1)
        d1.karten_austeilen()
        print("Dealer erste Karte",d1.erste_karte_dealer())
        dealers_erste_karte_message=(f"Erste Karte des Dealers {d1.erste_karte_dealer()}")
        conn.send(dealers_erste_karte_message.encode("utf-8"))
        time.sleep(1)
        client_karten_message=f"{p1.name} deine Karten {p1.karten_zeigen()}"
        conn.send(client_karten_message.encode("utf-8"))
        #print("Client Karten",p1.karten_zeigen())
        time.sleep(1)
        hand_wert_message=f"{p1.name}, der Wert deiner Hand beträgt {p1.handwert_berechnen()}"
        conn.send(hand_wert_message.encode("utf-8"))
        while True:
            handwert=p1.handwert_berechnen()
            if handwert == 21:
                einsatz=int(betrag*2.5)
                p1.kontostand+=einsatz
                conn.send(f"{p1.name} du hast ein BlackJack du bekommst das 2.5 Fache deines Einsatzes dein neuer Kontostand beträgt {p1.kontostand}".encode("utf-8"))
                time.sleep(1)
                break
            ziehen_oder_halten_message=f"{p1.name} möchtest du halten oder ziehen (h/z)?"
            conn.send(ziehen_oder_halten_message.encode("utf-8"))
            time.sleep(1)
            entscheidung=conn.recv(1024).decode("utf-8").strip()
            print(entscheidung)
            if entscheidung=="z" and p1.handwert_berechnen()<21:
                d1.karte_ziehen(p1)
                client_karten_message=f"{p1.name} deine neue Karte {p1.karten_zeigen()}"
                conn.send(client_karten_message.encode("utf-8"))
                handwert=p1.handwert_berechnen()
                handwert_message=f"{p1.name}, der Wert deiner Hand ist nun {handwert}\n"
                conn.send(handwert_message.encode("utf-8"))
                if handwert > 21:
                    conn.send(f"{p1.name} du hast verloren".encode("utf-8"))
                    time.sleep(1)
                    conn.send(f"{p1.name} du hast verloren".encode("utf-8"))
                    time.sleep(1)
                    break
                if handwert == 21:
                    einsatz=int(betrag*2.5)
                    p1.kontostand+=einsatz
                    conn.send(f"{p1.name} du hast ein BlackJack du bekommst das 2.5 Fache deines einsatzes dein neuer Kontostand beträgt {p1.kontostand}".encode("utf-8"))
                    time.sleep(1)
                    conn.send(f"{p1.name} du hast ein BlackJack du bekommst das 2.5 Fache deines einsatzes dein neuer Kontostand beträgt {p1.kontostand}".encode("utf-8"))
                    time.sleep(1)
                    break
            elif entscheidung =="h":
                while d1.berechne_handwert() <=17:
                    d1.karte_ziehen(d1)
                dealer_karten_message=f"Zweite Karte des Dealers {d1.karten[1].karte()}"
                conn.send(dealer_karten_message.encode("utf-8"))
                dealer_handwert=d1.berechne_handwert()
                delaer_karten=d1.karten_zeigen()
                dealer_karten_message=f"Die Karten des Dealers sind {delaer_karten}\n"
                conn.send(dealer_karten_message.encode("utf-8"))
                dealer_handwert_message=f"Die Hand des Dealers hat einen Wert von {dealer_handwert} \n"
                conn.send(dealer_handwert_message.encode("utf-8"))
                handwert=p1.handwert_berechnen()
                if dealer_handwert > 21 or dealer_handwert < handwert:
                    if handwert == 21:
                        einsatz=int(betrag*2.5)
                        p1.kontostand+=einsatz
                        conn.send(f"{p1.name} du hast ein BlackJack du bekommst das 2.5 Fache deines einsatzes dein neuer Kontostand beträgt {p1.kontostand}".encode("utf-8"))
                        time.sleep(1)
                        break
                    else:
                        einsatz=int(betrag*2)
                        p1.kontostand+=einsatz
                        conn.send(f"{p1.name} du hast gewonnen du bekommst deinen Einsatz zurück dein neuer Kontostand beträgt {p1.kontostand}".encode("utf-8"))
                        time.sleep(1)
                        break
                elif dealer_handwert > handwert:
                    conn.send(f"{p1.name} du hast verloren".encode("utf-8"))
                    time.sleep(1)
                    break
                else:
                    conn.send("Unentschieden".encode("utf-8"))
                    time.sleep(1)
                break
            else:
                conn.send("Ungültige eingabe bitte h oder z".encode("utf-8"))
                time.sleep(1)
        while True:
            weiterspielen_message=f"Möchtest du weiter spielen?(j/n)"
            conn.send(weiterspielen_message.encode("utf-8"))
            time.sleep(1)
            antwort=conn.recv(1024).decode("utf-8")
            print(antwort)
            if antwort == "j":
                p1.karten.clear()
                d1.karten.clear()
                break
            elif antwort == "n":
                conn.send("Verbindung wird geschlossen".encode("utf-8"))
                conn.close()
                return
            else:
                conn.send("Ungültige eingabe nur j und n".encode("utf-8"))
            break
#Server Program
def server_program():
    #IP des Servers Port für connection
    host=''
    port=50002
    #Socket erstellen
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) Braucht man damit keine Fehlermeldung beim Raspberry kommt
    #s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
    s.bind((host,port))
    print("Server online")
    #Anzahl an Clients die auf den Server können
    s.listen(12)
    #Client anfragen akzeptieren
    while True:
        conn, address=s.accept()
        with lock:
            client_list.append(address)
        #threads erstellen 
        client_thread=threading.Thread(target=thread_funktion,args=(conn,address))
        client_thread.start() 
    s.close()
#main
if __name__=='__main__':
    server_program()
