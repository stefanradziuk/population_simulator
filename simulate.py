import random
from enum import Enum
from math import *
import matplotlib.pyplot as plt
import arcade

# todo better bookkeeping and graphing (incl. recovery stats)

BOX_WIDTH = 600
BOX_HEIGHT = 600
SCREEN_TITLE = "Population Simulator"

GRAPH_HEIGHT = 100

BG_COLOR = (250, 250, 250)
HEALTHY_COLOR = (124, 198, 254)
INFECTED_COLOR = (231, 187, 227)
RECOVERED_COLOR = (204, 232, 204)

BG_COLOR_PLT = (BG_COLOR[0] / 255, BG_COLOR[1] / 255, BG_COLOR[2] / 255)
HEALTHY_COLOR_PLT = (HEALTHY_COLOR[0] / 255, HEALTHY_COLOR[1] / 255, HEALTHY_COLOR[2] / 255)
INFECTED_COLOR_PLT = (INFECTED_COLOR[0] / 255, INFECTED_COLOR[1] / 255, INFECTED_COLOR[2] / 255)
RECOVERED_COLOR_PLT = (RECOVERED_COLOR[0] / 255, RECOVERED_COLOR[1] / 255, RECOVERED_COLOR[2] / 255)

# some simulation constants to play with
STEP_SIZE = 0.5
STEPS_PER_FRAME = 1
POPULATION_SIZE_ROOT = 8  # set to 0 for debugging setup
PERSON_RADIUS = 20
RECOVERY_PERIOD = 350
RESOLUTION_FACTOR = BOX_WIDTH / (POPULATION_SIZE_ROOT + 1)


class HealthState(Enum):
    HEALTHY = 0
    INFECTED = 1
    RECOVERED = 2


state_colors = {HealthState.HEALTHY: HEALTHY_COLOR,
                HealthState.INFECTED: INFECTED_COLOR,
                HealthState.RECOVERED: RECOVERED_COLOR}


class Person:
    def __init__(self, person_id, coords):
        self._person_id = person_id
        self.coords = coords
        self.health_state = HealthState.HEALTHY
        self.infection_date = - RECOVERY_PERIOD * 8
        self.direction = random.uniform(0, tau)
        self.velocity = STEP_SIZE

    @property
    def id(self):
        return self._person_id

    def infect(self, date):
        self.health_state = HealthState.INFECTED
        self.infection_date = date

    def recover(self):
        self.health_state = HealthState.RECOVERED

    def is_healthy(self):
        return self.health_state == HealthState.HEALTHY

    def is_infected(self):
        return self.health_state == HealthState.INFECTED

    def has_recovered(self):
        return self.health_state == HealthState.RECOVERED

    def step(self):
        new_x = self.coords[0] + self.velocity * cos(self.direction)
        new_y = self.coords[1] + self.velocity * sin(self.direction)

        if not (PERSON_RADIUS < new_x < BOX_WIDTH - PERSON_RADIUS):
            self.bounce_h()
            new_x = self.coords[0] + self.velocity * cos(self.direction)

        if not (PERSON_RADIUS < new_y < BOX_HEIGHT - PERSON_RADIUS):
            self.bounce_v()
            new_y = self.coords[1] + self.velocity * sin(self.direction)

        self.coords = (new_x, new_y)
        self.direction %= tau

    def draw(self):
        arcade.draw_circle_filled(center_x=self.coords[0],
                                  center_y=self.coords[1] + GRAPH_HEIGHT,
                                  radius=PERSON_RADIUS,
                                  color=state_colors.get(self.health_state))

    def bounce_angle(self, other_person):
        dx = self.coords[0] - other_person.coords[0]
        dy = self.coords[1] - other_person.coords[1]
        return atan2(dy, dx)

    # implements oblique collision physics
    @staticmethod
    def bounce(person1, person2):
        bounce_angle = person1.bounce_angle(person2)

        # angles relative to the collision axis
        alpha = person1.direction - bounce_angle
        beta = person2.direction - bounce_angle

        # calculate the velocities tangent and normal
        # with regards to the collision axis
        v1_tan = person1.velocity * sin(alpha)
        v1_nor = person1.velocity * cos(alpha)
        v2_tan = person2.velocity * sin(beta)
        v2_nor = person2.velocity * cos(beta)

        person1.velocity = sqrt(pow(v1_tan, 2) + pow(v2_nor, 2))
        person2.velocity = sqrt(pow(v2_tan, 2) + pow(v1_nor, 2))

        person1.direction = atan2(v1_tan, v2_nor)
        person2.direction = atan2(v2_tan, v1_nor)

        person1.direction += bounce_angle
        person2.direction += bounce_angle

    @staticmethod
    def distance(person1, person2):
        return sqrt(pow(person1.coords[0] - person2.coords[0], 2)
                    + pow(person1.coords[1] - person2.coords[1], 2))

    @staticmethod
    def are_colliding(person1, person2):
        return Person.distance(person1, person2) <= 2 * PERSON_RADIUS

    def bounce_v(self):
        self.direction = tau - self.direction

    def bounce_h(self):
        self.direction = pi - self.direction


