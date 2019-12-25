import logging
from subprocess import Popen, PIPE


class PipeFacade:
    def __init__(self, command: str):
        self._pipe = Popen(command,
                           stdin=PIPE,
                           stdout=PIPE)

    def write(self, string: str):
        self._pipe.stdin.write(string.encode())
        self._pipe.stdin.flush()

    def read(self, n: int):
        return self._pipe.stdout.read(n)

    def kill(self):
        self._pipe.kill()


class PlantUMLProcessHandler:

    PIPE_DELIMITER = b'DELIM'

    def __init__(self, path: str):
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
        self.pipe = PipeFacade(command)

    def __del__(self):
        self.logger.debug("Destroying pipe")
        self.pipe.kill()

    def _check_pipe_delimiter(self, output):
        result = output
        if self.PIPE_DELIMITER.startswith(output):
            # We already read the first symbol
            output = self.pipe.read(len(self.PIPE_DELIMITER) - 1)
            result += output
            if result == self.PIPE_DELIMITER:
                # Reading newline
                self.pipe.read(2)
                return True, b''
        return False, result

    def generate_png(self, diagram_text: str):
        if diagram_text[-1] != "\n":
            diagram_text += "\n"

        self.pipe.write(diagram_text)
        result = b''
        while True:
            output = self.pipe.read(1)
            res = self._check_pipe_delimiter(output)
            if not res[0]:
                output = res[1]
            else:
                break
            result += output
        self.logger.debug("Diagram received: size=%d", len(result))
        return result
