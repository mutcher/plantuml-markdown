import logging
import time

from markdown.blockprocessors import BlockProcessor
from base64 import b64encode
import re
import markdown.util
from subprocess import Popen, PIPE


class PlantUMLProcessHandler:

    PIPE_DELIMITER = b'DELIM'

    def __init__(self, path):
        self.logger = logging.getLogger("PlantUmlProcessHandler")

        java_executable = "java"
        java_arguments = {"-jar": path,
                          "-png": None,
                          "-nthread": "auto",
                          "-pipe": None,
                          "-pipedelimitor": self.PIPE_DELIMITER.decode()}

        command = java_executable
        for argument in java_arguments:
            command += " " + argument
            value = java_arguments[argument]
            if value:
                command += " " + value

        self.logger.debug("Handler cmd=%s", command)
        self.pipe = Popen(command,
                          stdin=PIPE,
                          stdout=PIPE)

    def __del__(self):
        self.logger.debug("Destroying pipe")
        self.pipe.kill()

    def check_pipe_delimiter(self, output):
        result = output
        if self.PIPE_DELIMITER.startswith(output):
            # We already read the first symbol
            output = self.pipe.stdout.read(len(self.PIPE_DELIMITER) - 1)
            result += output
            if result == self.PIPE_DELIMITER:
                # Reading newline
                self.pipe.stdout.read(2)
                return True, b''
        return False, result

    def process_png(self, text):
        self.pipe.stdin.write(text.encode())
        self.pipe.stdin.flush()
        result = b''
        while True:
            output = self.pipe.stdout.read(1)
            res = self.check_pipe_delimiter(output)
            if not res[0]:
                output = res[1]
            else:
                break
            result += output
        self.logger.debug("Diagram received: size=%d", len(result))
        return result


class PlanUmlBlockProcessor(BlockProcessor):
    STARTUML = "@startuml"
    ENDUML = "@enduml\n"

    def __init__(self, parser, plant_uml_handler):
        super(PlanUmlBlockProcessor, self).__init__(parser)
        self.RE = re.compile(r'\s*\`\`\`plantuml')
        self.plantuml_handler = plant_uml_handler
        self.logger = logging.getLogger("PlantUmlBlockProcessor")

    def test(self, parent, block):
        if block:
            return self.RE.match(block)
        else:
            return False

    def run(self, parent, blocks):
        lines = []
        while len(lines) == 0 or lines[-1] != '```':
            block = blocks.pop(0).rstrip()
            if not block:
                self.logger.info("Empty block has skipped")
                return block

            tmp_lines = block.split("\n")
            lines.extend(tmp_lines)

        self.logger.debug("Lines=\"%s\"", lines)

        content = '\n'.join(lines[1:-1])
        content = '\n'.join([PlanUmlBlockProcessor.STARTUML,
                             content,
                             PlanUmlBlockProcessor.ENDUML])
        self.logger.debug("Processing %s", content)

        res = self.plantuml_handler.process_png(content)
        if res:
            p = markdown.util.etree.SubElement(parent, "p")
            img = markdown.util.etree.SubElement(p, "img")
            inline_png = "data:image/png;base64,"
            image_data = b64encode(res)
            img.attrib = {"src": inline_png + image_data.decode()}
        else:
            self.logger.error("Result of plantuml is empty")

        return blocks
