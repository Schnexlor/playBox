# playBox1.71.py

from soundplayer import SoundPlayer
import RPi.GPIO as GPIO
import time

class LED(object):
    rgb = None
    coulor = None
    pin = None
    state = 0

    def __init__(self, coulor):
        self.coulor = coulor 
        if coulor == 3:
            self.rgb = []
            self.initRGBLED()
        else:
            self.initLED()

    #set pins of RGBLED[pinRed, pinGreen, pinBlue]
    def initRGBLED(self):
        self.rgb = [5,6,13]
        for i in range(0,3,1):
            GPIO.setup(self.rgb[i],GPIO.OUT)

    def setRGBCoulor(self, r, g, b):
        if not self.rgb == None:
            GPIO.output(self.rgb[0], r)
            GPIO.output(self.rgb[1], g)
            GPIO.output(self.rgb[2], b)
    def flashRGBLED(self, frequency):
        if not self.rgb == None:
            for i in range(0,2,1):
                for j in range(0,2,1):
                    for k in range(0,2,1):
                        self.setRGBCoulor(i, j, k)
                        time.sleep(frequency)
    #set pins of LEDs
    def initLED(self):
        if self.coulor == 0:
            self.pin = 16       #pin red
        elif self.coulor == 1:
            self.pin = 20       #pin green
        elif self.coulor == 2:
            self.pin = 26       #pin blue
        GPIO.setup(self.pin,GPIO.OUT)
        self.setLED(0)
    def setLED(self, state):
        if self.rgb == None:
            GPIO.output(self.pin, state)
    def flashLED(self, frequency, repetitions):
        if self.rgb == None:
            for i in range(0, repetitions, 1):
                for j in range(0,2,1):
                    GPIO.output(self.pin, j)
                    time.sleep(frequency)

class LEDManager(object):
    running = False
    leds = []

    def __init__(self):
        self.running = True

    def add(self, led):
        self.leds.append(led)

    def load(self):
        if playlistOp.isActive():           
            for i in range(0,3,1):
                buttons[i].led.setLED(1)
            buttons[3].led.setRGBCoulor(0,1,0)
        elif volume.isActive():
            buttons[3].led.setRGBCoulor(0,1,0)
            buttons[0].led.setLED(1)
            buttons[1].led.setLED(0)
            buttons[2].led.setLED(1)
        elif player.isActive():
            buttons[player.getCoulor()].led.setLED(1)
            if player.isPlaying():
                buttons[3].led.setRGBCoulor(0,1,1)
            else:
                buttons[3].led.setRGBCoulor(1,1,0)
        else:
            buttons[3].led.setRGBCoulor(0,0,1)


class Button(object):
    pin = None
    coulor = None          #0 := ROT,          1 := BLUE,      2 := GREEN,     3 := WHITE
    led = None

    def __init__(self, pin, coulor):
        GPIO.setup(pin, GPIO.IN, GPIO.PUD_UP)
        self.pin = pin
        self.coulor = coulor
        self.led = LED(coulor)
        ledOp.add(self.led)


    def pushed(self):
        if GPIO.input(self.pin) == GPIO.LOW:
            return True
        else:
            return False

class PlaylistManager(object):
    active = None
    playlistList0 = []
    playlistList1 = []
    playlistList2 = []
    allPlaylists = [playlistList0, playlistList1, playlistList2]
    selection = []
    #playlist contains ["name", number of tracks, played on buttoncoulor]
    def __init__(self):
        self.active = False
        self.selection = [0,0,0]

    def activate(self):
        self.active = True
    def isActive(self):
        return self.active
    def deActivate(self):
        self.active = False
        for i in range(0,3,1):
            buttons[i].led.setLED(0)
        buttons[player.getCoulor()].led.setLED(1)

    def getPlaylist(self, coulor):
        return self.allPlaylists[coulor][self.selection[coulor]]

    def addPlaylist(self, playlist):
        self.allPlaylists[playlist[2]].append(playlist)

    def nextPlaylist(self, coulor):
        if self.selection[coulor] < len(self.allPlaylists[coulor]) - 1:
            self.selection[coulor] += 1
        else:
            self.selection[coulor] = 0
        print("Playlist selection: Red: " + self.getPlaylist(0)[0] + ", Blue: " + self.getPlaylist(1)[0] + ", Green: " + self.getPlaylist(2)[0])
        buttons[coulor].led.flashLED(0.1,1)

    def getByCoulor(self, coulor):
        returnPlaylists = []
        for i in range(0, len(self.allPlaylists),1):
            if self.allPlaylists[i][2] == coulor:
                returnPlaylists[len(returnPlaylists)] = self.allPlaylists[i]
        return returnPlaylists

