---
sidebar_position: 1
title: QuickLook
---

# QuickLook

## ¿Qué es QuickLook?

QuickLook es un framework de Apple que permite previsualizar una amplia variedad de tipos de archivos directamente dentro de tu aplicación iOS, macOS, iPadOS o visionOS sin necesidad de implementar visualizadores personalizados para cada formato. Soporta de forma nativa documentos PDF, imágenes (JPEG, PNG, HEIC, RAW), archivos de Office (Word, Excel, PowerPoint), archivos de iWork (Pages, Numbers, Keynote), modelos 3D (USDZ, Reality), archivos de texto, CSV, RTF, y muchos más formatos.

El framework proporciona una experiencia de usuario consistente con el resto del sistema operativo, incluyendo gestos de zoom, navegación entre múltiples archivos, opciones para compartir e incluso anotaciones sobre documentos. Esto significa que los usuarios obtienen una interfaz familiar y pulida sin que el desarrollador tenga que invertir tiempo en construir visualizadores desde cero.

QuickLook es especialmente útil cuando tu aplicación maneja archivos descargados, adjuntos de correo electrónico, documentos almacenados en la nube, o cualquier tipo de contenido multimedia que el usuario necesite inspeccionar rápidamente. Su integración es sencilla tanto en proyectos UIKit como en SwiftUI, lo que lo convierte en una herramienta esencial en el arsenal de cualquier desarrollador iOS.

## Casos de uso principales

- **Previsualización de adjuntos en apps de mensajería o correo:** Permite a los usuarios ver PDFs, imágenes, documentos de Office y otros archivos adjuntos sin salir de la aplicación, proporcionando una experiencia fluida y nativa.

- **Explorador de archivos o gestor documental:** Aplicaciones que manejan sistemas de archivos locales o en la nube pueden usar QuickLook para que el usuario inspeccione cualquier documento antes de abrirlo, descargarlo o compartirlo.

- **Visualización de modelos 3D y realidad aumentada:** QuickLook soporta archivos USDZ y Reality, permitiendo previsualizar modelos tridimensionales e incluso colocarlos en el mundo real mediante AR, ideal para apps de comercio electrónico, decoración de interiores o educación.

- **Aplicaciones empresariales con reportes y facturas:** Apps de gestión que generan o reciben PDFs, hojas de cálculo o presentaciones pueden mostrar estos documentos de forma instantánea sin depender de librerías de terceros.

- **Galerías de imágenes con soporte multi-formato:** Cuando necesitas mostrar imágenes en formatos variados (RAW, HEIC, TIFF, PNG, JPEG) con capacidades de zoom y navegación, QuickLook ofrece una solución robusta y optimizada.

- **Previsualización antes de compartir o exportar:** Permite al usuario revisar el contenido de un archivo antes de enviarlo por AirDrop, correo electrónico u otras vías de compartición, reduciendo errores y mejorando la confianza del usuario.

## Instalación y configuración

### Agregar el framework al proyecto

QuickLook viene incluido en el SDK de iOS, por lo que no necesitas instalar dependencias externas mediante CocoaPods, SPM o Carthage. Simplemente importa el módulo en los archivos donde lo necesites:

```swift
import QuickLook
```

Para proyectos SwiftUI que utilicen la vista nativa de previsualización:

```swift
import SwiftUI
import QuickLook
```

### Configuración en el proyecto

No se requieren permisos especiales en `Info.plist` para utilizar QuickLook con archivos locales. Sin embargo, si tu aplicación descarga archivos desde Internet o accede a archivos fuera de su sandbox, considera lo siguiente:

```xml
<!-- Si descargas archivos desde Internet -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
</dict>

<!-- Si accedes a archivos del usuario -->
<key>UIFileSharingEnabled</key>
<true/>
<key>LSSupportsOpeningDocumentsInPlace</key>
<true/>
```

### Requisitos mínimos

| Plataforma | Versión mínima |
|-----------|---------------|
| iOS | 4.0+ (QLPreviewController) |
| iOS (SwiftUI) | 15.0+ (quickLookPreview) |
| macOS | 10.6+ |
| visionOS | 1.0+ |

## Conceptos clave

### QLPreviewController

Es el componente principal del framework en UIKit. Se trata de un `UIViewController` especializado que presenta una interfaz completa de previsualización. Funciona con un patrón de delegación mediante `QLPreviewControllerDataSource` para proveer los archivos a mostrar, y `QLPreviewControllerDelegate` para controlar el comportamiento de la navegación y las transiciones.

