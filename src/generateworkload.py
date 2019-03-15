import os
import sys
import random
import numpy as np

class BCScript:
    def __init__(self, agent_name_co, driver_name_co, thread_group_name_co, script_path, profile_path):
        self.agent_name = agent_name_co
        self.driver_name = driver_name_co
        self.thread_group_name = thread_group_name_co
        self.script = open(script_path, "w")
        self.profile_path = profile_path

    def build_up_slope(self, cur_tps, new_tps, tps_record):
        """ We use a finite number of squares to approximate a slope.
            A square takes a certain amount of time to form the shape. 
            We set this time to 1 minute for now. """
        time_min = random.randint(1, 10)
        self.script.write("# Up Slope = {}\n".format(str(time_min)))
        up_per_min = (new_tps - cur_tps) / time_min
        for i in range(time_min - 1):
            self.script.write("# TPS = {}\n".format(str(cur_tps + (i + 1) * int(up_per_min))))
            self.script.write("Alter-BCThreadGroups -AgentName {} -Drivers {} -ThreadGroups {} -ThreadCount {}\n".format(self.agent_name, self.driver_name, self.thread_group_name, str(cur_tps + (i + 1) * int(up_per_min))))
            self.script.write("Start-Sleep -s 60\n")
            for j in range(60):
                tps_record.append(cur_tps + (i + 1) * int(up_per_min))

        self.script.write("# TPS = {}\n".format(str(int(new_tps))))
        self.script.write("Alter-BCThreadGroups -AgentName {} -Drivers {} -ThreadGroups {} -ThreadCount {}\n".format(self.agent_name, self.driver_name, self.thread_group_name, str(int(new_tps))))
        self.script.write("Start-Sleep -s 60\n")
        for j in range(60):
            tps_record.append(int(new_tps))
        return new_tps, time_min

    def build_down_slope(self, cur_tps, new_tps, tps_record):
        """ We use a finite number of squares to approximate a slope.
            A square takes a certain amount of time to form the shape. 
            We set this time to 1 minute for now. """
        time_min = random.randint(1, 10)
        self.script.write("# Down Slope = {}\n".format(str(time_min)))
        down_per_min = (cur_tps - new_tps) / time_min
        if down_per_min <= 1:
            self.script.write("# TPS = {}\n".format(str(new_tps)))
            self.script.write("Alter-BCThreadGroups -AgentName {} -Drivers {} -ThreadGroups {} -ThreadCount {}\n".format(self.agent_name, self.driver_name, self.thread_group_name, str(int((cur_tps + new_tps) / 2)))) 
            for j in range(60):
                tps_record.append(new_tps)
        else:
            for i in range(time_min - 1):
                self.script.write("# TPS = {}\n".format(str(int(cur_tps - down_per_min))))
                self.script.write("Alter-BCThreadGroups -AgentName {} -Drivers {} -ThreadGroups {} -ThreadCount {}\n".format(self.agent_name, self.driver_name, self.thread_group_name, str(int(cur_tps - down_per_min / 2))))
                cur_tps = cur_tps - down_per_min
                self.script.write("Start-Sleep -s 60\n")
                for j in range(60):
                    tps_record.append(int(cur_tps - down_per_min))
            self.script.write("# TPS = {}\n".format(str(new_tps)))
            self.script.write("Alter-BCThreadGroups -AgentName {} -Drivers {} -ThreadGroups {} -ThreadCount {}\n".format(self.agent_name, self.driver_name, self.thread_group_name, str(int((cur_tps + new_tps) / 2))))
            self.script.write("Start-Sleep -s 60\n")
            for j in range(60):
                tps_record.append(new_tps)
        return new_tps, time_min

    def build_flat_curve(self, cur_tps, tps_record):
        random.seed()
        time_min = random.randint(2, 20)

        for i in range(time_min * 60):
            tps_record.append(cur_tps)

        self.script.write("# Hold for {}\n".format(time_min))
        self.script.write("Start-Sleep -s {}\n".format(str(time_min * 60)))
        return time_min

    def build_initialization(self, bp_path):
        self.script.write("New-BCAPIAgent -AgentName {}\n".format(self.agent_name))
        self.script.write("Open-BCProfile -AgentName {} -Profile {}\n".format(self.agent_name, bp_path))
        self.script.write("Launch-BCDrivers -AgentName {} -Drivers {}\n".format(self.agent_name, self.driver_name))
        self.script.write("Run-BCWorkers -AgentName {} -Drivers {}\n".format(self.agent_name, self.driver_name))
        return 1, 0

    def build_wait_time(self, alpha, cur_tps, tps_record):
        wait_time = np.random.exponential(alpha, 1)
        wait_time = min(20, 1 + int(wait_time))
        for i in range(wait_time * 60):
            tps_record.append(cur_tps)

        self.script.write("# Wait for {}\n".format(wait_time))
        self.script.write("Start-Sleep -s {}\n".format(str(wait_time * 60)))
        return wait_time

    def build_end(self):
        self.script.write("Stop-BCDrivers -AgentName {} -Drivers {}\n".format(self.agent_name, self.driver_name))

    def close(self):
        self.script.close()

    def generate_workload(self, burst_num, max_burst_height, min_burst_height):
        cur_tps, time_min = self.build_initialization(self.profile_path)
        # interesting_ticks contains the index(seconds since begining of workload) of the beginning and ending of all slopes in the generated workload.
        interesting_ticks = []
        tps_record = []

        new_time_min = self.build_wait_time(2, cur_tps, tps_record)
        interesting_ticks.append(60 * new_time_min)
        time_min = time_min + new_time_min
        for i in range(burst_num):
            # Build a up slope
            cur_tps, new_time_min = self.build_up_slope(cur_tps, max_burst_height, tps_record)
            time_min = time_min + new_time_min
            interesting_ticks.append(60 * time_min)

            # Build a flat curve
            new_time_min = self.build_flat_curve(cur_tps, tps_record)
            time_min = time_min + new_time_min
            interesting_ticks.append(60 * time_min)

            # Build a down slope
            cur_tps, new_time_min = self.build_down_slope(cur_tps, min_burst_height, tps_record)
            time_min = time_min + new_time_min
            interesting_ticks.append(60 * time_min)

            if i < burst_num - 1:
                # Build a gap
                new_time_min = self.build_wait_time(2, cur_tps, tps_record)
                time_min = time_min + new_time_min
                interesting_ticks.append(60 * time_min)

        self.build_end()
        self.close()

        return time_min, interesting_ticks, tps_record