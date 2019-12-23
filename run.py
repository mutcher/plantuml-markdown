import logging
import sys
from typing import List, ByteString
import markdown
import plantumlblockprocessor

logger = logging.getLogger("run")


class CommandLineOptions:
    @staticmethod
    def parse_arguments(arguments: List[str]):
        cmd_line_options = {}
        arguments.pop(0)
        while arguments:
            if arguments[0].startswith("-") or arguments[0].startswith("--"):
                argument = arguments.pop(0).lstrip('-')
                if argument == 'input':
                    cmd_line_options['input'] = arguments.pop(0)
                elif argument == 'output':
                    cmd_line_options['output'] = arguments.pop(0)
                elif argument == 'plantuml-jar-path':
                    cmd_line_options["plantuml_jar_path"] = arguments.pop(0)
                else:
                    logger.error("Unknown argument: %s", argument)
                    cmd_line_options["help"] = True
                    break
            else:
                logger.error("Cannot parse command line arguments: %s", " ".join(arguments))
                cmd_line_options["help"] = True
                break

        return CommandLineOptions(cmd_line_options)

    def __init__(self, cmd_line_options):
        self.input_file = cmd_line_options.get("input", None)
        self.output_file = cmd_line_options.get("output", None)
        self.show_help = cmd_line_options.get("help", False)
        self.plant_uml_jar_path = cmd_line_options.get("plantuml_jar_path", None)


def print_help():
    help_text = """
Usage: run.py [options]

Options:
    --plantuml-jar-path <path>      Path to plantuml.jar 
    --input <f>                     Input file name
    --output <f>                    Output file name"""
    print(help_text)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    options = CommandLineOptions.parse_arguments(sys.argv)
    if options.show_help:
        print_help()
    else:
        md = markdown.Markdown()
        plantumlhandler = plantumlblockprocessor.PlantUMLProcessHandler(options.plant_uml_jar_path)
        plantumlprocessor = plantumlblockprocessor.PlanUmlBlockProcessor(md.parser, plantumlhandler)
        md.parser.blockprocessors.register(plantumlprocessor, "plant-uml-processor", 165)

        md.convertFile(input=options.input_file,
                       output=options.output_file)
