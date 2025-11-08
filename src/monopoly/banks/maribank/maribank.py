import logging
import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, PdfConfig, StatementConfig
from monopoly.constants import (
    ISO8601,
    BankNames,
    DebitTransactionPatterns,
    EntryType,
)
from monopoly.identifiers import TextIdentifier
from .debit_statement import DebitStatement

logger = logging.getLogger(__name__)


class Maribank(BankBase):
    name = BankNames.MARIBANK

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(r"STATEMENT PERIOD: .* to (?P<statement_date>\d{2} \w{3} \d{4})"),
        header_pattern=re.compile(r"(SAVINGS - TRANSACTION DETAILS)"),
        transaction_date_format="%d %b",  # Handle both DD MMM and MMM formats
        transaction_pattern=DebitTransactionPatterns.MARIBANK,
        multiline_config=MultilineConfig(
            multiline_descriptions=True,
            description_margin=15,  # Increased margin for better multiline handling
        ),
        transaction_bound=90,  # Stop before SAVINGS - INTEREST DETAILS section
        safety_check=False,  # Disable safety check for this mixed format
    )

    identifiers = [
        [
            TextIdentifier(text="DEPOSIT AND INVESTMENT STATEMENT"),
            TextIdentifier(text="SAVINGS - TRANSACTION DETAILS"),
        ],
        [
            TextIdentifier(text="help@maribank.sg"),
        ],
    ]
    
    pdf_config = PdfConfig(
        ocr_identifiers=identifiers,  # Force OCR for Maribank PDFs
    )

    statement_configs = [debit]