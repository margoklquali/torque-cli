from collections import OrderedDict

import tabulate

from torque.constants import TorqueConfigKeys
from torque.view.view_helper import mask_token


class ConfigureListView:
    def __init__(self, config: dict):
        self.config = config

    def render(self):
        if not self.config:
            return "Config file is empty. Use 'torque configure set' to configure Torque CLI."

        result_table = []
        for profile in self.config.keys():
            item = OrderedDict()
            item["Profile Name"] = profile
            item["Torque Account"] = self.config[profile].get(TorqueConfigKeys.ACCOUNT, None)
            item["Space Name"] = self.config[profile].get(TorqueConfigKeys.SPACE, None)
            item["Token"] = mask_token(self.config[profile].get(TorqueConfigKeys.TOKEN, None))
            result_table.append(item)

        return tabulate.tabulate(result_table, headers="keys")
