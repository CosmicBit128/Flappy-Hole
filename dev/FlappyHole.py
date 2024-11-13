import pygame, sys, os, time, math, random, webbrowser
from pygame.locals import *
if sys.platform in ['linux', 'linux2']:
	import subprocess

from libraries.load_img import *

# Initialize pygame
pygame.init()

# Load Sounds
sounds = {
	"point": pygame.mixer.Sound("assets/sounds/point.mp3"),
	"flap": pygame.mixer.Sound("assets/sounds/flap.mp3"),
	"hit": pygame.mixer.Sound("assets/sounds/hit.mp3"),
	"fall": pygame.mixer.Sound("assets/sounds/fall.mp3"),
	"swoosh": pygame.mixer.Sound("assets/sounds/swoosh.mp3")
}

# Game States:
# -1 - Welcome Screen
#  0 - Main Screen
#  1 - Get Ready
#  2 - Playing
#  3 - Game Over
#  4 - Paused
#  5 - Settings
game_state = -1


def lerp(start, end, t):
	return start * (1 - t) + end * t

def write_bin_file(file: str, hex_data: str) -> None:
	# Convert string to data
	bin_data = bytes.fromhex(hex_data.replace(' ', ''))

	# Write data to a file
	with open(file, "wb") as f:
		f.write(bin_data)

def read_bin_file(file: str) -> bytes:
	# Read file
	with open(file, "rb") as f:
		bin_data = f.read()

	return ''.join(format(byte, '02x') for byte in bin_data)

def reset_hi():
	write_bin_file('settings.dat', '53 45 54 54 00 00 48 49 00 00 00 00 4E 4D 00 53 46 58 00 48 42 00')

def reload_sett():
	global hi_score, night_mode, sfx, hitboxes
	
	result = read_bin_file('settings.dat')
	
	hi_score = int(result[16:24], 16)
	night_mode = bool(int(result[28:30]))
	sfx = bool(int(result[36:38]))
	hitboxes = bool(int(result[42:44]))

# sett.dat format:
# 53 45 54 54 00 00 48 49 00 00 00 00 4E 4D 00 53 46 58 00 48 42 00
# S  E  T  T  .  .  H  I  0  0  0  0  N  M  0  S  F  X  0  H  B  0
# Settings\00\00, HiScore 16x0000, Night Mode: False, SFX: False, HitBoxes: False

# Max High Score: 2^32 - 1 (4 294 967 295)	

