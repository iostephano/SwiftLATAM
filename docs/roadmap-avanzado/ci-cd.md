---
sidebar_position: 1
title: Ci Cd
---

# CI/CD para Desarrollo iOS

## ¿Qué es CI/CD?

**CI/CD** (Integración Continua / Entrega Continua) es un conjunto de prácticas que automatizan el proceso de compilar, probar y distribuir tu aplicación iOS cada vez que realizas cambios en el código. En lugar de hacer builds manuales, firmar certificados a mano y subir archivos `.ipa` manualmente a App Store Connect, un pipeline de CI/CD se encarga de todo esto por ti.

- **CI (Continuous Integration):** Cada push o pull request dispara automáticamente la compilación y ejecución de tests.
- **CD (Continuous Delivery/Deployment):** Una vez que los tests pasan, la app se empaqueta y distribuye automáticamente a TestFlight, App Store u otras plataformas de distribución.

## ¿Por qué es crucial para un dev iOS en LATAM?

En el ecosistema latinoamericano de desarrollo iOS, CI/CD resuelve problemas muy concretos:

1. **Equipos distribuidos:** Es común trabajar con equipos remotos entre México, Colombia, Argentina, Chile y otros países. CI/CD garantiza que el código de todos se integre correctamente sin depender de "la máquina de Juan".

2. **Reducción de costos:** Automatizar procesos reduce horas de trabajo manual. Para startups y empresas LATAM con presupuestos ajustados, esto es crítico.

3. **Consistencia en builds:** Elimina el clásico "en mi máquina sí compila". El pipeline es el único entorno de verdad.

4. **Velocidad de entrega:** El mercado móvil en Latinoamérica crece rápidamente. Poder entregar actualizaciones semanales en lugar de mensuales marca la diferencia competitiva.

5. **Profesionalización del proceso:** Muchas empresas LATAM buscan developers que dominen CI/CD. Es un diferenciador real en entrevistas técnicas.

## Herramientas principales para CI/CD en iOS

| Herramienta | Tipo | Costo | Ideal para |
|---|---|---|---|
| **GitHub Actions** | Cloud | Gratis (con límites) | Proyectos en GitHub |
| **Bitrise** | Cloud | Free tier generoso | Equipos mobile-first |
| **Xcode Cloud** | Cloud (Apple) | 25 hrs/mes gratis | Integración nativa Apple |
| **Fastlane** | Local/CI | Open source | Automatización de tareas |
| **GitLab CI** | Cloud/Self-hosted | Free tier | Empresas con GitLab |
| **CircleCI** | Cloud | Free tier | Equipos medianos |
| **Jenkins** | Self-hosted | Open source | Control total |

## Fastlane: La base de todo pipeline iOS

**Fastlane** es la herramienta más utilizada en el ecosistema iOS para automatizar tareas repetitivas. Casi todos los servicios de CI/CD lo integran.

### Instalación

```bash
# Instalar con Homebrew (recomendado)
brew install fastlane

# O con RubyGems
sudo gem install fastlane -NV
```

### Inicialización en tu proyecto

```bash
cd tu-proyecto-ios
fastlane init
```

### Estructura de archivos

```
tu-proyecto-ios/
├── fastlane/
│   ├── Appfile        # Configuración de la app (bundle ID, Apple ID)
│   ├── Fastfile       # Definición de lanes (acciones automatizadas)
│   ├── Matchfile      # Configuración de certificados (si usas match)
│   └── Pluginfile     # Plugins adicionales
```

### Appfile básico

```ruby
# fastlane/Appfile
app_identifier("com.miempresa.miapp")
apple_id("developer@miempresa.com")
team_id("ABC123DEF4")

# Para App Store Connect
itc_team_id("123456789")
```

### Fastfile con lanes esenciales

