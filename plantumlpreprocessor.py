import logging

from markdown.preprocessors import Preprocessor
from plantumlprocesshandler import PlantUMLProcessHandler
from base64 import b64encode


class PlantumlDiagramPreprocessor(Preprocessor):

    def __init__(self, md, plantuml_handler: PlantUMLProcessHandler):
        super(Preprocessor, self).__init__(md)
        self._process_handler = plantuml_handler

    def run(self, lines):
        result = []
        block = []
        is_block = False
        for line in lines:
            if is_block:
                if not line.startswith('```'):
                    block.append(line)
                else:
                    is_block = False
                    res = self._process_block(block)
                    if not res:
                        raise Exception("Cannot generate the diagram")
                    else:
                        result.append(res)
            else:
                if line.startswith('```plantuml'):
                    is_block = True
                    block = []
                else:
                    result.append(line)
        return result

    def _process_block(self, block):
        diagram_text = "@startuml\n"
        diagram_text += "\n".join(block)
        diagram_text += "@enduml"

        result = self._process_handler.generate_png(diagram_text)
        if result:
            img_format = '<p><img src="data:image/png;base64,%s" /></p>'
            return img_format % b64encode(result).decode()
        else:
            logging.error("Cannot generate the diagram")
            return ""
