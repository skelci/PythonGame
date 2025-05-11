#?attr CLIENT

from engine.datatypes import *

from engine.components.ui.border import Border
from engine.components.ui.text import Text
from engine.components.ui.button import Button
from engine.components.ui.input_box import InputBox
from engine.components.ui.widget import Widget
from engine.components.ui.icon import Icon
from engine.components.material import Material



class WarningWidget:
    current_warnings = {}

    def __init__(self, name, text):
        self.widget = Border(name, Vector(1300, 10), Vector(290, 30), 2, Color(255, 0, 0), Color(30, 0, 0, 70), False, 2,
            subwidgets={
                "text": Text("text", Vector(0, 0), Vector(285, 20), Color(255, 255, 255), "res/fonts/arial.ttf", text=text)
            },
            subwidget_offsets={
                "text": Vector(5, 0)
            },
            subwidget_alignments={
                "text": Alignment.CENTER_LEFT,
            }
        )


    def show(self):
        if not self.widget.visible:
            self.widget.position.y = 10 + len(WarningWidget.current_warnings) * 50
            self.widget.visible = True
            WarningWidget.current_warnings[self.widget.name] = (self.widget, 15)
            return
        
        WarningWidget.current_warnings[self.widget.name] = (self.widget, 10)
        

    @classmethod
    def tick(cls, delta_time):
        widgets_to_remove = []
        for widget, time_left in cls.current_warnings.values():
            time_left -= delta_time
            cls.current_warnings[widget.name] = (widget, time_left)
            if time_left <= 0:
                widget.visible = False
                widgets_to_remove.append(widget.name)
                for widget, _ in cls.current_warnings.values():
                    widget.position.y -= 50

        for widget_name in widgets_to_remove:
            del cls.current_warnings[widget_name]



class InventorySlot(Border):
    def __init__(self, name):
        super().__init__(name, Vector(0, 0), Vector(50, 50), 0, Color(150, 150, 150), Color(0, 0, 0, 100), True, 5, 
            subwidgets={
                "item_count": Text("item_count", Vector(0, 0), Vector(0, 20), Color(255, 255, 255), "res/fonts/arial.ttf", 1, True, " "),
                "item_icon": Icon("item_icon", Vector(0, 0), Vector(40, 40), Material(Color(255, 255, 255, 0)), 0, False)
            },
            subwidget_offsets={
                "item_count": Vector(-5, -5),
                "item_icon": Vector(0, 0),
            }, 
            subwidget_alignments={
                "item_count": Alignment.BOTTOM_RIGHT,
                "item_icon": Alignment.CENTER,
            }
        )



class Inventory(Widget):
    def __init__(self):
        super().__init__("Inventory", Vector(0, 0), Vector(1600, 900), Color(0, 0, 0, 0), 0, False,  
            subwidgets={
                "slot_1": InventorySlot("slot_1"),
                "slot_2": InventorySlot("slot_2"),
                "slot_3": InventorySlot("slot_3"),
                "slot_4": InventorySlot("slot_4"),
                "slot_5": InventorySlot("slot_5"),
                "slot_6": InventorySlot("slot_6"),
                "slot_7": InventorySlot("slot_7"),
                "slot_8": InventorySlot("slot_8"),
                "slot_9": InventorySlot("slot_9"),
                "slot_10": InventorySlot("slot_10"),
            },
            subwidget_offsets={
                "slot_1": Vector(-250, -50),
                "slot_2": Vector(-200, -50),
                "slot_3": Vector(-150, -50),
                "slot_4": Vector(-100, -50),
                "slot_5": Vector(-50, -50),
                "slot_6": Vector(0, -50),
                "slot_7": Vector(50, -50),
                "slot_8": Vector(100, -50),
                "slot_9": Vector(150, -50),
                "slot_10": Vector(200, -50),
            },
            subwidget_alignments={
                "slot_1": Alignment.BOTTOM_CENTER,
                "slot_2": Alignment.BOTTOM_CENTER,
                "slot_3": Alignment.BOTTOM_CENTER,
                "slot_4": Alignment.BOTTOM_CENTER,
                "slot_5": Alignment.BOTTOM_CENTER,
                "slot_6": Alignment.BOTTOM_CENTER,
                "slot_7": Alignment.BOTTOM_CENTER,
                "slot_8": Alignment.BOTTOM_CENTER,
                "slot_9": Alignment.BOTTOM_CENTER,
                "slot_10": Alignment.BOTTOM_CENTER,
            }
        )



class CredentialsInputBox(InputBox):
    def tick(self, delta_time, triggered_keys, pressed_keys, mouse_pos):
        super().tick(delta_time, triggered_keys, pressed_keys, mouse_pos)
        if self.is_in_focus:
            if Keys.TAB in triggered_keys:
                mmcs = self.engine_ref.widgets["main_menu-credentials"].subwidgets
                mmcs_username = mmcs["prompt_field-username"].subwidgets["input_box"]
                mmcs_password = mmcs["prompt_field-password"].subwidgets["input_box"]
                mmcs_username.is_in_focus = not mmcs_username.is_in_focus
                mmcs_password.is_in_focus = not mmcs_password.is_in_focus
                triggered_keys.remove(Keys.TAB)



