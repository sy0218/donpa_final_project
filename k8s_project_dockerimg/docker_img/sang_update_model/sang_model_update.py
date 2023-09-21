from kubeflow.katib import KatibClient
from sklearn.metrics import mean_absolute_error
import yaml
import pandas as pd
import time
import argparse
import joblib
import xgboost as xgb


time.sleep(580)
while True:
    test_yaml = '/app/exp/sang.yaml'

    with open(test_yaml, "r") as yaml_file:
        experiment_config = yaml.load(yaml_file)

    name = experiment_config['metadata']['name']
    namespace = experiment_config['metadata']['namespace']


    katib_client = KatibClient()

    time.sleep(10)
    if katib_client.get_experiment_status(name,namespace) == 'Succeeded':

        experiment = katib_client.get_experiment(name=name,namespace=namespace)

        lr=experiment['status']['currentOptimalTrial']['parameterAssignments'][0]['value']
        n=experiment['status']['currentOptimalTrial']['parameterAssignments'][1]['value']
        d=experiment['status']['currentOptimalTrial']['parameterAssignments'][2]['value']

        katib_client.delete_experiment(name,namespace)

        new_model = xgb.XGBRegressor(random_state=10,
                                     learning_rate=float(lr),
                                     n_estimators=int(n),
                                     max_depth=int(d)
                                     )
        X_train_sc_ec = pd.read_csv('/app/csv/X_train_sc_ec.csv')
        X_validation_sc_ec = pd.read_csv('/app/csv/X_validation_sc_ec.csv')
        Y_train = pd.read_csv('/app/csv/Y_train.csv')
        Y_validation = pd.read_csv('/app/csv/Y_validation.csv')


        # 새로운 모델 성능 평가
        new_model.fit(X_train_sc_ec, Y_train)
        new_pred_validation = new_model.predict(X_validation_sc_ec)
        new_mae_validation = mean_absolute_error(Y_validation, new_pred_validation)

        # 모델을 파일로 저장
        joblib.dump(new_model, '/app/model/sang_model.pkl')
        
        break
