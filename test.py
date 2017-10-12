#!/usr/bin/python

from ansible_runner.runner import Runner

runner = Runner(
	options = 'conf.json',
	host_list = ['127.0.0.1'],
	playbook = ['/etc/ansible/playbooks/test.yml'])
runner.run()
