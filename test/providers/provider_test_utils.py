from abc import ABCMeta
import unittest


class ProviderTestBase(unittest.TestCase, metaclass=ABCMeta):
    def assert_source_time_ranges(self, source_time_ranges, expected_start_date,
                                  expected_end_date, expected_paths, expected_index):
        self.assertEqual(expected_start_date, source_time_ranges[0])
        self.assertEqual(expected_end_date, source_time_ranges[1])
        for path in expected_paths:
            self.assertIn(path, source_time_ranges[2].replace('\\', '/'))
        self.assertEqual(expected_index, source_time_ranges[3])

    @staticmethod
    def get_source_dir_list(source_dir):
        return source_dir.replace('\\', '/').split('/')
