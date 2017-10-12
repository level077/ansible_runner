#!/usr/bin/python

#from options import ansible_options

import os
import json
from ansible.inventory import Inventory
from ansible.vars import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.executor import playbook_executor
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase


def ansible_options(options):
        _ansible_option = {}
        if os.path.isfile(str(options)):
            with open(options, "r") as f:
                _ansible_option = json.load(f)
        elif isinstance(options, dict):
             _ansible_option = options
	return _ansible_option

class Options():
    def __init__(self,options=None,verbosity=None,inventory=None,listhosts=None,subset=None,module_paths=None,extra_vars=None,forks=10,ask_vault_pass=None,vault_password_files=None,new_vault_password_files=None,output_file=None,tags='',skip_tags='',one_line=None,tree=None,ask_sudo_pass=None,ask_su_pass=None,sudo=None,sudo_user=None,become=None,become_method=None,become_user=None,become_ask_pass=None,ask_pass=None,private_key_file=None,remote_user=None,connection='smart',timeout=None,ssh_common_args=None,sftp_extra_args=None,scp_extra_args=None,ssh_extra_args=None,poll_interval=None,seconds=None,check=None,syntax=None,diff=None,force_handlers=None,flush_cache=None,listtasks=None,listtags=None,module_path=None,conn_pass=None,become_pass=None):
        self.verbosity = verbosity
        self.inventory = inventory
	self.listhosts = listhosts
	self.subset = subset
	self.module_paths = module_paths
	self.extra_vars = extra_vars
	self.forks = forks
	self.ask_vault_pass = ask_vault_pass
	self.vault_password_files = vault_password_files
	self.new_vault_password_files = new_vault_password_files
	self.output_file = output_file
	self.tags = tags
	self.skip_tags = skip_tags
	self.one_line = one_line
	self.tree = tree
	self.ask_sudo_pass = ask_sudo_pass
	self.ask_su_pass = ask_su_pass
	self.sudo = sudo
	self.become = become
	self.become_method = become_method
	self.become_user = become_user
	self.become_ask_pass = become_ask_pass
	self.ask_pass = ask_pass
	self.private_key_file = private_key_file
	self.remote_user = remote_user
	self.connection = connection
	self.timeout = timeout
	self.ssh_common_args = ssh_common_args
	self.sftp_extra_args = sftp_extra_args
	self.scp_extra_args = scp_extra_args
	self.ssh_extra_args = ssh_extra_args
	self.poll_interval = poll_interval
	self.seconds = seconds
	self.check = check
	self.syntax = syntax 
	self.diff = diff
	self.force_handlers = force_handlers
	self.flush_cache = flush_cache
	self.listtasks = listtasks
	self.listtags = listtags
	self.module_path = module_path
	self.conn_pass = conn_pass
	self.become_pass = become_pass
	options = ansible_options(options)
	_options = [x for x in dir(self) if not x.startswith('__')]
	for k,v in options.items():
	    if k in _options:
	        setattr(self,k,v)

class ResultCallback(CallbackBase):
    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host
        json_result = json.dumps({host.name: result.task_name}, indent=4)
        print(json_result)

    def v2_runner_on_failed(self, result, ignore_errors=False):
	host = result._host
	json_result = json.dumps({host.name: result._result}, indent=4)
	print(json_result)

class CustomPlaybookExecutor(playbook_executor.PlaybookExecutor):
    def __init__(self,playbooks,inventory,variable_manager,loader,options,passwords,stdout_callback):
        super(CustomPlaybookExecutor,self).__init__(playbooks,inventory,variable_manager,loader,options,passwords)
	self._stdout_callback = stdout_callback
	if options.listhosts or options.listtasks or options.listtags or options.syntax:
            self._tqm = None
        else:
            self._tqm = TaskQueueManager(inventory=inventory, variable_manager=variable_manager, loader=loader, options=options, passwords=passwords,stdout_callback=self._stdout_callback)

class Runner():
    def __init__(self,options=None,host_list=[],playbook=[],run_data={},verbosity=0):
        self.run_data = run_data
        self.options = Options(options=options,verbosity=verbosity)
	passwords = {'conn_pass':self.options.conn_pass,'become_pass':self.options.become_pass}
	self.loader = DataLoader()
	self.variable_manager = VariableManager()
	self.variable_manager.extra_vars = self.run_data
	self.inventory = Inventory(loader=self.loader,variable_manager=self.variable_manager,host_list=host_list)
	self.result_callback = None #ResultCallback()
	#self.variable_manager.set_inventory(self.inventory)
	self.pbex = CustomPlaybookExecutor(
	    playbooks = playbook,
	    inventory = self.inventory,
	    variable_manager = self.variable_manager,
	    loader = self.loader,
	    options = self.options,
	    passwords = passwords,
	    stdout_callback = self.result_callback) 

    def run(self):
        self.pbex.run()

if __name__ == "__main__":
    runner = Runner(
	options = 'conf.json',
	host_list = ['127.0.0.1'],
        playbook = ['/etc/ansible/playbooks/test.yml'],
        run_data = {'port':2379,'install_path':'/tmp','db_path':'/tmp','maxmemory':'3G'}	
    )
    runner.run()
