"""Tests for Turkish syllabification module."""

import pytest

from durak import Syllabifier, SyllableInfo, syllabify


class TestBasicSyllabification:
    """Test basic syllabification functionality."""

    @pytest.mark.parametrize(
        "word,expected",
        [
            # Single syllable
            ("ev", ["ev"]),
            ("el", ["el"]),
            ("su", ["su"]),
            ("göz", ["göz"]),
            # Two syllables
            ("kitap", ["ki", "tap"]),
            ("okul", ["o", "kul"]),
            ("gözlük", ["göz", "lük"]),
            ("deniz", ["de", "niz"]),
            ("kapı", ["ka", "pı"]),
            ("çocuk", ["ço", "cuk"]),
            # Three syllables
            ("merhaba", ["mer", "ha", "ba"]),
            ("anlamak", ["an", "la", "mak"]),
            ("İstanbul", ["İs", "tan", "bul"]),
            ("karmaşık", ["kar", "ma", "şık"]),
            ("öğrenci", ["öğ", "ren", "ci"]),
            ("çalışmak", ["ça", "lış", "mak"]),
            # Four syllables
            ("Türkiye", ["Tür", "ki", "ye"]),
            ("bilgisayar", ["bil", "gi", "sa", "yar"]),
            ("merhametli", ["mer", "ha", "met", "li"]),
            # Five+ syllables
            ("öğretmen", ["öğ", "ret", "men"]),
            ("cumhuriyet", ["cum", "hu", "ri", "yet"]),
        ],
    )
    def test_syllabify_basic(self, word, expected):
        """Test basic syllabification of common Turkish words."""
        result = syllabify(word)
        assert result == expected, f"Failed for '{word}': got {result}, expected {expected}"

    def test_syllabify_with_separator(self):
        """Test syllabification with custom separator."""
        assert syllabify("merhaba", separator="-") == "mer-ha-ba"
        assert syllabify("kitap", separator=".") == "ki.tap"
        assert syllabify("okul", separator=" ") == "o kul"

    def test_syllabify_empty_string(self):
        """Test empty string handling."""
        assert syllabify("") == []
        assert syllabify("", separator="-") == ""

    def test_syllabify_case_preservation(self):
        """Test that original casing is preserved."""
        assert syllabify("İSTANBUL") == ["İS", "TAN", "BUL"]
        assert syllabify("Türkiye") == ["Tür", "ki", "ye"]
        assert syllabify("MERHABA") == ["MER", "HA", "BA"]
        assert syllabify("KiTaP") == ["Ki", "TaP"]


class TestSyllablePatterns:
    """Test specific syllable patterns and linguistic rules."""

    def test_vowel_vowel_boundary(self):
        """Test V.V pattern - break between vowels."""
        assert syllabify("şair") == ["şa", "ir"]  # poet
        assert syllabify("dua") == ["du", "a"]  # prayer

    def test_single_consonant_boundary(self):
        """Test VC.V and V.CV patterns."""
        assert syllabify("ana") == ["a", "na"]  # mother (V.CV)
        assert syllabify("ata") == ["a", "ta"]  # father/ancestor (V.CV)
        assert syllabify("para") == ["pa", "ra"]  # money (CV.CV)

    def test_consonant_cluster_boundary(self):
        """Test VCC.V patterns."""
        assert syllabify("anlamak") == ["an", "la", "mak"]  # to understand
        assert syllabify("kurtarmak") == ["kur", "tar", "mak"]  # to save
        assert syllabify("korkak") == ["kor", "kak"]  # coward

    def test_valid_onset_clusters(self):
        """Test that valid Turkish onset clusters stay together."""
        # These should keep onset clusters
        assert syllabify("tren") == ["tren"]  # train
        assert syllabify("kral") == ["kral"]  # king
        # Note: program is loanword, may vary
        assert syllabify("prova") == ["pro", "va"]  # rehearsal


