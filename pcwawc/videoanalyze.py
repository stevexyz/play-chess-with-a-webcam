#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
'''
Created on 2019-12-08

@author: wf
'''
from pcwawc.args import Args
from pcwawc.boardfinder import BoardFinder, Corners
from pcwawc.chessimage import ChessBoardVision
from pcwawc.detectorfactory import MoveDetectorFactory
from pcwawc.eventhandling import Observable
from pcwawc.environment import Environment

import sys

class VideoAnalyzer(Observable):
    """ analyzer for chessboard videos - may be used from command line or web app"""
    def __init__(self,args,vision=None,logger=None):
        super(VideoAnalyzer,self).__init__()
        if vision is None:
            self.vision=ChessBoardVision(args)
        else:
            self.vision=vision
        self.logger=logger    
        self.args=args
        self.debug=args.debug
        if self.debug:
            self.log("Warp: %s" % (args.warpPointList))
  
        # not recording
        self.videopath=None
        self.videoout=None
        
    def open(self):
        self.vision.open(self.args.input)
            
    def close(self):
        if self.videoout is not None:
            self.stopVideoRecording()
        self.vision.close()
           
    def hasImage(self):
        return self.vision.hasImage 
    
    def hasImageSet(self):
        return self.cbImageSet is not None
            
    def isRecording(self):
        return self.videoout is not None        
        
    def startVideoRecording(self,path,filename):
        self.open()
        self.videofilename = filename
        # make sure the path exists
        Environment.checkDir(path)
        self.videopath=path+self.videofilename
        return filename
    
    def stopVideoRecording(self):
        self.videoout.release()
        self.videopath=None
        self.videoout=None  
        return self.videofilename
    
    def videoPause(self):
        ispaused = not self.vision.video.paused()
        self.vision.video.pause(ispaused)
        return ispaused
        
    def analyze(self):
        self.open()
        if self.args.autowarp:
            self.autoWarp()
        while True:
            cbImageSet=self.nextImageSet()
            if cbImageSet is None:
                break
            if self.debug:
                self.vision.video.showImage(cbImageSet.debugImage().image,"debug")
        self.close()    
        
    def nextImageSet(self):    
        self.cbImageSet=self.vision.readChessBoardImage()
        if not self.vision.hasImage:
            return None
        self.processImageSet(self.cbImageSet)
        return self.cbImageSet
            
    def processImageSet(self,cbImageSet):   
        cbImageSet.warpAndRotate(self.args.nowarp) 
        # analyze the board if warping is active
        self.fire(cbImageSet=cbImageSet)
        cbImageSet.prepareGUI()
        # do we need to record?
        if self.videopath is not None:
            cbWarped=cbImageSet.cbWarped
            # is the output open?
            if self.videoout is None:
                # create correctly sized output
                video=self.vision.video
                self.videoout=video.prepareRecording(self.videopath,cbWarped.width,cbWarped.height)
         
            self.videoout.write(cbWarped.image)   
            self.log("wrote frame %d to recording " % (self.vision.video.frames)) 
        return
    
    def findChessBoard(self):
        return self.findTheChessBoard(self.vision.video.frame,self.vision.video)
    
    def findTheChessBoard(self,image,video):
        finder = BoardFinder(image,video=video)
        corners=finder.findOuterCorners()
        # @FIXME - use property title and frame count instead
        title = 'corners_%s.jpg' % (video.fileTimeStamp())
        histograms=finder.getHistograms(image, title, corners)    
        finder.expand(image,title,histograms,corners)
        if self.debug:
            corners.showDebug(image,title)
            finder.showPolygonDebug(image,title,corners)
            finder.showHistogramDebug(histograms,title,corners)
        trapez=corners.trapez8x8
        self.vision.warp.pointList=trapez.tolist()
        self.vision.warp.updatePoints()    
        return corners
    
    def log(self, msg):
        if self.debug:
            if self.logger is not None:
                self.logger.info(msg)
            else:
                print(msg)    
    
    def setDebug(self, debug):
        self.debug=debug
        BoardFinder.debug=debug
        Corners.debug=debug
        self.vision.debug=debug
        if self.moveDetector is not None:
            self.moveDetector.debug=debug
            
    def onMove(self,event):
        move=event.move
        self.vision.board.move(move)
        
    def autoWarp(self):
        self.nextImageSet()
        self.findChessBoard()    
        
    def setUpDetector(self):
        self.moveDetector=MoveDetectorFactory.create(self.args.detector,self.vision)
        self.subscribe(self.moveDetector.onChessBoardImage)
        self.moveDetector.subscribe(self.onMove)
        
    def changeDetector(self,newDetector):
        self.unsubscribe(self.moveDetector.onChessBoardImage)
        self.moveDetector=newDetector
        self.subscribe(self.moveDetector.onChessBoardImage)

if __name__ == '__main__':
    cmdLineArgs = Args("Chessboard Video analyzer")
    args = cmdLineArgs.parse(sys.argv[1:])
    videoAnalyzer=VideoAnalyzer(args)
    videoAnalyzer.setUpDetector()
    videoAnalyzer.setDebug(args.debug)
    videoAnalyzer.analyze()
