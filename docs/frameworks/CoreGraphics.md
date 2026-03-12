---
sidebar_position: 1
title: CoreGraphics
---

# CoreGraphics

## ¿Qué es CoreGraphics?

CoreGraphics, también conocido como **Quartz 2D**, es el motor de renderizado 2D de bajo nivel de Apple. Este framework proporciona una API ligera y extremadamente potente para el dibujo bidimensional, incluyendo trazados basados en vectores, transformaciones geométricas, gestión del color, renderizado de imágenes fuera de pantalla (offscreen rendering), generación y lectura de documentos PDF, y mucho más. Es el cimiento sobre el cual se construyen frameworks de más alto nivel como UIKit y SwiftUI.

A diferencia de frameworks más abstractos, CoreGraphics opera directamente sobre un **contexto gráfico** (`CGContext`), que actúa como un lienzo virtual donde se ejecutan todas las operaciones de dibujo. Esto brinda un control granular sobre cada píxel, cada curva y cada transformación, lo que lo convierte en la herramienta ideal cuando los componentes estándar de la interfaz no son suficientes para lograr un diseño visual particular.

Se recomienda usar CoreGraphics cuando necesitas crear gráficos personalizados, generar imágenes dinámicamente, manipular píxeles directamente, dibujar formas geométricas complejas, crear filtros de imagen propios o generar documentos PDF de forma programática. Si bien SwiftUI y UIKit cubren la mayoría de las necesidades de interfaz, CoreGraphics es insustituible cuando se requiere máximo rendimiento y control absoluto en el renderizado 2D.

## Casos de uso principales

- **Dibujo de gráficas y visualización de datos**: Creación de gráficos de barras, líneas, pastel y otros tipos de visualizaciones completamente personalizadas sin depender de librerías de terceros.

- **Generación dinámica de imágenes**: Crear avatares con iniciales, thumbnails con marcas de agua, badges con contadores o imágenes compuestas en tiempo de ejecución.

- **Creación y manipulación de PDFs**: Generar facturas, reportes, tickets o cualquier documento PDF de forma programática, así como leer y renderizar páginas de PDFs existentes.

- **Interfaces de usuario personalizadas**: Dibujar botones, controles, indicadores de progreso y otros elementos con formas y gradientes que no son posibles con los componentes estándar de UIKit o SwiftUI.

- **Procesamiento de imágenes a nivel de píxel**: Acceder y modificar los datos brutos de una imagen (bitmap) para aplicar filtros, transformaciones o análisis personalizado.

- **Máscaras y recortes complejos**: Crear formas de recorte sofisticadas para imágenes, vistas o animaciones que van más allá de los bordes redondeados simples.

## Instalación y configuración

CoreGraphics es un **framework del sistema** incluido en todas las plataformas Apple, por lo que **no requiere instalación adicional** ni dependencias externas. Está disponible de forma nativa en iOS, macOS, tvOS, watchOS y visionOS.

### Importación

```swift
import CoreGraphics

// En la mayoría de los casos, si ya importas UIKit o SwiftUI,
// CoreGraphics se incluye implícitamente
import UIKit    // Incluye CoreGraphics automáticamente
import SwiftUI  // Incluye CoreGraphics automáticamente
```

### Requisitos mínimos

| Plataforma | Versión mínima |
|-----------|---------------|
| iOS       | 2.0+          |
| macOS     | 10.0+         |
| tvOS      | 9.0+          |
| watchOS   | 2.0+          |
| visionOS  | 1.0+          |

### Permisos en Info.plist

CoreGraphics **no requiere permisos especiales** en `Info.plist`. Sin embargo, si trabajas con imágenes del usuario o guardas archivos PDF, podrías necesitar permisos relacionados con la galería de fotos (`NSPhotoLibraryUsageDescription`) o el sistema de archivos, dependiendo de tu caso de uso.

### Configuración en SPM / CocoaPods

Al ser un framework del sistema, **no necesitas agregarlo como dependencia** en Swift Package Manager, CocoaPods ni Carthage. Simplemente importa y úsalo.

## Conceptos clave

### 1. Contexto Gráfico (`CGContext`)

El concepto más fundamental de CoreGraphics. Un `CGContext` es una superficie de dibujo abstracta que contiene toda la información necesaria para renderizar contenido: el destino de salida (pantalla, imagen en memoria, PDF), el estado gráfico actual (colores, transformaciones, recortes) y los parámetros de renderizado. Todo lo que dibujas, lo dibujas **dentro** de un contexto.

```swift
// Crear un contexto de imagen bitmap
UIGraphicsBeginImageContextWithOptions(CGSize(width: 200, height: 200), false, 0.0)
let contexto = UIGraphicsGetCurrentContext()
// ... operaciones de dibujo ...
let imagen = UIGraphicsGetImageFromCurrentImageContext()
UIGraphicsEndImageContext()
```

