# schnudiPlayer1.4.py

from soundplayer import SoundPlayer
import RPi.GPIO as GPIO
import time

#set button and LEDs GPIO Nr. (not PIN number)
BUTTON_TIER = 23
BUTTON_MUSIK = 24
BUTTON_HOERBUCH = 25
BUTTON_PAUSE = 27
LED_TIER = 16
LED_MUSIK = 20
LED_HOERBUCH = 26
LED_STATE_RED = 5 
LED_STATE_GREEN = 6
LED_STATE_BLUE = 13

def setup():
    #setup GPIOs
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_TIER, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(BUTTON_MUSIK, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(BUTTON_HOERBUCH, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(BUTTON_PAUSE, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(LED_TIER,GPIO.OUT)
    GPIO.setup(LED_MUSIK,GPIO.OUT)
    GPIO.setup(LED_HOERBUCH,GPIO.OUT)
    GPIO.setup(LED_STATE_RED,GPIO.OUT)
    GPIO.setup(LED_STATE_GREEN,GPIO.OUT)
    GPIO.setup(LED_STATE_BLUE,GPIO.OUT)
    stateLED("BLUE")

class Player(object):

    #player based on SoundPlayer

    # set libraryPath and type
    libraryPath = "/home/pi/schnudiPlayer/library/"
    container = ".mp3"
    
    playlist = ""
    max_trackID = 0
    trackID = 0
    volume = 0

    activePlayer = None
    isPlaying = None

    def __init__(self, playlist, volume):
        self.playlist = playlist[0]
        self.max_trackID = playlist[1]
        self.trackID = 0
        self.volume = volume

    def start(self):          
            self.activePlayer = SoundPlayer(self.libraryPath + self.playlist + "/" + str(self.trackID) + self.container)
            playerLED(self.playlist, 1)
            self.activePlayer.play(self.volume)
            #print("Player.isPlaying:")
            #print(self.activePlayer.isPlaying())
            self.isPlaying = True
            stateLED("CYAN")
            print("Playlist " + self.playlist + ", Track: " + str(self.trackID) + ", Volume: " + str(self.volume) + " started.")
            return True

    def stop(self):
        if self.activePlayer == None:
            return False
        else:
            stateLED("PURPLE")
            if self.activePlayer.isPlaying():
                self.activePlayer.stop()
                time.sleep(0.2)
            playerLED(self.playlist, 0)  
            #print(self.playlist + " stopped.")            
            self.playlist = None            
            self.isPlaying = None
            return True

    def pause(self):
        playing = self.isPlaying
        if playing:
            self.activePlayer.pause()
            self.isPlaying = False
            #print(self.playlist + " paused")
            stateLED("YELLOW")
            return True
        else:
            return False

    def resume(self):
        playing = self.isPlaying
        if not playing:
            self.activePlayer.resume()
            self.isPlaying = True
            #print(self.playlist + " resume")
            stateLED("CYAN")
            return True
        else:
            return False

    def nextTrack(self):
        isPlaying = self.isPlaying
        playlist = self.playlist
        if isPlaying:
            self.stop()
            self.playlist = playlist
            self.nextTrackID()           
            self.start()
            #print(self.playlist + str(self.trackID))
            return True
        else:
            return False

    def nextTrackID(self):
        check = self.max_trackID - self.trackID
        if check == 1:
            self.trackID = 0
        else:
            self.trackID += 1

    def switchRunningPlaylist(self, new_playlist):
        runningPlaylist = self.playlist
        if runningPlaylist == None:
            return False
        elif runningPlaylist == new_playlist[0]:
            return False
        else:
            if self.stop():
                self.playlist = new_playlist[0]
                self.max_trackID = new_playlist[1]
                self.trackID = 0

                #print("switched to: " + self.playlist)
                
                self.start()
                return True
            else:
                return False

        #print(runningPlaylist + " " + self.playlist + " " + str(self.trackID))

# RGB LED
def stateLED(coulor):
    if coulor == "RED":
        GPIO.output(LED_STATE_RED, 1)
        GPIO.output(LED_STATE_GREEN, 0)
        GPIO.output(LED_STATE_BLUE, 0)
    elif coulor == "GREEN":
        GPIO.output(LED_STATE_RED, 0)
        GPIO.output(LED_STATE_GREEN, 1)
        GPIO.output(LED_STATE_BLUE, 0)
    elif coulor == "BLUE":
        GPIO.output(LED_STATE_RED, 0)
        GPIO.output(LED_STATE_GREEN, 0)
        GPIO.output(LED_STATE_BLUE, 1)
    elif coulor == "YELLOW":
        GPIO.output(LED_STATE_RED, 1)
        GPIO.output(LED_STATE_GREEN, 1)
        GPIO.output(LED_STATE_BLUE, 0)
    elif coulor == "PURPLE":
        GPIO.output(LED_STATE_RED, 1)
        GPIO.output(LED_STATE_GREEN, 0)
        GPIO.output(LED_STATE_BLUE, 1)
    elif coulor == "CYAN":
        GPIO.output(LED_STATE_RED, 0)
        GPIO.output(LED_STATE_GREEN, 1)
        GPIO.output(LED_STATE_BLUE, 1)
    elif coulor == "WHITE":
        GPIO.output(LED_STATE_RED, 1)
        GPIO.output(LED_STATE_GREEN, 1)
        GPIO.output(LED_STATE_BLUE, 1)
    elif coulor == "OFF":
        GPIO.output(LED_STATE_RED, 0)
        GPIO.output(LED_STATE_GREEN, 0)
        GPIO.output(LED_STATE_BLUE, 0)

# flash RGB LED
def flashStateLED(frequency, repetitions):
    for i in range(repetitions):
        stateLED("BLUE")
        time.sleep(frequency)
        stateLED("CYAN")
        time.sleep(frequency)
        stateLED("GREEN")
        time.sleep(frequency)
        stateLED("YELLOW")
        time.sleep(frequency)
        stateLED("RED")
        time.sleep(frequency)
        stateLED("PURPLE")
        time.sleep(frequency)
        stateLED("WHITE")
        time.sleep(frequency)
        stateLED("BLUE")

#choose LED by playlist name (folder in Player.libraryPath)
def playerLED(playlist, value):
    if playlist == "ALL":
        GPIO.output(LED_TIER, value)
        GPIO.output(LED_MUSIK, value)
        GPIO.output(LED_HOERBUCH, value)
    elif playlist == "tier":
        GPIO.output(LED_TIER, value)
    elif playlist == "musik":
        GPIO.output(LED_MUSIK, value)
    elif playlist == "hoerbuch":
        GPIO.output(LED_HOERBUCH, value)
    return playlist


#run
setup()
freshStart = True               #freshly started
playerLED("ALL", 0)
stateLED("BLUE")


#set volume
mainVolume = 0.01

#set playlists [foldername in Player.libraryPath, number of tracks]
tier = ["tier",13]
musik = ["musik", 12]
hoerbuch = ["hoerbuch", 5]

#main()
while True:
    try:
        if GPIO.input(BUTTON_PAUSE) == GPIO.LOW:
            if freshStart:
                flashStateLED(0.5, 1)
            elif player.isPlaying:
                player.pause()
            else:
                player.resume()
            time.sleep(0.5)
            
        if GPIO.input(BUTTON_TIER) == GPIO.LOW:
            checkForFreshStart = freshStart
            if checkForFreshStart:
                player = Player(tier,mainVolume)
                if player.start():
                    freshStart = False
            elif player.isPlaying:
                if player.playlist == tier[0]:
                    player.nextTrack()
                else:
                    player.switchRunningPlaylist(tier)
            else:
                if player.playlist == tier[0]:
                    player.resume()
                else:
                    player.switchRunningPlaylist(tier)
            time.sleep(0.5)

        if GPIO.input(BUTTON_MUSIK) == GPIO.LOW:
            checkForFreshStart = freshStart
            if checkForFreshStart:
                player = Player(musik, mainVolume)
                if player.start():
                    freshStart = False
            elif player.isPlaying:
                if player.playlist == musik[0]:
                    player.nextTrack()
                else:
                    player.switchRunningPlaylist(musik)
            else:
                if player.playlist == musik[0]:
                    player.resume()
                else:
                    player.switchRunningPlaylist(musik)
            time.sleep(0.5)

        if GPIO.input(BUTTON_HOERBUCH) == GPIO.LOW:
            checkForFreshStart = freshStart
            if checkForFreshStart:
                player = Player(hoerbuch, mainVolume)
                if player.start():
                    freshStart = False
            elif player.isPlaying:
                if player.playlist == hoerbuch[0]:
                    player.nextTrack()
                else:
                    player.switchRunningPlaylist(hoerbuch)
            else:
                if player.playlist == hoerbuch[0]:
                    player.resume()
                else:
                    player.switchRunningPlaylist(hoerbuch)
            time.sleep(0.5)    

        time.sleep(0.1)

    except KeyboardInterrupt:
        player.stop()
        GPIO.cleanup()