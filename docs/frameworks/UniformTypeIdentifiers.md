---
sidebar_position: 1
title: UniformTypeIdentifiers
---

# UniformTypeIdentifiers

## ¿Qué es UniformTypeIdentifiers?

**UniformTypeIdentifiers** es el framework moderno de Apple que proporciona un sistema unificado y tipado para identificar tipos de contenido en todas las plataformas del ecosistema Apple. Introducido en iOS 14 y macOS 11, reemplaza al antiguo sistema basado en cadenas de texto (`kUTType...`) definido en `MobileCoreServices` y `CoreServices`, ofreciendo una API Swift-first con seguridad de tipos en tiempo de compilación y autocompletado completo en Xcode.

El sistema de **Uniform Type Identifiers (UTIs)** funciona como una jerarquía de tipos donde cada tipo de contenido tiene un identificador único (por ejemplo, `public.jpeg`, `public.plain-text`, `com.adobe.pdf`). Esta jerarquía permite que un tipo herede de otros: una imagen JPEG es a la vez una imagen, un dato binario y un contenido genérico. Este concepto de **conformidad** es fundamental porque permite escribir código que acepta "cualquier imagen" sin tener que enumerar cada formato específico.

Este framework es esencial cuando tu aplicación necesita trabajar con archivos, compartir contenido, implementar Drag & Drop, utilizar selectores de documentos, gestionar el portapapeles o declarar tipos de archivo personalizados. Si tu app interactúa de cualquier forma con el sistema de archivos o con el intercambio de datos entre aplicaciones, UniformTypeIdentifiers será una pieza central de tu arquitectura.

## Casos de uso principales

- **Selectores de documentos y archivos**: Configurar `UIDocumentPickerViewController` o el modificador `.fileImporter()` de SwiftUI para filtrar por tipos de archivo específicos (PDF, imágenes, hojas de cálculo, etc.).

- **Drag & Drop**: Definir qué tipos de contenido puede arrastrar y soltar tu aplicación, tanto como origen como destino, mediante `NSItemProvider` y la conformidad de tipos.

- **Compartir contenido (Share Sheet)**: Especificar los tipos de datos que tu extensión de compartir acepta o que tu aplicación puede exportar a otras apps.

- **Portapapeles (UIPasteboard / NSPasteboard)**: Leer y escribir datos en el portapapeles con identificación precisa del tipo de contenido, permitiendo que otras apps interpreten correctamente la información.

- **Tipos de archivo personalizados**: Declarar formatos propietarios de tu aplicación (por ejemplo, `.myapp`) que el sistema operativo reconoce, asocia con tu app y muestra con iconos personalizados.

- **Validación y filtrado de archivos**: Verificar programáticamente si un archivo o URL corresponde a un tipo esperado antes de procesarlo, evitando errores en tiempo de ejecución.

## Instalación y configuración

### Agregar el framework al proyecto

`UniformTypeIdentifiers` está incluido en el SDK de todas las plataformas Apple a partir de iOS 14, macOS 11, tvOS 14 y watchOS 7. No requiere instalación mediante CocoaPods, SPM ni ningún gestor de dependencias externo.

### Import necesario

```swift
import UniformTypeIdentifiers
```

### Declaración de tipos personalizados en Info.plist

Si necesitas declarar tipos de archivo propietarios, debes configurar las claves `UTExportedTypeDeclarations` o `UTImportedTypeDeclarations` en tu archivo `Info.plist`:

```xml
<key>UTExportedTypeDeclarations</key>
<array>
    <dict>
        <key>UTTypeIdentifier</key>
        <string>com.miempresa.miapp.proyecto</string>
        <key>UTTypeDescription</key>
        <string>Archivo de Proyecto MiApp</string>
        <key>UTTypeConformsTo</key>
        <array>
            <string>public.data</string>
            <string>public.content</string>
        </array>
        <key>UTTypeTagSpecification</key>
        <dict>
            <key>public.filename-extension</key>
            <array>
                <string>miapp</string>
            </array>
            <key>public.mime-type</key>
            <string>application/x-miapp-project</string>
        </dict>
    </dict>
</array>
```

### Requisitos mínimos de despliegue

| Plataforma | Versión mínima |
|-----------|---------------|
| iOS       | 14.0          |
| macOS     | 11.0          |
| tvOS      | 14.0          |
| watchOS   | 7.0           |
| visionOS  | 1.0           |

## Conceptos clave

### 1. UTType — La estructura central

`UTType` es una estructura (`struct`) que representa un tipo de contenido. Apple proporciona cientos de tipos predefinidos como constantes estáticas: `UTType.pdf`, `UTType.jpeg`, `UTType.plainText`, `UTType.movie`, etc. Cada instancia contiene un identificador único, una descripción legible, extensiones de archivo asociadas y tipos MIME.

