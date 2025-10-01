import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
import unittest

# Ensure the project module is importable when running the tests from repo root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "pyVersion"))

from corrector import (
    ALPHABET,
    corregir_frase,
    generate_variations,
    load_lemario,
)


class LoadLemarioTests(unittest.TestCase):
    def test_load_lemario_ignores_blank_lines(self):
        with NamedTemporaryFile("w+", encoding="utf-8", delete=False) as handle:
            handle.write("hola\n\n adiós \n")
            temp_path = handle.name

        lemario = load_lemario(temp_path)
        self.assertEqual(lemario, {"hola", "adiós"})


class GenerateVariationsTests(unittest.TestCase):
    def setUp(self):
        self.lemario = {"hola", "halo", "ola", "hola", "hola", "hol"}

    def test_variations_cover_single_edit_operations(self):
        swap_variations = generate_variations("hloa", self.lemario)
        insertion_variations = generate_variations("hla", self.lemario)
        deletion_variations = generate_variations("holaa", self.lemario)
        substitution_variations = generate_variations("hela", self.lemario)

        self.assertIn("hola", swap_variations)
        self.assertIn("hola", insertion_variations)
        self.assertIn("hola", deletion_variations)
        self.assertIn("hola", substitution_variations)

    def test_variations_are_sorted(self):
        variations = generate_variations("hol", self.lemario)
        self.assertEqual(variations, sorted(variations))


class CorregirFraseTests(unittest.TestCase):
    def setUp(self):
        self.lemario = {"hola", "mundo", "adiós"}

    def test_selector_replaces_word(self):
        def selector(original, variations):
            self.assertEqual(original, "holq")
            self.assertEqual(variations, ["hola"])
            return variations[0]

        resultado = corregir_frase("holq mundo", self.lemario, selector)
        self.assertEqual(resultado, "hola mundo")

    def test_selector_keeps_original_when_none(self):
        def selector(original, variations):
            return None

        resultado = corregir_frase("holq mundo", self.lemario, selector)
        self.assertEqual(resultado, "holq mundo")

    def test_known_word_preserves_original_casing(self):
        resultado = corregir_frase("Hola mundo", self.lemario)
        self.assertEqual(resultado, "Hola mundo")


if __name__ == "__main__":
    unittest.main()
