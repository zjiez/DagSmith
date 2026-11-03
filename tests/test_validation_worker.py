import io
import json
import sys
import types
import unittest
from unittest.mock import patch

from dagsmith.core.validation_worker import main


class ValidationWorkerTests(unittest.TestCase):
    def check_worker(self, bag_class):
        module = types.ModuleType('airflow.dag_processing.dagbag')
        module.DagBag = bag_class
        output = io.StringIO()
        with patch.dict(sys.modules, {'airflow.dag_processing.dagbag': module}):
            with patch('sys.stdin', io.StringIO('# candidate')), patch('sys.stdout', output):
                self.assertEqual(main(), 0)
        self.assertEqual(json.loads(output.getvalue()), {'errors': [], 'dag_count': 1})

    def test_airflow_33_constructor(self):
        class DagBag:
            def __init__(self, dag_folder=None, safe_mode=True):
                assert safe_mode is False
                self.dags = {'test': object()}
                self.import_errors = {}
        self.check_worker(DagBag)

    def test_older_constructor_disables_examples(self):
        class DagBag:
            def __init__(self, dag_folder=None, include_examples=True, safe_mode=True):
                assert include_examples is False
                assert safe_mode is False
                self.dags = {'test': object()}
                self.import_errors = {}
        self.check_worker(DagBag)