### 2. Conformidad (Conformance)

La conformidad es la relación jerárquica entre tipos. Un tipo **conforma** a otro cuando es una especialización del mismo. Por ejemplo, `UTType.jpeg` conforma a `UTType.image`, que a su vez conforma a `UTType.data`. Esto permite escribir filtros genéricos: aceptar `.image` automáticamente acepta JPEG, PNG, HEIC, TIFF y cualquier otro formato de imagen.

### 3. Tipos declarados vs. dinámicos

Los **tipos declarados** son aquellos registrados en el sistema (por Apple o por tu Info.plist). Los **tipos dinámicos** se crean en tiempo de ejecución cuando el sistema encuentra un archivo con una extensión desconocida. Estos tipos dinámicos tienen identificadores con el prefijo `dyn.` y ofrecen funcionalidad limitada.

### 4. Supertypes y Subtypes

Cada `UTType` puede exponer sus `supertypes` (tipos padre de los que hereda) y puedes consultar si un tipo es subtipo de otro. Esta navegación bidireccional de la jerarquía es fundamental para implementar lógica de filtrado flexible.

### 5. Tag Specification

El **tag specification** es el mecanismo que mapea un UTType a sus representaciones concretas: extensiones de archivo (`.pdf`, `.txt`), tipos MIME (`application/pdf`, `text/plain`) y otros esquemas de identificación del sistema operativo.

### 6. UTType como Identifiable y Hashable

`UTType` conforma a `Identifiable`, `Hashable`, `Equatable`, `Sendable` y `Codable`, lo que lo hace perfecto para usarlo en colecciones, como identificador en listas de SwiftUI, en contextos concurrentes y para serialización.

## Ejemplo básico

```swift
import UniformTypeIdentifiers

// ==============================================
// Ejemplo básico: Exploración de tipos UTType
// ==============================================

// Acceder a tipos predefinidos del sistema
let tipoPDF = UTType.pdf
let tipoJPEG = UTType.jpeg
let tipoTexto = UTType.plainText

// Obtener información descriptiva de un tipo
print("Identificador: \(tipoPDF.identifier)")
// → "com.adobe.pdf"

print("Descripción: \(tipoPDF.localizedDescription ?? "Sin descripción")")
// → "Documento PDF"

print("Extensión preferida: \(tipoPDF.preferredFilenameExtension ?? "N/A")")
// → "pdf"

print("Tipo MIME preferido: \(tipoPDF.preferredMIMEType ?? "N/A")")
// → "application/pdf"

// -----------------------------------------------
// Verificar conformidad (jerarquía de tipos)
// -----------------------------------------------

// ¿Es JPEG una imagen?
let esImagen = tipoJPEG.conforms(to: .image)
print("¿JPEG es imagen? \(esImagen)") // → true

// ¿Es JPEG un dato público?
let esDato = tipoJPEG.conforms(to: .data)
print("¿JPEG es data? \(esDato)") // → true

// ¿Es JPEG un video?
let esVideo = tipoJPEG.conforms(to: .movie)
print("¿JPEG es video? \(esVideo)") // → false

// -----------------------------------------------
// Crear un UTType desde una extensión de archivo
// -----------------------------------------------
if let tipoDesdeExtension = UTType(filenameExtension: "png") {
    print("Tipo para .png: \(tipoDesdeExtension.identifier)")
    // → "public.png"
    print("¿Es imagen? \(tipoDesdeExtension.conforms(to: .image))")
    // → true
}

// Crear un UTType desde un tipo MIME
if let tipoDesdeMIME = UTType(mimeType: "application/json") {
    print("Tipo para application/json: \(tipoDesdeMIME.identifier)")
    // → "public.json"
}

// -----------------------------------------------
// Obtener todas las extensiones asociadas a un tipo
// -----------------------------------------------
if let tags = UTType.image.tags[.filenameExtension] {
    print("Extensiones de imagen conocidas: \(tags)")
}
```

## Ejemplo intermedio

