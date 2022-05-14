#!/usr/bin/python3
from sys import argv
from dataclasses import dataclass

#argv = ['./Scheduler_project.py', 'RR', '20', 'input.txt']

#
# Defining DataClasses to have custom variables
#

# Data related to each Process in the RoundRobin algorithm
@dataclass
class RProc:
	Letter: str
	ArrivalTime: int
	BurstTime: int

# Data related to each Process in the priority scheduler algorithm
@dataclass
class PProc:
	Letter: str
	Priority: int
	BurstTime: int

# Object containing data about the TimeLine
@dataclass
class TimelineObject:
	Letter: str
	StartTime: int
	EndTime: int

# Data related to the Process timings
@dataclass
class PData:
	Arrivalt: int  # Arrival Time
	Responset: int # Response Time
	Turnt: int     # Turnaround Time

# Data that will be returned from RR and PR functions
@dataclass
class Result:
	ATt: float
	ARt: float
	CPUt: list

#
# Round Robin algorithm
#

def RR(quantum: int, file: str) -> Result:
	# Read the input file
	with open(file, "r") as tasks:
		arrival = 0
		procs = [] # ready queue (list of processes)
		letter = 65 # ASCII value of A is 65
		Task_Data = {} # dictionary of Process timings
		for task in tasks:
			task = task.strip().split(" ")
			if task[0] == "proc":
				# add process (Letter, ArrivalTime, BurstTime) to the ready queue
				procs.append(RProc(chr(letter),arrival,int(task[2])))
				# Save the timings for the process (only Arrival Time, others are -1 = unknown)
				Task_Data[chr(letter)] = PData(arrival,-1,-1)
				letter += 1
			elif task[0] == "idle":
				# add the idle value to the arrival time
				arrival += int(task[1])
			elif task[0] == "Done":
				break
			else:
				raise Exception("Invalid operation :" + str(task[0]))
	CurrentTime = 0
	index = 0 # index of the process for RoundRobin
	TimeLine = []
	exec_this_run = True # variable to track if a process has been executed this cycle/run
	while True:
		# if no processes are left in ready queue : break the loop
		if len(procs) == 0:
			break
		
		# if the index is out of range, change it back to 0(start)
		if index > len(procs)-1:
			# if no processes can be executed, increase CurrentTime
			if exec_this_run == False:
				CurrentTime += 1
			exec_this_run = False
			index = 0

		# if process should not be executed, go to the next one
		if procs[index].ArrivalTime > CurrentTime:
			index += 1
			continue
		
		#
		# Process execution logic
		#

		if procs[index].BurstTime <= quantum:
			# if BurstTime is smaller or equal, process is completed and removed
			exec_this_run = True
			# if it's the first execution, save the ResponseTime to Task_Data
			if Task_Data[procs[index].Letter].Responset == -1:
				Task_Data[procs[index].Letter].Responset = CurrentTime - procs[index].ArrivalTime
			# save execution to the TimeLine
			TimeLine.append(TimelineObject(procs[index].Letter, CurrentTime, CurrentTime + procs[index].BurstTime))
			
			CurrentTime += procs[index].BurstTime
			# save Turnaround time to Task_Data
			Task_Data[procs[index].Letter].Turnt = CurrentTime - procs[index].ArrivalTime
			# remove process from the ready queue
			del procs[index]
		else:
			# if the Burst time is bigger, remove quantum from it
			exec_this_run = True
			# if it's the first execution, save the ResponseTime to Task_Data
			if Task_Data[procs[index].Letter].Responset == -1:
				Task_Data[procs[index].Letter].Responset = CurrentTime - procs[index].ArrivalTime
			# save execution to the TimeLine
			TimeLine.append(TimelineObject(procs[index].Letter, CurrentTime, CurrentTime + quantum))
			
			procs[index].BurstTime -= quantum
			CurrentTime += quantum
			index += 1
	
	tot_tt = 0 # total TurnAround time
	tot_rt = 0 # total Response time
	for data in Task_Data:
		tot_tt += Task_Data[data].Turnt
		tot_rt += Task_Data[data].Responset
	
	return Result(tot_tt/len(Task_Data),tot_rt/len(Task_Data),TimeLine)

