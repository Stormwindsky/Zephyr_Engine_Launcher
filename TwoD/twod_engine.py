import pygame
import sys
import tkinter as tk
from tkinter import simpledialog
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

# --- Tkinter Integration (For initial dialog) ---

def show_initial_dialog():
    """Displays the initial dialog to choose between 'Create' or 'Test'."""
    root = tk.Tk()
    root.withdraw()
    selection = simpledialog.askstring(
        title=GAME_TITLE,
        prompt="Select an option:\n1. Create Game\n2. Test Game",
        initialvalue="1"
    )
    if selection == "1":
        return "create"
    elif selection == "2":
        print("Testing mode selected (Not implemented yet).")
        return None
    else:
        return None

# --- PyGame Main Engine Class ---

class TwoDEngine:
    def __init__(self):
        pygame.init()
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

        # Editor State Variables
        self.editor_mode = False
        self.editor_menu_open = False
        self.settings_menu_open = False 

        # Viewport/Camera variables
        self.camera_x = 0 
        self.camera_y = 0 
        self.zoom_level = 1.0

    def handle_settings_input(self, key):
        """Handle input specific to the settings menu."""
        
        # Change Transparency (Alpha)
        if key == pygame.K_EQUALS or key == pygame.K_KP_PLUS: # Touche '=' ou '+'
            self.settings['grid_alpha'] = min(255, self.settings['grid_alpha'] + 10)
            save_settings(self.settings)
        
        elif key == pygame.K_MINUS or key == pygame.K_KP_MINUS: # Touche '-'
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
            self.editor_mode = True
            print("Entering Editor Mode...")
        else:
            self.running = False

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
                # Correction: Titre raccourci et y_offset à 30
                self.draw_menu_content(menu_x, menu_width, "EDITOR MENU ('0' to close)") 
                
            elif self.settings_menu_open:
                self.draw_settings_content(menu_x, menu_width)

        # 4. Status Text (Always on top)
        status_text = f"Zoom: {self.zoom_level:.2f} | Cam: ({self.camera_x:.0f}, {self.camera_y:.0f}) | T_Size: {self.settings['tile_size']}"
        text_surface = self.font.render(status_text, True, LIGHT_GRAY)
        self.screen.blit(text_surface, (10, 10))
        
    def draw_menu_content(self, menu_x, menu_width, title):
        """Draws generic menu content, respecting menu width. Corrected Y offset and title size."""
        
        padding = 10
        # Offset initial (30) pour éviter que le texte ne soit coupé par la barre de titre.
        y_offset = 30 
        
        # Title
        title_surface = self.font.render(title, True, WHITE)
        self.screen.blit(title_surface, (menu_x + padding, y_offset))
        y_offset += title_surface.get_height() + padding
        
        # Placeholder content (Utilise deux lignes si besoin)
        content_lines = [
            "(Area for Tile/Object Selection)",
            "(Soon...)"
        ]
        
        for line in content_lines:
            line_surface = self.font.render(line, True, LIGHT_GRAY)
            self.screen.blit(line_surface, (menu_x + padding, y_offset))
            y_offset += line_surface.get_height() + 5
        
    def draw_settings_content(self, menu_x, menu_width):
        """Draws the dedicated Settings menu with better text positioning. Corrected Y offset and text wrapping."""
        
        padding = 10
        # Offset initial (30) pour éviter que le texte ne soit coupé par la barre de titre.
        y_offset = 30 
        
        # Title (Titre raccourci)
        title = "SETTINGS MENU ('1' to close)"
        title_surface = self.font.render(title, True, WHITE)
        self.screen.blit(title_surface, (menu_x + padding, y_offset))
        y_offset += title_surface.get_height() + padding * 2 

        # Grid Settings
        current_color = self.settings['grid_color']
        current_alpha = self.settings['grid_alpha']
        
        # Utilisation de listes divisées pour simuler le text wrapping
        info_lines = [
            "--- Grid Settings ---",
            f"Color (R,G,B): {current_color}",
            f"Transparency (0-255): {current_alpha} ({current_alpha/2.55:.0f}%)",
            "",
            "Controls:",
            # Lignes divisées pour s'assurer qu'elles rentrent
            "  '-'/'+'(or'=') to change",
            "  Transparency (Alpha)",
            "  'R'/'G'/'B' to toggle Color",
            "  component"
        ]
        
        # Render and blit each line
        for line in info_lines:
            line_surface = self.font.render(line, True, LIGHT_GRAY)
            self.screen.blit(line_surface, (menu_x + padding, y_offset))
            y_offset += line_surface.get_height() + 5 


# --- Execution ---
if __name__ == "__main__":
    game = TwoDEngine()
    game.run()
