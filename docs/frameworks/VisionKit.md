---
sidebar_position: 1
title: VisionKit
---

# VisionKit

## ¿Qué es VisionKit?

VisionKit es un framework de Apple que proporciona a los desarrolladores acceso directo a las capacidades de escaneo de documentos, reconocimiento de texto en vivo (Live Text) y análisis visual integrado del sistema operativo. Originalmente introducido en iOS 13 como una herramienta para escanear documentos mediante la cámara, VisionKit ha evolucionado significativamente hasta convertirse en una suite completa de herramientas de análisis visual que incluyen interacción con texto, códigos QR, y datos estructurados dentro de imágenes.

A diferencia del framework **Vision** (que se enfoca en el procesamiento y análisis de imágenes a bajo nivel mediante modelos de aprendizaje automático), VisionKit ofrece **componentes de interfaz de usuario listos para usar**. Esto significa que puedes integrar funcionalidades complejas como el escaneo de documentos o la selección de texto dentro de fotografías sin necesidad de construir toda la interfaz desde cero. VisionKit se encarga de la experiencia de usuario, la captura, el procesamiento y la entrega de resultados.

Este framework es ideal cuando necesitas incorporar funcionalidades de escaneo documental, reconocimiento óptico de caracteres (OCR) con interacción directa del usuario, detección de datos estructurados (direcciones, teléfonos, URLs) en imágenes, o capacidades de búsqueda visual (Visual Look Up). Su uso es particularmente relevante en aplicaciones empresariales, de productividad, educativas y financieras donde la digitalización de información física es un flujo de trabajo habitual.

## Casos de uso principales

### 1. Escaneo de documentos
Digitalización de documentos físicos como contratos, recibos, facturas o identificaciones. VisionKit ofrece detección automática de bordes, corrección de perspectiva, ajuste de color y generación de PDFs multipágina.

### 2. Reconocimiento de texto en vivo (Live Text)
Permite a los usuarios interactuar con texto detectado dentro de imágenes o del feed de la cámara en tiempo real: copiar, traducir, buscar o compartir texto visible en fotografías.

### 3. Captura de datos estructurados
Extracción automática de información relevante como números de teléfono, direcciones de correo electrónico, URLs, fechas y direcciones postales detectadas en imágenes o a través de la cámara.

### 4. Lectura de códigos de barras y QR
Detección e interpretación de códigos QR, códigos de barras y otros formatos codificados presentes en documentos o en el entorno del usuario.

### 5. Búsqueda visual (Visual Look Up)
Identificación de objetos, plantas, animales, obras de arte y puntos de interés dentro de fotografías, proporcionando información contextual al usuario.

### 6. Escaneo de tarjetas de presentación
Captura y extracción automática de datos de contacto desde tarjetas de visita físicas para crear registros de contactos en la aplicación.

## Instalación y configuración

### Agregar el framework al proyecto

VisionKit viene incluido como framework del sistema en iOS, por lo que no requiere instalación mediante gestores de paquetes. Simplemente impórtalo en los archivos donde lo necesites:

```swift
import VisionKit
```

### Permisos necesarios en Info.plist

Para funcionalidades que requieren acceso a la cámara, debes agregar la clave correspondiente en tu archivo `Info.plist`:

```xml
<!-- Acceso a la cámara para escaneo de documentos y Live Text -->
<key>NSCameraUsageDescription</key>
<string>Necesitamos acceso a la cámara para escanear documentos y reconocer texto.</string>
```

### Requisitos de plataforma

| Funcionalidad | Disponibilidad mínima |
|---|---|
| `VNDocumentCameraViewController` | iOS 13.0+ |
| `DataScannerViewController` | iOS 16.0+ |
| `ImageAnalyzer` / `ImageAnalysisInteraction` | iOS 16.0+ (macOS 13.0+) |
| Soporte de Subject Lifting | iOS 17.0+ |

### Verificación de compatibilidad del dispositivo

Es fundamental verificar si el dispositivo soporta las capacidades avanzadas antes de intentar usarlas:

```swift
import VisionKit

// Verificar soporte para DataScanner (Live Text con cámara)
let soportaDataScanner = DataScannerViewController.isSupported

// Verificar disponibilidad específica del reconocimiento de texto
let soportaReconocimientoTexto = DataScannerViewController.isAvailable

// Verificar soporte para análisis de imágenes (Live Text en imágenes estáticas)
let soportaAnalisis = ImageAnalyzer.isSupported
```

## Conceptos clave

### 1. VNDocumentCameraViewController