```ruby
# fastlane/Fastfile

default_platform(:ios)

platform :ios do

  # ==========================================
  # LANE: Tests
  # Ejecuta todos los tests unitarios y UI
  # ==========================================
  desc "Ejecutar todos los tests"
  lane :tests do
    scan(
      project: "MiApp.xcodeproj",
      scheme: "MiApp",
      devices: ["iPhone 15"],
      code_coverage: true,
      output_directory: "./fastlane/test_output",
      output_types: "html,junit"
    )
  end

  # ==========================================
  # LANE: Beta (TestFlight)
  # Compila y sube a TestFlight
  # ==========================================
  desc "Subir nueva build a TestFlight"
  lane :beta do
    # Incrementar el número de build automáticamente
    increment_build_number(
      build_number: latest_testflight_build_number + 1
    )

    # Gestionar certificados con match
    match(type: "appstore", readonly: true)

    # Compilar la app
    build_app(
      project: "MiApp.xcodeproj",
      scheme: "MiApp",
      export_method: "app-store",
      output_directory: "./build",
      output_name: "MiApp.ipa"
    )

    # Subir a TestFlight
    upload_to_testflight(
      skip_waiting_for_build_processing: true,
      changelog: "Nueva build automática desde CI/CD"
    )

    # Notificar al equipo via Slack
    slack(
      message: "✅ Nueva build subida a TestFlight",
      slack_url: ENV["SLACK_WEBHOOK_URL"],
      default_payloads: [:git_branch, :git_author]
    )
  end

  # ==========================================
  # LANE: Release (App Store)
  # Sube a App Store para revisión
  # ==========================================
  desc "Subir a App Store para review"
  lane :release do
    # Asegurar que estamos en la rama main
    ensure_git_branch(branch: "main")

    # Asegurar que no hay cambios sin commitear
    ensure_git_status_clean

    # Ejecutar tests antes de release
    tests

    match(type: "appstore", readonly: true)

    build_app(
      project: "MiApp.xcodeproj",
      scheme: "MiApp",
      export_method: "app-store"
    )

    upload_to_app_store(
      force: true,
      skip_metadata: false,
      skip_screenshots: true,
      submit_for_review: true,
      automatic_release: false,
      submission_information: {
        add_id_info_uses_idfa: false
      }
    )

    # Crear tag en git
    add_git_tag(tag: "release/#{get_version_number}")
    push_git_tags
  end

  # ==========================================
  # LANE: Lint
  # Análisis estático del código
  # ==========================================
  desc "Ejecutar SwiftLint"
  lane :lint do
    swiftlint(
      mode: :lint,
      config_file: ".swiftlint.yml",
      strict: true,
      raise_if_swiftlint_error: true
    )
  end
end
```

## Gestión de certificados con Match

Uno de los mayores dolores de cabeza en equipos iOS es la gestión de certificados y perfiles de aprovisionamiento. **Fastlane Match** resuelve esto almacenando los certificados de forma encriptada en un repositorio Git privado.

```bash
# Inicializar match
fastlane match init
```

```ruby
# fastlane/Matchfile
git_url("https://github.com/miempresa/certificates.git")
storage_mode("git")

type("appstore")
app_identifier(["com.miempresa.miapp"])

# Encriptar con una contraseña fuerte
# La contraseña se guarda en la variable de entorno MATCH_PASSWORD
```

```bash
# Generar certificados de desarrollo
fastlane match development

# Generar certificados de App Store
fastlane match appstore

# Solo lectura (para CI/CD)
fastlane match appstore --readonly
```

## GitHub Actions: Pipeline completo

GitHub Actions es la opción más popular y accesible. Ofrece **runners macOS** necesarios para compilar apps iOS.

### Workflow para Pull Requests

```yaml
# .github/workflows/ios-ci.yml
name: iOS CI

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: 🔍 SwiftLint
    runs-on: macos-14
    steps:
      - name: Checkout código
        uses: actions/checkout@v4

      - name: Ejecutar SwiftLint
        run: |
          brew install swiftlint
          swiftlint lint --strict --reporter github-actions-logging

  test:
    name: 🧪 Tests
    runs-on: macos-14
    needs: lint
    steps:
      - name: Checkout código
        uses: actions/checkout@v4

      - name: Seleccionar Xcode
        run: sudo xcode-select -s /Applications/Xcode_15.4.app

      - name: Cache de SPM
        uses: actions/cache@v4
        with:
          path: |
            ~/Library/Caches/org.swift.swiftpm
            .build
          key: ${{ runner.os }}-spm-${{ hashFiles('**/Package.resolved') }}
          restore-keys: |
            ${{ runner.os }}-spm-

      - name: Resolver dependencias
        run: |
          xcodebuild -resolvePackageDependencies \
            -project MiApp.xcodeproj \
            -scheme MiApp

      - name: Ejecutar tests
        run: |
          xcodebuild test \
            -project MiApp.xcodeproj \
            -scheme MiApp \
            -destination 'platform=iOS Simulator,name=iPhone 15,OS=17.5' \
            -enableCodeCoverage YES \
            -resultBundlePath TestResults.xcresult \
            | xcpretty --report junit

      - name: Subir resultados de tests
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: TestResults.xcresult

  build:
    name: 🔨 Build
    runs-on: macos-14
    needs: test
    steps:
      - name: Checkout código
        uses: actions/checkout@v4

      - name: Seleccionar Xcode
        run: sudo xcode-select -s /Applications/Xcode_15.4.app

      - name: Compilar app
        run: |
          xcodebuild build \
            -project MiApp.xcodeproj \
            -scheme MiApp \
            -destination 'generic/platform=iOS' \
            -configuration Release \
            CODE_SIGN_IDENTITY="" \
            CODE_SIGNING_REQUIRED=NO \
            | xcpretty
```