### QLPreviewItem

Es el protocolo que deben conformar los objetos que representan archivos a previsualizar. Requiere implementar una propiedad `previewItemURL` que devuelve la URL local del archivo. Opcionalmente, se puede proporcionar un `previewItemTitle` para personalizar el título mostrado en la barra de navegación. `NSURL` ya conforma este protocolo de forma predeterminada.

### QLPreviewControllerDataSource

Este protocolo define dos métodos obligatorios: `numberOfPreviewItems(in:)` para indicar cuántos archivos se van a previsualizar, y `previewController(_:previewItemAt:)` para devolver cada archivo en un índice específico. Esto permite navegar entre múltiples documentos deslizando horizontalmente.

### quickLookPreview (SwiftUI)

A partir de iOS 15, SwiftUI ofrece el modificador `.quickLookPreview($url)` que acepta un `Binding<URL?>`. Cuando la URL no es `nil`, se presenta automáticamente la previsualización. Cuando el usuario cierra la vista previa, el binding se establece a `nil`. Es la forma más idiomática y sencilla de integrar QuickLook en aplicaciones SwiftUI.

### QLPreviewingController

Este protocolo se utiliza para crear **extensiones de QuickLook** (QuickLook Preview Extensions) que permiten a tu aplicación proveer previsualizaciones de tipos de archivo personalizados dentro del sistema operativo. Es útil cuando tu app define formatos de archivo propios y quieres que sean previsualizables desde Archivos, Mail u otras apps.

### Thumbnails (QLThumbnailGenerator)

El framework también incluye `QLThumbnailGenerator`, una clase que genera miniaturas (thumbnails) de archivos de forma asíncrona. Esto es extremadamente útil para mostrar vistas previas en listas, colecciones o grids sin tener que abrir el archivo completo.

## Ejemplo básico

```swift
import UIKit
import QuickLook

/// ViewController básico que previsualiza un único archivo PDF
/// incluido en el bundle de la aplicación.
class BasicPreviewViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground

        // Crear botón para abrir la previsualización
        let previewButton = UIButton(type: .system)
        previewButton.setTitle("Ver documento PDF", for: .normal)
        previewButton.titleLabel?.font = .preferredFont(forTextStyle: .headline)
        previewButton.addTarget(self, action: #selector(showPreview), for: .touchUpInside)

        // Centrar el botón en la pantalla
        previewButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(previewButton)
        NSLayoutConstraint.activate([
            previewButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            previewButton.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }

    @objc private func showPreview() {
        // Crear el controlador de previsualización
        let previewController = QLPreviewController()

        // Asignar el dataSource para proveer los archivos
        previewController.dataSource = self

        // Presentar modalmente
        present(previewController, animated: true)
    }
}

// MARK: - QLPreviewControllerDataSource
extension BasicPreviewViewController: QLPreviewControllerDataSource {

    /// Indica cuántos archivos se van a previsualizar
    func numberOfPreviewItems(in controller: QLPreviewController) -> Int {
        return 1
    }

    /// Devuelve el archivo a previsualizar en el índice dado
    func previewController(
        _ controller: QLPreviewController,
        previewItemAt index: Int
    ) -> QLPreviewItem {
        // Obtener la URL del PDF incluido en el bundle
        guard let pdfURL = Bundle.main.url(
            forResource: "documento-ejemplo",
            withExtension: "pdf"
        ) else {
            // Si no se encuentra, devolver una URL vacía (evitar crash)
            fatalError("El archivo documento-ejemplo.pdf no se encontró en el bundle")
        }
        return pdfURL as QLPreviewItem
    }
}
```

## Ejemplo intermedio