```swift
import SwiftUI
import UniformTypeIdentifiers

// ================================================================
// Ejemplo intermedio: Selector de archivos con filtros dinámicos
// y vista previa del tipo de archivo seleccionado
// ================================================================

/// Modelo que representa un archivo seleccionado por el usuario
struct ArchivoSeleccionado: Identifiable {
    let id = UUID()
    let url: URL
    let nombre: String
    let tipo: UTType
    let tamaño: Int64
    
    /// Categoría legible del archivo basada en conformidad UTType
    var categoria: String {
        if tipo.conforms(to: .image) { return "🖼️ Imagen" }
        if tipo.conforms(to: .movie) { return "🎬 Video" }
        if tipo.conforms(to: .audio) { return "🎵 Audio" }
        if tipo.conforms(to: .pdf) { return "📄 PDF" }
        if tipo.conforms(to: .spreadsheet) { return "📊 Hoja de cálculo" }
        if tipo.conforms(to: .presentation) { return "📽️ Presentación" }
        if tipo.conforms(to: .sourceCode) { return "💻 Código fuente" }
        if tipo.conforms(to: .text) { return "📝 Texto" }
        if tipo.conforms(to: .archive) { return "🗜️ Archivo comprimido" }
        return "📎 Otro"
    }
    
    /// Descripción legible del tipo de archivo
    var descripcionTipo: String {
        tipo.localizedDescription ?? tipo.identifier
    }
}

/// Enumeración de filtros predefinidos para el selector de archivos
enum FiltroArchivo: String, CaseIterable, Identifiable {
    case todos = "Todos"
    case imagenes = "Imágenes"
    case documentos = "Documentos"
    case multimedia = "Multimedia"
    case codigo = "Código"
    
    var id: String { rawValue }
    
    /// Convierte el filtro a un array de UTType para el file importer
    var tiposPermitidos: [UTType] {
        switch self {
        case .todos:
            return [.item]
        case .imagenes:
            return [.image]
        case .documentos:
            return [.pdf, .plainText, .rtf, .spreadsheet, .presentation]
        case .multimedia:
            return [.movie, .audio, .image]
        case .codigo:
            return [.sourceCode, .json, .xml, .yaml]
        }
    }
}

// -----------------------------------------------
// Vista principal con selector de archivos
// -----------------------------------------------
struct SelectorArchivosView: View {
    @State private var mostrarSelector = false
    @State private var filtroActual: FiltroArchivo = .todos
    @State private var archivosSeleccionados: [ArchivoSeleccionado] = []
    @State private var errorMensaje: String?
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                // Selector de filtro
                Picker("Tipo de archivo", selection: $filtroActual) {
                    ForEach(FiltroArchivo.allCases) { filtro in
                        Text(filtro.rawValue).tag(filtro)
                    }
                }
                .pickerStyle(.segmented)
                .padding(.horizontal)
                
                // Botón para abrir el selector
                Button {
                    mostrarSelector = true
                } label: {
                    Label("Seleccionar archivos", systemImage: "doc.badge.plus")
                        .font(.headline)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(.blue)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                }
                .padding(.horizontal)
                
                // Lista de archivos seleccionados
                if archivosSeleccionados.isEmpty {
                    ContentUnavailableView(
                        "Sin archivos",
                        systemImage: "folder.badge.questionmark",
                        description: Text("Selecciona archivos usando el botón superior")
                    )
                } else {
                    List(archivosSeleccionados) { archivo in
                        VStack(alignment: .leading, spacing: 4) {
                            Text(archivo.nombre)
                                .font(.headline)
                            
                            HStack {
                                Text(archivo.categoria)
                                Spacer()
                                Text(archivo.descripcionTipo)
                                    .foregroundStyle(.secondary)
                            }
                            .font(.caption)
                            
                            Text("Extensión: .\(archivo.tipo.preferredFilenameExtension ?? "desconocida")")
                                .font(.caption2)
                                .foregroundStyle(.tertiary)
                        }
                        .padding(.vertical, 4)
                    }
                }
            }
            .navigationTitle("Gestor de Archivos")
            // Modificador fileImporter de SwiftUI con tipos UTType
            .fileImporter(
                isPresented: $mostrarSelector,
                allowedContentTypes: filtroActual.tiposPermitidos,
                allowsMultipleSelection: true
            ) { resultado in
                procesarResultado(resultado)
            }
            .alert("Error", isPresented: .constant(errorMensaje != nil)) {
                Button("OK") { errorMensaje = nil }
            } message: {
                Text(errorMensaje ?? "")
            }
        }
    }
    
    /// Procesa el resultado del selector de archivos
    private func procesarResultado(_ resultado: Result<[URL], Error>) {
        switch resultado {
        case .success(let urls):
            archivosSeleccionados = urls.compactMap { url in
                // Obtener acceso seguro al recurso
                guard url.startAccessingSecurityScopedResource() else {
                    return nil
                }
                defer { url.stopAccessingSecurityScopedResource() }
                
                // Determinar el tipo UTType desde la extensión del archivo
                let tipo = UTType(filenameExtension: url.pathExtension) ?? .data
                
                // Obtener el tamaño del archivo
                let tamaño = (try? FileManager.default
                    .attributesOfItem(atPath: url.path)[.size] as? Int64) ?? 0
                
                return ArchivoSeleccionado(
                    url: url,
                    nombre: url.lastPathComponent,