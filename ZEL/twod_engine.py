import pygame
import sys
import json
import os
import math

# --- Global Settings ---
GAME_TITLE = "TwoD Engine Prototype"
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
FONT_SIZE = 24 
INITIAL_WIDTH = 800
INITIAL_HEIGHT = 600

# --- Paramètres JSON et Défauts ---
SETTINGS_FILE = "editor_settings.json"

# Valeurs de base par défaut pour le JSON
DEFAULT_SETTINGS = {
    "grid_color": [255, 255, 255], # Blanc
    "grid_alpha": 127,             # 50% de Transparence
    "tile_size": 32                # Taille de tuile par défaut
}

# --- Utility Function: HSV to RGB Conversion ---
def hsv_to_rgb(h, s, v):
    """
    Converts HSV values to RGB.
    h: 0-360 (degrees)
    s: 0-1 (saturation)
    v: 0-1 (value/brightness)
    Returns (r, g, b) tuple with values 0-255.
    """
    if s == 0:
        return (int(v * 255), int(v * 255), int(v * 255))

    i = math.floor(h / 60)
    f = h / 60 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)

    r, g, b = 0, 0, 0

    # Ensure i is between 0 and 5
    i = int(i) % 6

    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    elif i == 5:
        r, g, b = v, p, q

    return (int(r * 255), int(g * 255), int(b * 255))

# --- PyGame Main Engine Class ---

