#?attr CLIENT

from engine.core.game_base import ClientGameBase

from engine.datatypes import *
from engine.components.background import Background, BackgroundLayer

from .blocks import *
from .widgets import *



class NetworkHandler:
    engine_ref = None

    @staticmethod
    def init(engine_ref):
        NetworkHandler.engine_ref = engine_ref


    @staticmethod
    def connected_from_another_location(data):
        NetworkHandler.engine_ref.stop()


    @staticmethod
    def update_inventory(data):
        slot_num=0

        for key, value in data.items():
            slot_num += 1

            slot_key=f"slot_{slot_num}"
            slot_icon = NetworkHandler.engine_ref.widgets["Inventory"].subwidgets[slot_key].subwidgets["item_icon"]

            match key:
                case "Stick":           slot_icon.material = Material("res/textures/stick.png")
                case "Leaf":            slot_icon.material = Material("res/textures/leaf.png")
                case "Wood":            slot_icon.material = Material("res/textures/wood.png")
                case "SandPile":        slot_icon.material = Material("res/textures/sand_pile.png")
                case "DirtPile":        slot_icon.material = Material("res/textures/dirt_pile.png")
                case "Rock":            slot_icon.material = Material("res/textures/rock.png")
                case "Coal":            slot_icon.material = Material("res/textures/coal.png")
                case "RawIronNugget":   slot_icon.material = Material("res/textures/iron_nugget.png")
                case "RawGoldNugget":   slot_icon.material = Material("res/textures/gold_nugget.png")
                case "Diamond":         slot_icon.material = Material("res/textures/diamond.png")
                case "Seed":            slot_icon.material = Material("res/textures/seed.png")
                case _: raise ValueError(f"Unknown item type: {key}")
            
            NetworkHandler.engine_ref.widgets["Inventory"].subwidgets[slot_key].subwidgets["item_count"].text = str(value)


    @staticmethod
    def register_outcome(data):
        if data > 0:
            return
        elif data == -1:
            NetworkHandler.engine_ref.widgets["invalid_port_warning"].show()
        elif data == -2:
            NetworkHandler.engine_ref.widgets["failed_connection_warning"].show()
        elif data == -3:
            NetworkHandler.engine_ref.widgets["invalid_credentials_warning"].show()



class ClientGame(ClientGameBase):
    def __init__(self):
        super().__init__()
        eng = self.engine
        NetworkHandler.init(eng)
        register_actor_templates(eng)

        eng.set_camera_width(16 * 2)
        eng.resolution = Vector(1600, 900)

        self.true_scroll = [0, 0]
        self.game_map = {}
        self.loaded_chunks = set()

        eng.hide_all_stats()
        eng.widgets["fps"].visible = True
    
        self.switched_to_login_menu = False
        self.authenticated = False

        eng.register_background(Background("sky", (BackgroundLayer(Material(Color(100, 175, 255)), 20, 0.25), )))
        eng.register_background(Background("main_menu", (BackgroundLayer(Material(Color(19, 3, 31)), eng.camera_width, 0), )))
        eng.current_background = "main_menu"

        invalid_port_warning = WarningWidget("invalid_port_warning", "Invalid port number")
        failed_connection_warning = WarningWidget("failed_connection_warning", "Failed to connect to server")
        invalid_credentials_warning = WarningWidget("invalid_credentials_warning", "Invalid username or password")
        user_already_logged_in_warning = WarningWidget("user_already_logged_in_warning", "User is already logged in")
        username_already_exists_warning = WarningWidget("username_already_exists_warning", "Username already exists")
        wrong_credentials_warning = WarningWidget("wrong_credentials_warning", "Wrong username or password")

        eng.register_widget(invalid_port_warning.widget)
        eng.register_widget(failed_connection_warning.widget)
        eng.register_widget(invalid_credentials_warning.widget)
        eng.register_widget(user_already_logged_in_warning.widget)
        eng.register_widget(username_already_exists_warning.widget)
        eng.register_widget(wrong_credentials_warning.widget)
        eng.register_widget(ServerPromptMenu())
        eng.register_widget(CredentialsMenu())
        eng.register_widget(Inventory())

        eng.regisrer_network_command("connected_from_another_location", NetworkHandler.connected_from_another_location)
        eng.regisrer_network_command("register_outcome", NetworkHandler.register_outcome)
        eng.regisrer_network_command("update_inventory", NetworkHandler.update_inventory)
        
        #?ifdef ENGINE
        eng.connect("localhost", 5555)
        #?endif


    def handle_login(self):
        if self.engine.network and self.engine.network.connected and not self.switched_to_login_menu:
            self.switched_to_login_menu = True
            self.engine.widgets["ServerPromptMenu"].visible = False
            self.engine.widgets["CredentialsMenu"].visible = True
            #?ifdef ENGINE
            self.engine.network.send("login", ("test", "test"))
            #?endif
            return False

        if self.engine.check_network() and not self.authenticated:
            self.authenticated = True
            self.engine.widgets["Inventory"].visible = True
            self.engine.widgets["CredentialsMenu"].visible = False
            self.engine.join_level("Overworld")
            return True

        return self.engine.check_network()


    def tick(self):
        delta_time = super().tick()

        # print(f"FPS: {sum(self.engine.stats['fps']) / len(self.engine.stats['fps']) * 1000:.2f}")
        if Keys.F11 in self.engine.triggered_keys:
            self.engine.fullscreen = not self.engine.fullscreen

        WarningWidget.tick(delta_time)
        if not self.handle_login():
            return

        player_key = f"__Player_{self.engine.network.id}"
        if player_key in self.engine.level.actors:
            player = self.engine.level.actors[player_key]
 
            # Smooth chase camera: adjust true_scroll to follow the player.
            self.true_scroll[0] += (player.position.x - self.true_scroll[0]) * 0.1
            self.true_scroll[1] += (player.position.y - self.true_scroll[1]) * 0.1
            
            # Update the camera position of the engine so that rendering follows.
            self.engine.camera_position = Vector(self.true_scroll[0],self.true_scroll[1])                      




