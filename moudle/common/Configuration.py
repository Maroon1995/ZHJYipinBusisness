import yaml


def readConfig(
        yaml_file: str = "F:\\Accumulation\\BaiduNetdiskWorkspace\\Project\\pythonworkspace\\OnlyMaterialZHJSys\\resource\\configuration.yaml"):
    """
    读取yaml配置文件
    :param yaml_file: yaml文件路径
    :return:
    """
    with open(yaml_file, 'r', encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    return cfg