### Workflow para deploy a TestFlight

```yaml
# .github/workflows/ios-testflight.yml
name: iOS Deploy TestFlight

on:
  push:
    branches: [main]

jobs:
  deploy:
    name: 🚀 Deploy a TestFlight
    runs-on: macos-14
    timeout-minutes: 45
    steps:
      - name: Checkout código
        uses: actions/checkout@v4

      - name: Seleccionar Xcode
        run: sudo xcode-select -s /Applications/Xcode_15.4.app

      - name: Instalar Fastlane
        run: brew install fastlane

      - name: Cache de Ruby gems
        uses: actions/cache@v4
        with:
          path: vendor/bundle
          key: ${{ runner.os }}-gems-${{ hashFiles('**/Gemfile.lock') }}

      - name: Configurar Ruby
        run: |
          bundle config path vendor/bundle
          bundle install --jobs 4 --retry 3

      - name: Deploy a TestFlight
        env:
          # Credenciales de App Store Connect
          APP_STORE_CONNECT_API_KEY_ID: ${{ secrets.ASC_KEY_ID }}
          APP_STORE_CONNECT_API_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}
          APP_STORE_CONNECT_API_KEY: ${{ secrets.ASC_API_KEY }}
          # Certificados con Match
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          MATCH_GIT_BASIC_AUTHORIZATION: ${{ secrets.MATCH_GIT_TOKEN }}
          # Notificaciones
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: bundle exec fastlane beta

      - name: Notificar en caso de error
        if: failure()
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          curl -X POST -H 'Content-type: application/json' \
            --data '{"text":"❌ Falló el deploy a TestFlight en rama ${{ github.ref_name }}"}' \
            $SLACK_WEBHOOK_URL
```

## App Store Connect API Key

Para autenticarte en CI/CD sin usar usuario/contraseña (que requeriría 2FA), utiliza una **API Key** de App Store Connect:

1. Ve a [App Store Connect → Users & Access → Keys](https://appstoreconnect.apple.com/access/api)
2. Genera una nueva key con rol **App Manager**
3. Descarga el archivo `.p8`
4. Guarda los valores como secretos en tu repositorio

```ruby
# En tu Fastfile, autenticarte con API Key
lane :beta do
  api_key = app_store_connect_api_key(
    key_id: ENV["APP_STORE_CONNECT_API_KEY_ID"],
    issuer_id: ENV["APP_STORE_CONNECT_API_ISSUER_ID"],
    key_content: ENV["APP_STORE_CONNECT_API_KEY"],
    is_key_content_base64: true
  )

  match(
    type: "appstore",
    api_key: api_key,
    readonly: true
  )

  build_app(scheme: "MiApp")

  upload_to_testflight(api_key: api_key)
end
```

## Xcode Cloud: La opción nativa de Apple

Si prefieres mantenerte dentro del ecosistema Apple, **Xcode Cloud** es una excelente alternativa que se configura directamente desde Xcode.

### Ventajas

- Integración nativa con Xcode y App Store Connect
- No necesitas configurar runners macOS
- 25 horas de cómputo gratis al mes
- Gestión automática de certificados

### Configuración

1. Abre tu proyecto en Xcode
2. Ve a **Product → Xcode Cloud → Create Workflow**
3. Selecciona las acciones y triggers

### Scripts personalizados

Xcode Cloud permite ejecutar scripts en distintas fases del build:

```bash
# ci_scripts/ci_post_clone.sh
#!/bin/sh

# Se ejecuta después de clonar el repositorio
echo "📦 Instalando dependencias..."

# Instalar herramientas con Homebrew
brew install swiftlint

# Si usas CocoaPods
# pod install

echo "✅ Dependencias instaladas"
```

```bash
# ci_scripts/ci_pre_xcodebuild.sh
#!/bin