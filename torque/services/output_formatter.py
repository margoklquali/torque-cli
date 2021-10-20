import json
import sys
from typing import Any

import tabulate
from colorama import Style

from torque.parsers.global_input_parser import GlobalInputParser


class OutputFormatter:
    def __init__(self, global_input_parser: GlobalInputParser):
        if global_input_parser.output_json:
            self.format_str = self.format_json_str
            self.format_list = self.format_json_list
            self.format_object = self.format_json_object
            self.styled_text = lambda style, message, newline: None
        else:
            self.format_str = self.format_default_str
            self.format_list = self.format_table
            self.format_object = self.format_object_default
            self.styled_text = self.styled_text_default

    def styled_text_default(self, style, message, newline):
        if message:
            sys.stdout.write(style + message)
            sys.stdout.write(Style.RESET_ALL)
        if newline:
            sys.stdout.write("\n")

    def yield_output(self, success: bool, output: Any):
        if not output:
            return

        output_str = self.format_output(output)

        if success:
            sys.stdout.write(output_str)
            sys.stdout.write("\n")
        else:
            sys.stderr.write(output_str)
            sys.stderr.write("\n")

    def format_output(self, output: Any) -> str:
        if isinstance(output, str):
            return self.format_str(output)
        elif isinstance(output, list):
            return self.format_list(output)
        else:
            return self.format_object(output)

    def format_default_str(self, output):
        return output

    def format_json_str(self, output):
        return json.dumps(output, indent=True)

    def format_json_list(self, output: list) -> str:
        return json.dumps(output, default=lambda x: x.json_serialize(), indent=True)

    def format_json_object(self, output: Any) -> str:
        return json.dumps(output, default=lambda x: x.json_serialize(), indent=True)

    def format_table(self, output: list) -> str:
        result_table = []
        for line in output:
            result_table.append(line.table_serialize() if callable(getattr(line, "json_serialize", None)) else line)

        return tabulate.tabulate(result_table, headers="keys")

    def format_object_default(self, output: Any) -> str:
        result_table = []
        for (k, v) in output.table_serialize().items():
            result_table.append([k, v])

        return tabulate.tabulate(result_table)