### 2. Sistema de coordenadas y transformaciones (`CGAffineTransform`)

CoreGraphics utiliza un sistema de coordenadas cartesiano. En macOS, el origen `(0,0)` está en la esquina **inferior izquierda**; en UIKit (iOS), el sistema está volteado y el origen está en la esquina **superior izquierda**. Las transformaciones afines permiten trasladar, rotar, escalar y combinar transformaciones de forma matricial.

```swift
// Transformación compuesta: escalar y rotar
var transform = CGAffineTransform.identity
transform = transform.scaledBy(x: 2.0, y: 2.0)
transform = transform.rotated(by: .pi / 4) // 45 grados
```

### 3. Trazados (`CGPath` / `CGMutablePath`)

Los trazados son la base del dibujo vectorial. Un trazado es una secuencia de líneas, arcos y curvas Bézier que definen una forma geométrica. Una vez definido, puedes trazar su contorno (*stroke*), rellenarlo (*fill*) o usarlo como máscara de recorte (*clip*).

### 4. Espacios de color (`CGColorSpace`)

CoreGraphics trabaja con diferentes espacios de color (sRGB, Display P3, escala de grises, CMYK, etc.). Elegir el espacio de color correcto es crucial para la fidelidad visual y el rendimiento. El espacio de color también determina cuántos componentes tiene cada color.

### 5. Imágenes bitmap (`CGImage`)

`CGImage` es la representación de bajo nivel de una imagen rasterizada. Proporciona acceso directo a los datos de píxeles y permite operaciones como recorte, creación de máscaras, y conversión entre formatos de color. Es el puente entre CoreGraphics y otros frameworks como Core Image o Vision.

### 6. Capas (`CGLayer`) y estado gráfico

CoreGraphics mantiene una **pila de estados gráficos**. Puedes guardar (`saveGState`) y restaurar (`restoreGState`) el estado completo del contexto (color de relleno, grosor de línea, transformación, región de recorte, etc.). Este mecanismo es esencial para aislar operaciones de dibujo sin efectos secundarios.

## Ejemplo básico

Este ejemplo muestra cómo dibujar formas simples en una vista personalizada de UIKit:

```swift
import UIKit

/// Vista personalizada que dibuja formas geométricas básicas
/// usando CoreGraphics directamente en el método draw(_:)
class FormasBasicasView: UIView {

    override func draw(_ rect: CGRect) {
        // Obtener el contexto gráfico actual proporcionado por UIKit
        guard let contexto = UIGraphicsGetCurrentContext() else { return }

        // === RECTÁNGULO CON RELLENO ===
        // Definir el color de relleno (azul con transparencia)
        contexto.setFillColor(UIColor.systemBlue.withAlphaComponent(0.7).cgColor)

        // Dibujar un rectángulo relleno
        let rectangulo = CGRect(x: 20, y: 20, width: 150, height: 100)
        contexto.fill(rectangulo)

        // === CÍRCULO CON BORDE ===
        // Configurar el color y grosor del trazo
        contexto.setStrokeColor(UIColor.systemRed.cgColor)
        contexto.setLineWidth(3.0)

        // Dibujar un círculo (elipse inscrita en un cuadrado)
        let circulo = CGRect(x: 200, y: 20, width: 100, height: 100)
        contexto.strokeEllipse(in: circulo)

        // === LÍNEA DIAGONAL ===
        contexto.setStrokeColor(UIColor.systemGreen.cgColor)
        contexto.setLineWidth(2.0)
        contexto.setLineCap(.round) // Extremos redondeados

        // Mover al punto inicial y trazar la línea
        contexto.move(to: CGPoint(x: 20, y: 150))
        contexto.addLine(to: CGPoint(x: 320, y: 250))
        contexto.strokePath()

        // === TRIÁNGULO RELLENO ===
        contexto.setFillColor(UIColor.systemOrange.cgColor)

        // Construir el trazado del triángulo punto a punto
        contexto.move(to: CGPoint(x: 160, y: 160))
        contexto.addLine(to: CGPoint(x: 100, y: 280))
        contexto.addLine(to: CGPoint(x: 220, y: 280))
        contexto.closePath() // Cierra el trazado automáticamente
        contexto.fillPath()
    }
}
```

## Ejemplo intermedio

Este ejemplo crea un **generador de avatares con iniciales** que produce imágenes dinámicamente, un caso de uso muy común en aplicaciones de mensajería y redes sociales:

```swift
import UIKit

/// Generador de avatares con iniciales usando CoreGraphics.
/// Produce imágenes circulares con un gradiente de fondo y texto centrado.
struct AvatarGenerator {

    /// Configuración visual del avatar
    struct Configuracion {
        let tamaño: CGFloat
        let colorInicio: UIColor
        let colorFin: UIColor
        let fuenteTexto: UIFont
        let colorTexto: UIColor

        /// Configuración por defecto
        static let porDefecto = Configuracion(
            tamaño: 120,
            colorInicio: .systemIndigo,
            colorFin: .systemPurple,
            fuenteTexto: .systemFont(ofSize: 44, weight: .semibold),
            colorTexto: .white
        )
    }

    /// Genera un avatar circular con las iniciales del nombre proporcionado
    /// - Parameters:
    ///   - nombre: Nombre completo del usuario
    ///   - config: Configuración visual (opcional, usa valores por defecto)
    /// - Returns: UIImage con el avatar generado, o nil si falla el renderizado
    static func generar(
        nombre: String,
        config: Configuracion = .porDefecto
    ) -> UIImage? {
        let size = CGSize(width: config.tamaño, height: config.tamaño)

        // Usar el renderer moderno de UIKit (internamente usa CoreGraphics)
        let renderer = UIGraphicsImageRenderer(size: size)

        return renderer.image { rendererContext in
            let contexto = rendererContext.cgContext
            let rect = CGRect(origin: .zero, size: size)

            // --- 1. Crear máscara circular ---
            let circulo = CGPath(
                ellipseIn: rect,
                transform: nil
            )
            contexto.addPath(circulo)
            contexto.clip()

            // --- 2. Dibujar gradiente de fondo ---
            guard let gradiente = crearGradiente(
                inicio: config.colorInicio,
                fin: config.colorFin
            ) else { return }

            contexto.drawLinearGradient(
                gradiente,
                start: CGPoint(x: 0, y: 0),
                end: CGPoint(x: size.width, y: size.height),
                options: [.drawsBeforeStartLocation, .drawsAfterEndLocation]
            )

            // --- 3. Dibujar iniciales centradas ---
            let iniciales = extraerIniciales(de: nombre)

            // Calcular el tamaño del texto para centrarlo
            let atributos: [NSAttributedString.Key: Any] = [
                .font: config.fuenteTexto,
                .foregroundColor: config.colorTexto
            ]

            let textoSize = (iniciales as NSString).size(
                withAttributes: atributos
            )

            let puntoTexto = CGPoint(
                x: (size.width - textoSize.width) / 2.0,
                y: (size.height - textoSize.height) / 2.0
            )

            (iniciales as NSString).draw(
                at: puntoTexto,
                withAttributes: atributos
            )

            // --- 4. Dibujar borde sutil ---
            contexto.setStrokeColor(
                UIColor.white.withAlphaComponent(0.3).cgColor
            )
            contexto.setLineWidth(2.0)
            contexto.addPath(circulo)
            contexto.strokePath()
        }
    }

    /// Crea un gradiente lineal con dos colores
    private static func crearGradiente(
        inicio: UIColor,
        fin: UIColor
    ) -> CGGradient? {
        let espacio = CGColorSpaceCreateDeviceRGB()
        let colores = [inicio.cgColor, fin.cgColor] as CFArray
        return CGGradient(
            colorsSpace: espacio,
            colors: colores,
            locations: [0.0, 1.0]
        )
    }

    /// Extrae las iniciales (máximo 2 caracteres) del nombre
    private static func extraerIniciales(de nombre: String) -> String {
        let componentes = nombre
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .split(separator: " ")

        switch componentes.count {
        case 0:
            return "?"
        case 1:
            return String(componentes[0].prefix(1)).uppercased()
        default:
            let primera = componentes.first?.prefix(1) ?? ""
            let ultima = componentes.last?.prefix(1) ?? ""
            return "\(primera)\(ultima)".uppercased()
        }
    }
}

// MARK: - Uso

let avatar = AvatarGenerator.generar(nombre: "María García")
// avatar es un UIImage? de 120x120 con las iniciales "MG"
// sobre un gradiente circular indigo → púrpura
```

## Ejemplo avanzado

Este ejemplo implementa un **componente de gráfica de líneas reutilizable** siguiendo una arquitectura MVVM limpia, con separación de datos, lógica de presentación y renderizado:

```swift
import UIKit
import Combine

// MARK: - Modelo de datos

/// Representa un punto de datos en la gráfica
struct PuntoDatos: Identifiable {
    let id = UUID()
    let etiqueta: String
    let valor: Double
}

/// Configuración visual de la gráfica
struct ConfiguracionGrafica {
    let colorLinea: UIColor
    let colorRelleno: UIColor
    let colorEjes: UIColor
    let grosorLinea: CGFloat
    let mostrarPuntos: Bool
    let mostrarRelleno: Bool
    let animada: Bool
    