class PromptField(Border):
    def __init__(self, name, action = None):
        super().__init__(name, Vector(0, 0), Vector(500, 50), 0, Color(204, 255, 102), Color(255, 255, 153), True, 5,
            subwidgets={
                "input_box": CredentialsInputBox("input_box", Vector(0, 0), Vector(490, 40), Color(), "res/fonts/arial.ttf", 0, True, 22, action),
            },
            subwidget_offsets={
                "input_box": Vector(7, -7),
            },
            subwidget_alignments={
                "input_box": Alignment.CENTER_LEFT,
            }
        )



class PasswordInputBox(CredentialsInputBox):
    def tick(self, delta_time, triggered_keys, pressed_keys, mouse_pos):
        super().tick(delta_time, triggered_keys, pressed_keys, mouse_pos)
        cursor_char = "|" if self.is_cursor_visible else " "
        self.text = "*" * len(self.current_text[:self.cursor_position]) + cursor_char + "*" * len(self.current_text[self.cursor_position:])



class PasswordField(PromptField):
    def __init__(self, name, action = None):
        super().__init__(name, action)
        self.subwidgets["input_box"] = PasswordInputBox("input_box", Vector(0, 0), Vector(490, 40), Color(), "res/fonts/arial.ttf", 0, True, 22, action)



class PromptText(Text):
    def __init__(self, name, text):
        super().__init__(name, Vector(0, 0), Vector(500, 50), Color(255, 255, 255), "res/fonts/arial.ttf", 0, True, text)



class PromptButton(Button):
    def __init__(self, name, text, action = None):
        super().__init__(name, Vector(0, 0), Vector(500, 75), 0, Color(192, 32, 224), Color(32, 4, 48), True, 5,
            subwidgets={
                "text": Text("text", Vector(0, 0), Vector(200, 40), Color(192, 32, 224), "res/fonts/arial.ttf", 0, True, text),
            },
            subwidget_offsets={
                "text": Vector(0, 0),
            },
            subwidget_alignments={
                "text": Alignment.CENTER,
            },
            hover_color = Color(0, 0, 0),
            click_color = Color(64, 8, 96),
            action = action
        )



class ServerPromptMenu(Widget):
    def __init__(self):
        super().__init__("ServerPromptMenu", Vector(), Vector(1600, 900), Color(0, 0, 0, 0), 0, True,
            subwidgets={
                "prompt_field": PromptField("prompt_field", self.connect_to_server),
                "prompt_text": PromptText("prompt_text", "Server Address:"),
            },
            subwidget_offsets={
                "prompt_field": Vector(),
                "prompt_text": Vector(0, -53),
            },
            subwidget_alignments={
                "prompt_field": Alignment.CENTER,
                "prompt_text": Alignment.CENTER,
            }
        )


    def connect_to_server(self, server_address):
        if not server_address:
            return

        server_address = server_address.split(":")
        server_ip = server_address[0]
        if len(server_address) == 1:
            port = 5555
        else:
            try:
                port = int(server_address[1])
            except ValueError:
                self.engine_ref.widgets["invalid_port_warning"].show()
                return
            
        self.engine_ref.connect(server_ip, port)
        if not self.engine_ref.network.connected:
            self.engine_ref.widgets["failed_connection_warning"].show()



class CredentialsMenu(Widget):
    def __init__(self):
        super().__init__("CredentialsMenu", Vector(), Vector(1600, 900), Color(0, 0, 0, 0), 0, False,
            subwidgets={
                "prompt_field-username": PromptField("prompt_field-username"),
                "prompt_text-username": PromptText("prompt_text-username", "Username:"),
                "prompt_field-password": PasswordField("prompt_field-password"),
                "prompt_text-password": PromptText("prompt_text-password", "Password:"),
                "prompt_button-login": PromptButton("prompt_button-login", "Login", self.login),
                "prompt_button-register": PromptButton("prompt_button-register", "Register", self.register),
            },
            subwidget_offsets={
                "prompt_field-username": Vector(200, -50),
                "prompt_text-username": Vector(-190, -52),
                "prompt_field-password": Vector(200, 10),
                "prompt_text-password": Vector(-185, 8),
                "prompt_button-login": Vector(0, 100),
                "prompt_button-register": Vector(0, 200),
            },
            subwidget_alignments={
                "prompt_field-username": Alignment.CENTER,
                "prompt_text-username": Alignment.CENTER,
                "prompt_field-password": Alignment.CENTER,
                "prompt_text-password": Alignment.CENTER,
                "prompt_button-login": Alignment.CENTER,
                "prompt_button-register": Alignment.CENTER,
            }
        )


    def get_usernname_password(self):
        username = self.engine_ref.widgets["CredentialsMenu"].subwidgets["prompt_field-username"].subwidgets["input_box"].current_text
        password = self.engine_ref.widgets["CredentialsMenu"].subwidgets["prompt_field-password"].subwidgets["input_box"].current_text
        return username, password
    

    def login(self):
        username, password = self.get_usernname_password()
        if not username or not password:
            self.engine_ref.widgets["invalid_credentials_warning"].show()
            return
        self.engine_ref.network.send("login", (username, password))


    def register(self):
        username, password = self.get_usernname_password()
        if not username or not password:
            self.engine_ref.widgets["invalid_credentials_warning"].show()
            return
        self.engine_ref.network.send("register", (username, password))



    

