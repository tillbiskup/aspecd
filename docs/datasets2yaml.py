import aspecd.utils


class_names = ['Dataset', 'ExperimentalDataset', 'CalculatedDataset']

for class_name in class_names:
    yaml = aspecd.utils.Yaml()
    ds = aspecd.utils.object_from_class_name(".".join(['aspecd.dataset',
                                                       class_name]))
    yaml.dict = ds.to_dict()
    yaml.serialise_numpy_arrays()
    yaml.write_to(".".join([class_name, 'yaml']))
