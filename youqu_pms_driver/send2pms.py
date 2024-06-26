import json
import os
import pathlib
import re

import requests

SEND_PMS_RETRY_NUMBER = 2

runs_id_cmd_log = lambda x: re.sub(r"'run_case_id': '\d+', ", "", str(x))


class Send2Pms:
    """发送数据到pms"""

    __author__ = "huangmingqiang@uniontech.com"

    def __init__(self, username, password, task_id=None, suite_id=None):
        self.task_id = task_id
        self.suite_id = suite_id
        self.base_url = "https://pms.uniontech.com"
        loginurl = f'{self.base_url}/zentao/user-login.json'
        datauser = {"account": username, "password": password}
        self.session = requests.Session()
        self.session.post(loginurl, data=datauser)
        self.rootdir = pathlib.Path(".").absolute()
        self.reportdir = self.rootdir / "report"

    def get_run_case_id_map(self):
        with open(self.reportdir / f"pms_{self.task_id}" / "run_case_id_map.json") as f:
            run_case_id_map = json.load(f)
        return run_case_id_map

    def get_task_step_id(self, run_case_id):
        base_url = "https://pms.uniontech.com/testtask-runCase"
        self.run_case_html_url = f"{base_url}-{run_case_id}.html"
        res = self.session.get(self.run_case_html_url).text
        steps_id = re.findall(r"name='steps\[(\d+)\]'", res)
        if steps_id and steps_id[0]:
            return steps_id[0]
        return 201

    def get_suite_step_id(self, run_case_id):
        base_url = "https://pms.uniontech.com/testtask-runCase"
        self.run_case_html_url = f"{base_url}-0-{run_case_id}-1.html"
        res = self.session.get(self.run_case_html_url).json()
        steps_id = re.findall(r"name='steps\[(\d+)\]'", res)
        if steps_id and steps_id[0]:
            return steps_id[0]
        return 201

    def get_json_report(self):
        for filename in os.listdir(self.reportdir / "json"):
            json_file = self.reportdir / "json" / filename
            return json_file

    def send(self):
        json_file = self.get_json_report()
        run_case_id_map = self.get_run_case_id_map()
        with open(json_file, "r", encoding="utf") as f:
            json_data = json.load(f)
        cases_res = json_data.get("tests")
        for case in cases_res:
            case_id = re.findall(r"test_.*?_(\d+)", case.get("nodeid"))[0]
            run_case_id = run_case_id_map.get(case_id)
            if self.task_id:
                steps_id = self.get_task_step_id(run_case_id)
            elif self.suite_id:
                steps_id = self.get_suite_step_id(run_case_id)
            else:
                raise ValueError

            outcome = case.get("outcome")
            if outcome == "passed":
                result = "pass"
            elif outcome == "failed":
                result = "fail"
            else:
                continue
            data = {
                f"steps[{steps_id}]": result,
                f"reals[{steps_id}]": "",
                "case": case_id,
                "version": "1",
                f"labels{steps_id}[]": "",
                f"files{steps_id}[]": "",
            }
            res = self.session.post(url=self.run_case_html_url, data=data)
            print(self.run_case_html_url, res.status_code)

