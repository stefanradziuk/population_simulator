import random
from math import pi, sin, cos, sqrt, pow
import time
import pyglet
from pyglet.gl import *

# some constants to play with

step_size = 0.1
step_delay = 10
simulation_length = 100
person_radius = 0.2

window = pyglet.window.Window()

class Person:
    def __init__(self, coords):
        self.coords = coords
        self.healthy = True
        self.direction = random.uniform(0, 2 * pi)

    def infect(self):
        self.healthy = False

    def step(self):
        new_x = self.coords[0] + step_size * sin(self.direction)
        new_y = self.coords[1] + step_size * cos(self.direction)
        self.coords = (new_x, new_y)

    def draw(self):
        x = self.coords[0]
        y = self.coords[1]

        iterations = int(2 * person_radius * pi)
        s = sin(2 * pi / iterations)
        c = cos(2 * pi / iterations)
    
        dx, dy = person_radius, 0
    
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(x, y)
        for i in range(iterations+1):
            glVertex2f(x + dx, y + dy)
            dx, dy = (dx * c - dy * s), (dy * c + dx * s)
        glEnd()


    @staticmethod
    def distance(person1, person2):
        return sqrt(pow(person1.coords[0] - person2.coords[0], 2)
                  + pow(person1.coords[1] - person2.coords[1], 2))

class Simulation:
    def __init__(self, size_x, size_y):
        self.step_label = pyglet.text.Label(text="Simulation has not yet begun")
        self.collisions = 0

        self.population = set()
        for i in range(size_x):
            for j in range(size_y):
                self.population.add(Person((i, j)))

    def run(self):
        for step in range(simulation_length):
            print("Simulation step #%d" % step)
            self.step_label = pyglet.text.Label(text="Simulation step #%d" % step)
            step_collisions = 0
            for person in self.population:
                person.step()
                person.draw()
                for other_person in self.population:
                    if (not person is other_person) and Person.distance(person, other_person) < 2 * person_radius:
                        step_collisions += 1
            print("  collisions: %d" % step_collisions)
            collisions += step_collisions
            time.sleep(step_delay / 1000)
        print("%d total collisions" % collisions)

simulation = Simulation(10, 10)

@window.event
def on_draw():
    window.clear()
    simulation.run()
    simulation.step_label.draw()


pyglet.app.run()
