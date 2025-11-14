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
FONT_SIZE = 30
INITIAL_WIDTH = 800
INITIAL_HEIGHT = 600
SETTINGS_FILE = "editor_settings.json"

# --- JSON Functions for Settings ---

def load_settings():
    """Load settings from the JSON file or return defaults."""
    default_settings = {
        "grid_color": [255, 255, 255], # White
        "grid_alpha": 127,            # 50% transparency
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

        # Editor State Variables
        self.editor_mode = False
        self.editor_menu_open = False
        self.settings_menu_open = False # Variable for the Settings menu

        # Viewport/Camera variables
        self.camera_x = 0 # Horizontal offset (panning)
        self.camera_y = 0 # Vertical offset (panning)
        self.zoom_level = 1.0 # Zoom level

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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    
                    if self.editor_mode:
                        # Toggle Editor Menu ('0')
                        if event.key == pygame.K_0:
                            self.editor_menu_open = not self.editor_menu_open
                            self.settings_menu_open = False # Close settings when main menu opens
                        
                        # Toggle Settings Menu ('1')
                        if event.key == pygame.K_1:
                            self.settings_menu_open = not self.settings_menu_open
                            self.editor_menu_open = False # Close main menu when settings opens

                # Mouse Wheel Zoom/Dézoom
                if event.type == pygame.MOUSEBUTTONDOWN and self.editor_mode:
                    # Zoom In (scroll up: button 4) or Zoom Out (scroll down: button 5)
                    if event.button == 4:
                        self.zoom_level = min(4.0, self.zoom_level * 1.1)
                    if event.button == 5:
                        self.zoom_level = max(0.2, self.zoom_level / 1.1)

            # --- Key Held Down for Panning (Déplacement) ---
            if self.editor_mode:
                keys = pygame.key.get_pressed()
                pan_speed = 5 / self.zoom_level # Faster movement when zoomed in
                
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
        
        # Check if any side menu is open
        if self.editor_menu_open or self.settings_menu_open:
            
            menu_width = 300
            menu_height = current_height
            menu_x = current_width - menu_width
            
            # Menu Background
            pygame.draw.rect(self.screen, GRAY, (menu_x, 0, menu_width, menu_height))
            
            if self.editor_menu_open:
                # Editor Menu Content (Tiles, etc.)
                self.draw_menu_content(menu_x, "EDITOR MENU (Tiles, etc.) - Press '0' to close")
                
            elif self.settings_menu_open:
                # Settings Menu Content
                self.draw_settings_content(menu_x)

        # 4. Status Text (Always on top)
        status_text = f"Zoom: {self.zoom_level:.2f} | Cam: ({self.camera_x:.0f}, {self.camera_y:.0f}) | T_Size: {self.settings['tile_size']}"
        text_surface = self.font.render(status_text, True, LIGHT_GRAY)
        self.screen.blit(text_surface, (10, 10))
        
    def draw_menu_content(self, menu_x, title):
        """Draws generic menu content."""
        
        text_title = self.font.render(title, True, WHITE)
        self.screen.blit(text_title, (menu_x + 10, 10))
        
        text_content = self.font.render("(Area for Tile/Object Selection)", True, WHITE)
        self.screen.blit(text_content, (menu_x + 10, 50))
        
    def draw_settings_content(self, menu_x):
        """Draws the dedicated Settings menu."""
        
        title = "SETTINGS MENU (Press '1' to close)"
        text_title = self.font.render(title, True, WHITE)
        self.screen.blit(text_title, (menu_x + 10, 10))
        
        # Display Grid Settings
        current_color = self.settings['grid_color']
        current_alpha = self.settings['grid_alpha']
        
        info_text = [
            "",
            "--- Grid Settings ---",
            f"Color (R,G,B): {current_color}",
            f"Transparency (0-255): {current_alpha} ({current_alpha/2.55:.0f}%)",
            "",
            "Functionality coming soon:",
            "Use + / - to change Transparency",
            "Use R / G / B to cycle Color"
        ]
        
        y_offset = 60
        for line in info_text:
            line_surface = self.font.render(line, True, LIGHT_GRAY)
            self.screen.blit(line_surface, (menu_x + 10, y_offset))
            y_offset += FONT_SIZE + 5


# --- Execution ---
if __name__ == "__main__":
    game = TwoDEngine()
    game.run()
