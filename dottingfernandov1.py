'''Libraries importeren'''
import RPi.GPIO as GPIO
import time
#-----------------------------------------
'''GPIO Modes instellen'''
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#-----------------------------------------
'''Variabeles voor de GPIO-Pins'''
pinAvooruit = 10
pinAachteruit = 9
pinBvooruit = 8
pinBachteruit = 7
echoOutput = 17
echoInput = 18
lichtinput = 25
#----------------------------------------
'''Frequentie van de wielen'''
Frequency = 12
'''Percentage dat de banden gebruikt worden'''
DutyCycleA = 26
DutyCycleB = 35
Stop = 0
#----------------------------------------
'''Set the GPIO Pin mode to be Output'''
GPIO.setup(pinAvooruit, GPIO.OUT)
GPIO.setup(pinAachteruit, GPIO.OUT)
GPIO.setup(pinBvooruit, GPIO.OUT)
GPIO.setup(pinBachteruit, GPIO.OUT)

GPIO.setup(echoOutput, GPIO.OUT)
GPIO.setup(echoInput, GPIO.IN)

GPIO.setup(lichtinput, GPIO.IN)
#----------------------------------------
'''Andere variabelen'''
Grens_afstand = 25
achteruit_tijd = 0.5
omdraai_tijd = 0.4
Uturn_tijd = 0.7
Rondje_draaien = 8
counter = 0
#----------------------------------------
'''GPIO naar PWM-software naar frequentie in Hertz'''
pwmpinAvooruit = GPIO.PWM(pinAvooruit, Frequency)
pwmpinAachteruit = GPIO.PWM(pinAachteruit, Frequency)
pwmpinBvooruit = GPIO.PWM(pinBvooruit, Frequency)
pwmpinBachteruit = GPIO.PWM(pinBachteruit, Frequency)
#----------------------------------------
'''De software starten waarbij de auto stil zal staan'''
pwmpinAvooruit.start(Stop)
pwmpinAachteruit.start(Stop)
pwmpinBvooruit.start(Stop)
pwmpinBachteruit.start(Stop)
#---------------------------------------
'''stop functie'''
def stop():
    pwmpinAvooruit.ChangeDutyCycle(Stop)
    pwmpinAachteruit.ChangeDutyCycle(Stop)
    pwmpinBvooruit.ChangeDutyCycle(Stop)
    pwmpinBachteruit.ChangeDutyCycle(Stop)
#---------------------------------------
'''Vooruit rij functie'''
def Vooruit():
    pwmpinAvooruit.ChangeDutyCycle(DutyCycleA)
    pwmpinAachteruit.ChangeDutyCycle(float(0))
    pwmpinBvooruit.ChangeDutyCycle(DutyCycleB)
    pwmpinBachteruit.ChangeDutyCycle(Stop)
#---------------------------------------
'''Achteruit rij functie'''
def Achteruit():
    pwmpinAvooruit.ChangeDutyCycle(Stop)
    pwmpinAachteruit.ChangeDutyCycle(DutyCycleA)
    pwmpinBvooruit.ChangeDutyCycle(Stop)
    pwmpinBachteruit.ChangeDutyCycle(DutyCycleB)
#--------------------------------------
'''Links afslaan'''
def Links():
    pwmpinAvooruit.ChangeDutyCycle(Stop)
    pwmpinAachteruit.ChangeDutyCycle(DutyCycleA)
    pwmpinBvooruit.ChangeDutyCycle(DutyCycleB)
    pwmpinBachteruit.ChangeDutyCycle(Stop)
#--------------------------------------
'''Rechts afslaan'''
def Rechts():
    pwmpinAvooruit.ChangeDutyCycle(DutyCycleA)
    pwmpinAachteruit.ChangeDutyCycle(Stop)
    pwmpinBvooruit.ChangeDutyCycle(Stop)
    pwmpinBachteruit.ChangeDutyCycle(DutyCycleB)
#--------------------------------------
'''Meting maken'''
buffer = []

def Meting():
    global buffer
    GPIO.output(echoOutput, True)
    time.sleep(0.00001)
    GPIO.output(echoOutput, False)
    StartTime = time.time()
    StopTime = StartTime

    while GPIO.input(echoInput)==0:
        StartTime = time.time()
        StopTime = StartTime

    while GPIO.input(echoInput)==1:
        StopTime = time.time()

    ElapsedTime = StopTime - StartTime
    Afstand = (ElapsedTime * 34300)/2

    buffer.append(Afstand)
    if (len(buffer) > 3):
        buffer.pop(0)

    total = 0
    for i in range(0, len(buffer)):
        total += buffer[i]


    return total / len(buffer)
#--------------------------------------
'''Functie die true geeft als de sensor een 1 geeft'''
def Dichtbij(localGrens_afstand):
    Afstand = Meting()

    print("Grens_afstand: "+str(Afstand))
    if Afstand < localGrens_afstand:
        return True
    else:
        return False
#------------------------------------
'''Functie die een Uturn maakt'''
def Uturn():
    #Klein stukje achteruit
    print("Achteruit")
    Achteruit()
    time.sleep(achteruit_tijd)
    stop()

    #Naar rechts
    print("Rechts")
    Rechts()
    time.sleep(omdraai_tijd)
    stop()
    #Vooruit
    print("Vooruit")
    Vooruit()
    time.sleep(Uturn_tijd)
    stop()

    #Naar rechts
    print("Rechts")
    Rechts()
    time.sleep(omdraai_tijd)
    stop()
#------------------------------------
'''Witte stip vinden'''
def RijdtoverZwart():
    if GPIO.input(lichtinput) == 0:
        print("Rijdt over zwart oppervlak")
        Stop()
        time.sleep(5)
        return True
    else:
        print("Rijdt over wit oppervlak")
        return False
#---------------------------------------
'''Try-line om de volgorde van handelen te vertellen'''
try:
    GPIO.output(echoOutput, False)
    time.sleep(0.1)
    #Keep doing your thing!
    while True:
        Vooruit()
        time.sleep(0.1)
        if RijdtoverZwart():
            stop()
            time.sleep(5)
        elif Dichtbij(Grens_afstand):
            stop()
            Uturn()

        counter+=1
        print "counter is nu 1 " + str(counter)
        if counter == 4:
            print "HowNear before increment = " + str(Grens_afstand)
            Grens_afstand+=5
            print "counter is nu 4 = HowNear+=1 " + str(counter)
            print "HowNear after increment = " + str(Grens_afstand)

            if Grens_afstand == 45:
                Grens_afstand = 25;
            if counter == 5:
                print "counter is 5 , dus nu weer 1 " + str(counter)
                counter = 1
                print "counter moet nu weer 1 zijn " + str(counter)

        time.sleep(0.50)
except KeyboardInterrupt:
        GPIO.cleanup()

