import unittest

from main import build_all_checks_command


class JobCommandsTests(unittest.TestCase):
    def test_all_checks_command_runs_validation_then_unit_tests(self) -> None:
        command = build_all_checks_command()

        self.assertTrue(command[0].endswith('python') or 'python' in command[0].lower())
        self.assertIn('daily_jobs.validate_pipeline', command[2])
        self.assertIn('unittest', command[2])


if __name__ == '__main__':
    unittest.main()