#write_bin_file('settings.dat', f'53 45 54 54 00 00 48 49 00 00 00 07 4E 4D 00 53 46 58 01 48 42 01')
# Engine
class Engine():
	def __init__(self):
		global hitboxes

		self.clock = pygame.time.Clock()
		self.dt = 0 # Delta Time
		self.ct = 0 # Current Time
		self.cs = 0 # Current Second
		self.time = 0
		self.a_state = 0
		
		self.is_running = True
		
		reload_sett()
	
	def create_window(self, width = 800, height = 600, title = "PyGame Engine Window", resizable = True):
		if resizable:
			window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
		else:
			window = pygame.display.set_mode((width, height))
		pygame.display.set_caption(title)
		
		return window    

	def update(self):
		clk_tck = self.clock.tick(settings['max_fps']) 
		self.dt = round(clk_tck / settings['max_fps'])
		self.cs = clk_tck
		self.ct = pygame.time.get_ticks()
		self.time = self.clock.get_time() / 1000
		
		if self.ct % ((1/5) * 1000) < self.cs:
			self.a_state += 1
		
		self.x_center = (pygame.display.get_surface().get_width() - win_params['width']) / 2
		self.y_center = (pygame.display.get_surface().get_height() - win_params['height']) / 2
	
	def renderer(self):
		pygame.display.flip()
		
	def handle_events(self):
		global game_state, night_mode, sfx, hitboxes
		
		for event in pygame.event.get():
			# Check if window closed
			if event.type == pygame.QUIT:
				self.is_running = False
				
			if event.type == pygame.ACTIVEEVENT:
				if event.state == pygame.APPINPUTFOCUS and not event.gain:
					# Check if the window lost focus
					if game_state == 2:
						game_state = 4
			
			# Check for KeyDown event    
			if event.type == pygame.KEYDOWN:
				
				# If space pressed start game if not started and flap if started
				if event.key == pygame.K_SPACE:
					if game_state == 2:
						#print("Jumped!")
						game.flappy.y_vel = -6
						if sfx:
							pygame.mixer.Sound.play(sounds['flap'])
					elif game_state == 1:
						game_state = 2
						game.flappy.y_vel = -6
						if sfx:
							pygame.mixer.Sound.play(sounds['flap'])
						game.flappy.rect.x = 128
						game.flappy.rect.y = 256
						
				# If ESC pressed, pause / unpause the game
				if event.key == pygame.K_ESCAPE:
					self.pause()
			
			# Check if mouse clicked
			if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
			   
				# If not touching pause button - flap, if touching - pause
				if not pygame.Rect(self.x_center + 12, self.y_center + 12, 26, 28).collidepoint(pygame.mouse.get_pos()): 
					if game_state == 2:
						#print("Jumped!")
						game.flappy.y_vel = -6
						if sfx:
							pygame.mixer.Sound.play(sounds['flap'])
					elif game_state == 1:
						game_state = 2
						game.flappy.y_vel = -6
						if sfx:
							pygame.mixer.Sound.play(sounds['flap'])
						game.flappy.rect.x = 128
						game.flappy.rect.y = 256
				if pygame.Rect(self.x_center + 12, self.y_center + 12, 26, 28).collidepoint(pygame.mouse.get_pos()) and game_state in [2, 4]:
						if game_state == 4:
							game_state = 0
						elif game_state == 2:
							game_state = 4
					
				elif pygame.Rect(self.x_center + 12, self.y_center + 12, 26, 28).collidepoint(pygame.mouse.get_pos()):
					if game_state == 0:
						reload_sett()
						game_state = 5
					elif game_state == 5:
						game_state = 0
					
				if pygame.Rect(self.x_center + win_params['width'] // 2 - 14, self.y_center + 256, 26, 28).collidepoint(pygame.mouse.get_pos()) and game_state == 4:
					self.pause()
						
				# Night Mode Toggle
				if pygame.Rect(self.x_center + win_params['width'] // 2 - 8, self.y_center + win_params['height'] // 2 - 24, 16, 16).collidepoint(pygame.mouse.get_pos()) and game_state == 5:
					if night_mode:
						night_mode = False
						write_bin_file('settings.dat', f'53 45 54 54 00 00 48 49 {format(hi_score, '08X')} 4E 4D 00 53 46 58 {'0' + str(int(sfx))} 48 42 {'0' + str(int(hitboxes))}')
					else:
						night_mode = True
						write_bin_file('settings.dat', f'53 45 54 54 00 00 48 49 {format(hi_score, '08X')} 4E 4D 01 53 46 58 {'0' + str(int(sfx))} 48 42 {'0' + str(int(hitboxes))}')
						
				# Sound Effects Toggle
				if pygame.Rect(self.x_center + win_params['width'] // 2 - 8, self.y_center + win_params['height'] // 2 + 24, 16, 16).collidepoint(pygame.mouse.get_pos()) and game_state == 5:
					if sfx:
						sfx = False
						write_bin_file('settings.dat', f'53 45 54 54 00 00 48 49 {format(hi_score, '08X')} 4E 4D {'0' + str(int(night_mode))} 53 46 58 00 48 42 {'0' + str(int(hitboxes))}')
					else:
						sfx = True
						write_bin_file('settings.dat', f'53 45 54 54 00 00 48 49 {format(hi_score, '08X')} 4E 4D {'0' + str(int(night_mode))} 53 46 58 01 48 42 {'0' + str(int(hitboxes))}')
						
				# Hitbox Toggle
				if pygame.Rect(eng.x_center + win_params['width'] - 2, eng.y_center + win_params['height'] - 2, 2, 2).collidepoint(pygame.mouse.get_pos()) and game_state == 5:
					if hitboxes:
						hitboxes = False
						write_bin_file('settings.dat', f'53 45 54 54 00 00 48 49 {format(hi_score, '08X')} 4E 4D {'0' + str(int(night_mode))} 53 46 58 {'0' + str(int(sfx))} 48 42 00')
					else:
						hitboxes = True
						write_bin_file('settings.dat', f'53 45 54 54 00 00 48 49 {format(hi_score, '08X')} 4E 4D {'0' + str(int(night_mode))} 53 46 58 {'0' + str(int(sfx))} 48 42 01')
						
				if pygame.Rect(eng.x_center + win_params['width'] // 2 + 4, eng.y_center + 366, 80, 28).collidepoint(pygame.mouse.get_pos()) and game_state == 0:
					webbrowser.open('https://CosmicByte128.itch.io/flappy-hole')
				

				# Finally added!
				if pygame.Rect(eng.x_center + win_params['width'] // 2 - 40, eng.y_center + 366, 80, 28).collidepoint(pygame.mouse.get_pos()) and game_state == 3:
					# Create surface
					share_img_surface = pygame.Surface((96, 116))
					
					# Put everything onto the surface
					if game.flappy.score > hi_score:
						share_img_surface.blit(load_img("assets/textures/new_best.png"), (0, 0))
					else:
						share_img_surface.blit(load_img("assets/textures/score.png"), (0, 0))
			
					game.render_score(share_img_surface, game.flappy.score, 32, True)
					game.render_score(share_img_surface, max(hi_score, game.flappy.score), 74, True)
					
					# Create temp file
					pygame.image.save(share_img_surface, f'/tmp/temp.bmp')

					# Put into clipboard
					if sys.platform in ['linux', 'linux2']:
						with open(f'/tmp/temp.bmp', 'rb') as f:
							subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/bmp'], input=f.read())
						
						# Remove temp file
						os.remove(f'/tmp/temp.bmp')
					elif sys.platform == 'win32':
						with open(f'{os.environ.get('TEMP')}/temp.bmp', 'rb') as f:
							pygame.scrap.put(pygame.SCRAP_BMP, f.read())
						
						# Remove temp file
						os.remove(f'{os.environ.get('TEMP')}/temp.bmp')
					
					game.start_time = time.time()
					game.display_copied = True
					
	
	def pause(self):
		global game_state

		if game_state == 4:
			game_state = 2
		elif game_state == 2:
			game_state = 4
				
	def run(self):
		while self.is_running:
			self.handle_events()
			self.update()
			self.mainloop(window)
			game.flappy.update()
			window.blit(load_img('assets/textures/cursor.png'), pygame.mouse.get_pos())
			self.renderer()
		pygame.quit()
		sys.exit()
	
	def mainloop(self, window):
		global game_state, night_mode, sfx

		game.update()
		game.render()
		
		# Check window size
		if window.get_width() < win_params['width'] or window.get_height() < win_params['height']:
			window = eng.create_window(max(win_params['width'], window.get_width()), max(win_params['height'], window.get_height()), win_params['title'], False)
		

		match game_state:
			case -1:
				window.blit(load_img('assets/textures/welcome.png'), (0, 0))
				if self.ct >= 800 and self.ct < 4000:
					game_state = 0
			case 0:
				window.blit(load_img(f'assets/textures/logo{night_mode*'_dark'}.png'), (self.x_center + win_params['width'] // 2 - 108, self.y_center + 128 + (6 * math.sin(eng.ct / 25 / 9))))
					
				window.blit(load_img('assets/textures/copyright.png', None, night_mode), (self.x_center + 4, self.y_center + win_params['height'] - 22))
			
				if pygame.Rect(self.x_center + 12, self.y_center + 12, 26, 28).collidepoint(pygame.mouse.get_pos()):
					window.blit(load_img('assets/textures/buttons.png', (3 * 13, 0, 13, 13)), (self.x_center + 12, self.y_center + 14))
				else:
					window.blit(load_img('assets/textures/buttons.png', (3 * 13, 0, 13, 14)), (self.x_center + 12, self.y_center + 12))
			
				if not pygame.Rect(eng.x_center + win_params['width'] // 2 - 84, eng.y_center + 366, 80, 28).collidepoint(pygame.mouse.get_pos()):
					window.blit(load_img('assets/textures/gui_buttons.png', (0, 70, 40, 14)), (eng.x_center + win_params['width'] // 2 - 84, eng.y_center + 364))
				else:
					window.blit(load_img('assets/textures/gui_buttons.png', (0, 70, 40, 13)), (eng.x_center + win_params['width'] // 2 - 84, eng.y_center + 366))
					if pygame.mouse.get_pressed()[0]:
						game_state = 1
						game.pipe_x = [0, 320]
						game.flappy.rect.x = 128
						game.flappy.rect.y = 256
			
				if not pygame.Rect(eng.x_center + win_params['width'] // 2 + 4, eng.y_center + 366, 80, 28).collidepoint(pygame.mouse.get_pos()):
					window.blit(load_img('assets/textures/gui_buttons.png', (0, 3 * 14, 40, 14)), (eng.x_center + win_params['width'] // 2 + 4, eng.y_center + 364))
				else:
					window.blit(load_img('assets/textures/gui_buttons.png', (0, 3 * 14, 40, 13)), (eng.x_center + win_params['width'] // 2 + 4, eng.y_center + 366))
			case 1:
				window.blit(load_img('assets/textures/get_ready.png'), (self.x_center + win_params['width'] // 2 - 87, self.y_center + 205))
				window.blit(load_img('assets/textures/tutorial.png'), (self.x_center + win_params['width'] // 2 - 85, self.y_center + 296))
				
			case 2:
				if pygame.Rect(self.x_center + 12, self.y_center + 12, 26, 28).collidepoint(pygame.mouse.get_pos()):
					window.blit(load_img('assets/textures/buttons.png', (0 * 13, 0, 13, 13)), (self.x_center + 12, self.y_center + 14))
				else:
					window.blit(load_img('assets/textures/buttons.png', (0 * 13, 0, 13, 14)), (self.x_center + 12, self.y_center + 12))
					
			case 4:
				# Darken the area
				dark = pygame.Surface((win_params['width'], win_params['height']))
				dark.fill((0, 0, 0))
				dark.set_alpha(64)
				window.blit(dark, (self.x_center, self. y_center))
			
				# Show "PAUSED" text
				window.blit(load_img('assets/textures/paused.png', False, False, (4, 4)), (self.x_center + win_params['width'] // 2 - 56, self.y_center + 180))
			
				if pygame.Rect(self.x_center + win_params['width'] // 2 - 14, self.y_center + 258, 26, 28).collidepoint(pygame.mouse.get_pos()):
					window.blit(load_img('assets/textures/buttons.png', (1 * 13, 0, 13, 13)), (self.x_center + win_params['width'] // 2 - 14, self.y_center + 258))
				else:
					window.blit(load_img('assets/textures/buttons.png', (1 * 13, 0, 13, 14)), (self.x_center + win_params['width'] // 2 - 14, self.y_center + 256))
			
				if pygame.Rect(self.x_center + 12, self.y_center + 12, 26, 28).collidepoint(pygame.mouse.get_pos()):
					window.blit(load_img('assets/textures/buttons.png', (2 * 13, 0, 13, 13)), (self.x_center + 12, self.y_center + 14))
				else:
					window.blit(load_img('assets/textures/buttons.png', (2 * 13, 0, 13, 14)), (self.x_center + 12, self.y_center + 12))
					
			case 5:
				if pygame.Rect(self.x_center + 12, self.y_center + 12, 26, 28).collidepoint(pygame.mouse.get_pos()):
					window.blit(load_img('assets/textures/buttons.png', (4 * 13, 0, 13, 13)), (self.x_center + 12, self.y_center + 14))
				else:
					window.blit(load_img('assets/textures/buttons.png', (4 * 13, 0, 13, 14)), (self.x_center + 12, self.y_center + 12))
					
				window.blit(load_img('assets/textures/settings.png'), (self.x_center + win_params['width'] // 2 - 64, self.y_center + win_params['height'] // 2 - 58))
				
				if not night_mode:
					window.blit(load_img('assets/textures/checkbox.png', (0, 0, 8, 8)), (self.x_center + win_params['width'] // 2 - 8, self.y_center + win_params['height'] // 2 - 24))
				else:
					window.blit(load_img('assets/textures/checkbox.png', (8, 0, 8, 8)), (self.x_center + win_params['width'] // 2 - 8, self.y_center + win_params['height'] // 2 - 24))
				
				if not sfx:
					window.blit(load_img('assets/textures/checkbox.png', (0, 0, 8, 8)), (self.x_center + win_params['width'] // 2 - 8, self.y_center + win_params['height'] // 2 + 24))
				else:
					window.blit(load_img('assets/textures/checkbox.png', (8, 0, 8, 8)), (self.x_center + win_params['width'] // 2 - 8, self.y_center + win_params['height'] // 2 + 24))
					
				if not hitboxes:
					pygame.draw.rect(window, (255, 0, 0), pygame.Rect(eng.x_center + win_params['width'] - 2, eng.y_center + win_params['height'] - 2, 2, 2))
				else:
					pygame.draw.rect(window, (0, 255, 0), pygame.Rect(eng.x_center + win_params['width'] - 2, eng.y_center + win_params['height'] - 2, 2, 2))
				
		
# Player Class
class Flappy(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		
		# Set Flappy image and position
		self.image = load_img('assets/textures/flappy.png', (0, eng.a_state % 3 * 12, 17, 12))
		self.rect = self.image.get_rect()
		self.rect.x = 128
		self.rect.y = 256
		
		self.y_vel = 0 # Y Velocity
		
		self.ded_played = False # Check if death sound played
		
		self.gravity = -0.4 # Player gravity
		
		self.score = 0
		self.dead = False
		
		#self.new_mechanics = True
		
	def update(self):
		super().update()
		
		global game_state, hitboxes

		if game_state == 0:
			self.rect.x = 418
			self.rect.y = 136 + (6 * math.sin(eng.ct / 25 / 9))
			self.y_vel = 0
			
		if game_state == 2:
			self.image = load_img('assets/textures/flappy.png', (0, eng.a_state % 3 * 12, 17, 12))
			
			self.y_vel -= self.gravity
			self.rect.y += self.y_vel * eng.dt
			
			if self.rect.y < 112:
				self.rect.y = 112
				self.y_vel = 0

		#if not self.new_mechanics:
		self.pipe_rect = [pygame.Rect(game.pipe_x[0] + win_params['width'], 394, 52, 8), pygame.Rect(game.pipe_x[1] + win_params['width'], 394, 52, 8)]
		self.pipe_mrect = [pygame.Rect(game.pipe_x[0] + win_params['width'] + 23, 394, 4, 8), pygame.Rect(game.pipe_x[1] + win_params['width'] + 23, 394, 4, 8)]

		if self.rect.colliderect(self.pipe_mrect[0]) or self.rect.y >= 370 and self.rect.colliderect(self.pipe_mrect[1]):
			self.rect.y = 112
			self.score += 1
			if sfx:
				pygame.mixer.Sound.play(sounds['point'])
			
		if self.rect.colliderect(self.pipe_rect[1]) and not self.rect.colliderect(self.pipe_mrect[1]) or self.rect.colliderect(self.pipe_rect[0]) and not self.rect.colliderect(self.pipe_mrect[0]) or self.rect.y >= 376:
			while self.rect.colliderect(self.pipe_rect[0]) and not self.rect.colliderect(self.pipe_mrect[0]) or self.rect.colliderect(self.pipe_rect[1]) and not self.rect.colliderect(self.pipe_mrect[1]) or self.rect.y >= 376:
				self.rect.y -= 1
			game_state = 3
			if not self.ded_played:
				sounds['hit'].play()
				game.shake_screen()
				self.ded_played = True
					
		'''else:
			self.pipe_sides = [pygame.Rect(game.pipe_x[0] + win_params['width'], 370, 4, 24), pygame.Rect(game.pipe_x[0] + win_params['width'] + 48, 370, 4, 24), pygame.Rect(game.pipe_x[1] + win_params['width'], 370, 4, 24), pygame.Rect(game.pipe_x[1] + win_params['width'] + 48, 370, 4, 24)]
			collide = False
			for rect in self.pipe_sides:
				if self.rect.colliderect(rect):
					collide = True
				
			if collide:
				while collide:
					self.rect.y -= 1
					self.pipe_sides = [pygame.Rect(game.pipe_x[0], 370, 4, 24), pygame.Rect(game.pipe_x[0] + 48, 370, 4, 24), pygame.Rect(game.pipe_x[1], 370, 4, 24), pygame.Rect(game.pipe_x[1] + 48, 370, 4, 24)]
					collide = False
					for rect in self.pipe_sides:
						if self.rect.colliderect(rect):
							collide = True
				game_state = 3
				if not self.ded_played:
					sounds['hit'].play()
					game.shake_screen()
					self.ded_played = True
					
			elif self.rect.colliderect(pygame.Rect(game.pipe_x[0] + 4, 394, 44, 8)):
				self.rect.y = 112
				self.score += 1
				if sfx:
					pygame.mixer.Sound.play(sounds['point'])'''
		
		#print(str(round(eng.clock.get_fps() * 100) / 100) + " | " + str(round(self.y_vel * 10) / 10) + " | " + str(eng.a_state))

class GameSystem():
	def __init__(self, window):
		self.window = window
		self.bg_x = 0
		self.gnd_x = 0
		self.map_x = 0
		self.pipe_x = [0, 320]

		self.dx = 0
		self.dy = 0
		
		self.speed = 4
		self.flappy = Flappy()
		
		self.display_copied = False
		self.start_time = None
	
	def update(self):
		if game_state == 2:
			self.pipe_x[0] -= self.speed * eng.dt
			self.pipe_x[1] -= self.speed * eng.dt
		
		if game_state in [1, 2]:
			self.bg_x -= self.speed / 4 * eng.dt
			self.gnd_x -= self.speed * eng.dt
		
		if self.bg_x <= -278:
			self.bg_x = 0
			
		if self.gnd_x <= -308:
			self.gnd_x = 0
			
		if self.pipe_x[0] <= -win_params['width'] - 52:
			self.pipe_x[0] = random.randint(0, 24)
			
		if self.pipe_x[1] <= -win_params['width'] - 52:
			self.pipe_x[1] = random.randint(0, 24)

	def render(self):
		global game_state, hi_score, night_mode, sfx, hitboxes

		self.window.fill(settings['background'])
		
		if hitboxes:
			pygame.draw.line(self.window, (255, 0, 0), (eng.x_center, eng.y_center), (eng.x_center + win_params['width'], eng.y_center))

		# Draw Background
		for i in range(4):
			self.window.blit(load_img(f'assets/textures/{night_mode*'night_'}backdrop.png'), (eng.x_center + (i * 278) + self.bg_x + self.dx, eng.y_center + self.dy))
		
		# Draw Flappy
		if 0 <= game_state <= 4:
			self.window.blit(pygame.transform.rotate(self.flappy.image, -4 * self.flappy.y_vel), (self.flappy.rect.topleft[0] + eng.x_center, self.flappy.rect.topleft[1] + eng.y_center))

		# Draw Pipe 1
		self.window.blit(pygame.transform.flip(load_img('assets/textures/pipe.png'), False, True), (eng.x_center + round(self.pipe_x[0]) + win_params['width'], eng.y_center))
		self.window.blit(load_img('assets/textures/pipe.png'), (eng.x_center + self.pipe_x[0] + win_params['width'], eng.y_center + 370))

		# Draw Pipe 2
		self.window.blit(pygame.transform.flip(load_img('assets/textures/pipe.png'), False, True), (eng.x_center + self.pipe_x[1] + win_params['width'], eng.y_center))
		self.window.blit(load_img('assets/textures/pipe.png'), (eng.x_center + self.pipe_x[1] + win_params['width'], eng.y_center + 370))
		
		# Draw Ground
		for i in range(4):
			self.window.blit(pygame.transform.flip(load_img('assets/textures/ground.png', None, night_mode), False, True), (eng.x_center + (i * 308) + self.gnd_x + self.dx, eng.y_center + self.dy))
			self.window.blit(load_img('assets/textures/ground.png', None, night_mode), (eng.x_center + i * 308 + self.gnd_x + self.dx, eng.y_center + 400 + self.dy))
		
		# Cover sides of window
		# If you know what this is, then I guess you can enable this... (but then you will need to enable the window resize)
		#pygame.draw.rect(self.window, settings['background'], pygame.Rect(0, 0, eng.x_center, pygame.display.get_surface().get_height()))
		#pygame.draw.rect(self.window, settings['background'], pygame.Rect(window.get_width() - eng.x_center, 0, eng.x_center, pygame.display.get_surface().get_height()))
	
		# Render score
		if game_state == 2:
			self.render_score(self.window, self.flappy.score)
		
		# If GameOver flag set to True, display "Game Over" text
		if game_state == 3:
			window.blit(load_img("assets/textures/game_over.png"), (eng.x_center + win_params['width'] // 2 - 94, eng.y_center + 128))
			
			if self.flappy.score > hi_score:
				window.blit(load_img("assets/textures/new_best.png"), (eng.x_center + win_params['width'] // 2 - 48, eng.y_center + 205))
				#print(str(self.flappy.score.to_bytes(2, 'big')).replace('\\x', '').replace('b', '', 1).replace('\'', ''))
			else:
				window.blit(load_img("assets/textures/score.png"), (eng.x_center + win_params['width'] // 2 - 48, eng.y_center + 205))
				
			self.render_score(self.window, self.flappy.score, 238, True)
			self.render_score(self.window, max(hi_score, self.flappy.score), 282, True)


			if not pygame.Rect(eng.x_center + win_params['width'] // 2 - 84, eng.y_center + 332, 80, 28).collidepoint(pygame.mouse.get_pos()):
				window.blit(load_img('assets/textures/gui_buttons.png', (0, 14, 40, 14)), (eng.x_center + win_params['width'] // 2 - 84 + self.dx, eng.y_center + 332 + self.dy))
			else:
				if pygame.mouse.get_pressed()[0]:
					if sfx:
						sounds['swoosh'].play()
					self.flappy.rect.x = 128
					self.flappy.rect.y = 256
					self.flappy.y_vel = 0
					self.flappy.ded_played = False
					self.bg_x = 0
					self.gnd_x = 0
					self.pipe_x = [0, 320]
					game_state = 1
					
					if self.flappy.score > hi_score:
						hi_score = self.flappy.score
						print(format(hi_score, '08X'))
						write_bin_file('settings.dat', f'53 45 54 54 00 00 48 49 {format(hi_score, '08X')} 4E 4D {'0' + str(int(night_mode))} 53 46 58 {'0' + str(int(sfx))} 48 42 {'0' + str(int(hitboxes))}')
						reload_sett()
						
					self.flappy.score = 0
						
				window.blit(load_img('assets/textures/gui_buttons.png', (0, 14, 40, 13)), (eng.x_center + win_params['width'] // 2 - 84 + self.dx, eng.y_center + 334 + self.dy))
				

			if not pygame.Rect(eng.x_center + win_params['width'] // 2 + 4, eng.y_center + 332, 80, 28).collidepoint(pygame.mouse.get_pos()):
				window.blit(load_img('assets/textures/gui_buttons.png', (0, 0, 40, 14)), (eng.x_center + win_params['width'] // 2 + 4 + self.dx, eng.y_center + 332 + self.dy))
			else:
				if pygame.mouse.get_pressed()[0]:
					game_state = 0
					if sfx:
						sounds['swoosh'].play()
					
					if self.flappy.score > hi_score:
						hi_score = self.flappy.score
						write_bin_file('settings.dat', f'53 45 54 54 00 00 48 49 {format(hi_score, '08X')} 4E 4D {'0' + str(int(night_mode))} 53 46 58 {'0' + str(int(sfx))} 48 42 {'0' + str(int(hitboxes))}')
						reload_sett()
						
					self.flappy.score = 0
					self.flappy.ded_played = False
					self.pipe_x = [0, 320]
					if sfx:
						sounds['swoosh'].play()
				window.blit(load_img('assets/textures/gui_buttons.png', (0, 0, 40, 13)), (eng.x_center + win_params['width'] // 2 + 4 + self.dx, eng.y_center + 334 + self.dy))
				
			if not pygame.Rect(eng.x_center + win_params['width'] // 2 - 40, eng.y_center + 366, 80, 28).collidepoint(pygame.mouse.get_pos()):
				window.blit(load_img('assets/textures/gui_buttons.png', (0, 56, 40, 14)), (eng.x_center + win_params['width'] // 2 - 40 + self.dx, eng.y_center + 364 + self.dy))
			else:
				window.blit(load_img('assets/textures/gui_buttons.png', (0, 56, 40, 13)), (eng.x_center + win_params['width'] // 2 - 40 + self.dx, eng.y_center + 366 + self.dy))

			#pygame.draw.line(self.window, (0, 255, 0), (eng.x_center + win_params['width'] // 2 - 94 + load_img("assets/textures/game_over.png").get_width() // 2, 112), (eng.x_center + eng.x_center + win_params['width'] // 2 - 94 + load_img("assets/textures/game_over.png").get_width() // 2, 180))
			#pygame.draw.line(self.window, (255, 0, 0), (320, 0), (320, 512))
				
			if self.display_copied:
				window.blit(load_img('assets/textures/copied.png'), (window.get_width() // 2 - 123, 96))
				if not time.time() - self.start_time < 1:
					self.display_copied = False
					


		###########################
		###### DRAW HITBOXES ######
		###########################
		
		if hitboxes:
			# Pipe hitboxes
			pygame.draw.rect(window, (255, 255, 0), pygame.Rect(game.pipe_x[0] + win_params['width'] + eng.x_center, eng.y_center + 394, 52, 8), 1)
			pygame.draw.rect(window, (255, 255, 0), pygame.Rect(game.pipe_x[1] + win_params['width'] + eng.x_center, eng.y_center + 394, 52, 8), 1)
			pygame.draw.rect(window, (255, 0, 255), pygame.Rect(game.pipe_x[0] + win_params['width'] + 23 + eng.x_center, eng.y_center + 394, 4, 8), 1)
			pygame.draw.rect(window, (255, 0, 255), pygame.Rect(game.pipe_x[1] + win_params['width'] + 23 + eng.x_center, eng.y_center + 394, 4, 8), 1)
			
			pygame.draw.rect(self.window, (0, 255, 255), pygame.Rect(eng.x_center + self.pipe_x[0] + win_params['width'], eng.y_center, 52, 142), 1)
			pygame.draw.rect(self.window, (0, 255, 255), pygame.Rect(eng.x_center + self.pipe_x[0] + win_params['width'], eng.y_center + 370, 52, 142), 1)
			
			pygame.draw.rect(self.window, (0, 255, 255), pygame.Rect(eng.x_center + self.pipe_x[1] + win_params['width'], eng.y_center, 52, 142), 1)
			pygame.draw.rect(self.window, (0, 255, 255), pygame.Rect(eng.x_center + self.pipe_x[1] + win_params['width'], eng.y_center + 370, 52, 142), 1)
				
			# Flappy Hitboxes
			if not game_state == 5: 
				pygame.draw.rect(window, (255, 0, 0), pygame.Rect(self.flappy.rect.x + eng.x_center, self.flappy.rect.y + eng.y_center, self.flappy.rect.w, self.flappy.rect.h), 1)
				pygame.draw.line(window, (255, 255, 255), (eng.x_center + self.flappy.rect.x + 17, eng.y_center + self.flappy.rect.y + 12), ((eng.x_center + self.flappy.rect.x + 17) + 32 * math.cos(math.radians(4 * self.flappy.y_vel)), (eng.y_center + self.flappy.rect.y + 12) + 32 * math.sin(math.radians(4 * self.flappy.y_vel))))
			
			# Background Hitboxes
			for i in range(4):
				pygame.draw.rect(self.window, (0, 255, 0), pygame.Rect(eng.x_center + (i * 284) + self.bg_x, eng.y_center, 288, 512), 1)
				
			# Ground Hitboxes
			pygame.draw.line(self.window, (255, 0, 0), (eng.x_center, eng.y_center + 112), (eng.x_center + win_params['width'], eng.y_center + 112))
			pygame.draw.line(self.window, (255, 0, 0), (eng.x_center, eng.y_center + 399), (eng.x_center + win_params['width'], eng.y_center + 399))

		
	def render_score(self, surface: pygame.Surface, score: int, y: int = 128, small: bool = False, center: bool = True):
		score_str = str(score)
		
		offset = 3

		if small:
			digit_width = 3 * 6 # Height: 7
		else:
			digit_width = 3 * 7 # Height: 10
		
		total_width = len(score_str) * (digit_width + 2)
		
		x = (surface.get_width() - (total_width + (len(score_str) - 1) * offset)) // 2

		i = 0
		for digit_str in score_str:

			digit = int(digit_str)
			
			if small:
				surface.blit(all_small_digits[digit], (x, eng.y_center + y))
				if hitboxes:
					pygame.draw.rect(self.window, (0, 255, 255), pygame.Rect(x, eng.y_center + y, digit_width, 21), 1)
			else:
				surface.blit(all_digits[digit], (x, eng.y_center + y))
				if hitboxes:
					pygame.draw.rect(self.window, (0, 255, 255), pygame.Rect(x, eng.y_center + y, digit_width, 30), 1)
		
			
			#print(f'/{digit_str}/')
			x += digit_width + offset
			i += 1
			
	def shake_screen(self):
		shake_intensity = 2
		shake_duration = 0.2  # in seconds
		start_time = time.time()

		while time.time() - start_time < shake_duration:
			self.dx = random.randint(-shake_intensity, shake_intensity)
			self.dy = random.randint(-shake_intensity, shake_intensity)
			self.render()
			if time.time() - start_time < shake_duration / 2:
				wc = pygame.Surface((win_params['width'], win_params['height'])) # White Cover :D
				wc.fill((255, 255, 255))
				wc.set_alpha(lerp(0, 510, (time.time() - start_time) * 5))
				window.blit(wc, (eng.x_center + self.dx, eng.y_center + self.dy))
			else:
				wc = pygame.Surface((win_params['width'], win_params['height'])) # White Cover :D
				wc.fill((255, 255, 255))
				wc.set_alpha(lerp(510, 0, (time.time() - start_time) * 5))
				window.blit(wc, (eng.x_center + self.dx, eng.y_center + self.dy))
			eng.renderer()
		self.dx = 0
		self.dy = 0


if __name__=='__main__':
	pygame.mouse.set_visible(False)

	eng = Engine()
	win_params = {
		"width": 640,
		"height": 512,
		"title": "FlappyHole"
	}
	window = eng.create_window(win_params['width'], win_params['height'], win_params['title'], False)
	pygame.display.set_icon(load_img('assets/textures/icon.png'))

	# Initialize scrap module
	pygame.scrap.init()

	game = GameSystem(window)

	# Game Variables
	score = 0

	settings = {
		"max_fps": 30,
		"background": (48, 48, 48)
	}

	# Rendering
	all_digits = [load_img('assets/textures/digits.png', (n * 7, 0, 7, 10), False, (3, 3)) for n in range(10)]
	all_small_digits = [load_img('assets/textures/small_digits.png', (n * 6, 0, 6, 7), False, (3, 3)) for n in range(10)]

	eng.run()
		
	# Get any digit: load_img('assets/textures/digits.png', (n * 7, 0, 7, 10))
	# Get any small digit: load_img('assets/textures/small_digits.png', (n * 6, 0, 6, 7))
		
	# Get any flappy: load_img('assets/textures/flappy.png', (0, n * 12, 17, 12))

	# Get any button: load_img('assets/textures/gui_buttons.png', (0, n * 14, 40, 14))

	# Get any checkbox: load_img('assets/textures/checkbox.png', (0, n * 8, 8, 8))
