"""
Turkish Syllabification Module

Implements rule-based syllable segmentation for Turkish words following
linguistic principles of onset-nucleus-coda structure and Turkish phonotactics.

References:
- Eryiğit & Adalı (2004): Turkish syllabification
- Turkish phonology: (C)(C)V(C)(C) syllable structure
"""

import unicodedata
from dataclasses import dataclass
from typing import List, Optional, Union

# Turkish alphabet vowels (including circumflex variants)
VOWELS = frozenset("aeıioöuüâîû")

# Turkish alphabet consonants
CONSONANTS = frozenset("bcçdfgğhjklmnprsştvyzqwx")


@dataclass
class SyllableInfo:
    """Detailed syllable analysis information."""

    word: str
    syllables: List[str]
    count: int
    structure: List[str]  # e.g., ['CV', 'CVC', 'V']

    def __str__(self) -> str:
        return f"{self.word} → {'-'.join(self.syllables)} ({self.count} syllables)"


class Syllabifier:
    """
    Turkish syllabification engine using rule-based linguistic patterns.

    Turkish syllable structure: (C)(C)V(C)(C)
    - Onset: 0-2 consonants (optional)
    - Nucleus: 1 vowel (mandatory)
    - Coda: 0-2 consonants (optional)
    """

    def __init__(self):
        self.vowels = VOWELS
        self.consonants = CONSONANTS

    def syllabify(
        self, word: str, separator: Optional[str] = None
    ) -> Union[List[str], str]:
        """
        Syllabify a Turkish word.

        Args:
            word: Turkish word to syllabify
            separator: Optional separator for joining syllables (e.g., '-')

        Returns:
            List of syllables if separator is None, otherwise joined string

        Examples:
            >>> syllabifier = Syllabifier()
            >>> syllabifier.syllabify("merhaba")
            ['mer', 'ha', 'ba']
            >>> syllabifier.syllabify("merhaba", separator="-")
            'mer-ha-ba'
        """
        if not word:
            return "" if separator else []

        # Normalize Unicode (NFC) to handle combining characters like İ
        word = unicodedata.normalize("NFC", word)

        # Preserve case for output, but work with lowercase
        original_word = word
        word_lower = word.lower()

        syllables = self._segment(word_lower)

        # Restore original casing
        syllables = self._restore_case(syllables, original_word)

        if separator is not None:
            return separator.join(syllables)
        return syllables

    def _segment(self, word: str) -> List[str]:
        """
        Core syllabification algorithm.

        Turkish syllable boundary rules:
        - V.V       → break between vowels (o.ku)
        - VC.V      → break before single C before V (mer.ha.ba)
        - V.CV      → break before CV sequence (a.çık)
        - VCC.V     → break before last C of cluster (anl.a.mak → should be an.la.mak)
        - VC.CV     → break between C's (kit.ap)
        """
        syllables = []
        current = ""

        i = 0
        while i < len(word):
            char = word[i]
            current += char

            # Check if current character is a vowel
            if char in self.vowels:
                # Look ahead to determine syllable boundary
                if i + 1 < len(word):
                    next_chars = word[i + 1 :]
                    break_point = self._find_break_point(current, next_chars)

                    if break_point == 0:
                        # Break immediately after current syllable
                        syllables.append(current)
                        current = ""
                    elif break_point > 0:
                        # Break after consuming break_point characters
                        current += next_chars[:break_point]
                        syllables.append(current)
                        current = ""
                        i += break_point
                else:
                    # Last vowel in word
                    syllables.append(current)
                    current = ""

            i += 1

        # Append any remaining characters
        if current:
            if syllables:
                # Merge with last syllable if it's consonants only
                syllables[-1] += current
            else:
                syllables.append(current)

        return syllables

    def _find_break_point(self, current_syllable: str, remaining: str) -> int:
        """
        Determine where to break syllable boundary.

        Turkish syllable boundary rules (ONSET MAXIMIZATION):
        - V.V       → break immediately (o.ku)
        - V.CV      → break before C, C goes to next syllable (ki.tap, a.na)
        - VCC.V     → break between Cs (mer.ha.ba, an.la.mak)
        - VCCC.V    → break after first C (türk.çe, actually depends on cluster)

        Args:
            current_syllable: Current syllable ending in vowel
            remaining: Remaining characters in word

        Returns:
            Number of characters from remaining to consume before breaking:
            - 0: Break immediately (next syllable starts here)
            - N: Take N consonants before breaking
        """
        if not remaining:
            return 0

        # Count consecutive consonants at start of remaining
        consonant_count = 0
        for char in remaining:
            if char in self.consonants:
                consonant_count += 1
            else:
                break

        # V.V: Break immediately between vowels
        if consonant_count == 0:
            return 0

        # V.CV: Single consonant goes to NEXT syllable (onset maximization)
        # Examples: ki.tap, a.na, o.kul
        if consonant_count == 1:
            return 0  # Break immediately, consonant starts next syllable

        # VCC.V: Two consonants - check if they form valid onset
        if consonant_count == 2:
            cluster = remaining[:2]
            if self._is_valid_onset(cluster):
                # Both consonants can be onset of next syllable (e.g., tren)
                return 0
            else:
                # Split between consonants: first → coda, second → onset
                # Examples: mer.ha.ba (rh), an.la.mak (nl), kit.ap (tap edge case)
                return 1

        # VCCC+: Three or more consonants
        # Standard rule: take first consonant as coda, rest form onset
        # Examples: türk.çe (rkç → rk.çe)
        if consonant_count >= 3:
            # Take first consonant as coda
            return 1

        return 0

    def _is_valid_onset(self, cluster: str) -> bool:
        """
        Check if consonant cluster can be a valid Turkish syllable onset.

        Common Turkish onset clusters:
        - tr, pr, kr, gr, br, dr (e.g., tren, program, krema, grup, bröv, drama)

        Note: This is conservative - Turkish mostly prefers single consonant onsets.
        """
        valid_onsets = {
            "tr",
            "pr",
            "kr",
            "gr",
            "br",
            "dr",
            "fr",  # loanwords
            "pl",
            "kl",
            "bl",
            "fl",
            "gl",
        }
        return cluster in valid_onsets

    def _restore_case(self, syllables: List[str], original: str) -> List[str]:
        """
        Restore original casing to syllables.

        Args:
            syllables: Lowercase syllables
            original: Original word with casing

        Returns:
            Syllables with restored casing
        """
        result = []
        char_index = 0

        for syllable in syllables:
            restored = ""
            for char in syllable:
                if char_index < len(original):
                    # Copy case from original
                    if original[char_index].isupper():
                        restored += char.upper()
                    else:
                        restored += char
                    char_index += 1
                else:
                    restored += char
            result.append(restored)

        return result

    def count(self, word: str) -> int:
        """
        Count syllables in a word.

        Args:
            word: Turkish word

        Returns:
            Number of syllables

        Example:
            >>> syllabifier = Syllabifier()
            >>> syllabifier.count("merhaba")
            3
        """
        syllables = self.syllabify(word)
        return len(syllables) if isinstance(syllables, list) else 0

    def analyze(self, word: str) -> SyllableInfo:
        """
        Analyze word and return detailed syllable information.

        Args:
            word: Turkish word

        Returns:
            SyllableInfo with syllables, count, and structure

        Example:
            >>> syllabifier = Syllabifier()
            >>> info = syllabifier.analyze("kitap")
            >>> print(info)
            kitap → ki-tap (2 syllables)
        """
        syllables = self.syllabify(word)
        if isinstance(syllables, str):
            syllables = syllables.split("-")

        # Determine syllable structure (CV, CVC, etc.)
        structure = []
        for syl in syllables:
            struct = ""
            for char in syl.lower():
                if char in self.vowels:
                    struct += "V"
                elif char in self.consonants:
                    struct += "C"
            structure.append(struct)

        return SyllableInfo(
            word=word, syllables=syllables, count=len(syllables), structure=structure
        )


# Convenience function for direct usage
_default_syllabifier = Syllabifier()


def syllabify(word: str, separator: Optional[str] = None) -> Union[List[str], str]:
    """
    Syllabify a Turkish word (convenience function).

    Args:
        word: Turkish word to syllabify
        separator: Optional separator for joining syllables

    Returns:
        List of syllables or joined string if separator provided

    Examples:
        >>> from durak import syllabify
        >>> syllabify("merhaba")
        ['mer', 'ha', 'ba']
        >>> syllabify("kitap", separator="-")
        'ki-tap'
    """
    return _default_syllabifier.syllabify(word, separator)
