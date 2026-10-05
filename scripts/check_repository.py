#!/usr/bin/env python3
"""Check local references and media snapshots using only the standard library."""

import argparse
from collections import defaultdict
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = Path("docs/inventario-midia.json")
CATALOG = Path("docs/catalogo-midia.md")
IGNORED = {".git", ".cache", ".venv", "__pycache__", "node_modules", ".DS_Store", "Thumbs.db"}
CATEGORIES = {
    "assets/images/vehicles/": "Veículos",
    "assets/images/locations/": "Locais e construções",
    "assets/images/mods/": "Mods e itens",
    "assets/images/references/": "Capturas de referência",
    "assets/audio/": "Áudio",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if value and name in {"href", "src", "poster"}:
                self.references.append(value)
            if value and (name == "id" or (tag == "a" and name == "name")):
                self.ids.append(value)

    handle_startendtag = handle_starttag


def without_code(text):
    text = re.sub(r"(?ms)^\s*(```|~~~)[^\n]*\n.*?^\s*\1[^\S\n]*$", "", text)
    return re.sub(r"`[^`\n]*`", "", text)


def markdown_ids(text):
    """GitHub-style anchors for the simple ATX headings used in this repo."""
    ids, counts = set(), defaultdict(int)
    for heading in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*#*\s*$", without_code(text)):
        heading = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", heading)
        heading = re.sub(r"<[^>]+>", "", heading).lower()
        slug = re.sub(r"[^\w\s-]", "", heading).strip().replace(" ", "-")
        suffix = f"-{counts[slug]}" if counts[slug] else ""
        ids.add(slug + suffix)
        counts[slug] += 1
    return ids


def reference_data(path):
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".html":
        parser = PageParser()
        parser.feed(text)
        return parser.references, set(parser.ids)
    if path.suffix == ".md":
        refs = re.findall(r"!?\[[^]\n]*\]\(<?([^\s)>]+)>?(?:\s+[\"'][^\n]*?[\"'])?\)", without_code(text))
        return refs, markdown_ids(text)
    refs = re.findall(r"url\(\s*[\"']?([^\s)\"']+)[\"']?\s*\)", text)
    return refs, set()


def check_references(root):
    root = root.resolve()
    errors = []
    documents = sorted(p for p in root.rglob("*") if p.is_file()
                       and p.suffix in {".md", ".html", ".css"}
                       and not any(part in IGNORED for part in p.relative_to(root).parts))
    anchors = {}
    for source in documents:
        label = source.relative_to(root).as_posix()
        try:
            refs, anchors[source] = reference_data(source)
            if source.suffix == ".html":
                text = source.read_text(encoding="utf-8")
                if not text.strip():
                    errors.append(f"{label}: HTML vazio")
                parser = PageParser()
                parser.feed(text)
                if len(parser.ids) != len(set(parser.ids)):
                    errors.append(f"{label}: IDs HTML duplicados")
        except (OSError, UnicodeError) as error:
            errors.append(f"{label}: não foi possível ler o documento: {error}")
            continue
        for ref in refs:
            try:
                url = urlsplit(ref)
            except ValueError as error:
                errors.append(f"{label}: URL inválida: {ref}: {error}")
                continue
            if url.scheme or url.netloc:
                continue  # External URLs are deliberately not fetched.
            local_path = unquote(url.path)
            if local_path.startswith("/"):
                errors.append(f"{label}: URL local absoluta; use caminho relativo: {ref}")
                continue
            try:
                target = (source.parent / local_path).resolve() if local_path else source
            except (OSError, ValueError) as error:
                errors.append(f"{label}: URL local inválida: {ref}: {error}")
                continue
            if not target.is_relative_to(root) or ".git" in target.relative_to(root).parts:
                errors.append(f"{label}: referência fora do conteúdo do repositório: {ref}")
                continue
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                errors.append(f"{label}: arquivo ausente: {ref}")
                continue
            if url.fragment and target.suffix in {".html", ".md"}:
                if target not in anchors:
                    try:
                        anchors[target] = reference_data(target)[1]
                    except (OSError, UnicodeError) as error:
                        errors.append(f"{label}: não foi possível ler o destino: {error}")
                        continue
                if unquote(url.fragment) not in anchors[target]:
                    errors.append(f"{label}: fragmento ausente: {ref}")
    return errors


def media_paths(root):
    paths = []
    for folder in (root / "assets/images", root / "assets/audio"):
        if folder.exists():
            paths.extend(p for p in folder.rglob("*") if p.is_file()
                         and not any(part in IGNORED for part in p.relative_to(root).parts))
    return sorted(paths)


def valid_signature(path, data):
    if path.suffix.lower() in {".jpg", ".jpeg"}:
        return data.startswith(b"\xff\xd8\xff")
    if path.suffix.lower() == ".png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if path.suffix.lower() == ".mp3":
        return data.startswith(b"ID3") or (len(data) >= 2 and data[0] == 0xFF and data[1] & 0xE0 == 0xE0)
    return False


def load_inventory(root):
    data = json.loads((root / INVENTORY).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("files"), list):
        raise ValueError("schema inválido: esperado schema_version 1 e lista files")
    return data


def catalog_text(entries):
    lines = [
        "# Catálogo de mídias", "",
        "> Arquivo gerado por `python3 scripts/check_repository.py --update-inventory`. Não editar manualmente.", "",
        "Os arquivos originais foram preservados. Caminhos anteriores, tamanhos exatos e SHA-256 estão no [inventário JSON](inventario-midia.json).",
        "As categorias indicam o tema nominal das referências, não compatibilidade ou autoria confirmadas. Consulte as ressalvas e permissões no [relatório de verificação](auditoria.md).", "",
    ]
    for prefix, title in CATEGORIES.items():
        group = sorted((e for e in entries if e["path"].startswith(prefix)), key=lambda e: e["path"])
        if not group:
            continue
        lines += [f"## {title}", "", "| Arquivo | Tamanho |", "| --- | ---: |"]
        for entry in group:
            name = Path(entry["path"]).name
            lines.append(f"| [{name}](../{quote(entry['path'], safe='/')}) | {entry['size_bytes'] / 1024:.1f} KiB |")
        lines.append("")
    other = [e for e in entries if not any(e["path"].startswith(prefix) for prefix in CATEGORIES)]
    if other:
        lines += ["## Outras mídias", ""]
        lines += [f"- [{e['path']}](../{quote(e['path'], safe='/')})" for e in sorted(other, key=lambda e: e["path"])]
        lines.append("")
    hashes = defaultdict(list)
    for entry in entries:
        hashes[entry["sha256"]].append(entry["path"])
    duplicates = sorted(sorted(group) for group in hashes.values() if len(group) > 1)
    lines += ["## Duplicatas binárias", ""]
    if duplicates:
        for index, group in enumerate(duplicates, 1):
            lines += [f"### Grupo {index}", ""]
            lines += [f"- [{Path(path).name}](../{quote(path, safe='/')})" for path in group]
            lines.append("")
        lines += ["Esses arquivos têm o mesmo SHA-256. A duplicação é sinalizada, mas não bloqueia a verificação.", ""]
    else:
        lines += ["Nenhuma duplicata binária encontrada.", ""]
    return "\n".join(lines)


def update_inventory(root):
    previous = load_inventory(root) if (root / INVENTORY).exists() else {"schema_version": 1, "files": []}
    old_entries = {entry["path"]: entry for entry in previous["files"]}
    entries = []
    for path in media_paths(root):
        name = path.relative_to(root).as_posix()
        content = path.read_bytes()
        if not valid_signature(path, content):
            raise ValueError(f"{name}: formato não suportado ou assinatura inválida")
        entries.append({
            "path": name,
            "original_path": old_entries.get(name, {}).get("original_path"),
            "size_bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        })
    previous["files"] = entries
    (root / INVENTORY).parent.mkdir(parents=True, exist_ok=True)
    (root / INVENTORY).write_text(json.dumps(previous, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / CATALOG).write_text(catalog_text(entries), encoding="utf-8")


def check_inventory(root):
    errors, warnings = [], []
    try:
        entries = load_inventory(root)["files"]
    except (OSError, ValueError) as error:
        return [f"{INVENTORY}: {error}"], warnings
    actual = {p.relative_to(root).as_posix(): p for p in media_paths(root)}
    seen, hashes = set(), defaultdict(list)
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            errors.append("Inventário: entrada inválida")
            continue
        name = entry["path"]
        if name in seen:
            errors.append(f"Inventário: caminho duplicado: {name}")
        seen.add(name)
        if "original_path" not in entry or (entry["original_path"] is not None and not isinstance(entry["original_path"], str)):
            errors.append(f"{name}: original_path inválido ou ausente")
        if type(entry.get("size_bytes")) is not int or entry["size_bytes"] <= 0:
            errors.append(f"{name}: size_bytes inválido")
        if not isinstance(entry.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]):
            errors.append(f"{name}: campo sha256 inválido")
        if name not in actual:
            errors.append(f"Inventário: mídia ausente ou fora das pastas de mídia: {name}")
            continue
        content = actual[name].read_bytes()
        if not valid_signature(actual[name], content):
            errors.append(f"{name}: formato não suportado ou assinatura inválida")
        if entry.get("size_bytes") != len(content):
            errors.append(f"{name}: tamanho diferente do inventário")
        digest = hashlib.sha256(content).hexdigest()
        if entry.get("sha256") != digest:
            errors.append(f"{name}: SHA-256 diferente do inventário")
        hashes[digest].append(name)
    for name in sorted(set(actual) - seen):
        errors.append(f"Mídia sem entrada no inventário: {name}")
    for group in hashes.values():
        if len(set(group)) > 1:
            warnings.append("Duplicata binária preservada: " + ", ".join(sorted(set(group))))
    if not errors:
        try:
            if (root / CATALOG).read_text(encoding="utf-8") != catalog_text(entries):
                errors.append(f"{CATALOG}: catálogo desatualizado")
        except (OSError, UnicodeError) as error:
            errors.append(f"{CATALOG}: {error}")
    return errors, warnings


def check_repository(root):
    errors, warnings = check_inventory(root)
    return check_references(root) + errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Verificar referências locais e integridade das mídias.")
    parser.add_argument("--update-inventory", action="store_true", help="Aceitar mídias atuais e regenerar inventário/catálogo após revisão intencional.")
    args = parser.parse_args()
    if args.update_inventory:
        try:
            update_inventory(ROOT)
        except (OSError, ValueError, KeyError, TypeError) as error:
            print(f"ERRO: não foi possível atualizar o inventário: {error}")
            return 1
        print("Inventário e catálogo atualizados. Revise o diff antes de aceitar os novos hashes.")
    errors, warnings = check_repository(ROOT)
    for warning in warnings:
        print(f"AVISO: {warning}")
    for error in errors:
        print(f"ERRO: {error}")
    if errors:
        print(f"Verificação falhou: {len(errors)} erro(s).")
        return 1
    print(f"OK: referências locais, catálogo e {len(media_paths(ROOT))} mídias verificados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
