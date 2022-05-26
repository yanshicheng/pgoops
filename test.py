# pip install ansible-runner
# https://ansible-runner.readthedocs.io/en/stable/
import ansible_runner
import os

base_dir = os.path.join(os.getcwd(), "upload", "iac", "helloworld")

ansible_runner.run(private_data_dir=base_dir, playbook="deploy.yaml")
