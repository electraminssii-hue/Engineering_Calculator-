from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from math import sqrt

def fa_to_en(text):
    fa_digits = '۰۱۲۳۴۵۶۷۸۹'
    en_digits = '0123456789'
    return text.translate(str.maketrans(fa_digits, en_digits))

def sanitize_input(instance, value):
    instance.text = fa_to_en(value)

class LCDLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = 36
        self.bold = True
        self.color = (0, 1, 0, 1)
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

class EngineeringCalculator(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=20, **kwargs)
        Window.clearcolor = (0.05, 0.05, 0.05, 1)
        self.inputs = []
        self.focused_input = None
        self.computed_flags = [False, False, False]

        header = Label(text='🔧 Electrical Engineering Calculator', font_size=42, bold=True,
                       size_hint_y=None, height=80, color=(1, 1, 0.8, 1))
        with header.canvas.before:
            Color(0.15, 0.15, 0.4, 1)
            header.rect = Rectangle(size=header.size, pos=header.pos)
            header.bind(size=lambda *a: setattr(header.rect, 'size', header.size),
                        pos=lambda *a: setattr(header.rect, 'pos', header.pos))
        self.add_widget(header)

        top_row = GridLayout(cols=4, spacing=15, size_hint_y=None, height=100)
        labels = ['Power (P)', 'Voltage (V)', 'Resistance (R)', 'Current (I)']
        for i in range(4):
            ti = TextInput(hint_text=labels[i], multiline=False,
                           font_size=32, size_hint=(1, None), height=80,
                           background_color=(0.2, 0.25, 0.3, 1),
                           foreground_color=(1, 1, 1, 1),
                           use_bubble=False, use_handles=False)
            ti.bind(text=sanitize_input)
            ti.bind(focus=self.set_focus)
            if i < 3:
                ti.bind(text=self.update_dependent_values)
            self.inputs.append(ti)
            top_row.add_widget(ti)
        self.add_widget(top_row)

        self.top_result = LCDLabel(text='Top row result', size_hint_y=None, height=80)
        self.calc_result = LCDLabel(text='Calculation result', size_hint_y=None, height=80)
        self.add_widget(self.top_result)
        self.add_widget(self.calc_result)

        input_grid = GridLayout(cols=4, spacing=15, size_hint_y=None, height=500)
        for i in range(16):
            ti = TextInput(hint_text=f'Input {i+1}', multiline=False,
                           font_size=28, size_hint_y=None, height=70,
                           background_color=(0.15, 0.2, 0.25, 1),
                           foreground_color=(1, 1, 1, 1),
                           use_bubble=False, use_handles=False)
            ti.bind(text=sanitize_input)
            ti.bind(focus=self.set_focus)
            self.inputs.append(ti)
            input_grid.add_widget(ti)
        self.add_widget(input_grid)

        def styled_button(text, func):
            btn = Button(text=text, font_size=28,
                         background_color=(0.2, 0.4, 0.6, 1),
                         color=(1, 1, 1, 1))
            btn.bind(on_press=func)
            with btn.canvas.before:
                Color(0.1, 0.1, 0.1, 0.5)
                rect = Rectangle(size=btn.size, pos=btn.pos)
            btn.bind(size=lambda *a: setattr(rect, 'size', btn.size),
                     pos=lambda *a: setattr(rect, 'pos', btn.pos))
            return btn

        button_grid = GridLayout(cols=3, spacing=15, size_hint_y=None, height=240)
        buttons = [
            ('Series Resistance', self.calc_r_series),
            ('Parallel Resistance', self.calc_r_parallel),
            ('Series Capacitance', self.calc_c_series),
            ('Parallel Capacitance', self.calc_c_parallel),
            ('Series Inductance', self.calc_l_series),
            ('Parallel Inductance', self.calc_l_parallel),
        ]
        for text, func in buttons:
            button_grid.add_widget(styled_button(text, func))
        self.add_widget(button_grid)

        nav_grid = GridLayout(cols=4, spacing=15, size_hint_y=None, height=100)
        for direction in ['Left', 'Right', 'Up', 'Down']:
            nav_grid.add_widget(styled_button(direction, lambda x, d=direction.lower(): self.move_focus(d)))
        self.add_widget(nav_grid)

        clear_grid = GridLayout(cols=3, spacing=15, size_hint_y=None, height=100)
        clear_grid.add_widget(styled_button('🧹 Clear Selected', self.clear_selected))
        clear_grid.add_widget(styled_button('⌫ Clear Last', self.clear_last_char))
        clear_grid.add_widget(styled_button('🧼 Clear All', self.clear_all))
        self.add_widget(clear_grid)

        keypad = GridLayout(cols=3, spacing=10, size_hint_y=None, height=320)
        keys = [
            '1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
            '.', '0', '⌫'
        ]
        for key in keys:
            btn = styled_button(key, self.keypad_input)
            keypad.add_widget(btn)
        self.add_widget(keypad)

    def set_focus(self, instance, value):
        if value:
            self.focused_input = instance
            Window.release_all_keyboards()

    def keypad_input(self, instance):
        key = instance.text
        if not self.focused_input:
            return
        text = self.focused_input.text
        if key == '.' and '.' in text:
            return
        elif key == '⌫':
            self.clear_last_char(None)
        elif key in ['n', 'µ', 'k', 'M']:
            unit_map = {'n': 1e-9, 'µ': 1e-6, 'k': 1e3, 'M': 1e6}
            try:
                val = float(text)
                self.focused_input.text = str(val * unit_map[key])
            except:
                self.focused_input.text = 'Error'
        else:
            self.focused_input.text += key

    def move_focus(self, direction):
        if not self.focused_input:
            return
        idx = self.inputs.index(self.focused_input)
        if direction == 'left':
            idx = max(0, idx - 1)
        elif direction == 'right':
            idx = min(len(self.inputs) - 1, idx + 1)
        elif direction == 'up':
            idx = max(0, idx - 4)
        elif direction == 'down':
            idx = min(len(self.inputs) - 1, idx + 4)
        self.inputs[idx].focus = True

    def clear_selected(self, instance):
        if self.focused_input:
            self.focused_input.text = ''

    def clear_last_char(self, instance):
        if self.focused_input:
            self.focused_input.text = self.focused_input.text[:-1]

    def clear_all(self, instance):
        for i in self.inputs:
            i.text = ''
        self.top_result.text = 'Top row result'
        self.calc_result.text = 'Calculation result'
        self.computed_flags = [False, False, False]

    def update_dependent_values(self, instance, value):
        try:
            def safe_float(text):
                return float(text) if text.strip() and text.count('.') <= 1 else None

            P_text = self.inputs[0].text.strip()
            V_text = self.inputs[1].text.strip()
            R_text = self.inputs[2].text.strip()

            P = safe_float(P_text)
            V = safe_float(V_text)
            R = safe_float(R_text)

            entered = [P_text != '' and not self.computed_flags[0],
                       V_text != '' and not self.computed_flags[1],
                       R_text != '' and not self.computed_flags[2]]

            indices = [i for i, ok in enumerate(entered) if ok]
            if len(indices) != 2:
                self.top_result.text = 'Enter any two values (P, V, R)'
                return

            self.computed_flags = [False, False, False]
            I = None

            if indices == [0, 1]:
                I = P / V
                R = V / I
                self.inputs[2].text = f'{R:.2f}'
                self.computed_flags[2] = True
            elif indices == [0, 2]:
                I = sqrt(P / R)
                V = I * R
                self.inputs[1].text = f'{V:.2f}'
                self.computed_flags[1] = True
            elif indices == [1, 2]:
                I = V / R
                P = V * I
                self.inputs[0].text = f'{P:.2f}'
                self.computed_flags[0] = True

            def fmt(val):
                return f'{val:.2f}' if val is not None else '--'

            self.inputs[3].text = fmt(I)
            self.top_result.text = f'P={fmt(P)}, V={fmt(V)}, R={fmt(R)}, I={fmt(I)}'
        except:
            self.top_result.text = 'Invalid input or calculation error.'

    def get_values(self, start=4):
        try:
            return [float(i.text) for i in self.inputs[start:] if i.text.strip()]
        except:
            return None

    def calc_r_series(self, instance):
        values = self.get_values()
        self.calc_result.text = f'Series Resistance: {sum(values):.2f} Ω' if values else 'Invalid input.'

    def calc_r_parallel(self, instance):
        values = self.get_values()
        self.calc_result.text = f'Parallel Resistance: {1 / sum(1 / v for v in values):.2f} Ω' if values and all(v != 0 for v in values) else 'Invalid input.'

    def calc_c_series(self, instance):
        values = self.get_values()
        self.calc_result.text = f'Series Capacitance: {1 / sum(1 / v for v in values):.6f} F' if values and all(v != 0 for v in values) else 'Invalid input.'

    def calc_c_parallel(self, instance):
        values = self.get_values()
        self.calc_result.text = f'Parallel Capacitance: {sum(values):.6f} F' if values else 'Invalid input.'

    def calc_l_series(self, instance):
        values = self.get_values()
        self.calc_result.text = f'Series Inductance: {sum(values):.6f} H' if values else 'Invalid input.'

    def calc_l_parallel(self, instance):
        values = self.get_values()
        if values and all(v != 0 for v in values):
            result = 1 / sum(1 / v for v in values)
            self.calc_result.text = f'Parallel Inductance: {result:.6f} H'
        else:
            self.calc_result.text = 'Invalid input.'

class EngCalcApp(App):
    def build(self):
        return EngineeringCalculator()

if __name__ == '__main__':
    EngCalcApp().run()