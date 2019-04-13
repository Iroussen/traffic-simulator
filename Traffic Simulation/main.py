# coding = utf-8
from simulation import *
from map import *
from time import *
from math import exp
import decimal

# Discretize time
decimal.getcontext().prec = 6 # Set the precision for the decimal module
t = decimal.Decimal(0)
dt_s = decimal.Decimal(1)/decimal.Decimal(100)
dt_g = 40 # [ms] # Time interval for graphic update()

delay = 0
average_speed = 0

def next_steps(dt_d, steps):
    T = perf_counter()
    global t
    global average_speed
    dt = float(dt_d)
    for i in range(steps):
        average_speed = 0
        # Generate vehicles
        for gen in generators:
            veh = gen.generate(t)

        # Update acceleration, speed and position of each vehicle
        for veh in vehicles:
            try:
                a = veh.acceleration_IIDM()
                veh.x = veh.x + veh.v*dt + max(0, 0.5*a*dt*dt)
                veh.v = max(0, veh.v + a*dt)
                average_speed += veh.v

                if (veh.road.length - veh.x) <= ((veh.v*veh.v)/(2*veh.b_max) + 30) :
                    veh.turn_speed()

            except:
                next_road_id = None if veh.next_road == None else veh.next_road.id
                leader_index = None if veh.leader == None else vehicles.index(veh.leader)

                print("ERROR DURING THE SIMULATION, while working on {}, going from road {} to {}, following {}"
                .format(vehicles.index(veh), veh.road.id, next_road_id, leader_index))
                raise


        if len(vehicles) > 0:
            average_speed = (average_speed / len(vehicles)) * 3.6

        # Check if the vehicles must change road
        for road in roads:
            road.outgoing_veh(road.first_vehicle(road.cross1))
            road.outgoing_veh(road.first_vehicle(road.cross2))

        for veh in deleted_vehicles:
            gui.map.delete(veh.rep)
        deleted_vehicles.clear()

        t+= dt_d

    global delay
    delay = perf_counter() - T

def update():
    global delay
    global average_speed
    T = perf_counter()
    if gui.controls.play.get():
        # next_steps(decimal.Decimal(dt_g/1000*gui.controls.speed.get()), 1) # less precise but faster
        next_steps(dt_s, int((dt_g/(1000*float(dt_s)))*gui.controls.speed.get()))
        gui.map.draw_vehicle(vehicles)
        gui.controls.time_str.set("Current time : " + str(t) + " s.")
        gui.controls.nb_veh.set(len(vehicles))
        gui.controls.avg_speed.set("{:.4f}".format(average_speed))
        mouseover()
        delay += perf_counter() - T + delay
        gui.map.after(int(dt_g * exp(-delay*1000/dt_g)), update)
    else:
        mouseover()
        gui.map.after(dt_g, update)


mouse_x, mouse_y = 0, 0

def mouseover():
    x, y = gui.map.canvasx(mouse_x), gui.map.canvasy(mouse_y)
    objects = gui.map.find_overlapping(x,y,x,y)
    txt = ""
    for obj in objects:
        tags = gui.map.gettags(obj)
        if "road" in tags:
            for road in roads:
                if road.rep == obj:
                    txt = txt + "Road " + str(roads.index(road)) + "  "
                    break
        elif "cross" in tags:
            for cross in crosses:
                if cross.rep == obj:
                    txt = txt + "Cross " + str(crosses.index(cross)) + "  "
                    break
        elif "vehicle" in tags:
            for veh in vehicles:
                if veh.rep == obj:
                    next_road_id = None if veh.next_road == None else veh.next_road.id
                    leader_index = None if veh.leader == None else vehicles.index(veh.leader)
                    txt = txt + "Vehicle {} (going to: {}, leader: {})".format(vehicles.index(veh), next_road_id, leader_index)
                    break
    gui.map.itemconfigure(tag, text=txt)
    gui.map.coords(tag, x+15, y+15)

def moved(event):
    global mouse_x, mouse_y
    mouse_x, mouse_y = event.x, event.y

gui.map.bind("<Motion>", moved)
tag = gui.map.create_text(10, 10, text="", anchor="nw")

gui.map.after(dt_g, update)
gui.root.mainloop()