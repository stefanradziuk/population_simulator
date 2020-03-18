import random
from math import pi, sin, cos, sqrt, pow
import time
import arcade
import matplotlib.pyplot as plt

# some constants to play with

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Population Simulator"

HEALTHY_COLOR = arcade.color.AMAZON
INFECTED_COLOR = arcade.color.CARMINE_RED

STEP_SIZE = 2
STEP_DELAY = 1             # ms
SIMULATION_LENGTH = 600
PERSON_RADIUS = 0.1
POPULATION_LENGTH = 10

RESOLUTION_FACTOR = SCREEN_WIDTH / POPULATION_LENGTH

class Person:
    def __init__(self, coords):
        self.coords = coords
        self.healthy = True
        self.direction = random.uniform(0, 2 * pi)

    def infect(self):
        self.healthy = False

    def is_infected(self):
        return not self.healthy

    def step(self):
        new_x = (self.coords[0] + STEP_SIZE * sin(self.direction)) % SCREEN_WIDTH
        new_y = (self.coords[1] + STEP_SIZE * cos(self.direction)) % SCREEN_HEIGHT
        self.coords = (new_x, new_y)

    def draw(self):
        arcade.draw_circle_filled(self.coords[0],
                                  self.coords[1],
                                  PERSON_RADIUS * RESOLUTION_FACTOR,
                                  HEALTHY_COLOR if self.healthy else INFECTED_COLOR)

    @staticmethod
    def distance(person1, person2):
        return sqrt(pow(person1.coords[0] - person2.coords[0], 2)
                  + pow(person1.coords[1] - person2.coords[1], 2))

    @staticmethod
    def collide(person1, person2):
        return Person.distance(person1, person2) <= 2 * PERSON_RADIUS * RESOLUTION_FACTOR

class Simulation:
    def __init__(self, size_x, size_y):
        print("Simulation has not yet begun")
        self.collisions = 0
        self.step = 0

        self.healthy = size_x * size_y - 1
        self.infected = 1
        self.history = []

        self.population = set()
        for i in range(size_x):
            for j in range(size_y):
                new_person = Person((i * RESOLUTION_FACTOR,  j * RESOLUTION_FACTOR))
                if i == POPULATION_LENGTH / 2 and j == POPULATION_LENGTH / 2:
                    new_person.infect()
                self.population.add(new_person)

    def runStep(self):
            print("Simulation step #%d" % self.step)
            step_collisions = 0

            for person in self.population:
                person.step()
                for other_person in self.population:

                    if (not person is other_person) and Person.collide(person, other_person):
                        step_collisions += 1
                        if person.is_infected() ^ other_person.is_infected():
                            person.infect()
                            other_person.infect()
                            self.healthy -= 1
                            self.infected += 1

            print("  collisions: %d" % step_collisions)
            self.collisions += step_collisions
            self.step += 1
            self.history.append((self.healthy, self.infected))
            time.sleep(STEP_DELAY / 1000)

    def end(self):
        arcade.close_window()
        print("%d total collisions" % self.collisions)
        plt.plot(self.history)
        plt.ylabel('Simulation history')
        plt.show()

class SimulationWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.simulation = Simulation(POPULATION_LENGTH, POPULATION_LENGTH)

    def on_draw(self):
        arcade.start_render()
        for person in self.simulation.population:
            person.draw()

    def on_update(self, delta_time):
        self.simulation.runStep()
        if self.simulation.step >= SIMULATION_LENGTH:
            self.simulation.end()

def main():
    SimulationWindow()
    arcade.run()

if __name__ == "__main__":
    main()

