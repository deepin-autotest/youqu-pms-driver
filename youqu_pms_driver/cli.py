import click


@click.option("--pms-user", default=None, type=click.STRING, help="")
@click.option("--pms-password", default=None, type=click.STRING, help="")
@click.option("--task-id", default=None, type=click.STRING, help="")
@click.option("--suite-id", default=None, type=click.STRING, help="")
@click.option("--send2pms", default=None, type=click.STRING, help="")
def cli(
        pms_user,
        pms_password,
        task_id,
        suite_id,
        send2pms,
):
    if task_id:
        from youqu_pms_driver.task import Task
        Task(pms_user, pms_password).write_case_data(task_id)
    elif send2pms:
        from youqu_pms_driver.suite import Suite
        Suite(pms_user, pms_password).write_case_data(task_id)
    if send2pms:
        from youqu_pms_driver.send2pms import Send2Pms
        Send2Pms(pms_user, pms_password, task_id, suite_id).send()


if __name__ == "__main__":
    cli()