Es el controlador de vista que presenta la interfaz completa de escaneo de documentos del sistema. Gestiona automáticamente la detección de bordes del documento, la estabilización de imagen, la corrección de perspectiva y permite al usuario capturar múltiples páginas en una sola sesión. El resultado es un objeto `VNDocumentCameraScan` que contiene las imágenes procesadas de cada página escaneada.

### 2. DataScannerViewController

Introducido en iOS 16, es el controlador que habilita la experiencia de **Live Text** mediante la cámara. Permite reconocer y capturar texto, códigos de barras y datos estructurados en tiempo real. Ofrece un alto grado de personalización: puedes filtrar por tipos de datos específicos, definir regiones de interés dentro del encuadre e implementar validaciones personalizadas sobre los elementos reconocidos.

### 3. ImageAnalyzer e ImageAnalysisInteraction

`ImageAnalyzer` es la clase responsable de procesar imágenes estáticas para detectar texto y datos estructurados. `ImageAnalysisInteraction` (en UIKit) e `ImageAnalysisOverlayView` (en macOS/SwiftUI) son las capas de interacción que se superponen sobre las imágenes para permitir al usuario seleccionar, copiar y actuar sobre el contenido detectado, replicando la experiencia nativa de Live Text de Fotos.

### 4. RecognizedItem

Representa un elemento individual reconocido por el `DataScannerViewController`. Puede ser de tipo `.text` (texto reconocido) o `.barcode` (código de barras/QR). Cada item incluye la transcripción del contenido, los límites geométricos dentro de la vista y un identificador único para su seguimiento entre frames.

### 5. Tipos de datos reconocibles (DataScannerViewController.RecognizedDataType)

Define qué tipo de información debe buscar el escáner. Los tipos principales son `.text(languages:)` para reconocimiento de texto (con especificación opcional de idiomas) y `.barcode(symbologies:)` para códigos, donde puedes especificar simbologías como `.qr`, `.ean13`, `.code128`, entre muchas otras.

### 6. Subject Lifting (iOS 17+)

Capacidad que permite identificar y aislar sujetos principales dentro de una imagen (personas, objetos, animales) separándolos del fondo. Se integra a través de `ImageAnalysisInteraction` y permite experiencias como copiar el sujeto o arrastrarlo a otra aplicación.

## Ejemplo básico

El siguiente ejemplo muestra cómo implementar el escáner de documentos clásico de VisionKit:

```swift
import UIKit
import VisionKit

/// Controlador que presenta el escáner de documentos del sistema
/// y gestiona los resultados del escaneo.
class DocumentScannerViewController: UIViewController {

    // MARK: - Lifecycle

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        presentarEscaner()
    }

    // MARK: - Escaneo de documentos

    /// Presenta el escáner de documentos nativo de VisionKit
    private func presentarEscaner() {
        // Verificar que el dispositivo soporte escaneo de documentos
        guard VNDocumentCameraViewController.isSupported else {
            mostrarAlerta(
                titulo: "No disponible",
                mensaje: "Este dispositivo no soporta escaneo de documentos."
            )
            return
        }

        // Crear e instanciar el controlador del escáner
        let escaner = VNDocumentCameraViewController()
        escaner.delegate = self
        present(escaner, animated: true)
    }

    /// Procesa las imágenes escaneadas (ejemplo: guardar como PDF)
    private func procesarEscaneo(_ escaneo: VNDocumentCameraScan) {
        print("📄 Documentos escaneados: \(escaneo.pageCount) páginas")

        for indice in 0..<escaneo.pageCount {
            // Obtener la imagen de cada página escaneada
            let imagen = escaneo.imageOfPage(at: indice)
            print("  → Página \(indice + 1): \(imagen.size)")

            // Aquí podrías guardar en disco, enviar a un servidor,
            // procesar con Vision para OCR, etc.
        }
    }

    private func mostrarAlerta(titulo: String, mensaje: String) {
        let alerta = UIAlertController(
            title: titulo,
            message: mensaje,
            preferredStyle: .alert
        )
        alerta.addAction(UIAlertAction(title: "OK", style: .default))
        present(alerta, animated: true)
    }
}

// MARK: - VNDocumentCameraViewControllerDelegate

extension DocumentScannerViewController: VNDocumentCameraViewControllerDelegate {

    /// Se invoca cuando el usuario termina de escanear exitosamente
    func documentCameraViewController(
        _ controller: VNDocumentCameraViewController,
        didFinishWith scan: VNDocumentCameraScan
    ) {
        controller.dismiss(animated: true) { [weak self] in
            self?.procesarEscaneo(scan)
        }
    }

    /// Se invoca cuando el usuario cancela el escaneo
    func documentCameraViewControllerDidCancel(
        _ controller: VNDocumentCameraViewController
    ) {
        controller.dismiss(animated: true) {
            print("✖️ Escaneo cancelado por el usuario")
        }
    }

    /// Se invoca cuando ocurre un error durante el escaneo
    func documentCameraViewController(
        _ controller: VNDocumentCameraViewController,
        didFailWithError error: Error
    ) {
        controller.dismiss(animated: true) { [weak self] in
            self?.mostrarAlerta(
                titulo: "Error de escaneo",
                mensaje: error.localizedDescription
            )
        }
    }
}
```

