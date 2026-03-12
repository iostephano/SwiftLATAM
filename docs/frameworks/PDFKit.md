---
sidebar_position: 1
title: PDFKit
---

# PDFKit

## ¿Qué es PDFKit?

PDFKit es un framework nativo de Apple que permite visualizar, manipular, anotar y generar documentos PDF directamente dentro de aplicaciones iOS y macOS. Introducido originalmente en macOS y posteriormente disponible en iOS a partir de la versión 11, PDFKit proporciona un conjunto completo de clases que abstraen la complejidad del formato PDF, ofreciendo a los desarrolladores una API robusta y de alto nivel para trabajar con este tipo de documentos.

El framework abarca desde la simple visualización de un archivo PDF hasta operaciones avanzadas como la búsqueda de texto, la creación de anotaciones, la extracción de contenido, la manipulación de páginas individuales (insertar, eliminar, reordenar) y la generación programática de documentos completos. PDFKit se integra de forma natural tanto con UIKit como con SwiftUI, lo que lo convierte en la solución preferida cuando se necesita trabajar con PDFs sin depender de bibliotecas de terceros.

Es la elección ideal cuando tu aplicación necesita mostrar manuales, reportes, facturas, contratos o cualquier tipo de documento en formato PDF. Al ser un framework de primera parte, garantiza rendimiento optimizado, compatibilidad con las últimas versiones del sistema operativo y un mantenimiento continuo por parte de Apple. Además, no requiere dependencias externas, lo que reduce el tamaño del binario y simplifica la gestión de paquetes del proyecto.

## Casos de uso principales

- **Visor de documentos PDF**: Implementar un lector completo con navegación por páginas, zoom, búsqueda de texto y marcadores. Ideal para aplicaciones de lectura, educación o gestión documental.

- **Generación de reportes y facturas**: Crear documentos PDF de forma programática a partir de datos dinámicos de la aplicación, como informes financieros, recibos de compra o historiales médicos.

- **Anotaciones y firma de documentos**: Permitir al usuario agregar notas, resaltados, dibujos a mano alzada y firmas digitales sobre documentos PDF existentes, esencial en aplicaciones legales y corporativas.

- **Extracción y búsqueda de texto**: Buscar términos específicos dentro de documentos extensos, extraer contenido textual para indexación o análisis, y permitir la selección y copia de texto.

- **Manipulación de páginas**: Reorganizar, insertar, eliminar o fusionar páginas de uno o varios documentos PDF, útil en aplicaciones de productividad y gestión documental.

- **Previsualización de archivos**: Mostrar vistas previas en miniatura (thumbnails) de documentos PDF dentro de listas, colecciones o galerías de documentos descargados.

## Instalación y configuración

PDFKit es un framework incluido de forma nativa en el SDK de iOS (desde iOS 11) y macOS (desde macOS 10.4), por lo que **no requiere instalación mediante gestores de paquetes** como SPM, CocoaPods o Carthage.

### Import necesario

En cualquier archivo donde necesites utilizar PDFKit, simplemente agrega el import correspondiente:

```swift
import PDFKit
```

### Permisos en Info.plist

PDFKit en sí mismo no requiere permisos especiales. Sin embargo, dependiendo de dónde se obtengan los archivos PDF, podrías necesitar configurar permisos adicionales:

```xml
<!-- Si accedes a archivos desde la galería de fotos o el almacenamiento -->
<key>NSDocumentsFolderUsageDescription</key>
<string>Necesitamos acceso a tus documentos para abrir archivos PDF.</string>

<!-- Si descargas PDFs de internet (App Transport Security) -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
</dict>

<!-- Si usas UIDocumentPickerViewController para seleccionar PDFs -->
<key>LSSupportsOpeningDocumentsInPlace</key>
<true/>
<key>UIFileSharingEnabled</key>
<true/>
```

### Compatibilidad

| Plataforma | Versión mínima |
|-----------|---------------|
| iOS | 11.0+ |
| macOS | 10.4+ |
| Mac Catalyst | 13.0+ |
| visionOS | 1.0+ |

### Configuración en SwiftUI

Para integrar `PDFView` en SwiftUI, necesitarás crear un wrapper con `UIViewRepresentable`, ya que PDFKit está basado en UIKit. Esto se muestra en detalle en los ejemplos posteriores.

## Conceptos clave

### 1. PDFView