class Simulation:
    def __init__(self, size_x, size_y):
        print("Simulation initiating")
        self.collisions = 0
        self.step = 0
        self.can_bounce_again = {}
        self.infection_dates = {}

        # todo move those elsewhere
        self.healthy = size_x * size_y - 1
        self.infected = 1
        self.healthy_history = []
        self.infected_history = []

        if POPULATION_SIZE_ROOT <= 0:
            # debugging mode
            self.population = [Person(0, (400, 300)), Person(1, (200, 300))]
            self.population[0].direction = pi
            self.population[1].direction = 0.3
        else:
            self.population = []
            for i in range(size_x):
                coord_x = (i + 1) * RESOLUTION_FACTOR
                for j in range(size_y):
                    coord_y = (j + 1) * RESOLUTION_FACTOR
                    new_person = Person(len(self.population), (coord_x, coord_y))
                    if i == POPULATION_SIZE_ROOT // 2 and j == POPULATION_SIZE_ROOT // 2:
                        self.infect(new_person)
                    self.population.append(new_person)
        self.init_collision_history()

    def run_step(self):
        self.recovery_check()
        for i, person in enumerate(self.population):
            for j, other_person in enumerate(self.population[:i]):
                key = (person.id, other_person.id)
                if Person.are_colliding(person, other_person):
                    if self.can_bounce_again.get(key):
                        Person.bounce(person, other_person)
                        self.can_bounce_again[key] = True  # todo
                        # self.can_bounce_again[key] = False
                    if person.is_infected() and other_person.is_healthy():
                        self.infect(other_person)
                    elif other_person.is_infected() and person.is_healthy():
                        self.infect(person)
                else:
                    self.can_bounce_again[key] = True
            person.step()

        self.step += 1
        self.healthy_history.append(self.healthy)
        self.infected_history.append(self.infected)

    def plot(self):
        line = plt.plot(self.infected_history)
        plt.setp(line, color=INFECTED_COLOR_PLT, linewidth=3.0, label='Infected')
        plt.ylabel('Simulation history')
        plt.show()

    def init_collision_history(self):
        for i in range(len(self.population)):
            for j in range(i):
                self.can_bounce_again[(i, j)] = True

    def infect(self, person):
        person.infect(self.step)
        self.infection_dates[person.id] = self.step
        self.healthy -= 1
        self.infected += 1
        # todo manipulate history

    def recovery_check(self):
        for person_id in self.infection_dates.keys():
            if self.infection_dates[person_id] + RECOVERY_PERIOD == self.step:
                self.population[person_id].recover()
                self.healthy += 1
                self.infected -= 1
                # todo manipulate history


class SimulationWindow(arcade.Window):
    def __init__(self):
        super().__init__(BOX_WIDTH, BOX_HEIGHT + GRAPH_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(BG_COLOR)
        self.simulation = Simulation(POPULATION_SIZE_ROOT, POPULATION_SIZE_ROOT)

    def on_draw(self):
        arcade.start_render()
        for person in self.simulation.population:
            person.draw()
        self.redraw_live_graph()
        if self.simulation.infected <= 0:
            self.on_close()

    def on_update(self, delta_time):
        for i in range(STEPS_PER_FRAME):
            self.simulation.run_step()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.Q:
            self.on_close()

    def on_close(self):
        self.simulation.plot()
        arcade.close_window()

    def redraw_live_graph(self):
        prev_x = 0
        prev_y = 0
        for step, infected in enumerate(self.simulation.infected_history[::10]):
            curr_x = step * 2
            curr_y = infected / len(self.simulation.population) * GRAPH_HEIGHT
            arcade.draw_line(start_x=prev_x,
                             start_y=prev_y,
                             end_x=curr_x,
                             end_y=curr_y,
                             line_width=4,
                             color=arcade.color.BLACK)
            prev_x = curr_x
            prev_y = curr_y


def main():
    SimulationWindow()
    arcade.run()


if __name__ == "__main__":
    main()
