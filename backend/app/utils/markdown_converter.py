"""Markdown to required format converter.

This module converts Markdown text to a single-line required format while preserving LaTeX formulas.
"""
import re
from typing import Dict, List


class MarkdownConverter:
    """Convert Markdown text to single-line required format."""

    # Regex patterns
    INLINE_FORMULA_PATTERN = r'\$([^\$]+)\$'
    BLOCK_FORMULA_PATTERN = r'\$\$([^\$]+)\$\$'
    HEADING_PATTERN = r'^#{1,6}\s+'
    BOLD_PATTERN = r'\*\*(.+?)\*\*|__(.+?)__'
    ITALIC_PATTERN = r'\*(.+?)\*|_(.+?)_'
    STRIKETHROUGH_PATTERN = r'~~(.+?)~~'
    LINK_PATTERN = r'\[([^\]]+)\]\([^\)]+\)'
    IMAGE_PATTERN = r'!\[([^\]]*)\]\([^\)]+\)'
    CODE_INLINE_PATTERN = r'`([^`]+)`'
    CODE_BLOCK_PATTERN = r'```[^\n]*\n(.+?)```'
    BLOCKQUOTE_PATTERN = r'^>\s+'
    LIST_PATTERN = r'^[\*\-\+]\s+|^\d+\.\s+'
    HORIZONTAL_RULE_PATTERN = r'^[\*\-_]{3,}$'

    def __init__(self) -> None:
        """Initialize converter."""
        self.formula_placeholders: Dict[str, str] = {}
        self.placeholder_counter = 0

    def convert(self, markdown_text: str) -> str:
        """
        Convert Markdown text to single-line required format.

        Args:
            markdown_text: Input Markdown text

        Returns:
            str: Single-line formatted text with LaTeX formulas preserved

        Example:
            >>> converter = MarkdownConverter()
            >>> text = "**题目：**\\n求解以下方程：\\n$$x^2 + 2x + 1 = 0$$"
            >>> converter.convert(text)
            '题目：求解以下方程：$$x^2 + 2x + 1 = 0$$'
        """
        if not markdown_text:
            return ""

        # Reset state
        self.formula_placeholders = {}
        self.placeholder_counter = 0

        # Step 1: Protect formulas with placeholders
        text = self._protect_formulas(markdown_text)

        # Step 2: Remove Markdown formatting
        text = self._remove_markdown_formatting(text)

        # Step 3: Clean up whitespace and newlines
        text = self._clean_whitespace(text)

        # Step 4: Restore formulas
        text = self._restore_formulas(text)

        return text.strip()

    def _protect_formulas(self, text: str) -> str:
        """
        Replace LaTeX formulas with placeholders.

        Args:
            text: Input text

        Returns:
            str: Text with formulas replaced by placeholders
        """
        # Protect block formulas first ($$...$$)
        def replace_block_formula(match: re.Match) -> str:
            placeholder = f"__FORMULA_BLOCK_{self.placeholder_counter}__"
            self.formula_placeholders[placeholder] = f"$${match.group(1)}$$"
            self.placeholder_counter += 1
            return placeholder

        text = re.sub(
            self.BLOCK_FORMULA_PATTERN,
            replace_block_formula,
            text,
            flags=re.DOTALL
        )

        # Protect inline formulas ($...$)
        def replace_inline_formula(match: re.Match) -> str:
            placeholder = f"__FORMULA_INLINE_{self.placeholder_counter}__"
            self.formula_placeholders[placeholder] = f"${match.group(1)}$"
            self.placeholder_counter += 1
            return placeholder

        text = re.sub(
            self.INLINE_FORMULA_PATTERN,
            replace_inline_formula,
            text
        )

        return text

    def _remove_markdown_formatting(self, text: str) -> str:
        """
        Remove Markdown formatting syntax.

        Args:
            text: Input text

        Returns:
            str: Text with Markdown formatting removed
        """
        # Remove code blocks (preserve content)
        text = re.sub(self.CODE_BLOCK_PATTERN, r'\1', text, flags=re.DOTALL)

        # Remove inline code (preserve content)
        text = re.sub(self.CODE_INLINE_PATTERN, r'\1', text)

        # Remove images (keep alt text)
        text = re.sub(self.IMAGE_PATTERN, r'\1', text)

        # Remove links (keep text)
        text = re.sub(self.LINK_PATTERN, r'\1', text)

        # Remove bold (keep text)
        text = re.sub(self.BOLD_PATTERN, lambda m: m.group(1) or m.group(2), text)

        # Remove italic (keep text)
        text = re.sub(self.ITALIC_PATTERN, lambda m: m.group(1) or m.group(2), text)

        # Remove strikethrough (keep text)
        text = re.sub(self.STRIKETHROUGH_PATTERN, r'\1', text)

        # Process line by line for line-specific patterns
        lines = text.split('\n')
        processed_lines = []

        for line in lines:
            # Remove headings
            line = re.sub(self.HEADING_PATTERN, '', line)

            # Remove blockquotes
            line = re.sub(self.BLOCKQUOTE_PATTERN, '', line)

            # Remove list markers
            line = re.sub(self.LIST_PATTERN, '', line)

            # Skip horizontal rules
            if re.match(self.HORIZONTAL_RULE_PATTERN, line.strip()):
                continue

            # Skip empty lines will be handled later
            processed_lines.append(line)

        text = '\n'.join(processed_lines)

        return text

    def _clean_whitespace(self, text: str) -> str:
        """
        Clean up whitespace and newlines.

        Args:
            text: Input text

        Returns:
            str: Text with cleaned whitespace
        """
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)

        # Replace newlines with spaces
        text = text.replace('\n', ' ')

        # Replace multiple spaces again (may be created by newline replacement)
        text = re.sub(r' +', ' ', text)

        return text

    def _restore_formulas(self, text: str) -> str:
        """
        Restore formulas from placeholders.

        Args:
            text: Input text with placeholders

        Returns:
            str: Text with formulas restored
        """
        for placeholder, formula in self.formula_placeholders.items():
            text = text.replace(placeholder, formula)

        return text


def markdown_to_required_format(markdown_text: str) -> str:
    """
    Convert Markdown text to single-line required format.

    This is a convenience function that creates a converter and performs the conversion.

    Args:
        markdown_text: Input Markdown text

    Returns:
        str: Single-line formatted text

    Example:
        >>> text = "**题目：**\\n求解以下方程：\\n$$x^2 + 2x + 1 = 0$$"
        >>> markdown_to_required_format(text)
        '题目：求解以下方程：$$x^2 + 2x + 1 = 0$$'
    """
    converter = MarkdownConverter()
    return converter.convert(markdown_text)
