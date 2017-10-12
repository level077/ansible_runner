#!/usr/bin/python

import json
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase

class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in
    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """
    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result
        This method could store the result in an instance attribute for retrieval later
        """
        host = result._host
        print json.dumps({host.name: result._result}, indent=4)

    def v2_runner_on_failed(self, result,**kwargs):
	host = result._host
        print json.dumps({host.name: result._result}, indent=4)

Options = namedtuple('Options',['connection','module_path','forks','become','become_method','become_user','check','verbosity'])
options = Options(connection='smart',module_path='',forks=5,become=None,become_method=None,become_user=None,check=False,verbosity=True)

variable_manager = VariableManager()
loader = DataLoader()

results_callback = ResultCallback()

passwords = dict(conn_pass='xxxxxxx')
inventory = Inventory(loader=loader,variable_manager=variable_manager,host_list=["127.0.0.1"])
variable_manager.set_inventory(inventory)

play_src = dict(
	name = 'ansible api test',
	hosts = 'all',
	gather_facts = 'no',
	tasks = [
		dict(action=dict(module='shell',args='ifconfig eth5'),register='shell_out')
	]
)

play = Play().load(play_src,variable_manager=variable_manager,loader=loader)

tmq = None
try:
  tmq = TaskQueueManager(
		inventory = inventory,
		variable_manager = variable_manager,
		loader = loader,
		options = options,
		passwords = passwords,
		#stdout_callback=results_callback
		stdout_callback=None
	)
  result = tmq.run(play)
  #print result
finally:
  if tmq is not None:
    tmq.cleanup()
