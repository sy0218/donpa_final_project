import kfp
import kfp.components as comp
from kfp import dsl

@dsl.pipeline(
    name='wwww',
    description='sang xgb test1'
)
def sang_xgb_pipline():
    model_pvc = dsl.PipelineVolume('model-pvc')
    encoder_pvc = dsl.PipelineVolume('encoder-pvc')
    scaler_pvc = dsl.PipelineVolume('scaler-pvc')
    csv_pvc = dsl.PipelineVolume('sang-csv-pvc')
    yaml_pvc = dsl.PipelineVolume('katib-yaml-pvc')

    data_load = dsl.ContainerOp(
        name='data load',
        image='kubeflow-registry.default.svc.cluster.local:30000/sang_data_load:latest',
        command=['python', 'main.py','1'],
        pvolumes={'/home/jovyan/csv': csv_pvc,
                  '/home/jovyan/encoder': encoder_pvc,
                  '/home/jovyan/scaler': scaler_pvc}
    )

    katib_run = dsl.ContainerOp(
        name='katib run',
        image='kubeflow-registry.default.svc.cluster.local:30000/sang_katib_start:latest',
        command=['python', 'sang_katib_start.py','1'],
        pvolumes={'/app/exp': yaml_pvc}
    )

    model_update = dsl.ContainerOp(
        name='model update',
        image='kubeflow-registry.default.svc.cluster.local:30000/sang_model_update:latest',
        command=['python', 'sang_model_update.py','1'],
        pvolumes={'/app/exp': yaml_pvc,
                  '/app/model': model_pvc,
                  '/app/csv': csv_pvc}
    )

    katib_run.after(data_load)
    model_update.after(katib_run)

if __name__ == "__main__":
    import kfp.compiler as compiler
    compiler.Compiler().compile(sang_xgb_pipline, __file__ + ".tar.gz")

