# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 17:43:24 2024

@author: Helen
"""
import simpy
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

SETUP_TIME_MIN = 5
SETUP_TIME_MAX = 15
# SETUP_TIME = 15

MID_SETUP_TIME_MIN = 2
MID_SETUP_TIME_MAX = 5
# MID_SETUP_TIME = 7

TREATMENT_TIME_MIN = 1
TREATMENT_TIME_MAX = 2
# TREATMENT_TIME = 2

ENTRY_TIME_MIN = 1
ENTRY_TIME_MAX = 3
# ENTRY_TIME = 2

EXIT_TIME_MIN = 1
EXIT_TIME_MAX = 3
# EXIT_TIME = 2

# NUM_BEAMS = 2

SIM_TIME = 90

ARRIVAL_INTERVAL_MEAN = 15

PATIENT_LIMIT = 20

NUM_TREATMENT_ROOMS = 3

waiting_room = {}

patientList =[]

# random.seed(9)
 
fig, ax = plt.subplots(figsize=(25, 6))
room_events = {x: [] for x in range(NUM_TREATMENT_ROOMS)}

def add_event(room_num, pat_name, event_time, event_type):
    room_events[room_num].append({
        'index': None,
        'pat_name': pat_name,
        'event_time': round(event_time, 1),
        'event_type': event_type,
        })

class Patient(object):
    def __init__(self, name, env, treatment_rooms, synch):
        self.name = name
        self.env = env
        self.treatment_rooms = treatment_rooms
        # self.treatment_rooms = random.choices([1, 2, 3], [0.4, 0.4, 0.2])[0]
        self.synch = synch
        # self.num_beams = NUM_BEAMS
        self.num_beams = random.choices([1, 2, 4], [0.5, 0.3, 0.2])[0]
        # print(f"{self.name} has {self.num_beams} beams")
        self.treatment_room = None
        self.action = env.process(self.go_through_treatment())

    def go_through_treatment(self):
        #print(f"{self.name}")
        while True:
            waiting_pat = next(((k, v) for k, v in waiting_room.items() if v['waiting_end'] is None), None)
            tx_room = next((x for x in self.treatment_rooms if not x.users), None)

            if tx_room is not None and (waiting_pat is None or waiting_pat[0] == self.name):

                if self.name in waiting_room:
                    waiting_room[self.name]['waiting_end'] = self.env.now

                self.treatment_room = tx_room
                break

            else:
                if self.name not in waiting_room:
                    waiting_room[self.name] = {
                        'waiting_start': self.env.now,
                        'waiting_end': None,
                        }

                yield self.env.timeout(0.5)

        t = self.env.now
        add_event(self.treatment_rooms.index(self.treatment_room), self.name, t, 1)
        # print(f"{self.name} enters Treatment Room {self.treatment_rooms.index(self.treatment_room)+1} at {t}")
        with self.treatment_room.request() as req_room:
            yield req_room
            yield self.env.timeout(random.uniform(ENTRY_TIME_MIN, ENTRY_TIME_MAX))
            yield self.env.process(self.do_setup())

            for i in range(self.num_beams):
                with self.synch.request() as req_synch:
                    yield req_synch
                    # yield self.env.timeout(0.5)
                    yield self.env.process(self.do_treatment(i))
                    self.synch.release(req_synch)  # release the synch after each treatment

                if i < (self.num_beams - 1):
                    # yield self.env.timeout(0.5)
                    yield self.env.process(self.do_mid_setup())

        t = self.env.now
        add_event(self.treatment_rooms.index(self.treatment_room), self.name, t, 7)
        # print(f"{self.name} leaves Treatment Room {self.treatment_rooms.index(self.treatment_room)+1} at {t}")
        yield self.env.process(self.patient_exit())
        t = self.env.now
        add_event(self.treatment_rooms.index(self.treatment_room), self.name, t, 8)

    def do_setup(self):
        # setup_time = SETUP_TIME
        setup_time = random.uniform(SETUP_TIME_MIN, SETUP_TIME_MAX)
        t = self.env.now
        add_event(self.treatment_rooms.index(self.treatment_room), self.name, t, 2)
        # print(f"{self.name} starts setup in Treatment Room {self.treatment_rooms.index(self.treatment_room)+1} at {t}")
        yield self.env.timeout(setup_time)
        t = self.env.now
        add_event(self.treatment_rooms.index(self.treatment_room), self.name, t, 3)
        # print(f"{self.name} finishes setup at {t}")

    def do_treatment(self, i):
        # treatment_time = TREATMENT_TIME
        treatment_time = random.uniform(TREATMENT_TIME_MIN, TREATMENT_TIME_MAX)
        t = self.env.now
        add_event(self.treatment_rooms.index(self.treatment_room), self.name, t, 4)
        # print(f"{self.name} starts beam {i+1} in Treatment Room {self.treatment_rooms.index(self.treatment_room)+1} at {t}")
        yield self.env.timeout(treatment_time)
        t = self.env.now
        add_event(self.treatment_rooms.index(self.treatment_room), self.name, t, 5)
        # print(f"{self.name} finishes treatment of beam {i+1} at {t}")

    def do_mid_setup(self):
        # setup_time = SETUP_TIME / 2
        mid_setup_time = random.uniform(MID_SETUP_TIME_MIN, MID_SETUP_TIME_MAX)
        yield self.env.timeout(mid_setup_time)
        t = self.env.now
        add_event(self.treatment_rooms.index(self.treatment_room), self.name, t, 6)
        # print(f"{self.name} finishes mid treatment setup at {t}")
    
    def patient_exit(self):
        # exit_time = EXIT_TIME
        exit_time = random.uniform(EXIT_TIME_MIN, EXIT_TIME_MAX)
        yield self.env.timeout(exit_time)
        # print(f"{self.name} leaves Treatment Room {self.treatment_rooms.index(self.treatment_room)+1} at {self.env.now:.2f}")
        t = self.env.now
        add_event(self.treatment_rooms.index(self.treatment_room), self.name, t, 8)

def patient_generator(env, treatment_rooms, synch):
    # for i in range(NUM_TREATMENT_ROOMS):
        # Patient(f"Patient {i}", env, treatment_rooms, synch)

    # while True:
    # for i in range(PATIENT_LIMIT):  # stop creating patients once the limit is reached
        # yield env.timeout(random.expovariate(1.0 / ARRIVAL_INTERVAL_MEAN))
        # Patient(f"Patient {i}", env, treatment_rooms, synch)
        # i += 1
    i = 1
    for i in range(1,4):
       Patient(f"   Patient {i}", env, treatment_rooms, synch)
       patientList.append(i) 

    while True:
        i += 1
        yield env.timeout(random.expovariate(1.0/ARRIVAL_INTERVAL_MEAN))
        Patient(f"   Patient {i}", env, treatment_rooms, synch)
        patientList.append(i)
        

def run_simulation():
    env = simpy.Environment()
    treatment_rooms = [simpy.Resource(env, capacity=1) for _ in range(NUM_TREATMENT_ROOMS)]
    synch = simpy.Resource(env, capacity=1)  # one synch
    env.process(patient_generator(env, treatment_rooms, synch))
    env.run(until=SIM_TIME)

run_simulation()

room_numbers = range(NUM_TREATMENT_ROOMS)

event_colors = [
    'none', # 0: wait for patient to enter room
    'none', # 1: enter room
    '#ffe066', # 2: start setup event, yellow
    '#66ccff', # 3: finish setup event, blue
    '#ff80bf', # 4: waiting for beam, pink
    '#00cc00', # 5: beam delivery, green
    '#66ccff', # 6: mid-beam setup event, blue
    '#8791a5', # 7: leave room, gray
    '#8791a5', # 8:
    ]

def plot_sim():
    for k, v in room_events.items():
        y = NUM_TREATMENT_ROOMS - k - 1
        for i in range(len(v)-1):
            e0 = v[i]
            e1 = v[i+1]

            if e0['pat_name'] in waiting_room:
                ax.add_patch(Rectangle((waiting_room[e0['pat_name']]['waiting_start'], y+0.7),
                                    waiting_room[e0['pat_name']]['waiting_end'] - waiting_room[e0['pat_name']]['waiting_start'],
                                    0.16, linewidth=0.5, edgecolor='k', facecolor='#b3c6ff', alpha=0.5, rasterized=True))
            t_begin = e0['event_time']
            t_end = e1['event_time']
            ax.add_patch(Rectangle((e0['event_time'], y), e1['event_time'] - e0['event_time'],
                                   0.9, linewidth=1, edgecolor='none', facecolor=event_colors[e1['event_type']]))
            
            ax.plot([t_begin, t_end], [y, y], alpha=0)

            if e0['event_type'] == 1:
                plt.text(e0['event_time']+0.2, y+0.3, e0['pat_name'])

    ax.set_xlim(left=0)
    ax.set_ylim(bottom=-0.5, top=4.0)
    plt.yticks(ticks=[x+0.45 for x in room_numbers], labels=[str(NUM_TREATMENT_ROOMS-x) for x in room_numbers])
    ax.set_ylabel('room number')
    ax.set_xlabel('time [minute]')

plot_sim()