import subprocess
import psutil
import time

log = open('eval-' + str(int(time.time())) + '.log', 'a')
log.write('Index, RAM(MB),CPU(%)\n')

process = subprocess.Popen('python mtd_strategy_selection_agent.py'.split(), cwd='..')

index = 0
tracker = psutil.Process(process.pid)
while True:
  mem = str(tracker.memory_info().rss / 1024 ** 2)
  cpu = str(tracker.cpu_percent(interval=10.0))
  print("Index   " + str(index))
  print("MEM [MB] " + mem)
  print("CPU [%] " + cpu)
  log.write(str(index) + "," + mem + "," + cpu + "\n")
  index += 1
  #time.sleep(9)



