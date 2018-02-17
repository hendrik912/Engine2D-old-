from quadtree import *
import game_state
import scene
import input_handler

# initialize pygame and create window
pygame.init()
pygame.mixer.init()
game_state.surface = pygame.display.set_mode((game_state.WIDTH, game_state.HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()


"""
- alles auf githhub schieben
- Circle 
- steering behavior
- composit shapes
  - creation
  - indices?
  - collision a vs b 
   alle parts von a gegen alle parts von b

- containment collision anstatt check_border
- Physics Engine
 
Sonstiges:
 - collision detection a posteriori zu a priori umwandeln ? 
 - creator modus
  - punkte, federn, motoren.. 
 - labyrinth
  
Optimierung:

- wiederholte translation in render... gibts irgendeine bessere Lösung?
- transformations von children, transformations kopien etc.
- keep static entities in inserted in the quadtree?
- nur die entitäten rendern, die im sichtfeld liegen
  

"""

def process_input():

    # Process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            game_state.RUNNING = False

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 4:
                game_state.ZOOM *= (1 + game_state.ZOOMSTEP)
                if game_state.ZOOM > game_state.MAXZOOM:
                    game_state.ZOOM = game_state.MAXZOOM
            elif event.button == 5:
                game_state.ZOOM *= (1-game_state.ZOOMSTEP)
                if game_state.ZOOM < game_state.MINZOOM:
                    game_state.ZOOM = game_state.MINZOOM

        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            if event.type == pygame.KEYDOWN:
                b = True
            else:
                b = False

            ih = input_handler.InputHandler
            try:
                control = ih.keys[event.key]
                ih.controls[control] = b
            except KeyError:
                pass


def set_min_zoom(scene):
    mz_w = game_state.MINZOOM = game_state.WIDTH / scene.width
    mz_h = game_state.MINZOOM = game_state.HEIGHT / scene.height
    if mz_w < mz_h:
        game_state.MINZOOM = mz_h
    else:
        game_state.MINZOOM = mz_w


def loop():
    sc = scene.Scene(game_state.WIDTH * 2, game_state.HEIGHT * 1.5)
    set_min_zoom(sc)
    scene.setup(sc)

    while game_state.RUNNING:

        clock.tick(game_state.FPS)
        dt = clock.get_time() / 100

        sc.clear(game_state.surface)
        process_input()
        sc.update(dt)
        sc.render(game_state.surface)

    pygame.quit()

if __name__ == "__main__":
    loop()