Es la clase principal de visualización. Hereda de `UIView` y proporciona toda la interfaz de usuario para mostrar documentos PDF: scroll, zoom, navegación entre páginas y selección de texto. Es el equivalente a un "visor de PDF completo" que puedes integrar directamente en tu jerarquía de vistas.

```swift
let pdfView = PDFView()
pdfView.autoScales = true
pdfView.displayMode = .singlePageContinuous
```

### 2. PDFDocument

Representa un documento PDF completo. Encapsula el archivo y proporciona métodos para acceder a sus páginas, metadatos, buscar texto y realizar operaciones de escritura. Puede crearse desde una URL local, una URL remota o desde datos (`Data`) en memoria.

```swift
// Desde un archivo en el bundle
let url = Bundle.main.url(forResource: "manual", withExtension: "pdf")!
let document = PDFDocument(url: url)

// Desde datos descargados
let document = PDFDocument(data: pdfData)
```

### 3. PDFPage

Representa una página individual dentro de un `PDFDocument`. Cada página tiene sus propias dimensiones, contenido gráfico, texto y anotaciones. Puedes obtener información sobre su tamaño, extraer texto, agregar anotaciones o incluso dibujar contenido personalizado sobreescribiendo su método de renderizado.

### 4. PDFAnnotation

Permite agregar elementos interactivos y visuales sobre las páginas: texto libre, resaltados, subrayados, notas adhesivas, enlaces, formas geométricas, firmas y widgets de formulario. Cada anotación tiene un tipo (`PDFAnnotationSubtype`), una posición (`bounds`) y propiedades visuales configurables.

### 5. PDFSelection

Representa una selección de texto dentro del documento. Se utiliza principalmente en operaciones de búsqueda y selección de contenido. Permite obtener el texto seleccionado, conocer las páginas donde se encuentra y resaltar visualmente los resultados.

### 6. PDFThumbnailView

Vista auxiliar que muestra miniaturas de las páginas del documento. Se puede vincular directamente a un `PDFView` para proporcionar navegación visual rápida, similar a la barra lateral de miniaturas que se ve en Preview de macOS.

## Ejemplo básico

Este ejemplo muestra cómo crear un visor de PDF minimalista que carga un archivo desde el bundle de la aplicación:

```swift
import UIKit
import PDFKit

class BasicPDFViewController: UIViewController {
    
    // MARK: - Propiedades
    
    /// Vista principal para renderizar el documento PDF
    private let pdfView = PDFView()
    
    // MARK: - Ciclo de vida
    
    override func viewDidLoad() {
        super.viewDidLoad()
        configurarPDFView()
        cargarDocumento()
    }
    
    // MARK: - Configuración
    
    private func configurarPDFView() {
        // Añadir PDFView al view controller
        pdfView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(pdfView)
        
        // Configurar constraints para ocupar toda la pantalla
        NSLayoutConstraint.activate([
            pdfView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            pdfView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            pdfView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            pdfView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
        
        // Configurar el comportamiento del visor
        pdfView.autoScales = true                          // Ajustar zoom automáticamente
        pdfView.displayMode = .singlePageContinuous        // Scroll continuo
        pdfView.displayDirection = .vertical               // Desplazamiento vertical
        pdfView.backgroundColor = .systemGroupedBackground // Color de fondo
    }
    
    private func cargarDocumento() {
        // Cargar PDF desde el bundle de la aplicación
        guard let url = Bundle.main.url(forResource: "documento_ejemplo",
                                         withExtension: "pdf") else {
            print("❌ Error: No se encontró el archivo PDF en el bundle")
            return
        }
        
        guard let documento = PDFDocument(url: url) else {
            print("❌ Error: No se pudo crear el PDFDocument desde la URL")
            return
        }
        
        // Asignar el documento al visor
        pdfView.document = documento
        
        // Mostrar información básica del documento
        print("📄 Documento cargado exitosamente")
        print("📖 Número de páginas: \(documento.pageCount)")
        print("🔒 Está encriptado: \(documento.isEncrypted)")
        print("🔓 Está desbloqueado: \(documento.isUnlocked)")
    }
}
```

## Ejemplo intermedio

Este ejemplo implementa un visor de PDF con funcionalidades comunes: búsqueda de texto, navegación entre páginas, anotaciones y barra de miniaturas:

```swift
import UIKit
import PDFKit

// MARK: - Visor PDF con funcionalidades completas

class PDFViewerViewController: UIViewController {
    
    // MARK: - UI Components
    
    private let pdfView = PDFView()
    private let thumbnailView = PDFThumbnailView()
    private let searchBar = UISearchBar()
    private let pageLabel = UILabel()
    
    /// Almacena las selecciones encontradas en la búsqueda
    private var resultadosBusqueda: [PDFSelection] = []
    private var indiceBusquedaActual: Int = 0
    
    // MARK: - Ciclo de vida
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Visor PDF"
        view.backgroundColor = .systemBackground
        
        configurarInterfaz()
        configurarBarraNavegacion()
        configurarNotificaciones()
        cargarDocumento()
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
    
    // MARK: - Configuración de la interfaz
    
    private func configurarInterfaz() {
        // Configurar barra de búsqueda
        searchBar.delegate = self
        searchBar.placeholder = "Buscar en el documento..."
        searchBar.searchBarStyle = .minimal
        searchBar.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(searchBar)
        
        // Configurar vista de miniaturas lateral
        thumbnailView.translatesAutoresizingMaskIntoConstraints = false
        thumbnailView.thumbnailSize = CGSize(width: 40, height: 56)
        thumbnailView.layoutMode = .vertical
        thumbnailView.backgroundColor = .secondarySystemBackground
        view.addSubview(thumbnailView)
        
        // Configurar PDFView principal
        pdfView.translatesAutoresizingMaskIntoConstraints = false
        pdfView.autoScales = true
        pdfView.displayMode = .singlePageContinuous
        pdfView.displayDirection = .vertical
        pdfView.pageShadowsEnabled = true  // Sombras entre páginas
        pdfView.interpolationQuality = .high
        view.addSubview(pdfView)
        
        // Configurar etiqueta de página actual
        pageLabel.translatesAutoresizingMaskIntoConstraints = false
        pageLabel.textAlignment = .center
        pageLabel.font = .monospacedDigitSystemFont(ofSize: 14, weight: .medium)
        pageLabel.textColor = .secondaryLabel
        pageLabel.backgroundColor = .systemBackground.withAlphaComponent(0.9)
        pageLabel.layer.cornerRadius = 8
        pageLabel.clipsToBounds = true
        view.addSubview(pageLabel)
        
        // Vincular miniaturas con el visor PDF
        thumbnailView.pdfView = pdfView
        
        // Layout
        NSLayoutConstraint.activate([
            searchBar.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            searchBar.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            searchBar.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            
            thumbnailView.topAnchor.constraint(equalTo: searchBar.bottomAnchor),
            thumbnailView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            thumbnailView.widthAnchor.constraint(equalToConstant: 60),
            thumbnailView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            pdfView.topAnchor.constraint(equalTo: searchBar.bottomAnchor),
            pdfView.leadingAnchor.constraint(equalTo: thumbnailView.trailingAnchor),
            pdfView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            pdfView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            pageLabel.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor,
                                               constant: -16),
            pageLabel.centerXAnchor.constraint(equalTo: pdfView.centerXAnchor),
            pageLabel.widthAnchor.constraint(greaterThanOrEqualToConstant: 120),
            pageLabel.heightAnchor.constraint(equalToConstant: 32)
        ])
    }
    
    private func configurarBarraNavegacion() {
        // Botón para agregar anotación de resaltado
        let botonResaltado = UIBarButtonItem(
            image: UIImage(systemName: "highlighter"),
            style: .plain,
            target: self,
            action: #selector(agregarResaltado)
        )
        
        // Botón para agregar nota adhesiva
        let botonNota = UIBarButtonItem(
            image: UIImage(systemName: "note.text.badge.plus"),
            style: .plain,
            target: self,
            action: #selector(agregarNota)
        )
        
        // Botón para compartir el PDF
        let botonCompartir = UIBarButtonItem(
            barButtonSystemItem: .action,
            target: self,
            action: #selector(compartirPDF)
        )
        
        navigationItem.rightBarButtonItems = [botonCompartir, botonNota, botonResaltado]
    }
    
    private func configurarNotificaciones() {
        // Observar cambios de página para actualizar la etiqueta
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(paginaCambio),
            name: .PDFViewPageChanged,
            object: pdfView
        )
    }
    
    // MARK: - Carga del documento
    
    private func cargarDocumento() {
        guard let url = Bundle.main.url(for