import os

import pytest

from uidriver.ui_driver.testcase_generate import TestcaseGenerate

steps = {}


class TestCase:
    tg = TestcaseGenerate()
    tg.load_case(os.path.dirname(__file__)+'/'+str(__name__).split('.')[-1] + '.yaml')

    @pytest.mark.parametrize(
        'testcase',
        tg.testcase.steps_list,
        ids=tg.testcase.ids
    )
    def test_param(self, testcase):
        self.tg.run_case(testcase)