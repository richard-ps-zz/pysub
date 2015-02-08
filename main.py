# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
from PyQt4.phonon import Phonon
import sys
import pysrt

import threading


class Player(QMainWindow):

	def __init__(self,parent=None):
		super(Player,self).__init__()
		uic.loadUi("design.ui",self)
		self.subtitle = Subtitle(self)
		self.seekSlider.setMediaObject(self.videoPlayer.mediaObject())
		self.volumeSlider.setAudioOutput(self.videoPlayer.audioOutput())
		self.actionOpenVideo.triggered.connect(self.open_video)
		self.actionOpenSRT.triggered.connect(self.open_subtitle)
		self.set_button_images()
		self.set_button_events()
		
	def set_button_events(self):
		self.pauseButton.clicked.connect(self.pause)
		self.playButton.clicked.connect(self.play)

	def set_button_images(self):
		self.playButton.setIcon(QIcon('./img/play.png'))
		self.playButton.setIconSize(QSize(24,24))
		self.pauseButton.setIcon(QIcon('./img/pause.png'))
		self.pauseButton.setIconSize(QSize(24,24))

	def open_video(self):
		select = "Selecionar Vídeo"
		filter_types = "Todos os Arquivos(*.*);;Avi(.avi);;Mp4(.mp4)"
		video = QFileDialog.getOpenFileName(self,select,"",filter_types)
		self.source = Phonon.MediaSource(video)
		self.videoPlayer.load(self.source)
	
	def open_subtitle(self):
		select = "Selecionar Legenda"
		filter_types = "Todos os Arquivos(*.*);;SRT(.srt)"
		subtitle = QFileDialog.getOpenFileName(self,select,"",filter_types)
		self.subtitle_viewer.insertPlainText(open(subtitle).read().decode("UTF-8"))
		self.subtitle.set_subtitle(pysrt.open(subtitle, encoding='UTF-8'))
	
	def pause(self):
		self.videoPlayer.pause()
	
	def play(self):
		self.videoPlayer.play()
		self.subtitle.start()

class Subtitle(threading.Thread):

	def __init__(self, player):
		threading.Thread.__init__(self)
		self.stop = False
		self.video_player = player.videoPlayer
		self.current_time = player.videoPlayer.currentTime()
		self.label = player.label
		self.current_subtitle = 0
		self.subtitle_time = 0
		self.end_time = 0
		self.subtitle = None

	def set_subtitle(self, subtitle):
		self.subtitle = subtitle
		self.subtitle_time = self.watch_to_miliseconds(self.subtitle[self.current_subtitle].start)
		self.end_time = self.watch_to_miliseconds(self.subtitle[self.current_subtitle].end)

	def run(self):
		while not self.stop:
			#print "CURRENT TIME: " + str(self.current_time)
			#print "SUBTITLE TIME: " + str(self.subtitle_time)
			if self.current_time >= self.subtitle_time:
				self.update_subtitle(self.get_next_subtitle())
				self.current_subtitle += 1
			elif self.current_time >= self.end_time:
				self.erase_subtitle()
			self.update_current_time()

	def stop(self):
		self.stop = True

	def update_current_time(self):
		self.current_time = self.video_player.currentTime()

	def update_subtitle(self, subtitle):
		#print "SETTING SUBTITLE: ", subtitle
		self.label.setText(subtitle)

		watch_start = self.subtitle[self.current_subtitle+1].start
		watch_end = self.subtitle[self.current_subtitle].end

		self.subtitle_time = self.watch_to_miliseconds(watch_start)
		self.end_time = self.watch_to_miliseconds(watch_end)

	def watch_to_miliseconds(self, watch):
		return watch.hours * 3600000 + \
			   watch.minutes * 60000 + \
		       watch.seconds * 1000 + \
		       watch.milliseconds

	def get_next_subtitle(self):
		return self.subtitle[self.current_subtitle].text

	def erase_subtitle(self):
		self.label.setText("")

root = QApplication(sys.argv)
player = Player()
player.show()
sys.exit(root.exec_())
