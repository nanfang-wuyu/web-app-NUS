import RPi.GPIO as GPIO
from time import time


RED = 23
GREEN = 24
BLUE = 25
# global status 
# status = 0

CODES = {
    0xffa25d: "CH-",
    0xff629d: "CH",
    0xffe21d: "CH+",
    0xff22dd: "PREVIOUS",
    0xff02fd: "NEXT",
    0xffc23d: "PLAY/PAUSE",
    0xffe01f: "MINUS",
    0xffa857: "PLUS",
    0xff906f: "EQ",
    0xff6897: "0",
    0xff9867: "100+",
    0xffb04f: "200+",
    0xff30cf: "1",
    0xff18e7: "2",
    0xff7a85: "3",
    0xff10ef: "4",
    0xff38c7: "5",
    0xff5aa5: "6",
    0xff42bd: "7",
    0xff4ab5: "8",
    0xff52ad: "9",
}

def setup():
    GPIO.setmode(GPIO.BCM)  # Numbers GPIOs by physical location
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.setup(RED,GPIO.OUT)
    GPIO.output(RED,0)
    GPIO.setup(GREEN,GPIO.OUT)
    GPIO.output(GREEN,0)
    GPIO.setup(BLUE,GPIO.OUT)
    GPIO.output(BLUE,0)

def binary_aquire(pin, duration):
    # aquires data as quickly as possible
    t0 = time()
    results = []
    while (time() - t0) < duration:
        results.append(GPIO.input(pin))
    return results


def on_ir_receive(pinNo, bouncetime=150):
    # when edge detect is called (which requires less CPU than constant
    # data acquisition), we acquire data as quickly as possible
    data = binary_aquire(pinNo, bouncetime/1000.0)
    if len(data) < bouncetime:
        return
    rate = len(data) / (bouncetime / 1000.0)
    pulses = []
    i_break = 0
    # detect run lengths using the acquisition rate to turn the times in to microseconds
    for i in range(1, len(data)):
        if (data[i] != data[i-1]) or (i == len(data)-1):
            pulses.append((data[i-1], int((i-i_break)/rate*1e6)))
            i_break = i
    # decode ( < 1 ms "1" pulse is a 1, > 1 ms "1" pulse is a 1, longer than 2 ms pulse is something else)
    # does not decode channel, which may be a piece of the information after the long 1 pulse in the middle
    outbin = ""
    for val, us in pulses:
        if val != 1:
            continue
        if outbin and us > 2000:
            break
        elif us < 1000:
            outbin += "0"
        elif 1000 < us < 2000:
            outbin += "1"
    try:
        return int(outbin, 2)
    except ValueError:
        # probably an empty code
        return None


def destroy():
    GPIO.cleanup()

def mode(code,status):
    status = status
    if code == 0xffa25d:
        status = 1
    elif code == 0xff629d:
        status = 2
    elif code == 0xffe21d:
        status = 3
    else:
        status = 0

    return status
    
def rgb(status):
    status = status
    if status == 1:
        GPIO.output(RED,1)
        GPIO.output(GREEN,0)
        GPIO.output(BLUE,0)
    elif status == 2:
        GPIO.output(RED,0)
        GPIO.output(GREEN,1)
        GPIO.output(BLUE,0)
    elif status == 3:
        GPIO.output(RED,0)
        GPIO.output(GREEN,0)
        GPIO.output(BLUE,1)
    elif status == 0:
        GPIO.output(RED,0)
        GPIO.output(GREEN,0)
        GPIO.output(BLUE,0)
    



if __name__ == "__main__":
    setup()
    status = 0
    try:
        print("Starting IR Listener")
        while True:
            print("Waiting for signal")
            GPIO.wait_for_edge(27, GPIO.FALLING)
            code = on_ir_receive(27)
            if code:
                status = mode(code,status)
                
                # print(str(hex(code)))
            else:
                print("Invalid code")
            rgb(status)
            print(status)
    except KeyboardInterrupt:
        pass
    except RuntimeError:
        # this gets thrown when control C gets pressed
        # because wait_for_edge doesn't properly pass this on
        pass
    print("Quitting")
    destroy()