import sys
from ast import AST
from tokenize import TokenInfo
from typing import Sequence

from pylint import __version__
from pylint.lint import Run
from pylint.reporters import BaseReporter

if sys.version_info >= (3, 8):
    pass
else:
    pass

STDIN = 'stdin'
PREFIX = 'PL'

VERSION = __version__


class Reporter(BaseReporter):
    def __init__(self):
        self.errors = []
        super().__init__()

    def _display(self, layout):
        pass

    def handle_message(self, msg):
        # ignore `invalid syntax` messages, it is already checked by `pycodestyle`
        if msg.msg_id == 'E0001':
            return
        self.errors.append(dict(
            row=msg.line,
            col=msg.column,
            text='{prefix}{id} {msg} ({symbol})'.format(
                prefix=PREFIX,
                id=msg.msg_id,
                msg=msg.msg or '',
                symbol=msg.symbol,
            ),
            code=msg.msg_id,
        ))


class PyLintExt:
    name = 'pylint'
    version = VERSION

    def __init__(self, tree: AST, file_tokens: Sequence[TokenInfo], filename: str = STDIN) -> None:
        self.tree = tree
        self.filename = filename
        self.file_tokens = file_tokens

    def run(self):
        reporter = Reporter()
        Run(['--enable-all-extensions', self.filename], reporter=reporter, do_exit=False)
        for error in reporter.errors:
            yield error['row'], error['col'], error['text'], type(self)