#player based on SoundPlayer
class Player(object):
    # set libraryPath and type
    libraryPath = "/home/pi/playBox/library/"
    container = ".mp3"    
    playlistName = ""
    max_trackID = 0
    trackID = 0
    volume = 0
    coulor = None
    playing = None
    paused = None
    activePlayer = None
    freshStart = None

    def __init__(self, playlist, volume, playlistCoulor):
        self.playlistName = playlist[0]
        self.max_trackID = playlist[1]
        self.coulor = playlistCoulor
        self.trackID = 0
        self.volume = volume
        self.freshStart = True

    def getCoulor(self):
        return self.coulor

    def isActive(self):
        if not self.activePlayer == None:
            return True
        else:
            return False
    def isPlaying(self):
        return self.playing
    def isPaused(self):
        return self.paused
    def setPause(self):
        self.playing = False
        self.paused = True

    def getFreshStart(self):
        return self.freshStart
    def setFreshStart(self):
        self.freshStart = False

    def setVolume(self, volume):
        self.volume = volume

    def start(self):        
            self.activePlayer = SoundPlayer(self.libraryPath + self.playlistName + "/" + str(self.trackID) + self.container)
            self.setVolume(volume.getVolume())
            self.activePlayer.play(self.volume)
            self.playing = True
            self.paused = False
            if not self.getFreshStart():
                self.setFreshStart()
            print("Playlist " + self.playlistName + ", Track: " + str(self.trackID) + ", Volume: " + str(self.volume) + " started.")
            return True
    def stop(self):
        if self.isActive():
            self.activePlayer.stop()
        buttons[self.getCoulor()].led.setLED(0)      
        self.playlistName = ""            
        self.playing = None
        self.paused = None
    def pause(self):
        self.activePlayer.pause()
        self.setPause()
    def resume(self):
        self.activePlayer.resume()
        self.playing = True
        self.paused = False
          
    def nextTrack(self):
        playlistName = self.playlistName
        self.stop()
        time.sleep(0.2)
        self.playlistName = playlistName
        self.nextTrackID()           
        self.start()
    def lastTrack(self):
        playlistName = self.playlistName
        self.stop()
        time.sleep(0.2)
        self.playlistName = playlistName
        self.lastTrackID()
        self.start()
    def nextTrackID(self):
        trackNr = self.max_trackID - self.trackID
        if trackNr == 1:
            self.trackID = 0
        else:
            self.trackID += 1
    def lastTrackID(self):
        trackNr = self.trackID
        if trackNr == 0:
            self.trackID = self.max_trackID - 1
        else:
            self.trackID -= 1

    def switchRunningPlaylist(self, new_playlist, playlistCoulor):
        self.stop()
        time.sleep(0.2)
        self.playlistName = new_playlist[0]
        self.max_trackID = new_playlist[1]
        self.coulor = playlistCoulor
        self.trackID = 0                
        self.start()
            
    def reset(self):
        if self.isPlaying():
            self.stop()
        self.coulor = None
        self.max_trackID = 0
        self.trackID = 0

class Volume(object):
    volume = 0
    defaultVolume = None
    steps = None
    active = None

	#set default volume between 0 and 1 and set the steps of volume control
    def __init__(self, defaultVolume, steps):
        self.defaultVolume = defaultVolume
        self.volume = defaultVolume
        self.steps = steps
        self.active = False

    def getVolume(self):
        return self.volume
    def isActive(self):
        return self.active
    def activate(self):
        self.active = True    
    def deActivate(self):
        self.active = False
        for i in range(0,3,1):
            buttons[i].led.setLED(0)
        buttons[player.getCoulor()].led.setLED(1)

    def buttonPress(self, coulor):
        if coulor == 0:
            if not self.volume + self.steps >= 0.20:
                self.volume += self.steps
        elif coulor == 1:
            self.volume = self.defaultVolume
        elif coulor == 2:
            if not self.volume - self.steps <= 0:
                self.volume -= self.steps
        player.setVolume(self.volume)
        buttons[coulor].led.flashLED(0.1,1)

