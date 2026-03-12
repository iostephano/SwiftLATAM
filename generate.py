#!/usr/bin/env python3
"""
SwiftLATAM - Script Maestro de Generación de Contenido
Genera contenido completo para todos los docs usando la API de Claude.
Uso:
  python generate.py --section frameworks --all
  python generate.py --section frameworks --name SwiftUI
  python generate.py --all-sections
"""

import os
import json
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_URL = "https://api.anthropic.com/v1/messages"
MODEL   = "claude-opus-4-6"

# Todos los frameworks de Apple
FRAMEWORKS = [
    "ARKit", "AVFoundation", "Accessibility", "AppKit", "BackgroundTasks",
    "CareKit", "CloudKit", "Combine", "Contacts", "ContactsUI",
    "CoreAnimation", "CoreAudio", "CoreBluetooth", "CoreData", "CoreGraphics",
    "CoreImage", "CoreLocation", "CoreML", "CoreMotion", "CoreText",
    "CreateML", "CryptoKit", "EventKit", "EventKitUI", "FileManager",
    "Foundation", "GameplayKit", "HealthKit", "ImageIO", "KeychainServices",
    "LocalAuthentication", "MapKit", "Metal", "MetalKit", "ModelIO",
    "MultipeerConnectivity", "NaturalLanguage", "Network", "PDFKit", "PassKit",
    "PencilKit", "PhotoKit", "Photos", "QuickLook", "RealityKit", "ReplayKit",
    "SceneKit", "ScreenCaptureKit", "SoundAnalysis", "Speech", "SpriteKit",
    "StoreKit", "Swift", "SwiftData", "SwiftUI", "UIKit", "URLSession",
    "UniformTypeIdentifiers", "Vision", "VisionKit", "XCTest"
]

# Secciones con sus archivos intro
SECTIONS = {
    "roadmap-basico": {
        "title": "Roadmap Básico",
        "description": "La ruta de entrada para cualquier desarrollador iOS. Desde cero hasta tu primera app publicada.",
        "topics": [
            "fundamentos-swift", "xcode-setup", "uikit-basico", "swiftui-intro",
            "navegacion", "manejo-de-datos", "networking-basico", "publicar-app"
        ]
    },
    "roadmap-avanzado": {
        "title": "Roadmap Avanzado",
        "description": "Para desarrolladores con base sólida que quieren llevar sus apps al siguiente nivel.",
        "topics": [
            "arquitectura-clean", "concurrencia-avanzada", "performance",
            "testing-avanzado", "ci-cd", "seguridad", "accesibilidad-avanzada"
        ]
    },
    "apple-ecosystem": {
        "title": "Apple Ecosystem Professional",
        "description": "Más allá del iPhone: iPad, Mac, Watch, Vision Pro y cómo conectarlos todos.",
        "topics": [
            "ipad-development", "macos-catalyst", "watchos", "tvos", "visionos",
            "universal-apps", "handoff-continuity"
        ]
    },
    "especializaciones": {
        "title": "Especializaciones",
        "description": "Rutas especializadas para nichos específicos del ecosistema Apple.",
        "topics": [
            "fintech-ios", "healthtech-ios", "ar-vr", "machine-learning",
            "games-development", "enterprise-ios"
        ]
    },
    "product-skills": {
        "title": "Product + Human Skills",
        "description": "Las habilidades que diferencian a un buen desarrollador de un gran profesional.",
        "topics": [
            "product-thinking", "comunicacion-tecnica", "estimacion-proyectos",
            "code-review", "mentoria", "open-source", "portfolio"
        ]
    },
    "demos": {
        "title": "Demos",
        "description": "Proyectos prácticos y demos funcionales para aprender haciendo.",
        "topics": [
            "demo-fintech-app", "demo-health-tracker", "demo-ar-experience",
            "demo-ml-vision", "demo-widget", "demo-watch-app"
        ]
    },
    "framework-mastery": {
        "title": "Framework Mastery",
        "description": "Dominio profundo de un framework específico de Apple de principio a fin.",
        "topics": [
            "swiftui-mastery", "uikit-mastery", "combine-mastery",
            "coredata-mastery", "swiftdata-mastery"
        ]
    },
}

# ─── PROMPTS ──────────────────────────────────────────────────────────────────

