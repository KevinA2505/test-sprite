# SpriteGame – versión con sprites direccionales
# ================================================
# Requisitos: Python 3.8+ y `pip install pygame` (2.5 o superior).
# Coloca estos archivos en el mismo directorio:
# - Hope_walking_right_sprite.png (caminar lateral)
# - Hope_walking_back_sprite.png (caminar hacia arriba)
# - Hope_walking_front_sprite.png (caminar hacia abajo)

from pathlib import Path
import sys

import pygame

# --------------------------- Configuración global --------------------------- #
WIDTH, HEIGHT = 800, 600
FPS = 60

# Archivos de sprites direccionales
SPRITE_RIGHT = Path(__file__).with_name("Hope_walking_right_sprite.png")
SPRITE_BACK = Path(__file__).with_name("Hope_walking_back_sprite.png") 
SPRITE_FRONT = Path(__file__).with_name("Hope_walking_front_sprite.png")

FRAME_COUNT = 8
FRAME_W, FRAME_H = 256, 256  # Asumimos 256x256 por frame
SCALE = 0.3  # Sprite pequeño (30% del tamaño original)
SPEED = 200
FRAME_TIME = 0.10

# --------------------------- Clase Player ---------------------------------- #
class Player:
    """Gestiona posición, animación y entrada del personaje con sprites direccionales."""

    def __init__(self, sprite_sheets):
        # Cargar todos los sprites direccionales
        self.sprite_frames = {}
        
        # Cargar sprite para movimiento lateral (derecha)
        if 'right' in sprite_sheets:
            self.sprite_frames['right'] = self.load_sprite_frames(sprite_sheets['right'])
            self.sprite_frames['left'] = self.sprite_frames['right']  # Usamos flip para izquierda
        
        # Cargar sprite para movimiento hacia arriba
        if 'up' in sprite_sheets:
            self.sprite_frames['up'] = self.load_sprite_frames(sprite_sheets['up'])
        
        # Cargar sprite para movimiento hacia abajo
        if 'down' in sprite_sheets:
            self.sprite_frames['down'] = self.load_sprite_frames(sprite_sheets['down'])
        
        # Sprite por defecto
        self.current_direction = 'down'
        if 'down' not in self.sprite_frames and 'right' in self.sprite_frames:
            self.current_direction = 'right'
        
        # Posición inicial (centrado)
        if self.sprite_frames:
            first_frames = list(self.sprite_frames.values())[0]
            frame_size = first_frames[0].get_size()
            self.x = (WIDTH - frame_size[0]) / 2
            self.y = (HEIGHT - frame_size[1]) / 2
        
        print(f"Player initialized with directions: {list(self.sprite_frames.keys())}")

        self._elapsed = 0.0
        self._frame_index = 0
        self._moving = False
        self._last_horizontal_dir = 'right'  # Para recordar si miraba izq o der

    def load_sprite_frames(self, sheet):
        """Carga y procesa los frames de un sprite sheet."""
        print(f"Loading sprite sheet: {sheet.get_size()}")
        sheet_w, sheet_h = sheet.get_size()
        
        # Calcular dimensiones reales
        actual_frame_w = sheet_w // FRAME_COUNT
        actual_frame_h = sheet_h
        
        frames = []
        for i in range(FRAME_COUNT):
            try:
                x_pos = i * actual_frame_w
                if x_pos + actual_frame_w > sheet_w:
                    break
                
                frame_rect = pygame.Rect(x_pos, 0, actual_frame_w, actual_frame_h)
                frame = sheet.subsurface(frame_rect).convert_alpha()
                
                # Escalar
                if SCALE != 1.0:
                    dest_w = int(actual_frame_w * SCALE)
                    dest_h = int(actual_frame_h * SCALE)
                    frame = pygame.transform.scale(frame, (dest_w, dest_h))
                
                frames.append(frame)
                
            except Exception as e:
                print(f"Error extracting frame {i}: {e}")
                break
        
        return frames if frames else [self.create_emergency_frame()]

    def create_emergency_frame(self):
        """Crea un frame de emergencia si falla la carga."""
        emergency_frame = pygame.Surface((int(64 * SCALE), int(64 * SCALE)))
        emergency_frame.fill((255, 0, 0))
        return emergency_frame

    def handle_input(self, dt: float):
        keys = pygame.key.get_pressed()
        dx, dy = 0.0, 0.0
        new_direction = self.current_direction
        
        # Determinar movimiento y dirección del sprite
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= SPEED * dt
            new_direction = 'left'
            self._last_horizontal_dir = 'left'
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += SPEED * dt
            new_direction = 'right'
            self._last_horizontal_dir = 'right'
        
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= SPEED * dt
            new_direction = 'up'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += SPEED * dt
            new_direction = 'down'
        
        # Si hay movimiento diagonal, priorizar vertical
        if dy != 0.0:
            if dy < 0:
                new_direction = 'up'
            else:
                new_direction = 'down'
        elif dx != 0.0:
            # Solo cambiar dirección horizontal si no hay movimiento vertical
            new_direction = 'left' if dx < 0 else 'right'
        
        # Cambiar sprite si la dirección cambió y tenemos el sprite disponible
        if new_direction in self.sprite_frames:
            self.current_direction = new_direction
        elif new_direction == 'left' and 'right' in self.sprite_frames:
            # Usar sprite de derecha con flip para izquierda
            self.current_direction = 'left'
        elif new_direction in ['up', 'down'] and new_direction not in self.sprite_frames:
            # Si no tenemos sprite vertical, mantener el último horizontal
            pass  # Mantener dirección actual
        
        # El personaje está en movimiento si hay input
        self._moving = dx != 0.0 or dy != 0.0
        
        # Actualizar posición
        self.x += dx
        self.y += dy
        
        # Mantener dentro de los límites
        if self.sprite_frames:
            current_frames = self.sprite_frames.get(self.current_direction, 
                                                  list(self.sprite_frames.values())[0])
            frame_size = current_frames[0].get_size()
            self.x = max(0, min(WIDTH - frame_size[0], self.x))
            self.y = max(0, min(HEIGHT - frame_size[1], self.y))

    def update(self, dt: float):
        if self._moving:
            self._elapsed += dt
            if self._elapsed >= FRAME_TIME:
                self._elapsed -= FRAME_TIME
                current_frames = self.sprite_frames.get(self.current_direction, 
                                                      list(self.sprite_frames.values())[0])
                self._frame_index = (self._frame_index + 1) % len(current_frames)
        else:
            self._frame_index = 0

    def draw(self, surface: pygame.Surface):
        if not self.sprite_frames:
            return
        
        # Obtener frames de la dirección actual
        current_frames = self.sprite_frames.get(self.current_direction, 
                                              list(self.sprite_frames.values())[0])
        
        if not current_frames:
            return
            
        frame = current_frames[self._frame_index]
        
        # Aplicar flip horizontal para movimiento hacia la izquierda
        if self.current_direction == 'left':
            frame = pygame.transform.flip(frame, True, False)
        
        # Dibujar el frame
        surface.blit(frame, (int(self.x), int(self.y)))