class Playlist(object):
    playlist = []
    def __init__(self, playlistName, numberOfTracks, buttonCoulor):
        self.playlist = [playlistName, numberOfTracks, buttonCoulor]
        playlistOp.addPlaylist(self.playlist)

    def get(self):
        return self.playlist

def setup()    
    #initilise Buttons
    redButton = Button(23, 0)
    blueButton = Button(24, 1)
    greenButton = Button(25, 2)
    whiteButton = Button(27, 3)
    #set playlists "foldername in Player.libraryPath" = Playlist(number of tracks, coulor)
    tiere = Playlist("tiere", 13, 0)
    conniKaterMau = Playlist("conniKaterMau",13, 0)
    conniBauernhof = Playlist("conniBauernhof",6, 0)
    conniEinkaufen = Playlist("conniEinkaufen",12, 0)
    youtubeMusik = Playlist("youtubeMusik",12, 1)
    tierlieder = Playlist("tierlieder",20, 1)
    lieselotte = Playlist("lieselotte",19, 2)
    hoerbuchMix = Playlist("hoerbuchMix",5, 2)
    pawPatrol1 = Playlist("pawPatrol1",13, 2)
    neele = Playlist("neele",12, 2)

#run
playlistOp = PlaylistManager()
volume = Volume(0.01, 0.002)
player = Player(["", 0], volume.getVolume(), 0)
ledOp = LEDManager()
GPIO.setmode(GPIO.BCM)
setup()
buttons = [redButton, blueButton, greenButton, whiteButton]

#main()
while True:
    try:
    # switch between selected playlists
        if playlistOp.isActive():
            player.stop()
            #print("playlistOP activ")
            if whiteButton.pushed():
                playlistOp.deActivate()
                time.sleep(0.2)
            else:
                for i in range(0,3,1):
                    if buttons[i].pushed():
                        playlistOp.nextPlaylist(i)
                        time.sleep(0.2)
    # set volume
        elif volume.isActive():
            player.stop()
            #print("volume activ")
            if whiteButton.pushed():
                volume.deActivate()
                time.sleep(0.2)
            else:
                for i in range(0,3,1):
                    if buttons[i].pushed():
                        volume.buttonPress(i)
                        time.sleep(0.2)
    # in case of a fresh start
        elif player.getFreshStart():
            #print("freshStart activ")
            if whiteButton.pushed():
                playlistOp.activate()
                time.sleep(0.2)
            else:
                for i in range(0,3,1):
                    if buttons[i].pushed():
                        player.setFreshStart()
                        player.switchRunningPlaylist(playlistOp.getPlaylist(i), i)
                        time.sleep(0.2)
    #in case of player is paused
        elif player.isPaused():
            #print("player paused")
            if whiteButton.pushed():    
                #Playlistmanager.activate
                if redButton.pushed():
                    playlistOp.activate()
                    time.sleep(0.2)
                #Volume.activate()
                elif greenButton.pushed():
                    volume.activate()
                    time.sleep(0.2)
                #return to player                        
                else:
                    player.resume()
                    time.sleep(0.2)
            else:
                for i in range(0,3,1):
                    if buttons[i].pushed():
                        if player.getCoulor() == i:
                            player.lastTrack()
                            time.sleep(0.2)
                        else:
                            player.switchRunningPlaylist(playlistOp.getPlaylist(i), i)
                            time.sleep(0.2)
    #in case of player is playing
        else:
            #print("player playing")
            if whiteButton.pushed():
                player.pause()
                time.sleep(0.2)
            else:
                for i in range(0,3,1):
                    if buttons[i].pushed():
                        if player.coulor == i:
                            player.nextTrack()
                            time.sleep(0.2)
                        else:
                            player.switchRunningPlaylist(playlistOp.getPlaylist(i), i)
                            time.sleep(0.2)
        ledOp.load()
        time.sleep(0.1)

    except KeyboardInterrupt:
        player.stop()
        GPIO.cleanup()