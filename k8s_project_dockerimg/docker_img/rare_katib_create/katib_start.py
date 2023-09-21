from kubeflow.katib import KatibClient
import yaml
import argparse

test_yaml = '/app/exp/rare.yaml'

katib_client = KatibClient()

with open(test_yaml, "r") as yaml_file:
    experiment_config = yaml.load(yaml_file)

namespace = experiment_config['metadata']['namespace']

try:
    katib_client.create_experiment(experiment_config, namespace)
except:
    pass
