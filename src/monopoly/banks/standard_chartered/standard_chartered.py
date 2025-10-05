import logging
import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import (
    ISO8601,
    BankNames,
    CreditTransactionPatterns,
    DebitTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

logger = logging.getLogger(__name__)


class StandardChartered(BankBase):
    name = BankNames.STANDARD_CHARTERED

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(rf": {ISO8601.DD_MMM_YYYY}$"),
        header_pattern=re.compile(r"(Transaction.*Posting.*Amount)"),
        prev_balance_pattern=StatementBalancePatterns.STANDARD_CHARTERED,
        transaction_pattern=CreditTransactionPatterns.STANDARD_CHARTERED,
        transaction_date_format="%d %b",
    )

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf": {ISO8601.DD_MMM_YYYY}$"),
        header_pattern=re.compile(r"(Date.*Description.*Deposit.*Withdrawal.*Balance)"),
        prev_balance_pattern=StatementBalancePatterns.STANDARD_CHARTERED,
        transaction_pattern=DebitTransactionPatterns.STANDARD_CHARTERED,
        multiline_config=MultilineConfig(multiline_descriptions=True),
        transaction_date_format="%d %b %Y",
    )

    identifiers = [
        [
            MetadataIdentifier(
                title="eStatement",
                producer="iText",
            ),
            TextIdentifier("Standard Chartered"),
        ],
        [
            MetadataIdentifier(
                title="eStatement",
                producer="OpenPDF",
            ),
            TextIdentifier("Standard Chartered"),
        ]
    ]

    statement_configs = [credit, debit]
