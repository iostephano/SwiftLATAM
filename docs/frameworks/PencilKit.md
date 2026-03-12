---
sidebar_position: 1
title: PencilKit
---

# PencilKit

## ¿Qué es PencilKit?

PencilKit es el framework nativo de Apple que proporciona un entorno completo de dibujo y escritura a mano para aplicaciones iOS, iPadOS, macOS y visionOS. Desarrollado originalmente para potenciar la experiencia del Apple Pencil, este framework ofrece un canvas de dibujo de baja latencia con herramientas de tinta, lápiz, marcador, borrador y regla, todo con un rendimiento optimizado a nivel de sistema operativo. PencilKit es el mismo motor de renderizado que utiliza la app Notas de Apple internamente.

El framework abstrae toda la complejidad del manejo de trazos, presión, inclinación y azimut del Apple Pencil, permitiendo a los desarrolladores integrar capacidades de dibujo profesional en sus aplicaciones con muy pocas líneas de código. Además, gestiona automáticamente la serialización de los dibujos en un formato de datos compacto (`PKDrawing`), lo que facilita el almacenamiento y la recuperación de contenido dibujado.

PencilKit es ideal cuando necesitas incorporar funcionalidades de anotación sobre documentos, firma digital, toma de notas manuscritas, dibujo artístico o cualquier interacción que requiera entrada de lápiz o dedo directamente sobre la pantalla. Su integración es sencilla tanto en UIKit como en SwiftUI, lo que lo convierte en una solución versátil para proyectos de cualquier escala.

## Casos de uso principales

- **Aplicaciones de notas y cuadernos digitales**: Permite a los usuarios escribir y dibujar libremente, similar a la app Notas de Apple. Se pueden crear cuadernos con múltiples páginas, cada una con su propio `PKDrawing`.

- **Anotación sobre documentos PDF e imágenes**: Superponer un canvas de PencilKit sobre un visor de PDF o una imagen para que el usuario añada marcas, resaltados, flechas y texto manuscrito.

- **Firma electrónica en formularios**: Capturar la firma del usuario dentro de un área delimitada del canvas, exportarla como imagen y adjuntarla a documentos legales o contractuales.

- **Aplicaciones educativas e infantiles**: Crear pizarras interactivas donde los estudiantes puedan resolver problemas matemáticos, practicar caligrafía o realizar dibujos creativos con retroalimentación en tiempo real.

- **Herramientas de diseño y prototipado rápido**: Ofrecer un lienzo de bocetado donde diseñadores puedan crear wireframes, diagramas de flujo o ilustraciones conceptuales directamente desde el iPad.

- **Aplicaciones médicas y científicas**: Permitir a profesionales de la salud anotar sobre radiografías, diagramas anatómicos o gráficos de datos clínicos para documentar hallazgos.

## Instalación y configuración

### Agregar el framework al proyecto

PencilKit viene incluido en el SDK de iOS, por lo que **no requiere dependencias externas** ni gestores de paquetes. Solo necesitas importarlo directamente en los archivos donde lo utilices:

```swift
import PencilKit
```

### Requisitos mínimos

| Plataforma | Versión mínima |
|------------|---------------|
| iOS        | 13.0+         |
| iPadOS     | 13.0+         |
| macOS      | 10.15+ (Catalyst) / 14.0+ (nativo) |
| visionOS   | 1.0+          |

### Permisos en Info.plist

PencilKit **no requiere permisos especiales** en el archivo `Info.plist`. No necesita acceso a cámara, micrófono, almacenamiento ni ningún recurso protegido del sistema. El canvas opera completamente en memoria dentro del sandbox de la aplicación.

### Configuración en SwiftUI

Para SwiftUI, no se requiere configuración adicional más allá del import. El framework proporciona representaciones compatibles a través de `UIViewRepresentable` o, a partir de iOS 17, vistas nativas de SwiftUI.

### Configuración en UIKit con Storyboard

Si usas Storyboards, puedes agregar una `UIView` genérica en Interface Builder, cambiar su clase personalizada a `PKCanvasView` y conectarla mediante un `@IBOutlet`:

```swift
@IBOutlet weak var canvasView: PKCanvasView!
```

## Conceptos clave

### 1. PKCanvasView

Es el componente visual principal del framework. Se trata de una subclase de `UIScrollView` que proporciona la superficie de dibujo. Soporta zoom, scroll y maneja automáticamente la entrada del Apple Pencil y del dedo. Puedes configurar si acepta entrada táctil con `drawingPolicy` y si permite scroll con gestos estándar.