#
# Priority Scheduling algorithm
#

def PR(file: str) -> Result:
	# Read the input file
	with open(file, "r") as tasks:
		procs = [] # ready queue (list of processes)
		letter = 65 # ASCII value of A is 65
		TimeLine = []
		time = 0 # current execution time
		tot_idle = 0 # total idle time
		Task_Data = {} # dictionary of Process timings
		
		#
		# Priority scheduling simulation
		#
		
		for task in tasks:
			task = task.strip().split(" ")
			if task[0] == "proc":
				# add process (Letter, Priority, BurstTime) to the ready queue
				procs.append(PProc(chr(letter), int(task[1]), int(task[2])))
				# Save the timings for the process (only Arrival Time, others are -1 = unknown)
				Task_Data[chr(letter)] = PData(tot_idle, -1, -1)
				letter += 1
			elif task[0] == "idle":
				idle = int(task[1])
				tot_idle += idle
				# execute processes until idle is done
				while idle > 0:
					# if there is no process left, leave the loop
					if len(procs) == 0:
						break
					priorities = [] # list of all priorities in same order
					for proc in procs:
						priorities.append(proc.Priority)
					
					# get process with the highest priority (lowest value)
					high_prio = procs[priorities.index(min(priorities))]
					high_prio: PProc # Editor only, type suggestion
					
					# save execution to the TimeLine
					TimeLine.append(TimelineObject(high_prio.Letter,time, time + high_prio.BurstTime))
					# save Response time to Task_Data
					Task_Data[high_prio.Letter].Responset = time - Task_Data[high_prio.Letter].Arrivalt
					time += high_prio.BurstTime
					# save TurnAround time to Task_Data
					Task_Data[high_prio.Letter].Turnt = time - Task_Data[high_prio.Letter].Arrivalt
					idle -= high_prio.BurstTime # remove execution time from idle
					# remove process from ready queue
					del procs[priorities.index(min(priorities))]
			elif task[0] == "Done":
				# same routine as "idle" but does't stop until ready queue is empty
				while len(procs) != 0:
					priorities = []
					for proc in procs:
						priorities.append(proc.Priority)
					high_prio = procs[priorities.index(min(priorities))]
					high_prio: PProc
					TimeLine.append(TimelineObject(high_prio.Letter,time, time + high_prio.BurstTime))
					Task_Data[high_prio.Letter].Responset = time - Task_Data[high_prio.Letter].Arrivalt
					time += high_prio.BurstTime
					Task_Data[high_prio.Letter].Turnt = time - Task_Data[high_prio.Letter].Arrivalt
					del procs[priorities.index(min(priorities))]
			else:
				raise Exception("Invalid operation :" + str(task[0]))
	tot_tt = 0 # total TurnAround time
	tot_rt = 0 # total Response time
	for data in Task_Data:
		tot_tt += Task_Data[data].Turnt
		tot_rt += Task_Data[data].Responset
	return Result(tot_tt/len(Task_Data),tot_rt/len(Task_Data),TimeLine)

# 
# Printing inputs and results
# 

if not len(argv) == 4:
	raise Exception("Incorrect amount of arguments!")

print("Input File Name               :", argv[3])
if argv[1] == "RR":
	print("CPU Scheduling Alg            :", argv[1] + " (" + argv[2] + ")")
	result = RR(int(argv[2]),argv[3])
elif argv[1] == "PR":
	print("CPU Scheduling Alg            :", argv[1])
	result = PR(argv[3])
else:
	raise Exception(argv[1] + "is not a valid algorithm!")
result: Result
print("Avg. Turnaround time          :", result.ATt, "ms")
print("Avg. Response time in R queue :", result.ARt, "ms")
print("CPU timeline: ", end="")
for burst in result.CPUt:
	print(burst.Letter, "(", burst.StartTime, "→", burst.EndTime, "), ", sep="", end="")
print()
