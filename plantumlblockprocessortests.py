import unittest
import plantumlblockprocessor
import markdown.util


class MockedMarkdownParser:
    class MockedMd:
        tab_length = 4

    md = MockedMd()


class MockedProcessHandler:
    def process_png(self, input):
        # self.assertIsNotNone(input)
        # self.assertNotEqual(input, "")
        return input


class PlantUmlBlockProcessorTests(unittest.TestCase):
    def test_processor_test_function(self):
        block_processor = plantumlblockprocessor.PlanUmlBlockProcessor(MockedMarkdownParser(),
                                                                       MockedProcessHandler())
        self.assertFalse(block_processor.test(None, ""))
        self.assertFalse(block_processor.test(None, None))
        self.assertTrue(block_processor.test(None, "```plantuml\n```"))
        self.assertTrue(block_processor.test(None, "   ```plantuml\n```"))
        self.assertTrue(block_processor.test(None, "    ```plantuml\n```"))

    def test_processor_run_function(self):
        block_processor = plantumlblockprocessor.PlanUmlBlockProcessor(MockedMarkdownParser(),
                                                                       MockedProcessHandler())
        # block_processor.run()


if __name__ == '__main__':
    unittest.main()
