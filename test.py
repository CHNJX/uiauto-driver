from ui_driver.udf import setup_run


def test_setup_testcase():
    res = setup_run('testcase/dd.yml')
    print(res)

test_setup_testcase()