## Ejemplo intermedio

Este ejemplo implementa un escáner de texto en vivo y códigos QR usando `DataScannerViewController`:

```swift
import UIKit
import VisionKit

/// Controlador que utiliza DataScannerViewController para reconocer
/// texto y códigos de barras en tiempo real mediante la cámara.
class LiveTextScannerViewController: UIViewController {

    // MARK: - Propiedades de UI

    private let etiquetaResultado: UILabel = {
        let label = UILabel()
        label.translatesAutoresizingMaskIntoConstraints = false
        label.numberOfLines = 0
        label.textAlignment = .center
        label.font = .systemFont(ofSize: 16, weight: .medium)
        label.backgroundColor = UIColor.systemBackground.withAlphaComponent(0.85)
        label.layer.cornerRadius = 12
        label.clipsToBounds = true
        label.text = "Apunta la cámara hacia un texto o código QR"
        return label
    }()

    private let botonEscanear: UIButton = {
        let boton = UIButton(type: .system)
        boton.translatesAutoresizingMaskIntoConstraints = false
        boton.setTitle("Iniciar escáner", for: .normal)
        boton.titleLabel?.font = .systemFont(ofSize: 18, weight: .bold)
        boton.backgroundColor = .systemBlue
        boton.setTitleColor(.white, for: .normal)
        boton.layer.cornerRadius = 12
        return boton
    }()

    // MARK: - Propiedades

    /// Almacena los elementos reconocidos actualmente
    private var elementosReconocidos: [RecognizedItem] = []

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        configurarUI()
    }

    // MARK: - Configuración

    private func configurarUI() {
        title = "Escáner en Vivo"
        view.backgroundColor = .systemBackground

        view.addSubview(etiquetaResultado)
        view.addSubview(botonEscanear)

        NSLayoutConstraint.activate([
            etiquetaResultado.leadingAnchor.constraint(
                equalTo: view.leadingAnchor, constant: 20
            ),
            etiquetaResultado.trailingAnchor.constraint(
                equalTo: view.trailingAnchor, constant: -20
            ),
            etiquetaResultado.centerYAnchor.constraint(
                equalTo: view.centerYAnchor, constant: -40
            ),
            etiquetaResultado.heightAnchor.constraint(greaterThanOrEqualToConstant: 100),

            botonEscanear.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            botonEscanear.topAnchor.constraint(
                equalTo: etiquetaResultado.bottomAnchor, constant: 30
            ),
            botonEscanear.widthAnchor.constraint(equalToConstant: 220),
            botonEscanear.heightAnchor.constraint(equalToConstant: 50)
        ])

        botonEscanear.addTarget(
            self,
            action: #selector(iniciarEscaneo),
            for: .touchUpInside
        )
    }

    // MARK: - Escaneo

    @objc private func iniciarEscaneo() {
        // Verificar soporte del dispositivo
        guard DataScannerViewController.isSupported else {
            etiquetaResultado.text = "❌ DataScanner no está soportado en este dispositivo."
            return
        }

        guard DataScannerViewController.isAvailable else {
            etiquetaResultado.text = "❌ DataScanner no está disponible actualmente."
            return
        }

        // Configurar los tipos de datos a reconocer
        let tiposReconocidos: Set<DataScannerViewController.RecognizedDataType> = [
            .text(languages: ["es", "en"]),       // Texto en español e inglés
            .barcode(symbologies: [.qr, .ean13])  // Códigos QR y EAN-13
        ]

        // Crear el controlador del escáner con configuración personalizada
        let escaner = DataScannerViewController(
            recognizedDataTypes: tiposReconocidos,
            qualityLevel: .accurate,          // Priorizar precisión sobre velocidad
            recognizesMultipleItems: true,    // Permitir reconocer varios elementos a la vez
            isHighFrameRateTrackingEnabled: true, // Seguimiento fluido de elementos
            isPinchToZoomEnabled: true,       // Permitir zoom con pellizco
            isGuidanceEnabled: true,          // Mostrar guía al usuario
            isHighlightingEnabled: true       // Resaltar elementos detectados
        )

        escaner.delegate = self
        present(escaner, animated: true