def load_sprite_sheets():
    """Carga todos los sprite sheets disponibles."""
    sprite_sheets = {}
    
    # Intentar cargar cada sprite sheet
    sprites_to_load = {
        'right': SPRITE_RIGHT,
        'back': SPRITE_BACK,
        'front': SPRITE_FRONT
    }
    
    for direction, sprite_path in sprites_to_load.items():
        if sprite_path.exists():
            try:
                sheet = pygame.image.load(sprite_path).convert_alpha()
                sprite_sheets[direction] = sheet
                print(f"✓ Loaded {direction} sprite: {sprite_path.name}")
            except Exception as e:
                print(f"✗ Error loading {direction} sprite: {e}")
        else:
            print(f"✗ Missing {direction} sprite: {sprite_path.name}")
    
    # Mapear 'front' a 'down' para mejor legibilidad
    if 'front' in sprite_sheets:
        sprite_sheets['down'] = sprite_sheets.pop('front')
    if 'back' in sprite_sheets:
        sprite_sheets['up'] = sprite_sheets.pop('back')
    
    return sprite_sheets

def create_test_sprites():
    """Crea sprites de prueba si no se encuentran los archivos."""
    print("Creating test sprites...")
    sprite_sheets = {}
    
    # Colores para cada dirección
    colors = {
        'right': (0, 255, 0),    # Verde
        'up': (0, 0, 255),       # Azul  
        'down': (255, 255, 0)    # Amarillo
    }
    
    for direction, color in colors.items():
        test_surface = pygame.Surface((FRAME_W * FRAME_COUNT, FRAME_H))
        test_surface.fill((50, 50, 50))  # Fondo gris
        
        for i in range(FRAME_COUNT):
            # Dibujar formas diferentes según dirección
            x_offset = i * FRAME_W
            center_x = x_offset + FRAME_W // 2
            center_y = FRAME_H // 2
            
            if direction == 'right':
                # Flecha derecha
                points = [(center_x - 30, center_y - 20), (center_x + 30, center_y), 
                         (center_x - 30, center_y + 20)]
                pygame.draw.polygon(test_surface, color, points)
            elif direction == 'up':
                # Flecha arriba
                points = [(center_x, center_y - 30), (center_x - 20, center_y + 30), 
                         (center_x + 20, center_y + 30)]
                pygame.draw.polygon(test_surface, color, points)
            elif direction == 'down':
                # Flecha abajo
                points = [(center_x, center_y + 30), (center_x - 20, center_y - 30), 
                         (center_x + 20, center_y - 30)]
                pygame.draw.polygon(test_surface, color, points)
            
            # Agregar número del frame
            font = pygame.font.Font(None, 36)
            text = font.render(str(i), True, (255, 255, 255))
            test_surface.blit(text, (center_x - 10, center_y + 40))
        
        sprite_sheets[direction] = test_surface
    
    return sprite_sheets
def main():
    pygame.init()
    pygame.display.set_caption("Hope Walking - Directional Sprites")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Cargar sprites direccionales
    sprite_sheets = load_sprite_sheets()
    
    if not sprite_sheets:
        print("No sprite sheets found. Using test sprites.")
        sprite_sheets = create_test_sprites()
    
    if not sprite_sheets:
        print("ERROR: No sprites available!")
        return

    player = Player(sprite_sheets)

    # Bucle principal
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        player.handle_input(dt)
        player.update(dt)

        # Dibujar
        screen.fill((64, 128, 64))  # Fondo verde natural
        player.draw(screen)
        
        # Info mínima
        font = pygame.font.Font(None, 20)
        info_text = font.render(f"Direction: {player.current_direction.upper()} | Frame: {player._frame_index} | WASD to move", 
                               True, (255, 255, 255))
        screen.blit(info_text, (10, HEIGHT - 25))
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()