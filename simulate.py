import random
from math import *
import arcade
import matplotlib.pyplot as plt

# some constants to play with

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Population Simulator"

BG_COLOR = (255, 255, 255)
HEALTHY_COLOR = (124, 198, 254)
INFECTED_COLOR = (231, 187, 227)

HEALTHY_COLOR_PLT = (HEALTHY_COLOR[0] / 255, HEALTHY_COLOR[1] / 255, HEALTHY_COLOR[2] / 255)
INFECTED_COLOR_PLT = (INFECTED_COLOR[0] / 255, INFECTED_COLOR[1] / 255, INFECTED_COLOR[2] / 255)

STEP_SIZE = 1
STEPS_PER_FRAME = 1
POPULATION_SIZE_ROOT = 0  # 0 for testing setup
RESOLUTION_FACTOR = SCREEN_WIDTH / (POPULATION_SIZE_ROOT + 1)
PERSON_RADIUS = 60


class Person:
    def __init__(self, person_id, coords):
        self._person_id = person_id
        self.coords = coords
        self.is_healthy = True
        self.direction = random.uniform(0, 2 * pi)
        self.velocity = STEP_SIZE
        print("Created person with direction %f" % self.direction)

    @property
    def id(self):
        return self._person_id

    def infect(self):
        self.is_healthy = False

    def is_infected(self):
        return not self.is_healthy

    def vel_x(self):
        return self.velocity * cos(self.direction)

    def vel_y(self):
        return self.velocity * sin(self.direction)

    def step(self):
        new_x = self.coords[0] + self.vel_x()
        new_y = self.coords[1] + self.vel_y()

        if not (PERSON_RADIUS < new_x < SCREEN_WIDTH - PERSON_RADIUS):
            self.bounce_h()
            new_x = self.coords[0] + self.velocity * cos(self.direction)

        if not (PERSON_RADIUS < new_y < SCREEN_HEIGHT - PERSON_RADIUS):
            self.bounce_v()
            new_y = self.coords[1] + self.velocity * sin(self.direction)

        self.coords = (new_x, new_y)

    def draw(self):
        arcade.draw_circle_filled(self.coords[0],
                                  self.coords[1],
                                  PERSON_RADIUS,
                                  HEALTHY_COLOR if self.is_healthy else INFECTED_COLOR)

    def bounce_angle(self, other_person):
        dx = self.coords[0] - other_person.coords[0]
        dy = self.coords[1] - other_person.coords[1]
        if dx == 0:
            return abs(dy) / dy * pi / 2
        return atan2(dy, dx)

    @staticmethod
    def bounce(person1, person2):
        print("Bounce:\nPerson1 direction before: %f\nPerson2 direction before: %f" % (
            person1.direction, person2.direction))

        bounce_angle = person1.bounce_angle(person2)

        alpha = person1.direction - bounce_angle
        beta = person2.direction - bounce_angle

        v1_x = person1.velocity * sin(alpha)
        v1_y = person1.velocity * cos(alpha)

        v2_x = person2.velocity * sin(beta)
        v2_y = person2.velocity * cos(beta)

        person1.velocity = sqrt(pow(v1_y, 2) + pow(v2_x, 2))
        person2.velocity = sqrt(pow(v2_y, 2) + pow(v1_x, 2))

        person1.direction = atan2(v1_y, v2_x)  # todo atan possibly wrong (- pi / 2 < atan x < pi / 2)
        person1.direction += bounce_angle

        person2.direction = atan2(v2_y, v1_x)
        person2.direction += bounce_angle

        print("Bounce:\nPerson1 direction after: %f\nPerson2 direction after: %f" % (
            person1.direction, person2.direction))

    @staticmethod
    def distance(person1, person2):
        return sqrt(pow(person1.coords[0] - person2.coords[0], 2)
                    + pow(person1.coords[1] - person2.coords[1], 2))

    @staticmethod
    def are_colliding(person1, person2):
        return Person.distance(person1, person2) <= 2 * PERSON_RADIUS

    def bounce_v(self):
        self.direction = 2 * pi - self.direction

    def bounce_h(self):
        self.direction = 1 * pi - self.direction


class Simulation:
    def __init__(self, size_x, size_y):
        print("Simulation has not yet begun")
        self.collisions = 0
        self.step = 0
        self.can_bounce_again = {}

        self.healthy = size_x * size_y - 1
        self.infected = 1
        self.healthy_history = []
        self.infected_history = []

        if POPULATION_SIZE_ROOT <= 0:
            self.population = [Person(0, (400, 300)), Person(1, (200, 300))]
            self.population[0].direction = 0
            self.population[1].direction = 0.7
        else:
            self.population = []
            for i in range(size_x):
                coord_x = (i + 1) * RESOLUTION_FACTOR
                for j in range(size_y):
                    coord_y = (j + 1) * RESOLUTION_FACTOR
                    new_person = Person(len(self.population), (coord_x, coord_y))
                    if i == POPULATION_SIZE_ROOT // 2 and j == POPULATION_SIZE_ROOT // 2:
                        new_person.infect()
                    self.population.append(new_person)
        self.init_collision_history()

    def run_step(self):
        # print("Simulation step #%d" % self.step)
        step_collisions = 0

        for i in range(len(self.population)):
            person = self.population[i]
            for j in range(i):
                other_person = self.population[j]
                key = (person.id, other_person.id)
                if Person.are_colliding(person, other_person):
                    step_collisions += 1
                    print("Step %d" % self.step)
                    if self.can_bounce_again.get(key):
                        Person.bounce(person, other_person)
                        self.can_bounce_again[key] = False
                    if person.is_infected() ^ other_person.is_infected():
                        person.infect()
                        other_person.infect()
                        self.healthy -= 1
                        self.infected += 1
                else:
                    self.can_bounce_again[key] = True
            person.step()

        # print("\tHealthy: %d\n\tInfected: %d" % (self.healthy, self.infected))
        self.collisions += step_collisions
        self.step += 1
        self.healthy_history.append(self.healthy)
        self.infected_history.append(self.infected)

    def plot(self):
        line = plt.plot(self.infected_history)
        plt.setp(line, color=INFECTED_COLOR_PLT, linewidth=3.0, label='Infected')
        plt.ylabel('Simulation history')
        plt.show()

    def end(self):
        arcade.close_window()
        print("%d total collisions" % self.collisions)
        self.plot()

    def init_collision_history(self):
        for i in range(len(self.population)):
            for j in range(i):
                self.can_bounce_again[(i, j)] = True
        print(self.can_bounce_again)


class SimulationWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(BG_COLOR)
        self.simulation = Simulation(POPULATION_SIZE_ROOT, POPULATION_SIZE_ROOT)

    def on_draw(self):
        arcade.start_render()
        for person in self.simulation.population:
            person.draw()

    def on_update(self, delta_time):
        for i in range(STEPS_PER_FRAME):
            self.simulation.run_step()
        if self.simulation.healthy == 0:
            self.simulation.end()


def main():
    SimulationWindow()
    arcade.run()


if __name__ == "__main__":
    main()
