import logging
import time
from random import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Line, Ellipse
from kivy.logger import Logger

# Setup basic configuration for logging
logging.basicConfig(level=logging.DEBUG)

class MyPaintWidget(Widget):
    def __init__(self, **kwargs):
        super(MyPaintWidget, self).__init__(**kwargs)
        self.points = []# Initialize an empty list to store point coordinates
        self.time_stamps = []# Store timestamps for each point

    def on_touch_down(self, touch):
        current_time = time.time()
        self.time_stamps.append(current_time)# Record time at touch down
        Logger.info('Touchs: Down, Pos: {}, Time: {}'.format(touch.pos, current_time))

        app = App.get_running_app()# Get the instance of the running app
        app.coord_label.text = f"Last Point: {touch.pos}"# Update the label directly via the app instance

        if 'pressure' in touch.profile:# Check if pressure information is available
            Logger.info(f"Pressure detected: {touch.pressure}")
            line_width = max(1, touch.pressure * 10)# Scale the pressure to a suitable line width
        else:
            Logger.warning("Pressure not detected.")
            line_width = 1.0# Default line width if no pressure information is available

        color = (random(), 1, 1)
        with self.canvas:
            Color(*color, mode='hsv')
            d = max(1, line_width)# Draw a dot
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=line_width)

    def on_touch_move(self, touch):
        current_time = time.time()
        self.time_stamps.append(current_time)# Record time at touch move
        Logger.info('Touch: Move, Pos: {}, Time: {}'.format(touch.pos, current_time))

        app = App.get_running_app()
        app.coord_label.text = f"Last Point: {touch.pos}"# Update the label directly via the app instance

        if 'line' in touch.ud:
            if 'pressure' in touch.profile:
                touch.ud['line'].width = max(1, touch.pressure * 10)# Update the line width with pressure
        touch.ud['line'].points += [touch.x, touch.y]

    def on_touch_up(self, touch):
        if self.time_stamps:
            duration = self.time_stamps[-1] - self.time_stamps[0]
            fps = len(self.time_stamps) / duration if duration > 0 else 0
            Logger.info(f"Total Duration: {duration:.2f} seconds, FPS: {fps:.2f}")
            app = App.get_running_app()
            app.coord_label.text = f"Duration: {duration:.2f} s, FPS: {fps:.2f}"

class MyPaintApp(App):
    def build(self):
        self.coord_label = Label(size_hint=(1, 0.1), text='Last Point:') # Label to display coordinates
        self.painter = MyPaintWidget()
        clearbtn = Button(text='Clear', size_hint=(1, 0.1))
        clearbtn.bind(on_release=self.clear_canvas)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.coord_label)
        layout.add_widget(self.painter)
        layout.add_widget(clearbtn)
        return layout

    def clear_canvas(self, instance):
        self.painter.canvas.clear()
        self.painter.points = []# Reset the points list
        self.painter.time_stamps = []# Reset the timestamps list
        self.coord_label.text = "Canvas Cleared"

if __name__ == '__main__':
    MyPaintApp().run()