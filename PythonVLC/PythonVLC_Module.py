import time
import vlc

if (__name__ == "__main__"):
    fdir = r"D:"
    fname = r"Test.mp4"
    fpath = fdir + "\\" + fname

    vlc_instance = vlc.Instance()

    vlc_player = vlc_instance.media_player_new()

    vlc_media = vlc_instance.media_new(fpath)

    vlc_player.set_fullscreen(True)
    vlc_player.set_media(vlc_media)
    vlc_player.play()

    print("Playing")

    while (vlc_player.get_state() != vlc.State.Ended):
        pass
    
    print("Ending")

    exit(0)