class TestSyllabifier:
    """Test Syllabifier class methods."""

    def test_count_method(self):
        """Test syllable counting."""
        syllabifier = Syllabifier()
        assert syllabifier.count("ev") == 1
        assert syllabifier.count("kitap") == 2
        assert syllabifier.count("merhaba") == 3
        assert syllabifier.count("bilgisayar") == 4

    def test_analyze_method(self):
        """Test detailed syllable analysis."""
        syllabifier = Syllabifier()

        # Two syllable word
        info = syllabifier.analyze("kitap")
        assert isinstance(info, SyllableInfo)
        assert info.word == "kitap"
        assert info.syllables == ["ki", "tap"]
        assert info.count == 2
        assert info.structure == ["CV", "CVC"]

        # Three syllable word
        info = syllabifier.analyze("merhaba")
        assert info.word == "merhaba"
        assert info.syllables == ["mer", "ha", "ba"]
        assert info.count == 3
        assert info.structure == ["CVC", "CV", "CV"]

        # Single syllable
        info = syllabifier.analyze("ev")
        assert info.syllables == ["ev"]
        assert info.count == 1
        assert info.structure == ["VC"]

    def test_analyze_with_uppercase(self):
        """Test analysis preserves original case."""
        syllabifier = Syllabifier()
        info = syllabifier.analyze("TÜRK")
        assert info.word == "TÜRK"
        assert info.syllables == ["TÜRK"]


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_single_vowel_word(self):
        """Test single vowel words."""
        assert syllabify("a") == ["a"]
        assert syllabify("o") == ["o"]

    def test_words_starting_with_vowel(self):
        """Test words starting with vowels."""
        assert syllabify("anne") == ["an", "ne"]  # mother
        assert syllabify("elbise") == ["el", "bi", "se"]  # dress
        assert syllabify("öğretmen") == ["öğ", "ret", "men"]  # teacher

    def test_words_ending_with_consonants(self):
        """Test various coda patterns."""
        assert syllabify("türk") == ["türk"]
        assert syllabify("ders") == ["ders"]
        assert syllabify("gençlik") == ["genç", "lik"]  # youth

    def test_apostrophe_handling(self):
        """Test words with apostrophes (proper nouns + suffix)."""
        # Apostrophes should be treated as part of syllable
        assert syllabify("Ankara'da") == ["An", "ka", "ra", "'da"]
        assert syllabify("Ali'nin") == ["A", "li", "'nin"]

    def test_circumflex_vowels(self):
        """Test circumflex vowels (â, î, û)."""
        assert syllabify("hâlâ") == ["hâ", "lâ"]  # still
        assert syllabify("rûh") == ["rûh"]  # soul

    def test_dotted_i_and_undotted_i(self):
        """Test Turkish I/İ and ı/i distinction."""
        assert syllabify("ışık") == ["ı", "şık"]  # light
        assert syllabify("İzmir") == ["İz", "mir"]
        assert syllabify("ılık") == ["ı", "lık"]  # warm


class TestLinguisticAccuracy:
    """Test linguistic accuracy against known correct syllabifications."""

    @pytest.mark.parametrize(
        "word,expected",
        [
            # Common verbs
            ("yapmak", ["yap", "mak"]),
            ("gelmek", ["gel", "mek"]),
            ("gitmek", ["git", "mek"]),
            ("almak", ["al", "mak"]),
            ("vermek", ["ver", "mek"]),
            # Common nouns
            ("adam", ["a", "dam"]),
            ("kadın", ["ka", "dın"]),
            ("çocuk", ["ço", "cuk"]),
            ("insan", ["in", "san"]),
            ("hayat", ["ha", "yat"]),
            # Adjectives
            ("güzel", ["gü", "zel"]),
            ("kötü", ["kö", "tü"]),
            ("büyük", ["bü", "yük"]),
            ("küçük", ["kü", "çük"]),
            # Numbers
            ("bir", ["bir"]),
            ("iki", ["i", "ki"]),
            ("üç", ["üç"]),
            ("dört", ["dört"]),
            ("beş", ["beş"]),
            ("altı", ["al", "tı"]),
            ("yedi", ["ye", "di"]),
            ("sekiz", ["se", "kiz"]),
            ("dokuz", ["do", "kuz"]),
            ("on", ["on"]),
        ],
    )
    def test_common_words(self, word, expected):
        """Test syllabification of frequently used Turkish words."""
        assert syllabify(word) == expected


class TestIntegration:
    """Test integration with other durak modules."""

    def test_with_tokenization(self):
        """Test syllabification on tokenized text."""
        from durak import tokenize

        text = "Kitabı okudum."
        tokens = tokenize(text)

        syllabified = {
            token: syllabify(token) for token in tokens if token.isalpha()
        }

        assert syllabified["Kitabı"] == ["Ki", "ta", "bı"]
        assert syllabified["okudum"] == ["o", "ku", "dum"]

    def test_batch_processing(self):
        """Test batch syllabification."""
        words = ["ev", "kitap", "merhaba", "bilgisayar"]
        results = [syllabify(word) for word in words]

        assert results == [
            ["ev"],
            ["ki", "tap"],
            ["mer", "ha", "ba"],
            ["bil", "gi", "sa", "yar"],
        ]

    def test_filter_by_syllable_count(self):
        """Test filtering words by syllable count (useful for poetry)."""
        syllabifier = Syllabifier()
        words = ["ev", "kitap", "merhaba", "bilgisayar", "okul", "derslik"]

        # Find 2-syllable words
        two_syllable = [w for w in words if syllabifier.count(w) == 2]
        assert set(two_syllable) == {"kitap", "okul", "derslik"}

        # Find 3-syllable words
        three_syllable = [w for w in words if syllabifier.count(w) == 3]
        assert three_syllable == ["merhaba"]
