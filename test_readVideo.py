# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Video import Video

def test_ReadVideo():
    video=Video()
    video.open('chessVideo2019-10-17_134753.avi')
    video.play()

test_ReadVideo()
