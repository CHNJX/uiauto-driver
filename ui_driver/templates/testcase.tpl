import os

import pytest

from ui_driver.generate_testcase import GenerateTestcase

steps = {}


class TestCase:
    tg = GenerateTestcase()
    tg.load_case(os.path.dirname(__file__)+'/'+str(__name__).split('.')[-1] + '.yaml')

    @pytest.mark.parametrize(
        'testcase',
        tg.testcase.steps_list,
        ids=tg.testcase.ids
    )
    def test_param(self, testcase):
        self.tg.run_case(testcase)