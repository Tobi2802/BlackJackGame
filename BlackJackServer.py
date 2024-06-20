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
class Spieler: #Spieler Klasse
    def __init__(self, name, kontostand=100): #Initalisierung des Spielers
        self.name=name #Name des Spielers
        self.kontostand=kontostand #Kontostand des Spielers
        self.karten = [] #Hand des Spielers
    def begruessung(self): #Begrüsung des Spielers
        return f"Hallo {self.name}"
    def guthaben_info(self): #Gibt dem Spiler die Information wie viel Guthaben er hat
        return f"{self.name} dein Guthaben beträgt {self.kontostand}"
    def einsatz(self, betrag): #Funktion die überprüft ob die Menge die der Spieler setztn möchte möglich ist
        if betrag > self.kontostand: #Bedingung wenn der Spieler mehr setzten möchte als er hat
            return False, f"{self.name} du hast zu wenig Guthaben, dein Guthaben beträgt nur {self.kontostand}" # False startet die im Programm weiter unten stehende while-Schleife neu um die Frage erneut zu senden wie viel de Spieler setzen möchte
        else:
            self.kontostand -= betrag #Bedingung wenn es möglich ist den Betrag zu setzen
            return True, f"{self.name} dein neuer Kontostand ist {self.kontostand}" #Ture lässt die im Programm weiter unten stehende while-Schleife weiter laufen
    def karten_zeigen(self): #Gibt die Karten des Spielers aus
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
    def karte_ziehen(self,Spieler): #Funktion die eine Karte zum Dealer oder Spielerdeck hinzufügt Spieler dient hier nur als platzhalter
        Spieler.karten.append(self.deck.deck.pop())
    def berechne_handwert(self): #Funktionsweise wie bei der Berechnung des Handwertes des Spielers
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
        return f"{self.zeichen} {self.wert}"
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
    print(f"Verbindung von {address}") #Gibt die Ip des Clients aus
    #Nachrichten an Client senden
    willkommens_message="Willkommen bei BlackJack"
    conn.send(willkommens_message.encode('utf-8')) #Sendet Willkommensnachricht an den Client
    time.sleep(1)
    bereit_message="Sind Sie bereit?"
    conn.send(bereit_message.encode('utf-8')) #Fragt den Client ob er bereit ist
    time.sleep(1)
    b_message=conn.recv(1024).decode('utf-8') #Erhält ein b vom Client, welches signalisiert, dass dieser Bereit ist
    #Überprüfen ob alle Clients die Verbunden sind auch Bereit sind um das Spiel zu starten
    with lock:
        client_ready.append(b_message)
        if len(client_list)==len(client_ready):
            alle_bereit.set() #Setzt das Event
    alle_bereit.wait() #Wartet bis Event gesetzt ist
    time.sleep(1)
    alle_bereit_message="Alle Spieler sind bereit"
    conn.send(alle_bereit_message.encode('utf-8'))#Schickt dem Client die Nachricht, dass alle Spieler bereit sind
    time.sleep(1)
    name_eingeben_message="Geben Sie Ihren Namen ein"
    conn.send(name_eingeben_message.encode('utf-8')) #Fragt den Client nach seinem Namen
    name_message=conn.recv(1024).decode('utf-8') #Erhält den Namen vom Client
    p1=Spieler(name_message) #Erstellt einen neuen Spieler mir dem eingegebenen Namen
    begruessungs_message=p1.begruessung()
    conn.send(begruessungs_message.encode('utf-8')) #Schickt dem Spieler eine Begrüßung
    time.sleep(1)
    while True:
        guthaben_message=p1.guthaben_info()
        conn.send(guthaben_message.encode('utf-8')) #Schickt dem Client die Information wie viel Guthaben er hat 
        while True:
            betrag=int(conn.recv(1024).decode('utf-8')) #Bekommt den Betrag den der Client setzten möchte
            erfolg,einsatz_spieler=p1.einsatz(betrag) #Übergibt den eingesetzten Betrag dem Spieler
            conn.send(einsatz_spieler.encode('utf-8')) #Sendet dem Spieler seinen neuen Kontostand
            if erfolg: #Bedingung ob ein der gesetzte Betrag möglich ist wenn ja geht es weiter im Programm
                break
        d1=Dealer() #Dealer wird erstellt
        d1.deck_erhalten(Deck()) #Dem Dealer wird das Deck übergeben
        karten_dealen_message="Karten werden nun gedealt\n"
        conn.send(karten_dealen_message.encode('utf-8'))#Schickt dem Spieler die Information, dass die Karten nun ausgeteilt werden
        d1.clients_hinzufügen(p1) #Clients werden der Clientliste des Dealers hinzugfügt
        d1.karten_austeilen() #Karten werden dem Dealer und den CLients ausgeteilt
        dealers_erste_karte_message=(f"Erste Karte des Dealers {d1.erste_karte_dealer()}")
        conn.send(dealers_erste_karte_message.encode("utf-8"))#Sendet dem Spieler die Nachricht welche die erste Karte des Dealers ist
        time.sleep(1)
        client_karten_message=f"{p1.name} deine Karten {p1.karten_zeigen()}"
        conn.send(client_karten_message.encode("utf-8")) #Sendet dem Spieler seine Karten
        time.sleep(1)
        hand_wert_message=f"{p1.name}, der Wert deiner Hand beträgt {p1.handwert_berechnen()}"
        conn.send(hand_wert_message.encode("utf-8"))#Sendet dem Spieler welchen Wert seine Hand hat
        while True:
            handwert=p1.handwert_berechnen()#Berechnet den Handwert des Spielers
            if handwert == 21: #Bedingung wenn der Spieler Black Jack auf die Hand bekommt
                gewinn=int(betrag*2.5)#Der Einsatz wird mit 2.5 vervielfacht
                p1.kontostand+=gewinn #Gewinn wird dem Kontostand wird gewinn angerechnet
                conn.send(f"{p1.name} du hast ein BlackJack du bekommst das 2.5 Fache deines Einsatzes dein neuer Kontostand beträgt {p1.kontostand}".encode("utf-8"))#Dem Spieler wird mitgeteilt, dass er ein Black Jack hat und wie viel nun auf seinem Konto ist
                time.sleep(1)
                break
            ziehen_oder_halten_message=f"{p1.name} möchtest du halten oder ziehen (h/z)?"
            conn.send(ziehen_oder_halten_message.encode("utf-8"))#Fragt den Client ob er ziehen oder halten möchte 
            time.sleep(1)
            entscheidung=conn.recv(1024).decode("utf-8")#Bekommt die Entscheidung ob der Client halten oder ziehen möchte 
            if entscheidung=="z" and p1.handwert_berechnen()<21: #Bedingung wenn der Client ziehen möchte nur möglich wenn seine Hand einen geringeren Wert als 21 hat
                d1.karte_ziehen(p1) #Spieler zieht eine weitere Karte
                client_karten_message=f"{p1.name} deine neue Karte {p1.karten_zeigen()}"
                conn.send(client_karten_message.encode("utf-8")) #Nachricht an den Spieler welche Karte er erhalten hat
                handwert=p1.handwert_berechnen() #Der neue Wert der Hand des Spielers wird berechnet
                handwert_message=f"{p1.name}, der Wert deiner Hand ist nun {handwert}\n"
                conn.send(handwert_message.encode("utf-8")) #Nachricht des neuen Handwertes wird dem Spieler geschickt
                if handwert > 21:#Bedingung wenn der Wert der Hand größer als 21 ist
                    conn.send(f"{p1.name} du hast verloren".encode("utf-8")) #Sendet dem Spieler die Nachricht, dass der Verloren hat
                    time.sleep(1)
                    conn.send(f"{p1.name} du hast verloren".encode("utf-8"))
                    time.sleep(1)
                    break
                if handwert == 21:#Bedingung wenn der Spieler ein Black Jack hat
                    einsatz=int(betrag*2.5)#Der Einsatz wird mit 2.5 vervielfacht
                    p1.kontostand+=einsatz #Gewinn wird dem Kontostand wird gewinn angerechnet
                    conn.send(f"{p1.name} du hast ein BlackJack du bekommst das 2.5 Fache deines einsatzes dein neuer Kontostand beträgt {p1.kontostand}".encode("utf-8"))#Dem Spieler wird mitgeteilt, dass er ein Black Jack hat und wie viel nun auf seinem Konto ist
                    time.sleep(1)
                    conn.send(f"{p1.name} du hast ein BlackJack du bekommst das 2.5 Fache deines einsatzes dein neuer Kontostand beträgt {p1.kontostand}".encode("utf-8"))
                    time.sleep(1)
                    break
            elif entscheidung =="h":#Bedingung wenn der Spieler halten möchte
                while d1.berechne_handwert() <=17: #Bedingung wenn der Wert der Delaerhand unter oder 17 ist, da dieser bis dahin ziehen muss
                    d1.karte_ziehen(d1) #Dealer zieht solang bis die Bedingung erfüllt ist
                dealer_karten_message=f"Zweite Karte des Dealers {d1.karten[1].karte()}"
                conn.send(dealer_karten_message.encode("utf-8"))#Sendet die zweite Karte des Dealers an den Spieler
                dealer_handwert=d1.berechne_handwert() #Berechnet den Handwert des Dealers
                delaer_karten=d1.karten_zeigen() #Alle Karten des Dealers 
                dealer_karten_message=f"Die Karten des Dealers sind {delaer_karten}\n"
                conn.send(dealer_karten_message.encode("utf-8")) #Schickt die Hand des Dealers an den Spieler
                dealer_handwert_message=f"Die Hand des Dealers hat einen Wert von {dealer_handwert} \n"
                conn.send(dealer_handwert_message.encode("utf-8")) #Sendet den Wert der Dealerhand an den Spieler
                handwert=p1.handwert_berechnen() #Berechnet den Handwert des Spielers
                if dealer_handwert > 21 or dealer_handwert < handwert:#Bedingung wenn die Dealerhand über 21 ist oder die Dealerhandwert kleiner dem Wert der Spielerhand ist
                    if handwert == 21: #Bedingung wenn der Spieler ein Black Jack hat
                        einsatz=int(betrag*2.5)#Der Einsatz wird mit 2.5 vervielfacht
                        p1.kontostand+=einsatz#Gewinn wird dem Kontostand wird gewinn angerechnet
                        conn.send(f"{p1.name} du hast ein BlackJack du bekommst das 2.5 Fache deines einsatzes dein neuer Kontostand beträgt {p1.kontostand}".encode("utf-8"))#Dem Spieler wird mitgeteilt, dass er ein Black Jack hat und wie viel nun auf seinem Konto ist
                        time.sleep(1)
                        break
                    else: #Bedingung wenn der Spieler normal gewinnt
                        einsatz=int(betrag*2)#Der Einsatz wird mit 2 vervielfacht
                        p1.kontostand+=einsatz#Gewinn wird dem Kontostand wird gewinn angerechnet
                        conn.send(f"{p1.name} du hast gewonnen du bekommst deinen Einsatz zurück dein neuer Kontostand beträgt {p1.kontostand}".encode("utf-8"))#Dem Spieler wird mitgeteilt, dass er gewonnen hat und wie viel er auf seine Konto hat
                        time.sleep(1)
                        break
                elif dealer_handwert > handwert: #Bedingung wenn der Wert der Dealerhand großer ist als der des Spielers
                    conn.send(f"{p1.name} du hast verloren".encode("utf-8"))#Sendet dem Spieler, dass er verloren hat
                    time.sleep(1)
                    break
                else:
                    conn.send("Unentschieden".encode("utf-8"))#Sendet dem Spieler, dass das Spiel unendsieden ausgegangen
                    time.sleep(1)
                break
            else:
                conn.send("Ungültige eingabe bitte h oder z".encode("utf-8"))#Sendet, dass der Spieler eine ungültige eingabe gemacht hat und dass er ein h oder ein z eingeben muss
                time.sleep(1)
        while True:#weiterspielen
            weiterspielen_message=f"Möchtest du weiter spielen?(j/n)"
            conn.send(weiterspielen_message.encode("utf-8"))#Sendet die Frage ob der Spieler weiterspielen möchte
            time.sleep(1)
            antwort=conn.recv(1024).decode("utf-8")#Erhält vom Spieler die Antwort ob er weiterspielen möchte oder nicht
            if antwort == "j": #Bedingung wenn der Spieler weiterspielen möcht
                p1.karten.clear()#Karten des Spielers werden gelöscht
                d1.karten.clear()#Karten des Dealers werden gelöscht 
                break
            elif antwort == "n": #Bedingung wenn der Spieler nicht mehr Spielen will
                conn.send("Verbindung wird geschlossen".encode("utf-8")) #Sendet dem Spieler dass die Verbindung geschlossen wird 
                conn.close()#Verbindung wird geschlossen
                return
            else:
                conn.send("Ungültige eingabe nur j und n".encode("utf-8"))#Sendet dem Spieler, dass er eine ungültige Eingabe gemacht hat 
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
