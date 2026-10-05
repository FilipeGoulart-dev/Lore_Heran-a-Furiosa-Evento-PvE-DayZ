import json
from pathlib import Path
import tempfile
import unittest

from scripts.check_repository import (
    CATALOG,
    INVENTORY,
    check_repository,
    markdown_ids,
    update_inventory,
)


class RepositoryChecksTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.image = self.root / "assets/images/vehicles/ref.jpg"
        self.image.parent.mkdir(parents=True)
        # A minimal header is enough here: the verifier checks signatures, not decoding.
        self.image.write_bytes(b"\xff\xd8\xfftest-media")
        (self.root / "assets/css").mkdir()
        (self.root / "assets/css/styles.css").write_text(
            "body { background: url('../images/vehicles/ref.jpg'); }\n", encoding="utf-8"
        )
        (self.root / "docs").mkdir()
        (self.root / "docs/auditoria.md").write_text("# Auditoria\n", encoding="utf-8")
        (self.root / "docs/guia.md").write_text(
            "# Preparação\n\n[Início](../index.html#inicio)\n", encoding="utf-8"
        )
        self.index = self.root / "index.html"
        self.index.write_text(
            '<!doctype html><html lang="pt-BR"><head>'
            '<link rel="stylesheet" href="assets/css/styles.css"></head>'
            '<body id="inicio"><a href="docs/guia.md#prepara%C3%A7%C3%A3o">Guia</a>'
            '<img src="assets/images/vehicles/ref.jpg" alt="Referência"></body></html>\n',
            encoding="utf-8",
        )
        update_inventory(self.root)

    def assert_error(self, expected):
        errors, _ = check_repository(self.root)
        self.assertTrue(any(expected in error for error in errors), errors)

    def add_link(self, target):
        with self.index.open("a", encoding="utf-8") as file:
            file.write(f'<a href="{target}">Teste</a>\n')

    def test_valid_repository(self):
        self.assertEqual(check_repository(self.root), ([], []))

    def test_changed_media_is_detected(self):
        self.image.write_bytes(self.image.read_bytes() + b"changed")
        self.assert_error("SHA-256 diferente")
        self.assert_error("tamanho diferente")

    def test_missing_media_is_detected(self):
        self.image.unlink()
        self.assert_error("mídia ausente")

    def test_unlisted_media_is_detected(self):
        (self.image.parent / "new.jpg").write_bytes(self.image.read_bytes())
        self.assert_error("sem entrada no inventário")

    def test_duplicates_are_warnings(self):
        (self.image.parent / "copy.jpg").write_bytes(self.image.read_bytes())
        update_inventory(self.root)
        errors, warnings = check_repository(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("Duplicata binária", warnings[0])
        self.assertIn("Grupo 1", (self.root / CATALOG).read_text(encoding="utf-8"))

    def test_missing_local_link_is_detected(self):
        self.add_link("docs/missing.md")
        self.assert_error("arquivo ausente")

    def test_missing_html_fragment_is_detected(self):
        self.add_link("#missing")
        self.assert_error("fragmento ausente")

    def test_missing_markdown_fragment_is_detected(self):
        self.add_link("docs/guia.md#missing")
        self.assert_error("fragmento ausente")

    def test_encoded_relative_link(self):
        (self.image.parent / "com espaço.jpg").write_bytes(self.image.read_bytes())
        update_inventory(self.root)
        self.add_link("assets/images/vehicles/com%20espa%C3%A7o.jpg?download=1")
        self.assertEqual(check_repository(self.root)[0], [])

    def test_external_urls_and_code_examples_are_ignored(self):
        self.add_link("https://example.invalid/not-fetched")
        with (self.root / "docs/guia.md").open("a", encoding="utf-8") as file:
            file.write("\n```md\n[Exemplo](missing.md)\n```\n\n`[Exemplo](missing.md)`\n")
        self.assertEqual(check_repository(self.root), ([], []))

    def test_absolute_and_outside_paths_are_rejected(self):
        self.add_link("/index.html")
        self.add_link("%2e%2e/outside.md")
        self.assert_error("URL local absoluta")
        self.assert_error("fora do conteúdo")

    def test_css_reference_is_checked(self):
        (self.root / "assets/css/styles.css").write_text(
            "body { background: url('../missing.png'); }\n", encoding="utf-8"
        )
        self.assert_error("arquivo ausente")

    def test_invalid_media_signature_is_detected_and_not_accepted(self):
        self.image.write_bytes(b"not a JPEG")
        self.assert_error("assinatura inválida")
        with self.assertRaises(ValueError):
            update_inventory(self.root)

    def test_stale_catalog_is_detected(self):
        (self.root / CATALOG).write_text("# Alterado\n", encoding="utf-8")
        self.assert_error("catálogo desatualizado")

    def test_inventory_schema_and_duplicate_entries(self):
        inventory = json.loads((self.root / INVENTORY).read_text(encoding="utf-8"))
        inventory["files"].append(inventory["files"][0])
        (self.root / INVENTORY).write_text(json.dumps(inventory), encoding="utf-8")
        self.assert_error("caminho duplicado")
        (self.root / INVENTORY).write_text("[]\n", encoding="utf-8")
        self.assert_error("schema inválido")

    def test_update_preserves_original_path(self):
        inventory = json.loads((self.root / INVENTORY).read_text(encoding="utf-8"))
        inventory["files"][0]["original_path"] = "original-ref.jpg"
        (self.root / INVENTORY).write_text(json.dumps(inventory), encoding="utf-8")
        update_inventory(self.root)
        updated = json.loads((self.root / INVENTORY).read_text(encoding="utf-8"))
        self.assertEqual(updated["files"][0]["original_path"], "original-ref.jpg")
        self.assertEqual(check_repository(self.root), ([], []))

    def test_empty_html_and_duplicate_ids(self):
        self.index.write_text("\n", encoding="utf-8")
        self.assert_error("HTML vazio")
        self.index.write_text('<div id="same"></div><div id="same"></div>', encoding="utf-8")
        self.assert_error("IDs HTML duplicados")

    def test_invalid_urls_are_reported_without_crashing(self):
        self.add_link("http://[invalid")
        self.add_link("%00.jpg")
        self.assert_error("URL inválida")
        self.assert_error("URL local inválida")

    def test_invalid_inventory_fields_are_detected(self):
        inventory = json.loads((self.root / INVENTORY).read_text(encoding="utf-8"))
        inventory["files"][0].update(original_path=123, size_bytes=True, sha256="invalid")
        (self.root / INVENTORY).write_text(json.dumps(inventory), encoding="utf-8")
        self.assert_error("original_path inválido")
        self.assert_error("size_bytes inválido")
        self.assert_error("campo sha256 inválido")

    def test_markdown_anchors_include_accents_and_duplicate_suffixes(self):
        self.assertEqual(markdown_ids("# Preparação\n# Preparação\n## 1. A missão!\n"),
                         {"preparação", "preparação-1", "1-a-missão"})


if __name__ == "__main__":
    unittest.main()
