import subprocess

if (__name__ == "__main__"):
    fdir = r"D:"
    fname = r"RES_2436_752_FPS_60_GL1_10_0_GL2_11_208_GL3_20_192.mp4"
    fpath = fdir + "\\" + fname

    print("Dynamic Image Testing Pattern Beginning")
    SP_PythonVLC = subprocess.Popen(["vlc", "--directx-device={\\.\DISPLAY1}", "--fullscreen", "--play-and-exit", fpath])
    SP_PythonVLC.wait()
    print("Dynamic Image Testing Pattern Ending")
