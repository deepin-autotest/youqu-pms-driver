import json
import os

import requests

MAX_CASE_NUMBER = 100000


class Task:
    """获取测试套件关联的用例"""

    __author__ = "huangmingqiang@uniontech.com"

    def __init__(self, username, password):
        self.base_url = "https://pms.uniontech.com"
        loginurl = f'{self.base_url}/zentao/user-login.json'
        datauser = {"account": username, "password": password}
        self.session = requests.Session()
        self.session.post(loginurl, data=datauser)

    def get_task_data(self, task_id):
        task_json_url = f"https://pms.uniontech.com/testtask-cases-{task_id}-all-0-id_desc-4-{MAX_CASE_NUMBER}-1.json"
        try:
            res = self.session.get(task_json_url).json()
            data = json.loads(res.get("data"))
            runs = data.get("runs")
        except json.decoder.JSONDecodeError:
            raise EnvironmentError(
                f"{task_json_url} 未获取到有效数据！\n 请检查你的PMS账号密码是否正确。"
            )
        runs_ids = []
        run_case_id_map = {}
        for run_case_id in runs:
            # 产品库ID
            case_id = runs.get(run_case_id).get("case")
            runs_ids.append(case_id)
            run_case_id_map[case_id] = run_case_id
            # 用例库ID
            from_case_id = runs.get(run_case_id).get("fromCaseID")
            if from_case_id:
                runs_ids.append(from_case_id)
                run_case_id_map[from_case_id] = run_case_id
        return runs_ids, run_case_id_map

    def write_case_data(self, task_id):
        ids, run_case_id_map = self.get_task_data(task_id)
        with open(f'youqu-tags.txt', "w", encoding="utf-8") as f:
            f.write(" or ".join(ids))
        run_case_ids_dir = f"./report/pms_{task_id}"
        if not os.path.exists(run_case_ids_dir):
            os.makedirs(run_case_ids_dir)
        with open(os.path.join(run_case_ids_dir, "run_case_id_map.json"), "w", encoding="utf-8") as f:
            f.write(json.dumps(run_case_id_map, indent=2, ensure_ascii=False))
