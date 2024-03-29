import gzip
import base64
import os
from pathlib import Path
from typing import Dict


# this is base64 encoded source code
file_data: Dict = {file_data}

size = 64
iterations = 24000
batch_size = 128
ch_gen, ch_dis = 64, 64

yaml = """# conditional CIFAR10 generation with SN and projection discriminator
batchsize: {3}
iteration: {0}
iteration_decay_start: 18000
seed: 42
display_interval: {1}
progressbar_interval: {1}
snapshot_interval: {0}
evaluation_interval: {0}

models:
    generator:
        fn: resnet_{2}.py
        name: ResNetGenerator
        args:
            dim_z: 128
            bottom_width: 4
            ch: {4}
            n_classes: 120
            use_sn: True


    discriminator:
        fn: snresnet_{2}.py
        name: SNResNetProjectionDiscriminator
        args:
            ch: {5}
            n_classes: 120

dataset:
    dataset_fn: dog.py
    dataset_name: DogDataset
    args:
        crop: True
        size: {2}
        use_cache: False

adam_gen:
    alpha: 0.0002
    beta1: 0.0
    beta2: 0.9

adam_dis:
    alpha: 0.0005
    beta1: 0.0
    beta2: 0.9

updater:
    fn: updater.py
    name: Updater
    args:
        n_dis: 2
        n_gen_samples: 128
        conditional: True
        loss_type: hinge
""".format(iterations, iterations // 5, size, batch_size, ch_gen, ch_dis)

with open('/kaggle/working/config.yml', 'w') as f:
    f.write(yaml)


for path, encoded in file_data.items():
    print(path)
    path = Path(path)
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(gzip.decompress(base64.b64decode(encoded)))


def run(command):
    os.system('export PYTHONPATH=${PYTHONPATH}:/kaggle/working && ' + command)


run('python setup.py develop --install-dir /kaggle/working')
run('python easy_gold/train.py --config=/kaggle/working/config.yml --results_dir=/kaggle/working/logs/')
model_path = '/kaggle/working/logs/ResNetGenerator_{}.npz'.format(iterations)
run('python easy_gold/gen_images.py --config=/kaggle/working/config.yml --snapshot={} --conditional'.format(model_path))
