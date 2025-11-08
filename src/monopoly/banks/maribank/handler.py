"""Custom statement handler for Maribank."""

import logging
from functools import cached_property

from monopoly.config import StatementConfig
from monopoly.constants import EntryType
from monopoly.handler import StatementHandler as GenericStatementHandler
from monopoly.pdf import PdfParser
from monopoly.statements import BaseStatement

from .debit_statement import DebitStatement

logger = logging.getLogger(__name__)


class StatementHandler(GenericStatementHandler):
    """Custom statement handler for Maribank that uses MaribankDebitStatement class."""
    
    def __init__(self, parser: PdfParser):
        super().__init__(parser)
    
    def _get_statement(self) -> BaseStatement:
        """Override to use MaribankDebitStatement for debit statements."""
        pages = self.pages
        bank_name = self.bank.name

        for config in self.bank.statement_configs:
            if header := self.get_header(config):
                match config.statement_type:
                    case EntryType.DEBIT:
                        logger.debug("Statement type detected: %s (using MaribankDebitStatement)", EntryType.DEBIT)
                        return DebitStatement(pages, bank_name, config, header)
                    case EntryType.CREDIT:
                        # Use default CreditStatement for credit if ever needed
                        from monopoly.statements import CreditStatement
                        logger.debug("Statement type detected: %s", EntryType.CREDIT)
                        return CreditStatement(pages, bank_name, config, header)

        msg = "Could not find header in statement"
        raise RuntimeError(msg)