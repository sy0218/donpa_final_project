import kfp
import kfp.components as comp
from kfp import dsl


@dsl.pipeline(
    name='rare1-xgb',
    description='rare xgb test'
)

def rare_xgb_pipline():
    model_pvc = dsl.PipelineVolume('model-pvc')
    csv_pvc = dsl.PipelineVolume('csv-pvc')
    yaml_pvc = dsl.PipelineVolume('katib-yaml-pvc')


    data_load = dsl.ContainerOp(
        name='katib run',
        image='kubeflow-registry.default.svc.cluster.local:30000/katib_start:latest',
        command=['python','katib_start.py','1'],
        pvolumes={'/app/exp': yaml_pvc}
    )

    model_update = dsl.ContainerOp(
        name='model update',
        image='kubeflow-registry.default.svc.cluster.local:30000/model_update:latest',
        command=['python', 'model_update.py','1'],
        pvolumes={'/app/exp': yaml_pvc,
                  '/app/model': model_pvc,
                  '/app/csv': csv_pvc}
    )

    model_update.after(data_load)

if __name__ == "__main__":
    import kfp.compiler as compiler
    compiler.Compiler().compile(rare_xgb_pipline, __file__ + ".tar.gz")
