from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.graphics import Line, Color
from kivy.core.window import Window
from kivy.graphics import Line, InstructionGroup
from kivy.graphics import Line, InstructionGroup, Color


class MindMapWidget(Widget):
    def __init__(self, **kwargs):
        super(MindMapWidget, self).__init__(**kwargs)
        center_node = MindMapNode("Center Node")
        self.add_widget(center_node)
        self._keyboard = None
        Clock.schedule_once(self._request_keyboard, 1)
        Clock.schedule_once(self._position_center_node, 1)

    def _position_center_node(self, *args):
        center_node = self.children[-1]
        center_node.x = Window.width / 2 - center_node.width / 2
        center_node.y = Window.height / 2 - center_node.height / 2

    def request_keyboard(self, *args):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] in ('enter', 'numpadenter'):
            selected_nodes = [node for node in self.children if isinstance(node, MindMapNode) and node.selected]
            if len(selected_nodes) == 1:
                new_node = MindMapNode("New Node", selected_nodes[0].depth + 1)
                x_offset, y_offset = 50, 50
                new_node.x = selected_nodes[0].x + x_offset
                new_node.y = selected_nodes[0].y + y_offset
                self.add_widget(new_node)
                self.connect_nodes(selected_nodes[0], new_node)

    def connect_nodes(self, node1, node2):
        line_group = InstructionGroup()
        connection_color = [(1, 1, 1, 1), (1, 0, 0, 1), (1, 0.5, 0, 1), (1, 1, 0, 1), (0, 1, 0, 1)]
        line_group.add(Color(*connection_color[node2.depth]))
        line_group.add(
            Line(points=[node1.center_x, node1.center_y, node2.center_x, node2.center_y], width=2))
        self.canvas.add(line_group)
        node1.connection_lines.append((node2, line_group))
        node2.connection_lines.append((node1, line_group))


    def manage_node_selection(self, node):
        if not node.selected:
            for child in self.children:
                if isinstance(child, MindMapNode) and child != node and child.selected:
                    child.deselect_node()
        node.select_node()

    def _request_keyboard(self, *args):
        self.request_keyboard()


class MindMapNode(Button):
    def __init__(self, text, depth=0, **kwargs):
        super(MindMapNode, self).__init__(**kwargs)
        self.text = text
        self.size_hint = (None, None)
        self.size = (150, 50)
        self.offset = (0, 0)
        self.selected = False
        self.click_count = 0
        self.connection_lines = []
        self.depth = depth

    def select_node(self):
        if not self.selected:
            for node in self.parent.children:
                if isinstance(node, MindMapNode) and node != self and node.selected:
                    node.deselect_node()
        self.selected = not self.selected
        if self.selected:
            self.background_color = (1, 0, 0, 1)
        else:
            self.background_color = (1, 1, 1, 1)

    def deselect_node(self):
        self.selected = False
        self.background_color = (1, 1, 1, 1)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.offset = (touch.x - self.x, touch.y - self.y)
            self.parent.manage_node_selection(self)
            return True
        return super(MindMapNode, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.selected and (
                self.collide_point(touch.x - self.offset[0], touch.y - self.offset[1]) or self.collide_point(
                *touch.pos)):
            self.x = touch.x - self.offset[0]
            self.y = touch.y - self.offset[1]
            for connected_node, line_group in self.connection_lines:
                line_group.children[-1].points = [self.center_x, self.center_y, connected_node.center_x,
                                                  connected_node.center_y]
            return True
        return super(MindMapNode, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if self.click_count == 0:
                self.click_count += 1
                Clock.schedule_once(self.reset_click_count, 0.3)
                return True
            else:
                self.click_count = 0
                self.show_rename_popup()
                return True
        return False

    def move_node(self, dx, dy):
        self.x += dx
        self.y += dy

    def reset_click_count(self, *args):
        self.click_count = 0

    def select_node(self):
        self.selected = not self.selected
        if self.selected:
            self.background_color = (1, 0, 0, 1)
        else:
            self.background_color = (1, 1, 1, 1)

    def show_rename_popup(self):
        content = FloatLayout()
        text_input = TextInput(text=self.text, size_hint=(0.8, 0.2), pos_hint={"x": 0.1, "top": 0.8})
        submit_button = Button(text="Submit", size_hint=(0.3, 0.2), pos_hint={"x": 0.35, "y": 0.1})
        content.add_widget(text_input)
        content.add_widget(submit_button)
        popup = Popup(title="Rename Node", content=content, size_hint=(0.5, 0.5), auto_dismiss=False)

        def rename_node(*args):
            self.text = text_input.text
            popup.dismiss()
            self.parent.request_keyboard()  # 추가된 코드

        submit_button.bind(on_release=rename_node)
        popup.open()


class MindMapApp(App):
    def build(self):
        root_widget = MindMapWidget()
        return root_widget




if __name__ == "__main__":
    MindMapApp().run()

