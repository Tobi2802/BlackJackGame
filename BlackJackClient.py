import socket
import time

# Client Programm
def client_program():
    # IP des Servers und Port für Verbindung
    host = '127.0.0.1'
    port = 50002

    # Socket erstellen
    cs = socket.socket()
    cs.connect((host, port))

    def empfange_nachricht():
        return cs.recv(1024).decode('utf-8')

    def sende_nachricht(nachricht):
        cs.send(nachricht.encode('utf-8'))
    
    # Nachrichten vom Server empfangenj
    print(empfange_nachricht())  # Willkommen bei BlackJack
    print(empfange_nachricht())  # Bitte bereit gehen

    # Nachricht, dass Client bereit ist
    while True:
        message = input("dann drücken Sie b für Bereit: ")
        if message == "b":
            sende_nachricht(message)
            break
        else:
            print("Sie müssen b eingeben, um spielen zu können")
        
    print(empfange_nachricht())  # Alle Spieler sind bereit
    print(empfange_nachricht())  # Nachricht zur Namenseingabe
    name = input("Name: ")
    sende_nachricht(name)  # Benutzernamen dem Server schicken
    print(empfange_nachricht())  # Begrüßung
    while True:
        message_recv = cs.recv(1024).decode('utf-8')
        print(message_recv)  # Kontostand vor dem Setzen
        if "Guthaben beträgt 0" in message_recv:
            print ("Sie sind ein armer Schlucker mit keinem Geld, sowas brauchen wir hier nicht")
            cs.close()
            return
        while True:
            message = input("Wie viel wollen Sie setzen?: ")
            if message.isdigit():
                betrag = int(message)
                if betrag >= 1:
                    cs.send(message.encode('utf-8'))
                    message_recv = cs.recv(1024).decode('utf-8')
                    print(message_recv)  # Kontostand nach dem Setzen
                    if "neuer Kontostand" in message_recv:
                        break
                else:
                    print("Die Eingabe muss eine ganze Zahl größer als 0 sein.")
            else:
                print("Die Eingabe muss eine ganze Zahl und darf keine Buchstaben enthalten.")
                continue

        while True:
            message_recv = empfange_nachricht()  # Hand des Spielers
            print(message_recv)
            if "Blackjack" in message_recv or "verloren" in message_recv:
                break
            if "möchtest du halten oder ziehen" in message_recv:
                entscheidung = input("(h/z): ")
                sende_nachricht(entscheidung)
                if entscheidung == 'h':
                    break
                else:
                    continue

        while True:
            message_recv = empfange_nachricht()  # Nachricht, ob das Spiel vorbei ist oder nicht
            print(message_recv)
            if "verloren" in message_recv or "gewonnen" in message_recv or "Unentschieden" in message_recv:
                break

        # Frage, ob der Spieler weitermachen will
        while True:
            weiterspielen_message = empfange_nachricht()
            print(weiterspielen_message)
            while True:
                antwort = input("(j/n): ")
                if antwort == 'j' or antwort == 'n':
                    break
                else:
                    print("Ungültige Eingabe, bitte wähle 'j' oder 'n'.")   
            print(antwort)
            cs.send(antwort.encode('utf-8'))
    
            if antwort == 'n':
                print("Hier haben Sie ihr Geld. Das haben Sie nötig. Auf Wiedersehen!")
                cs.close()
                return # braucht man damit es schließt
            break # um wieder mit dem setzen zu beginnen

if __name__ == '__main__':
    client_program()