def prompt_framework(name: str) -> str:
    return f"""Eres un experto iOS developer hispanohablante. Genera documentación técnica completa en ESPAÑOL para el framework de Apple: **{name}**

El formato debe ser Markdown para Docusaurus con este frontmatter exacto al inicio:
---
sidebar_position: 1
title: {name}
---

Luego genera el contenido con esta estructura EXACTA:

# {name}

## ¿Qué es {name}?
[Descripción clara en 2-3 párrafos de qué es, para qué sirve y cuándo usarlo]

## Casos de uso principales
[Lista de 4-6 casos de uso reales con descripción breve]

## Instalación y configuración
[Cómo agregar al proyecto, permisos en Info.plist si aplica, imports necesarios]

## Conceptos clave
[Los 4-6 conceptos fundamentales que todo dev debe conocer, con explicación]

## Ejemplo básico
```swift
// Código Swift funcional y comentado que muestra el uso más básico
```

## Ejemplo intermedio
```swift
// Código Swift más completo mostrando un caso de uso real
```

## Ejemplo avanzado
```swift
// Código Swift con patrón de arquitectura limpia (MVVM o similar)
```

## Integración con otros frameworks
[Cómo {name} se integra con SwiftUI, UIKit, Combine u otros frameworks relevantes]

## Buenas prácticas
[5-7 buenas prácticas específicas para {name}]

## Errores comunes
[3-5 errores típicos y cómo evitarlos]

## Recursos adicionales
[Links a documentación oficial de Apple y recursos recomendados]

IMPORTANTE:
- Todo el texto explicativo en ESPAÑOL
- El código en Swift, bien comentado
- Ejemplos realistas y útiles para proyectos reales
- Mínimo 800 palabras de contenido
"""

def prompt_section_topic(section: str, topic: str, section_info: dict) -> str:
    return f"""Eres un experto iOS developer hispanohablante. Genera contenido técnico completo en ESPAÑOL para la sección **{section_info['title']}**, tema: **{topic}**

El formato debe ser Markdown para Docusaurus con este frontmatter exacto:
---
sidebar_position: 1
title: {topic.replace('-', ' ').title()}
---

Genera contenido educativo, práctico y bien estructurado sobre este tema en el contexto del desarrollo iOS en Latinoamérica.

Incluye:
- Explicación clara del concepto
- Por qué es importante para un dev iOS en LATAM
- Ejemplos prácticos con código Swift cuando sea relevante
- Pasos accionables
- Recursos recomendados

Mínimo 600 palabras. Todo en ESPAÑOL excepto el código.
"""

# ─── API CLIENT ───────────────────────────────────────────────────────────────

