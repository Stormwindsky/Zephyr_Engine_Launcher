import pygame
import sys
import tkinter as tk
from tkinter import simpledialog
from tkinter import colorchooser 
import json
import os

# --- Global Settings ---
GAME_TITLE = "TwoD Engine Prototype"
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
FONT_SIZE = 24 
INITIAL_WIDTH = 800
INITIAL_HEIGHT = 600
SETTINGS_FILE = "editor_settings.json"

# --- JSON Functions for Settings ---

def load_settings():
    """Load settings from the JSON file or return defaults."""
    default_settings = {
        "grid_color": [255, 255, 255], # White (R, G, B)
        "grid_alpha": 127,            # 50% transparency (0-255)
        "tile_size": 32               # Default tile size in pixels
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                # Merge with defaults in case some keys are missing
                return {**default_settings, **settings}
        except json.JSONDecodeError:
            print("Error reading settings file. Using default settings.")
            return default_settings
    return default_settings

def save_settings(settings):
    """Save current settings to the JSON file."""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        print("Settings saved successfully.")
    except IOError:
        print("Error saving settings file.")

# --- Tkinter Functions (Optimisé pour X11 et Anti-Crash) ---

def show_initial_dialog():
    """Displays the initial dialog to choose between 'Create' or 'Test'."""
    root = tk.Tk()
    root.withdraw()
    selection = simpledialog.askstring(
        title=GAME_TITLE,
        prompt="Select an option:\n1. Create Game\n2. Test Game",
        initialvalue="1"
    )
    root.destroy() 
    
    if selection == "1":
        return "create"
    elif selection == "2":
        print("Testing mode selected (Not implemented yet).")
        return None
    else:
        return None

def show_color_picker(current_rgb):
    """Displays the Tkinter color picker and returns the new [R, G, B] list or None."""
    root = tk.Tk()
    root.withdraw()
    
    initial_color = f'#{current_rgb[0]:02x}{current_rgb[1]:02x}{current_rgb[2]:02x}'
    
    color_code, rgb_tuple = colorchooser.askcolor(initialcolor=initial_color)
    
    root.destroy()
    
    if rgb_tuple is not None and len(rgb_tuple) == 3:
        return list(map(int, rgb_tuple)) 
    else:
        return None

# --- PyGame Main Engine Class ---

class TwoDEngine:
    def __init__(self):
        pass
    
    def initialize_pygame(self):
        """Initializes Pygame display and core components."""
        pygame.init()
        # Charger les paramètres initiaux
        self.settings = load_settings()
        
        # Pygame Setup
        self.screen = pygame.display.set_mode(
            (INITIAL_WIDTH, INITIAL_HEIGHT), 
            pygame.RESIZABLE
        )
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.color_index = 0 

        # UI State for Settings Menu
        self.transparency_slider_rect = None 
        self.transparency_slider_track = None 
        self.is_dragging_slider = False      
        self.reset_button_rect = None        
        self.color_button_rect = None 
        
        # Editor State Variables
        self.editor_mode = False
        self.editor_menu_open = False
        self.settings_menu_open = False 

        # Viewport/Camera variables
        self.camera_x = 0 
        self.camera_y = 0 
        self.zoom_level = 1.0


    def reset_grid_settings(self):
        """Resets grid color and alpha to default values."""
        default_settings = {
            "grid_color": [255, 255, 255],
            "grid_alpha": 127
        }
        self.settings['grid_color'] = default_settings['grid_color']
        self.settings['grid_alpha'] = default_settings['grid_alpha']
        save_settings(self.settings)
        # Recharger explicitement après reset
        self.settings = load_settings() 
        print("Grid settings reset to default.")

    def update_transparency_slider(self, mouse_x):
        """Updates the transparency (alpha) based on mouse position (X)."""
        if self.transparency_slider_rect and self.transparency_slider_track:
            slider_track_x = self.transparency_slider_track[0]
            slider_track_width = self.transparency_slider_track[2]
            
            clamped_x = max(slider_track_x, min(mouse_x, slider_track_x + slider_track_width))
            
            position_ratio = (clamped_x - slider_track_x) / slider_track_width
            
            new_alpha = int(position_ratio * 255)
            
            self.settings['grid_alpha'] = new_alpha
            
    def open_color_picker(self):
        """Opens the Tkinter color picker dialog and updates grid color if a new one is selected."""
        
        # 1. Pause Pygame et sauve les dimensions
        current_width = self.screen.get_width()
        current_height = self.screen.get_height()
        pygame.display.quit() 
        
        # 2. Appelle la fonction utilitaire 
        new_color = show_color_picker(self.settings['grid_color'])
        
        # 3. Redémarre Pygame
        pygame.display.init() 
        
        # 4. Re-crée l'écran
        try:
             self.screen = pygame.display.set_mode(
                 (current_width, current_height), 
                 pygame.RESIZABLE
             )
        except pygame.error:
             self.screen = pygame.display.set_mode(
                 (INITIAL_WIDTH, INITIAL_HEIGHT), 
                 pygame.RESIZABLE
             )
             
        pygame.display.set_caption(GAME_TITLE)
             
        if new_color:
            # Mise à jour des données
            self.settings['grid_color'] = new_color
            save_settings(self.settings)
            
            # CORRECTION CRUCIALE : Recharge les paramètres après la sauvegarde
            # Cela garantit que toutes les parties de l'objet self.settings sont rafraîchies.
            self.settings = load_settings() 
            
            print(f"Grid color updated to: {self.settings['grid_color']}")
            
    def handle_settings_input(self, key):
        """Handle input specific to the settings menu (legacy key controls)."""
        
        # Change Transparency (Alpha)
        if key == pygame.K_EQUALS or key == pygame.K_KP_PLUS:
            self.settings['grid_alpha'] = min(255, self.settings['grid_alpha'] + 10)
            save_settings(self.settings)
        
        elif key == pygame.K_MINUS or key == pygame.K_KP_MINUS:
            self.settings['grid_alpha'] = max(0, self.settings['grid_alpha'] - 10)
            save_settings(self.settings)

        # Change Grid Color Component (R, G, B)
        elif key == pygame.K_r:
            self.settings['grid_color'][0] = 255 if self.settings['grid_color'][0] == 0 else 0
            save_settings(self.settings)
            
        elif key == pygame.K_g:
            self.settings['grid_color'][1] = 255 if self.settings['grid_color'][1] == 0 else 0
            save_settings(self.settings)
            
        elif key == pygame.K_b:
            self.settings['grid_color'][2] = 255 if self.settings['grid_color'][2] == 0 else 0
            save_settings(self.settings)


    def run(self):
        """Main loop of the engine."""
        
        mode = show_initial_dialog()
        
        if mode == "create":
            self.initialize_pygame()
            self.editor_mode = True
            print("Entering Editor Mode...")
        else:
            return 

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
                    
                    # Toggle Settings Menu ('1')
                    elif event.key == pygame.K_1:
                        self.settings_menu_open = not self.settings_menu_open
                        self.editor_menu_open = False
                        
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

                            # Clic sur le bouton du Sélecteur de Couleurs
                            if self.color_button_rect and self.color_button_rect.collidepoint(mouse_x, mouse_y):
                                self.open_color_picker()
                                
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            if self.is_dragging_slider:
                                save_settings(self.settings) # Save settings when dragging stops
                            self.is_dragging_slider = False
                            
                    elif event.type == pygame.MOUSEMOTION:
                        if self.is_dragging_slider:
                            self.update_transparency_slider(event.pos[0]) # event.pos[0] est le x de la souris


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

        # Step 3: Cleanup
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
        """Draws generic menu content, respecting menu width. Corrected Y offset and text wrapping."""
        
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

        # --- 3. Transparency Slider ---
        
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
        
        # --- 4. Color / Colour (Bouton Sélecteur) ---
        color_header = self.font.render("Grid Color:", True, LIGHT_GRAY)
        self.screen.blit(color_header, (menu_x + padding, y_offset))
        y_offset += color_header.get_height() + 5
        
        # A. Bouton cliquable
        color_button_text = "OPEN COLOR PICKER"
        color_surface = self.font.render(color_button_text, True, BLACK)
        color_padding_y = 5
        
        self.color_button_rect = pygame.Rect(
            menu_x + padding, 
            y_offset, 
            color_surface.get_width() + padding * 2, 
            color_surface.get_height() + color_padding_y * 2
        )
        
        pygame.draw.rect(self.screen, WHITE, self.color_button_rect)
        self.screen.blit(color_surface, (menu_x + padding * 2, y_offset + color_padding_y))
        y_offset += self.color_button_rect.height + padding

        # B. Affichage de la couleur actuelle
        current_color = self.settings['grid_color']
        # Assurez-vous que l'affichage est mis à jour
        color_info = self.font.render(f"Current RGB: {current_color}", True, current_color)
        self.screen.blit(color_info, (menu_x + padding, y_offset))
        y_offset += color_info.get_height() + padding * 2
        
        # --- 5. Reset Button ---
        reset_text = "RESET GRID SETTINGS"
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

# --- Execution ---
if __name__ == "__main__":
    game = TwoDEngine()
    game.run()