```swift
let canvasView = PKCanvasView(frame: view.bounds)
canvasView.drawingPolicy = .pencilOnly // Solo acepta Apple Pencil
```

### 2. PKDrawing

Representa el modelo de datos de un dibujo completo. Contiene todos los trazos (`PKStroke`) realizados sobre el canvas. Es un tipo `Codable`, lo que significa que puedes serializarlo fácilmente a `Data` para almacenarlo en archivos, bases de datos o transmitirlo por red. También puedes combinar múltiples dibujos con el operador de unión.

```swift
let data = canvasView.drawing.dataRepresentation()
let drawing = try PKDrawing(data: data)
```

### 3. PKToolPicker

Es la paleta flotante de herramientas que Apple proporciona de forma estándar. Incluye selectores de bolígrafo, marcador, lápiz, borrador, regla y selector de color. Aparece automáticamente cuando el canvas se convierte en primer respondedor. Puedes personalizar qué herramientas están visibles y responder a cambios de selección.

### 4. PKStroke y PKStrokePath

`PKStroke` representa un trazo individual dentro de un dibujo. Cada trazo contiene un `PKStrokePath` (la geometría del trazo definida por puntos de control), una `PKInk` (el tipo de tinta y color) y una `CGAffineTransform` (transformación aplicada). Los puntos del path incluyen información de presión, inclinación, azimut y marca temporal.

### 5. PKInk e PKInkingTool

`PKInk` define las propiedades de la tinta: tipo (bolígrafo, marcador, lápiz) y color. `PKInkingTool` es la herramienta concreta que usa el usuario, con tipo, color y ancho de línea. A partir de iOS 17, se añadieron nuevos tipos como tinta de acuarela, crayón y lápiz de color.

### 6. PKLassoTool y PKEraserTool

Herramientas especializadas: el lazo permite seleccionar, mover, copiar y pegar trazos; el borrador puede operar en modo de objeto (borra trazos completos) o en modo de píxel (borra porciones de trazos). Estas herramientas se configuran y asignan directamente al canvas o al tool picker.

## Ejemplo básico

Este ejemplo muestra cómo presentar un canvas de dibujo funcional con la paleta de herramientas en un `UIViewController`:

```swift
import UIKit
import PencilKit

class BasicDrawingViewController: UIViewController {

    // MARK: - Propiedades
    private let canvasView = PKCanvasView()
    private let toolPicker = PKToolPicker()

    // MARK: - Ciclo de vida
    override func viewDidLoad() {
        super.viewDidLoad()
        configurarCanvas()
        configurarToolPicker()
    }

    // MARK: - Configuración del canvas
    private func configurarCanvas() {
        // Añadir el canvas a la vista principal
        canvasView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(canvasView)

        // Ocupar toda la pantalla
        NSLayoutConstraint.activate([
            canvasView.topAnchor.constraint(equalTo: view.topAnchor),
            canvasView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            canvasView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            canvasView.trailingAnchor.constraint(equalTo: view.trailingAnchor)
        ])

        // Permitir dibujar con dedo y Apple Pencil
        canvasView.drawingPolicy = .anyInput

        // Fondo blanco para el canvas
        canvasView.backgroundColor = .white

        // Habilitar scroll y zoom
        canvasView.isScrollEnabled = true
        canvasView.minimumZoomScale = 1.0
        canvasView.maximumZoomScale = 5.0
    }

    // MARK: - Configuración de la paleta de herramientas
    private func configurarToolPicker() {
        // Asociar el tool picker al canvas
        toolPicker.setVisible(true, forFirstResponder: canvasView)
        toolPicker.addObserver(canvasView)

        // Hacer que el canvas sea el primer respondedor para mostrar la paleta
        canvasView.becomeFirstResponder()
    }

    // MARK: - Guardar el dibujo como Data
    func guardarDibujo() -> Data {
        return canvasView.drawing.dataRepresentation()
    }

    // MARK: - Cargar un dibujo desde Data
    func cargarDibujo(desde data: Data) {
        do {
            let drawing = try PKDrawing(data: data)
            canvasView.drawing = drawing
        } catch {
            print("Error al cargar el dibujo: \(error.localizedDescription)")
        }
    }
}
```

## Ejemplo intermedio

Un caso de uso real: **anotación sobre una imagen** con posibilidad de exportar el resultado como imagen combinada y deshacer/rehacer acciones:

```swift
import UIKit
import PencilKit

class AnotacionImagenViewController: UIViewController {

    // MARK: - Propiedades
    private let canvasView = PKCanvasView()
    private let toolPicker = PKToolPicker()
    private let imagenFondo = UIImageView()
    private let undoManager_ = UndoManager()

    /// Imagen sobre la que se va a anotar
    var imagenBase: UIImage? {
        didSet {
            imagenFondo.image = imagenBase
        }
    }

    // MARK: - Ciclo de vida
    override func viewDidLoad() {
        super.viewDidLoad()
        configurarVista()
        configurarBarraNavegacion()
    }

    override var undoManager: UndoManager? {
        return undoManager_
    }

    // MARK: - Configuración
    private func configurarVista() {
        view.backgroundColor = .systemGray6

        // Configurar la imagen de fondo
        imagenFondo.contentMode = .scaleAspectFit
        imagenFondo.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(imagenFondo)

        // Configurar el canvas transparente encima de la imagen
        canvasView.translatesAutoresizingMaskIntoConstraints = false
        canvasView.backgroundColor = .clear
        canvasView.isOpaque = false
        canvasView.drawingPolicy = .anyInput
        canvasView.delegate = self
        view.addSubview(canvasView)

        // Constraints para ambas vistas (misma posición y tamaño)
        for subview in [imagenFondo, canvasView] {
            NSLayoutConstraint.activate([
                subview.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
                subview.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor),
                subview.leadingAnchor.constraint(equalTo: view.leadingAnchor),
                subview.trailingAnchor.constraint(equalTo: view.trailingAnchor)
            ])
        }

        // Configurar tool picker
        toolPicker.setVisible(true, forFirstResponder: canvasView)
        toolPicker.addObserver(canvasView)
        canvasView.becomeFirstResponder()

        // Establecer herramienta inicial: marcador rojo semitransparente
        let marcadorRojo = PKInkingTool(.marker, color: .systemRed.withAlphaComponent(0.5), width: 15)
        canvasView.tool = marcadorRojo
    }

    private func configurarBarraNavegacion() {
        navigationItem.title = "Anotar Imagen"

        // Botones de deshacer y rehacer
        let botonDeshacer = UIBarButtonItem(
            image: UIImage(systemName: "arrow.uturn.backward"),
            style: .plain,
            target: undoManager_,
            action: #selector(UndoManager.undo)
        )
        let botonRehacer = UIBarButtonItem(
            image: UIImage(systemName: "arrow.uturn.forward"),
            style: .plain,
            target: undoManager_,
            action: #selector(UndoManager.redo)
        )
        let botonExportar = UIBarButtonItem(
            image: UIImage(systemName: "square.and.arrow.up"),
            style: .plain,
            target: self,
            action: #selector(exportarImagen)
        )
        let botonLimpiar = UIBarButtonItem(
            title: "Limpiar",
            style: .plain,
            target: self,
            action: #selector(limpiarCanvas)
        )

        navigationItem.leftBarButtonItems = [botonDeshacer, botonRehacer]
        navigationItem.rightBarButtonItems = [botonExportar, botonLimpiar]
    }

    // MARK: - Acciones

    /// Combina la imagen de fondo con las anotaciones en una sola imagen
    @objc private func exportarImagen() {
        guard let imagenOriginal = imagenBase else { return }

        let tamano = imagenOriginal.size
        let renderer = UIGraphicsImageRenderer(size: tamano)

        let imagenFinal = renderer.image { contexto in
            // Dibujar la imagen base
            imagenOriginal.draw(in: CGRect(origin: .zero, size: tamano))

            // Dibujar las anotaciones del canvas escaladas al tamaño de la imagen
            let dibujoImagen = canvasView.drawing.image(
                from: canvasView.bounds,
                scale: tamano.width / canvasView.bounds.width
            )
            dibujoImagen.draw(in: CGRect(origin: .zero, size: tamano))
        }

        // Presentar el sheet de compartir
        let activityVC = UIActivityViewController(
            activityItems: [imagenFinal],
            applicationActivities: nil
        )
        present(activityVC, animated: true)
    }

    @objc private func limpiarCanvas() {
        canvasView.drawing = PKDrawing()
    }
}

// MARK: - PKCanvasViewDelegate
extension AnotacionImagenViewController: PKCanvasViewDelegate {

    /// Se llama cada vez que el usuario modifica el dibujo
    func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
        print("Número de trazos: \(canvasView.drawing.strokes.count)")
    }
}
```

## Ejemplo avanzado

Implementación completa con **arquitectura MVVM**, persistencia, miniaturas y soporte SwiftUI:

```swift
import SwiftUI
import PencilKit
import Combine

// MARK