def call_claude(prompt: str, retries: int = 3) -> str:
    if not API_KEY:
        raise ValueError("❌ ANTHROPIC_API_KEY no está configurada. Ejecuta: export ANTHROPIC_API_KEY='tu-key'")

    payload = json.dumps({
        "model": MODEL,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01"
    }

    for attempt in range(retries):
        try:
            req = urllib.request.Request(API_URL, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["content"][0]["text"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            if e.code == 429:
                wait = 30 * (attempt + 1)
                print(f"  ⏳ Rate limit, esperando {wait}s...")
                time.sleep(wait)
            else:
                raise Exception(f"HTTP {e.code}: {error_body}")
        except Exception as e:
            if attempt < retries - 1:
                print(f"  ⚠️  Error intento {attempt+1}: {e}. Reintentando...")
                time.sleep(5)
            else:
                raise

    raise Exception("❌ Agotados todos los reintentos")

# ─── FILE HELPERS ─────────────────────────────────────────────────────────────

def is_empty(filepath: Path) -> bool:
    """Retorna True si el archivo tiene menos de 200 caracteres (casi vacío)"""
    if not filepath.exists():
        return True
    return filepath.stat().st_size < 200

def write_file(filepath: Path, content: str):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")

# ─── GENERATORS ───────────────────────────────────────────────────────────────

def generate_framework(name: str, docs_path: Path, force: bool = False):
    filepath = docs_path / "frameworks" / f"{name}.md"
    
    if not force and not is_empty(filepath):
        print(f"  ⏭️  {name} ya tiene contenido, saltando...")
        return False

    print(f"  🔨 Generando {name}...")
    try:
        content = call_claude(prompt_framework(name))
        write_file(filepath, content)
        print(f"  ✅ {name} generado ({len(content)} chars)")
        time.sleep(2)  # Rate limit safety
        return True
    except Exception as e:
        print(f"  ❌ Error en {name}: {e}")
        return False

def generate_section_topic(section: str, topic: str, section_info: dict, docs_path: Path, force: bool = False):
    filepath = docs_path / section / f"{topic}.md"
    
    if not force and not is_empty(filepath):
        print(f"  ⏭️  {section}/{topic} ya tiene contenido, saltando...")
        return False

    print(f"  🔨 Generando {section}/{topic}...")
    try:
        content = call_claude(prompt_section_topic(section, topic, section_info))
        write_file(filepath, content)
        print(f"  ✅ {section}/{topic} generado ({len(content)} chars)")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"  ❌ Error en {section}/{topic}: {e}")
        return False

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SwiftLATAM Content Generator")
    parser.add_argument("--section",       help="Sección a generar: frameworks, roadmap-basico, etc.")
    parser.add_argument("--name",          help="Nombre específico (framework o topic)")
    parser.add_argument("--all",           action="store_true", help="Generar todo en la sección indicada")
    parser.add_argument("--all-sections",  action="store_true", help="Generar TODO el sitio")
    parser.add_argument("--force",         action="store_true", help="Sobreescribir archivos existentes")
    parser.add_argument("--docs",          default="docs",      help="Ruta a la carpeta docs (default: docs)")
    parser.add_argument("--dry-run",       action="store_true", help="Ver qué se generaría sin ejecutar")
    args = parser.parse_args()

    docs_path = Path(args.docs)
    if not docs_path.exists():
        print(f"❌ No se encontró la carpeta: {docs_path}")
        print("   Asegúrate de ejecutar este script desde la raíz de SwiftLATAM")
        return

    print("━" * 60)
    print("🚀 SwiftLATAM Content Generator")
    print("━" * 60)

    if not API_KEY and not args.dry_run:
        print("❌ Falta configurar: export ANTHROPIC_API_KEY='sk-ant-...'")
        return

    generated = 0
    skipped   = 0

    # ── Caso: un framework específico
    if args.section == "frameworks" and args.name:
        if args.dry_run:
            print(f"[DRY RUN] Generaría: frameworks/{args.name}.md")
        else:
            ok = generate_framework(args.name, docs_path, args.force)
            generated += 1 if ok else 0

    # ── Caso: todos los frameworks
    elif args.section == "frameworks" and args.all:
        print(f"\n📦 Frameworks ({len(FRAMEWORKS)} total)\n")
        for fw in FRAMEWORKS:
            if args.dry_run:
                filepath = docs_path / "frameworks" / f"{fw}.md"
                status = "VACÍO" if is_empty(filepath) else "tiene contenido"
                print(f"  [{status}] {fw}")
            else:
                ok = generate_framework(fw, docs_path, args.force)
                if ok: generated += 1
                else:  skipped  += 1

    # ── Caso: una sección específica
    elif args.section and args.section in SECTIONS and args.all:
        info = SECTIONS[args.section]
        print(f"\n📂 Sección: {info['title']} ({len(info['topics'])} topics)\n")
        for topic in info["topics"]:
            if args.dry_run:
                print(f"  [pendiente] {args.section}/{topic}")
            else:
                ok = generate_section_topic(args.section, topic, info, docs_path, args.force)
                if ok: generated += 1
                else:  skipped  += 1

    # ── Caso: todo el sitio
    elif args.all_sections:
        print("\n🌐 Generando SITIO COMPLETO\n")

        # Frameworks
        print(f"📦 Frameworks ({len(FRAMEWORKS)})\n")
        for fw in FRAMEWORKS:
            if args.dry_run:
                filepath = docs_path / "frameworks" / f"{fw}.md"
                status = "VACÍO" if is_empty(filepath) else "OK"
                print(f"  [{status}] {fw}")
            else:
                ok = generate_framework(fw, docs_path, args.force)
                if ok: generated += 1
                else:  skipped  += 1

        # Secciones
        for section, info in SECTIONS.items():
            print(f"\n📂 {info['title']}\n")
            for topic in info["topics"]:
                if args.dry_run:
                    print(f"  [pendiente] {section}/{topic}")
                else:
                    ok = generate_section_topic(section, topic, info, docs_path, args.force)
                    if ok: generated += 1
                    else:  skipped  += 1

    else:
        parser.print_help()
        print("\n📖 Ejemplos de uso:")
        print("  python generate.py --section frameworks --name SwiftUI")
        print("  python generate.py --section frameworks --all")
        print("  python generate.py --section roadmap-basico --all")
        print("  python generate.py --all-sections")
        print("  python generate.py --all-sections --dry-run   # ver sin ejecutar")
        return

    # ── Resumen
    if not args.dry_run:
        print("\n" + "━" * 60)
        print(f"✅ Generados: {generated} archivos")
        print(f"⏭️  Saltados:  {skipped} archivos (ya tenían contenido)")
        print("━" * 60)
        if generated > 0:
            print("\n🚀 Listo para publicar:")
            print("   git add .")
            print('   git commit -m "feat: contenido generado automáticamente"')
            print("   git push")
    else:
        print("\n[DRY RUN completado - no se escribió ningún archivo]")

if __name__ == "__main__":
    main()
