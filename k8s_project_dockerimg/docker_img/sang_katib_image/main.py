import pandas as pd
import xgboost as xgb
import argparse
from sklearn.metrics import mean_absolute_error

X_train_sc_ec = pd.read_csv('/home/jovyan/csv/X_train_sc_ec.csv')
X_validation_sc_ec = pd.read_csv('/home/jovyan/csv/X_validation_sc_ec.csv')
Y_train = pd.read_csv('/home/jovyan/csv/Y_train.csv')
Y_validation = pd.read_csv('/home/jovyan/csv/Y_validation.csv')

parser = argparse.ArgumentParser()
parser.add_argument('--learning_rate', required=False, type=float, default=0.1)
parser.add_argument('--n_estimators', required=False, type=int, default=100)
parser.add_argument('--max_depth', required=False, type=int, default=5)

args = parser.parse_args()


xgb_model = xgb.XGBRegressor(random_state=10,
                            learning_rate=args.learning_rate,
                            n_estimators=args.n_estimators,
                            max_depth=args.max_depth
                            )

xgb_model.fit(X_train_sc_ec, Y_train)


# 검증 데이터 예측
pred_validation = xgb_model.predict(X_validation_sc_ec)

# 성능평가
from sklearn.metrics import mean_absolute_error
mae_validation = mean_absolute_error(Y_validation, pred_validation)
print("mae_validation="+str(mae_validation))