class TwoDEngine:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.settings_loaded = False
        
        # Tentative de convertir la couleur par défaut (blanc) en HSV pour initialisation
        # Le blanc (255, 255, 255) correspond à H: 0, S: 0.0, V: 1.0
        self.current_hsv = [0, 0.0, 1.0]     
        pass
    
    def load_settings(self):
        """Loads settings from JSON file or creates a default one if not found."""
        try:
            with open(SETTINGS_FILE, 'r') as f:
                self.settings = json.load(f)
            print(f"Settings loaded from {SETTINGS_FILE}.")
        except FileNotFoundError:
            print(f"Settings file {SETTINGS_FILE} not found. Using defaults and saving.")
            self.settings = DEFAULT_SETTINGS.copy()
            self.save_settings() 
        except json.JSONDecodeError:
            print(f"Error reading {SETTINGS_FILE}. Using defaults.")
            self.settings = DEFAULT_SETTINGS.copy()
        
        self.settings_loaded = True
        
        # Lors du chargement, si la couleur n'est pas blanche (pour éviter de re-calculer 255,255,255 en HSV)
        # on utilise le RGB chargé. Comme on ne stocke pas HSV dans le JSON, c'est une approximation.
        # Pour une implémentation complète, on devrait stocker HSV ou utiliser un inverse de hsv_to_rgb.
        # On peut se contenter d'initialiser h, s, v basés sur la couleur du JSON si elle n'est pas purement grise (S>0).
        r, g, b = self.settings['grid_color']
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        
        if max_val == min_val: # Gris/Blanc/Noir
            self.current_hsv = [0, 0.0, max_val / 255.0]
        else: # Couleur
            # Simplification: si S > 0, on prend la Teinte/Saturation pour l'affichage du curseur
            # (nécessite une fonction RGB->HSV complète, que nous allons ignorer pour cette correction rapide)
            # On conserve simplement le blanc pour l'initialisation du curseur.
            pass


    def save_settings(self):
        """Saves current settings to the JSON file."""
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
            print(f"Settings saved to {SETTINGS_FILE}.")
        except Exception as e:
            print(f"Error saving settings to {SETTINGS_FILE}: {e}")

    def initialize_pygame(self):
        """Initializes Pygame display and core components, loading settings first."""
        self.load_settings() # CHARGEMENT DES PARAMÈTRES AVANT L'INITIALISATION DE PYGAME

        pygame.init()
        
        # Pygame Setup
        self.screen = pygame.display.set_mode(
            (INITIAL_WIDTH, INITIAL_HEIGHT), 
            pygame.RESIZABLE
        )
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, FONT_SIZE)

        # UI State for Settings Menu
        self.transparency_slider_rect = None 
        self.transparency_slider_track = None 
        self.is_dragging_slider = False      
        self.reset_button_rect = None        
        self.color_button_rect = None        
        
        # Color Picker State
        self.color_picker_open = False       
        self.color_picker_rect = None        
        self.is_dragging_color_cursor = False
        
        # Editor State Variables
        self.editor_mode = True 
        self.editor_menu_open = False
        self.settings_menu_open = False 

        # Viewport/Camera variables
        self.camera_x = 0 
        self.camera_y = 0 
        self.zoom_level = 1.0


    def reset_grid_settings(self):
        """Resets grid color and alpha to static default values (in memory and saves)."""
        self.settings['grid_color'] = list(DEFAULT_SETTINGS['grid_color'])
        self.settings['grid_alpha'] = DEFAULT_SETTINGS['grid_alpha']
        # Mettre à jour self.current_hsv pour correspondre au blanc par défaut
        self.current_hsv = [0, 0.0, 1.0] # Blanc en HSV
        self.save_settings()
        print("Grid settings reset to default and saved.")

    def update_transparency_slider(self, mouse_x):
        """Updates the transparency (alpha) based on mouse position (X) and saves."""
        if self.transparency_slider_rect and self.transparency_slider_track:
            slider_track_x = self.transparency_slider_track[0]
            slider_track_width = self.transparency_slider_track[2]
            
            clamped_x = max(slider_track_x, min(mouse_x, slider_track_x + slider_track_width))
            
            position_ratio = (clamped_x - slider_track_x) / slider_track_width
            
            new_alpha = int(position_ratio * 255)
            
            if self.settings['grid_alpha'] != new_alpha:
                self.settings['grid_alpha'] = new_alpha
                self.save_settings() 
                
    def open_color_picker(self):
        """Toggle the color picker mode."""
        self.color_picker_open = not self.color_picker_open
        print(f"Color Picker is {'OPEN' if self.color_picker_open else 'CLOSED'}.")
        
    def update_color_from_picker(self, mouse_x, mouse_y):
        """Updates the grid color based on the mouse position within the color wheel area."""
        if self.color_picker_rect and self.color_picker_rect.collidepoint(mouse_x, mouse_y):
            center_x = self.color_picker_rect.centerx
            center_y = self.color_picker_rect.centery
            radius = self.color_picker_rect.width / 2 
            
            # Calculer la distance et l'angle par rapport au centre
            dx = mouse_x - center_x
            dy = mouse_y - center_y
            
            distance = math.sqrt(dx**2 + dy**2)
            
            # La saturation (S) est proportionnelle à la distance du centre
            s = min(1.0, distance / radius) 
            
            # La teinte (H) est l'angle (en degrés)
            # math.atan2 retourne l'angle en radians (-pi à pi). Convertir en degrés (0-360)
            h = (math.degrees(math.atan2(dy, dx)) + 360) % 360
            
            # La valeur (V/luminosité) est fixée à 1.0 pour la roue chromatique
            v = 1.0 

            # Gérer le cas où l'on clique près du centre (désaturation maximale)
            if distance <= 1: 
                s = 0.0
            
            self.current_hsv = [h, s, v]
            
            # Convertir HSV en RGB pour la couleur de la grille
            new_rgb = hsv_to_rgb(h, s, v)
            
            if self.settings['grid_color'] != list(new_rgb):
                self.settings['grid_color'] = list(new_rgb)
                self.save_settings()
                
    def handle_settings_input(self, key):
        """Handle input specific to the settings menu. ONLY transparency remains."""
        
        # Change Transparency (Alpha)
        if key == pygame.K_EQUALS or key == pygame.K_KP_PLUS:
            self.settings['grid_alpha'] = min(255, self.settings['grid_alpha'] + 10)
            self.save_settings()
        
        elif key == pygame.K_MINUS or key == pygame.K_KP_MINUS:
            self.settings['grid_alpha'] = max(0, self.settings['grid_alpha'] - 10)
            self.save_settings()
            
    def run(self):
        """Main loop of the engine."""
        
        self.initialize_pygame()
        print("Entering Editor Mode (Settings loaded from JSON)...")

        # --- Main PyGame Loop ---
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        (event.w, event.h), 
                        pygame.RESIZABLE
                    )
                
                # Input Handling
                if event.type == pygame.KEYDOWN and self.editor_mode:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    
                    # Toggle Editor Menu ('0')
                    if event.key == pygame.K_0:
                        self.editor_menu_open = not self.editor_menu_open
                        self.settings_menu_open = False
                        self.color_picker_open = False 
                    
                    # Toggle Settings Menu ('1')
                    elif event.key == pygame.K_1:
                        self.settings_menu_open = not self.settings_menu_open
                        self.editor_menu_open = False
                        self.color_picker_open = False 
                        
                    # Handle Settings changes only if the settings menu is open
                    elif self.settings_menu_open:
                        self.handle_settings_input(event.key)

                # --- Gestion de la Souris (Glissement du Curseur et Clics) ---
                if self.editor_mode and self.settings_menu_open:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1: # Clic gauche
                            mouse_x, mouse_y = event.pos
                            
                            # Clic sur le Curseur de Transparence
                            if self.transparency_slider_rect and self.transparency_slider_rect.collidepoint(mouse_x, mouse_y):
                                self.is_dragging_slider = True
                                self.update_transparency_slider(mouse_x) 

                            # Clic sur le bouton Reset
                            if self.reset_button_rect and self.reset_button_rect.collidepoint(mouse_x, mouse_y):
                                self.reset_grid_settings()
                                
                            # Clic sur le bouton du Sélecteur de Couleur
                            if self.color_button_rect and self.color_button_rect.collidepoint(mouse_x, mouse_y):
                                self.open_color_picker()
                                
                            # Clic dans la zone du Sélecteur de Couleur (si ouvert)
                            if self.color_picker_open and self.color_picker_rect and self.color_picker_rect.collidepoint(mouse_x, mouse_y):
                                self.is_dragging_color_cursor = True
                                self.update_color_from_picker(mouse_x, mouse_y)

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.is_dragging_slider = False
                            self.is_dragging_color_cursor = False
                            
                    elif event.type == pygame.MOUSEMOTION:
                        if self.is_dragging_slider:
                            self.update_transparency_slider(event.pos[0])
                        
                        if self.is_dragging_color_cursor and self.color_picker_open:
                            self.update_color_from_picker(event.pos[0], event.pos[1])


                # Mouse Wheel Zoom/Dézoom
                if event.type == pygame.MOUSEBUTTONDOWN and self.editor_mode:
                    if event.button == 4:
                        self.zoom_level = min(4.0, self.zoom_level * 1.1)
                    if event.button == 5:
                        self.zoom_level = max(0.2, self.zoom_level / 1.1)

            # --- Key Held Down for Panning (Déplacement) ---
            if self.editor_mode:
                keys = pygame.key.get_pressed()
                pan_speed = 5 / self.zoom_level
                
                if keys[pygame.K_LEFT]:
                    self.camera_x += pan_speed
                if keys[pygame.K_RIGHT]:
                    self.camera_x -= pan_speed
                if keys[pygame.K_UP]:
                    self.camera_y += pan_speed
                if keys[pygame.K_DOWN]:
                    self.camera_y -= pan_speed
            
            # --- Drawing ---
            if self.editor_mode:
                self.draw_editor()
                
            pygame.display.flip()
            self.clock.tick(60)

        # Cleanup
        pygame.quit()
        sys.exit()

    def draw_grid(self):
        """Draws the transparent, zoomable, and pannable grid."""
        
        current_width, current_height = self.screen.get_size()
        tile_size = self.settings['tile_size']
        
        # Calculate zoomed grid step
        step = tile_size * self.zoom_level
        
        # Get the color and create a transparent surface
        r, g, b = self.settings['grid_color']
        grid_surface = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
        grid_surface.fill((0, 0, 0, 0)) # Completely transparent background
        
        # Adjust transparency
        alpha = self.settings['grid_alpha']
        color_with_alpha = (r, g, b, alpha)
        
        # Vertical lines
        x_start = self.camera_x % step - step
        while x_start < current_width:
            pygame.draw.line(grid_surface, color_with_alpha, (int(x_start), 0), (int(x_start), current_height))
            x_start += step

        # Horizontal lines
        y_start = self.camera_y % step - step
        while y_start < current_height:
            pygame.draw.line(grid_surface, color_with_alpha, (0, int(y_start)), (current_width, int(y_start)))
            y_start += step
            
        # Draw the transparent grid surface onto the main screen
        self.screen.blit(grid_surface, (0, 0))

    def draw_editor(self):
        """Draws the current state of the game editor."""
        
        current_width, current_height = self.screen.get_size()
        
        # 1. Background (Map View)
        self.screen.fill(BLACK)
        
        # 2. Draw Grid (Panoramique et Zoomable)
        self.draw_grid()
        
        # 3. Handle Side Menus
        if self.editor_menu_open or self.settings_menu_open:
            
            menu_width = 300
            menu_height = current_height
            menu_x = current_width - menu_width
            
            # Menu Background
            pygame.draw.rect(self.screen, GRAY, (menu_x, 0, menu_width, menu_height))
            
            if self.editor_menu_open:
                self.draw_menu_content(menu_x, menu_width, "EDITOR MENU ('0' to close)") 
                
            elif self.settings_menu_open:
                self.draw_settings_content(menu_x, menu_width)

        # 4. Status Text (Always on top)
        status_text = f"Zoom: {self.zoom_level:.2f} | Cam: ({self.camera_x:.0f}, {self.camera_y:.0f}) | T_Size: {self.settings['tile_size']}"
        text_surface = self.font.render(status_text, True, LIGHT_GRAY)
        self.screen.blit(text_surface, (10, 10))
        
    def draw_menu_content(self, menu_x, menu_width, title):
        """Draws generic menu content."""
        
        padding = 10
        y_offset = 30 
        
        # Title
        title_surface = self.font.render(title, True, WHITE)
        self.screen.blit(title_surface, (menu_x + padding, y_offset))
        y_offset += title_surface.get_height() + padding
        
        # Placeholder content
        content_lines = [
            "(Area for Tile/Object Selection)",
            "(Soon...)"
        ]
        
        for line in content_lines:
            line_surface = self.font.render(line, True, LIGHT_GRAY)
            self.screen.blit(line_surface, (menu_x + padding, y_offset))
            y_offset += line_surface.get_height() + 5

    def draw_settings_content(self, menu_x, menu_width):
        """Draws the dedicated Settings menu with complex UI elements (sliders, buttons)."""
        
        padding = 10
        y_offset = 30 
        
        # 1. Title
        title = "SETTINGS MENU ('1' to close)"
        title_surface = self.font.render(title, True, WHITE)
        self.screen.blit(title_surface, (menu_x + padding, y_offset))
        y_offset += title_surface.get_height() + padding * 2

        # 2. Grid Settings Header
        header_surface = self.font.render("Grid Settings:", True, LIGHT_GRAY)
        self.screen.blit(header_surface, (menu_x + padding, y_offset))
        y_offset += header_surface.get_height() + padding 

        # --- 3. Color Picker / Display ---
        
        # C. Draw Color Picker Area (Actual Color Wheel)
        picker_area_size = menu_width - padding * 2
        self.color_picker_rect = pygame.Rect(menu_x + padding, y_offset, picker_area_size, picker_area_size)
        
        self.draw_color_wheel(self.color_picker_rect)
        
        if self.color_picker_open:
            # Dessiner le CURSEUR sur la roue chromatique
            center_x = self.color_picker_rect.centerx
            center_y = self.color_picker_rect.centery
            radius = self.color_picker_rect.width / 2
            
            h, s, v = self.current_hsv
            
            # Calculer la position du curseur en fonction de H et S
            angle_rad = math.radians(h)
            
            # Distance du centre pour la saturation
            cursor_dist = s * radius 
            
            # Assurez-vous que le curseur ne dépasse pas le rayon
            cursor_dist = min(cursor_dist, radius)
            
            cursor_x = center_x + cursor_dist * math.cos(angle_rad)
            cursor_y = center_y + cursor_dist * math.sin(angle_rad)
            
            pygame.draw.circle(self.screen, BLACK, (int(cursor_x), int(cursor_y)), 8, 2) 
            pygame.draw.circle(self.screen, WHITE, (int(cursor_x), int(cursor_y)), 6, 2)


        y_offset += picker_area_size + padding
        
        # A. Current Color Display and Info
        current_color = self.settings['grid_color']
        color_text = f"Current RGB: {current_color}"
        color_surface = self.font.render(color_text, True, WHITE)
        
        # Color Swatch (Affichage de la couleur)
        swatch_size = 40
        swatch_rect = pygame.Rect(menu_x + padding, y_offset, swatch_size, swatch_size)
        pygame.draw.rect(self.screen, current_color, swatch_rect)
        pygame.draw.rect(self.screen, WHITE, swatch_rect, 1) # Border
        
        self.screen.blit(color_surface, (menu_x + padding + swatch_size + padding, y_offset + (swatch_size - color_surface.get_height()) // 2))
        y_offset += swatch_size + padding

        # B. Color Picker Button
        picker_text = "Toggle Color Picker (Click)"
        picker_surface = self.font.render(picker_text, True, BLACK if self.color_picker_open else WHITE)
        picker_padding_y = 5
        
        self.color_button_rect = pygame.Rect(
            menu_x + padding, 
            y_offset, 
            picker_surface.get_width() + padding * 2, 
            picker_surface.get_height() + picker_padding_y * 2
        )
        
        picker_color = (100, 200, 100) if not self.color_picker_open else (255, 100, 100) # Green / Red toggle
        pygame.draw.rect(self.screen, picker_color, self.color_button_rect)
        self.screen.blit(picker_surface, (menu_x + padding * 2, y_offset + picker_padding_y))
        y_offset += self.color_button_rect.height + padding * 2

        # --- 4. Transparency Slider ---
        
        # A. Draw Text and Value
        transparency_text = f"Transparency (0-255): {self.settings['grid_alpha']}"
        text_surface = self.font.render(transparency_text, True, WHITE)
        self.screen.blit(text_surface, (menu_x + padding, y_offset))
        y_offset += text_surface.get_height() + 5 

        # B. Draw Slider Track
        track_height = 8
        track_width = menu_width - padding * 2 
        track_y = y_offset
        
        self.transparency_slider_track = (menu_x + padding, track_y, track_width, track_height)
        pygame.draw.rect(self.screen, LIGHT_GRAY, self.transparency_slider_track)
        
        # C. Draw Slider Handle (Represents current alpha)
        alpha_ratio = self.settings['grid_alpha'] / 255.0
        handle_x = menu_x + padding + int(alpha_ratio * track_width)
        handle_y = track_y + track_height // 2 
        handle_radius = 8
        
        self.transparency_slider_rect = pygame.Rect(
            handle_x - handle_radius, 
            handle_y - handle_radius, 
            handle_radius * 2, 
            handle_radius * 2
        )
        
        pygame.draw.circle(self.screen, WHITE, (handle_x, handle_y), handle_radius)
        y_offset += track_height + padding * 2
        
        # --- 5. Reset Button ---
        reset_text = "RESET GRID SETTINGS (and Save)"
        reset_surface = self.font.render(reset_text, True, BLACK)
        reset_padding_y = 5
        
        self.reset_button_rect = pygame.Rect(
            menu_x + padding, 
            y_offset, 
            reset_surface.get_width() + padding * 2, 
            reset_surface.get_height() + reset_padding_y * 2
        )
        
        pygame.draw.rect(self.screen, LIGHT_GRAY, self.reset_button_rect)
        self.screen.blit(reset_surface, (menu_x + padding * 2, y_offset + reset_padding_y))
        y_offset += self.reset_button_rect.height + padding * 2

        # --- 6. Languages (Placeholder for .lang2D) ---
        lang_header = self.font.render("Languages settings:", True, LIGHT_GRAY)
        self.screen.blit(lang_header, (menu_x + padding, y_offset))
        y_offset += lang_header.get_height() + padding
        
        lang_lines = [
            "Reset Languages (Coming Soon)", 
            "Add Languages (Community Script .lang2D)"
        ]
        
        for line in lang_lines:
            line_surface = self.font.render(line, True, WHITE)
            self.screen.blit(line_surface, (menu_x + padding, y_offset))
            y_offset += line_surface.get_height() + 5 
            
    def draw_color_wheel(self, rect):
        """Dessine une roue chromatique HSV en utilisant la conversion HSV vers RGB."""
        
        wheel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        center_x = rect.width // 2
        center_y = rect.height // 2
        radius = min(center_x, center_y) - 2 
        
        # Dessiner la roue chromatique pixel par pixel pour le dégradé
        for x in range(rect.width):
            for y in range(rect.height):
                
                dx = x - center_x
                dy = y - center_y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance <= radius:
                    # Angle (teinte)
                    # Utiliser atan2 pour obtenir l'angle de la position (x, y) par rapport au centre (center_x, center_y)
                    angle_rad = math.atan2(dy, dx)
                    h = (math.degrees(angle_rad) + 360) % 360
                    
                    # Saturation (distance du centre)
                    s = distance / radius
                    
                    # Valeur (luminosité) - fixée à 1.0 pour la roue chromatique
                    v = 1.0
                    
                    rgb_color = hsv_to_rgb(h, s, v)
                    wheel_surface.set_at((x, y), rgb_color)
                else:
                    wheel_surface.set_at((x, y), (0, 0, 0, 0)) # Transparent en dehors du cercle
                    
        self.screen.blit(wheel_surface, (rect.x, rect.y))
        pygame.draw.circle(self.screen, WHITE, rect.center, int(radius) + 1, 1) 

# --- Execution ---
if __name__ == "__main__":
    game = TwoDEngine()
    game.run()