```swift
import UIKit
import QuickLook

/// Modelo que representa un archivo previsualizable.
/// Conforma QLPreviewItem para integrarse directamente con QuickLook.
class PreviewableFile: NSObject, QLPreviewItem {
    let fileName: String
    let fileExtension: String
    let displayTitle: String

    /// URL requerida por el protocolo QLPreviewItem
    var previewItemURL: URL? {
        // Buscar el archivo en el directorio de documentos de la app
        let documentsPath = FileManager.default.urls(
            for: .documentDirectory,
            in: .userDomainMask
        ).first!
        let fileURL = documentsPath.appendingPathComponent("\(fileName).\(fileExtension)")

        // Verificar que el archivo existe
        guard FileManager.default.fileExists(atPath: fileURL.path) else {
            return nil
        }
        return fileURL
    }

    /// Título opcional que se muestra en la barra de navegación
    var previewItemTitle: String? {
        return displayTitle
    }

    init(fileName: String, fileExtension: String, displayTitle: String) {
        self.fileName = fileName
        self.fileExtension = fileExtension
        self.displayTitle = displayTitle
    }
}

/// ViewController con tabla que muestra una lista de archivos
/// y permite previsualizarlos con QuickLook, incluyendo
/// navegación entre múltiples documentos.
class FileListViewController: UITableViewController {

    // Lista de archivos disponibles para previsualizar
    private var files: [PreviewableFile] = [
        PreviewableFile(
            fileName: "contrato-2024",
            fileExtension: "pdf",
            displayTitle: "Contrato 2024"
        ),
        PreviewableFile(
            fileName: "foto-producto",
            fileExtension: "jpg",
            displayTitle: "Foto del producto"
        ),
        PreviewableFile(
            fileName: "reporte-ventas",
            fileExtension: "xlsx",
            displayTitle: "Reporte de ventas Q4"
        ),
        PreviewableFile(
            fileName: "presentacion-proyecto",
            fileExtension: "pptx",
            displayTitle: "Presentación del proyecto"
        ),
        PreviewableFile(
            fileName: "modelo-silla",
            fileExtension: "usdz",
            displayTitle: "Modelo 3D - Silla"
        )
    ]

    // Índice del archivo seleccionado para comenzar la previsualización
    private var selectedIndex: Int = 0

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Mis documentos"
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "FileCell")
        navigationController?.navigationBar.prefersLargeTitles = true
    }

    // MARK: - UITableViewDataSource

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return files.count
    }

    override func tableView(
        _ tableView: UITableView,
        cellForRowAt indexPath: IndexPath
    ) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "FileCell", for: indexPath)
        let file = files[indexPath.row]

        var config = cell.defaultContentConfiguration()
        config.text = file.displayTitle
        config.secondaryText = "\(file.fileName).\(file.fileExtension)"

        // Asignar icono según tipo de archivo
        let iconName: String
        switch file.fileExtension {
        case "pdf": iconName = "doc.fill"
        case "jpg", "png", "heic": iconName = "photo.fill"
        case "xlsx", "csv": iconName = "tablecells.fill"
        case "pptx", "key": iconName = "rectangle.fill.on.rectangle.fill"
        case "usdz": iconName = "cube.fill"
        default: iconName = "doc.fill"
        }
        config.image = UIImage(systemName: iconName)

        cell.contentConfiguration = config
        cell.accessoryType = .disclosureIndicator
        return cell
    }

    // MARK: - UITableViewDelegate

    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)

        // Verificar que el archivo puede previsualizarse
        guard let fileURL = files[indexPath.row].previewItemURL,
              QLPreviewController.canPreview(files[indexPath.row]) else {
            showAlert(message: "No se puede previsualizar este archivo.")
            return
        }

        // Guardar el índice seleccionado y presentar QuickLook
        selectedIndex = indexPath.row

        let previewController = QLPreviewController()
        previewController.dataSource = self
        previewController.delegate = self
        previewController.currentPreviewItemIndex = selectedIndex

        // Usar navegación push para una experiencia más natural en tabla
        navigationController?.pushViewController(previewController, animated: true)
    }

    private func showAlert(message: String) {
        let alert = UIAlertController(
            title: "Error",
            message: message,
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "Aceptar", style: .default))
        present(alert, animated: true)
    }
}

// MARK: - QLPreviewControllerDataSource
extension FileListViewController: QLPreviewControllerDataSource {

    func numberOfPreviewItems(in controller: QLPreviewController) -> Int {
        // Permitir navegar entre todos los archivos válidos
        return files.count
    }

    func previewController(
        _ controller: QLPreviewController,
        previewItemAt index: Int
    ) -> QLPreviewItem {
        return files[index]
    }
}

// MARK: - QLPreviewControllerDelegate
extension FileListViewController: QLPreviewControllerDelegate {

    /// Se llama cuando el usuario cambia de archivo en la previsualización
    func previewController(
        _ controller: QLPreviewController,
        transitionViewFor item: QLPreviewItem
    ) -> UIView? {
        // Devolver la celda correspondiente para una animación de transición suave
        guard let file = item as? PreviewableFile,
              let index = files.firstIndex(where: { $0.fileName == file.fileName }) else {
            return nil
        }