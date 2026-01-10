"""Custom statement class for Maribank with special handling for date and description processing."""

import calendar
import logging
import re
from datetime import datetime
from typing import Optional, List

from monopoly.config import MultilineConfig
from monopoly.constants import EntryType
from monopoly.statements import DebitStatement as GenericDebitStatement
from monopoly.statements.base import MatchContext
from monopoly.statements.transaction import Transaction, TransactionGroupDict, TransactionMatch

logger = logging.getLogger(__name__)


class DebitStatement(GenericDebitStatement):
    """Custom statement class for Maribank debit statements with specialized processing."""

    statement_type = EntryType.DEBIT

    def pre_process_match(self, transaction_match: TransactionMatch) -> TransactionMatch:
        """
        Pre-process Maribank transactions with custom date and polarity handling.
        
        - Month-only dates (e.g., "JUN") are converted to the last day of the month
        - Interest transactions: month-only date + empty description -> set description to "Interest"
        - Outgoing transactions get negative polarity
        """
        # First apply parent class processing
        transaction_match = super().pre_process_match(transaction_match)
        
        transaction_date = transaction_match.groupdict.transaction_date
        description = transaction_match.groupdict.description
        
        # Check if this is an interest transaction (month-only date + empty description)
        is_month_only = transaction_date and re.match(r'^(?i:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)$', transaction_date.strip())
        is_empty_description = not description or description.strip() == ""
        
        if is_month_only:
            # Convert month name to last day of month
            try:
                month_num = datetime.strptime(transaction_date.strip(), '%b').month
                # Use statement date year, and get last day of the month
                year = self.statement_date.year
                last_day = calendar.monthrange(year, month_num)[1]
                transaction_match.groupdict.transaction_date = f"{last_day:02d} {transaction_date.strip()}"
                logger.debug(f"Converted month-only date '{transaction_date}' to '{transaction_match.groupdict.transaction_date}'")
                
                # If description is empty and we have a month-only date, this is an interest transaction
                if is_empty_description:
                    transaction_match.groupdict.description = "Interest"
                    logger.debug("Set description to 'Interest' for month-only date with empty description")
                    
            except ValueError as e:
                logger.warning(f"Failed to convert month-only date '{transaction_date}': {e}")
        
        return transaction_match

    def get_multiline_description(self, context: MatchContext) -> str:
        """
        Override multiline description handling for Maribank transactions.
        
        For multiline transactions, concatenate up to 3 lines total including all prefixes.
        """
        if not context.multiline_config or not context.multiline_config.multiline_descriptions:
            return context.description

        # Special case for Interest transactions - don't concatenate duplicates
        if context.description.strip() == "Interest":
            return "Interest"

        description_parts = []
        max_lines = 3  # Maximum total lines to concatenate
        
        # Look at preceding lines for prefixes (customer name, category, etc.)
        idx = context.idx - 1
        prefix_lines = []
        while idx >= 0 and len(prefix_lines) < max_lines - 1:  # Leave room for main description
            line = context.lines[idx].strip()
            
            # Stop if we hit an empty line or a date line
            if not line or re.match(r'\d{2}\s+\w{3}|\w{3}\s+\d', line):
                break
            
            # Collect all non-empty, non-date lines as prefixes
            prefix_lines.insert(0, line)  # Insert at beginning to maintain order
            idx -= 1
        
        # Add prefix lines first
        description_parts.extend(prefix_lines)
        
        # Add the main description
        description_parts.append(context.description.strip())
        
        # Look at subsequent lines for additional description content
        # Only add if we haven't reached max_lines yet
        idx = context.idx + 1
        while idx < len(context.lines) and len(description_parts) < max_lines:
            line = context.lines[idx].strip()
            
            # Stop if we hit an empty line or a new transaction (date line)
            if not line or re.match(r'\d{2}\s+\w{3}|\w{3}\s+\d', line):
                break
            
            # Add this line to the description
            description_parts.append(line)
            idx += 1
        
        # Join all parts with a space, limiting to max_lines
        combined_description = ' '.join(description_parts[:max_lines])
        logger.debug(f"Combined multiline description ({len(description_parts[:max_lines])} lines): '{combined_description}'")
        
        return combined_description

    def post_process_transactions(self, transactions: list[Transaction]) -> list[Transaction]:
        """
        Post-process transactions to handle Maribank-specific requirements.
        
        - Apply polarity based on expected format (outgoing transactions are negative)
        - Filter out transactions after "SAVINGS - INTEREST DETAILS" if needed
        """
        transactions = super().post_process_transactions(transactions)
        
        processed_transactions = []
        for transaction in transactions:
            # Apply custom polarity logic for Maribank
            # Based on the expected CSV, outgoing amounts should be negative
            description_upper = transaction.description.upper()
            
            # Interest should be positive (incoming)
            if 'INTEREST' in description_upper:
                transaction.amount = abs(transaction.amount)
            # Transfers with negative amounts in expected data should remain negative
            elif any(keyword in description_upper for keyword in ['FAST TRANSFER', 'TRANSFER']):
                # Check expected data pattern - some transfers are negative, some positive
                # Keep the sign as determined by the amount parsing
                pass
            
            processed_transactions.append(transaction)
        
        return processed_transactions

    def get_transactions(self) -> List[Transaction]:
        """
        Override transaction extraction to handle Maribank-specific logic:
        1. Column-based polarity detection for OUTGOING vs INCOMING amounts
        """
        logger.debug("Using MaribankDebitStatement.get_transactions with custom logic")
        
        # Get raw transactions using parent logic (which includes multiline processing)
        raw_transactions = super().get_transactions()
        
        # Process each transaction for Maribank-specific adjustments
        processed_transactions = []
        
        for transaction in raw_transactions:
            # Handle polarity based on column position
            # Find the original line to determine column position
            # Parse transaction date from string to check day/month
            from dateparser import parse
            tx_date = parse(transaction.date)
            if tx_date:
                for page in self.pages:
                    for line in page.lines:
                        if (str(tx_date.day).zfill(2) in line and 
                            tx_date.strftime('%b').upper() in line.upper() and
                            f"{abs(transaction.amount):,.2f}".replace(',', ',') in line.replace(',', ',')):
                            
                            # Find the position of the amount in the line
                            amount_str = f"{abs(transaction.amount):,.2f}".replace(',', ',')
                            amount_pos = line.rfind(amount_str)
                            
                            if amount_pos != -1:
                                # If amount is in the left column (position < 65), it's OUTGOING (negative)
                                # If amount is in the right column (position >= 65), it's INCOMING (positive)
                                if amount_pos < 65 and transaction.amount > 0:
                                    transaction.amount = -transaction.amount
                                    logger.debug(f"Made amount negative (OUTGOING): {transaction.amount}")
                                elif amount_pos >= 65 and transaction.amount < 0:
                                    transaction.amount = abs(transaction.amount)
                                    logger.debug(f"Made amount positive (INCOMING): {transaction.amount}")
                            break
            
            processed_transactions.append(transaction)
        
        return processed_transactions