---
sidebar_position: 1
title: CoreText
---

# CoreText

## ¿Qué es CoreText?

CoreText es el framework de bajo nivel de Apple para el diseño tipográfico y la representación de texto. Proporciona una API basada en C que permite un control granular y preciso sobre cómo se renderiza el texto en pantalla, incluyendo la gestión de fuentes, el cálculo de layouts tipográficos, la creación de líneas y glifos, y el manejo avanzado de atributos de texto. Es el motor que subyace a frameworks de más alto nivel como TextKit (UIKit) y SwiftUI Text, por lo que comprender CoreText otorga un entendimiento profundo de cómo funciona el texto en todas las plataformas Apple.

Este framework es especialmente relevante cuando los desarrolladores necesitan ir más allá de lo que ofrecen `UILabel`, `UITextView` o `SwiftUI.Text`. Casos como editores de texto personalizados, motores de renderizado PDF, sistemas de maquetación editorial o cualquier escenario donde se requiera un control pixel-perfect sobre la tipografía hacen de CoreText una herramienta indispensable. Al operar a nivel de Core Foundation, ofrece un rendimiento excepcional, aunque a costa de una API más verbosa y compleja.

CoreText está disponible en iOS, macOS, tvOS, watchOS y visionOS. Aunque muchos proyectos modernos pueden prescindir de él gracias a TextKit 2 y SwiftUI, sigue siendo la opción preferida cuando se necesitan optimizaciones de rendimiento extremas o funcionalidades tipográficas que los frameworks de alto nivel no exponen directamente.

## Casos de uso principales

- **Editores de texto personalizados**: Construcción de editores con control total sobre la selección, el cursor, el interlineado y la disposición de caracteres, como procesadores de texto profesionales o IDEs de código.

- **Renderizado de texto en contextos gráficos (PDF/imágenes)**: Dibujar texto directamente sobre `CGContext` para generar documentos PDF, imágenes con texto superpuesto o gráficos vectoriales con tipografía precisa.

- **Aplicaciones de maquetación editorial**: Apps tipo revista o libro digital donde el texto debe fluir alrededor de imágenes, columnas o formas irregulares, con control absoluto sobre cada aspecto tipográfico.

- **Motores de renderizado de texto para juegos**: Generación de texturas de texto de alto rendimiento para motores gráficos basados en Metal o OpenGL donde se necesita rasterizar glifos de forma eficiente.

- **Análisis y métricas tipográficas**: Obtener medidas exactas de glifos, ascendentes, descendentes, anchos de avance y bounding boxes para cálculos de layout precisos.

- **Sistemas de texto con atributos complejos**: Textos con múltiples estilos, idiomas bidireccionales (árabe, hebreo), ligaduras OpenType, variantes estilísticas y características tipográficas avanzadas.

## Instalación y configuración

CoreText es un framework del sistema incluido en todas las plataformas Apple. **No requiere instalación mediante SPM, CocoaPods ni Carthage**. Tampoco necesita permisos especiales en `Info.plist`.

### Import necesario

```swift
import CoreText
import CoreGraphics // Necesario para CGContext, CGRect, etc.
import Foundation   // Para CFAttributedString, CFString, etc.
```

### Configuración en Xcode

En la mayoría de los casos, simplemente agregar el `import CoreText` es suficiente. Sin embargo, si trabajas con un target que no lo enlaza automáticamente:

1. Selecciona tu **target** en Xcode.
2. Ve a **Build Phases** → **Link Binary With Libraries**.
3. Agrega `CoreText.framework`.

### Compatibilidad

| Plataforma | Versión mínima |
|------------|---------------|
| iOS        | 3.2+          |
| macOS      | 10.5+         |
| tvOS       | 9.0+          |
| watchOS    | 2.0+          |
| visionOS   | 1.0+          |

## Conceptos clave

### 1. CTFont

Representa una fuente tipográfica. Es el equivalente de bajo nivel a `UIFont`/`NSFont`. Permite acceder a métricas detalladas como ascendente, descendente, leading, unidades por em, tablas OpenType y glifos individuales.

```swift
// Crear una fuente de 18 puntos
let font = CTFontCreateWithName("Helvetica-Bold" as CFString, 18.0, nil)
let ascent = CTFontGetAscent(font)   // Distancia desde la línea base hacia arriba
let descent = CTFontGetDescent(font) // Distancia desde la línea base hacia abajo
```

### 2. CFAttributedString

Cadena de texto con atributos asociados a rangos específicos (fuente, color, interlineado, etc.). Es la entrada principal para el sistema de layout de CoreText. Es equivalente a `NSAttributedString` y se puede hacer bridge entre ambos.

### 3. CTFramesetter

Es el objeto central de layout. Recibe un `CFAttributedString` y genera un `CTFrame` que contiene todo el texto formateado y listo para renderizar dentro de un path (forma geométrica).

### 4. CTFrame

Representa un bloque de texto ya dispuesto dentro de una forma geométrica (`CGPath`). Contiene un array de `CTLine`, cada una representando una línea visible de texto. Es el resultado final del proceso de layout.

### 5. CTLine

Representa una línea de texto dentro de un `CTFrame`. Cada línea contiene uno o más `CTRun` (secuencias de glifos con atributos uniformes). Permite obtener métricas exactas de cada línea.

### 6. CTRun

Es la unidad más granular: una secuencia continua de glifos que comparten los mismos atributos. Dentro de una línea, un cambio de fuente, color o cualquier atributo genera un nuevo run.

**Jerarquía de objetos:**

```
CFAttributedString
    → CTFramesetter
        → CTFrame (dentro de un CGPath)
            → CTLine (una por cada línea visible)
                → CTRun (segmentos con atributos uniformes)
                    → CGGlyph (glifos individuales)
```

## Ejemplo básico

Este ejemplo muestra cómo renderizar texto simple en un `CGContext` usando CoreText:

```swift
import UIKit
import CoreText

/// Vista personalizada que renderiza texto usando CoreText directamente
class BasicCoreTextView: UIView {
    
    // Texto que se va a renderizar
    var text: String = "¡Hola, CoreText! Este es un ejemplo básico de renderizado tipográfico."
    
    override func draw(_ rect: CGRect) {
        // 1. Obtener el contexto gráfico actual
        guard let context = UIGraphicsGetCurrentContext() else { return }
        
        // 2. Voltear el sistema de coordenadas
        // CoreText usa coordenadas con origen abajo-izquierda (como macOS/PDF),
        // pero UIKit usa origen arriba-izquierda. Debemos transformar.
        context.textMatrix = .identity
        context.translateBy(x: 0, y: bounds.height)
        context.scaleBy(x: 1.0, y: -1.0)
        
        // 3. Crear los atributos del texto
        let font = CTFontCreateWithName("Avenir-Medium" as CFString, 20.0, nil)
        let attributes: [NSAttributedString.Key: Any] = [
            .font: font,
            .foregroundColor: UIColor.label.cgColor
        ]
        
        // 4. Crear la cadena atribuida
        let attributedString = NSAttributedString(string: text, attributes: attributes)
        
        // 5. Crear el framesetter a partir de la cadena atribuida
        let framesetter = CTFramesetterCreateWithAttributedString(attributedString as CFAttributedString)
        
        // 6. Definir el path donde se renderizará el texto
        let path = CGMutablePath()
        let textRect = bounds.insetBy(dx: 16, dy: 16) // Margen de 16pt
        path.addRect(textRect)
        
        // 7. Crear el frame de texto
        let frame = CTFramesetterCreateFrame(framesetter, CFRange(location: 0, length: 0), path, nil)
        
        // 8. Dibujar el frame en el contexto
        CTFrameDraw(frame, context)
    }
}
```

## Ejemplo intermedio

Este ejemplo muestra texto multi-estilo con columnas, un caso de uso real para aplicaciones editoriales:

```swift
import UIKit
import CoreText

/// Vista que renderiza texto en múltiples columnas con estilos variados
class MultiColumnCoreTextView: UIView {
    
    // Número de columnas
    var numberOfColumns: Int = 2
    
    // Espaciado entre columnas
    var columnSpacing: CGFloat = 20.0
    
    // Contenido atribuido
    var attributedContent: NSAttributedString?
    
    /// Configura el contenido con múltiples estilos tipográficos
    func configureContent() {
        let fullText = NSMutableAttributedString()
        
        // — Título con fuente grande y negrita —
        let titleFont = CTFontCreateWithName("Georgia-Bold" as CFString, 28.0, nil)
        let titleAttributes: [NSAttributedString.Key: Any] = [
            .font: titleFont,
            .foregroundColor: UIColor.systemIndigo.cgColor
        ]
        let title = NSAttributedString(
            string: "El Arte de la Tipografía Digital\n\n",
            attributes: titleAttributes
        )
        fullText.append(title)
        
        // — Cuerpo con fuente regular y ajuste de interlineado —
        let bodyFont = CTFontCreateWithName("Avenir-Book" as CFString, 15.0, nil)
        
        // Configurar estilo de párrafo con interlineado personalizado
        let paragraphSettings: [CTParagraphStyleSetting] = createParagraphSettings(
            lineSpacing: 6.0,
            paragraphSpacing: 12.0
        )
        let paragraphStyle = CTParagraphStyleCreate(paragraphSettings, paragraphSettings.count)
        
        let bodyAttributes: [NSAttributedString.Key: Any] = [
            .font: bodyFont,
            .foregroundColor: UIColor.label.cgColor,
            .paragraphStyle: paragraphStyle
        ]
        
        let bodyText = """
        CoreText es el framework de bajo nivel de Apple para controlar la tipografía. \
        Permite a los desarrolladores crear experiencias de lectura sofisticadas con \
        control total sobre cada aspecto del renderizado de texto.

        A diferencia de UILabel o SwiftUI Text, CoreText expone métricas de glifos, \
        permite fluir texto en formas arbitrarias y ofrece rendimiento óptimo para \
        escenarios exigentes como editores de texto o lectores de libros digitales.

        Este ejemplo demuestra cómo distribuir texto en múltiples columnas, una técnica \
        fundamental en aplicaciones de maquetación editorial profesional.
        """
        
        let body = NSAttributedString(string: bodyText, attributes: bodyAttributes)
        fullText.append(body)
        
        // — Texto destacado en itálica —
        let italicFont = CTFontCreateWithName("Avenir-BookOblique" as CFString, 14.0, nil)
        let italicAttributes: [NSAttributedString.Key: Any] = [
            .font: italicFont,
            .foregroundColor: UIColor.secondaryLabel.cgColor
        ]
        let footnote = NSAttributedString(
            string: "\n\nNota: Este texto se renderiza completamente con CoreText.",
            attributes: italicAttributes
        )
        fullText.append(footnote)
        
        self.attributedContent = fullText
        setNeedsDisplay()
    }
    
    /// Crea la configuración de estilo de párrafo
    private func createParagraphSettings(
        lineSpacing: CGFloat,
        paragraphSpacing: CGFloat
    ) -> [CTParagraphStyleSetting] {
        var lineSpacingValue = lineSpacing
        var paragraphSpacingValue = paragraphSpacing
        
        let settings: [CTParagraphStyleSetting] = [
            CTParagraphStyleSetting(
                spec: .lineSpacingAdjust,
                valueSize: MemoryLayout<CGFloat>.size,
                value: &lineSpacingValue
            ),
            CTParagraphStyleSetting(
                spec: .paragraphSpacingBefore,
                valueSize: MemoryLayout<CGFloat>.size,
                value: &paragraphSpacingValue
            )
        ]
        return settings
    }
    
    override func draw(_ rect: CGRect) {
        guard let context = UIGraphicsGetCurrentContext(),
              let attributedString = attributedContent else { return }
        
        // Transformar coordenadas (CoreText → UIKit)
        context.textMatrix = .identity
        context.translateBy(x: 0, y: bounds.height)
        context.scaleBy(x: 1.0, y: -1.0)
        
        // Crear el framesetter
        let framesetter = CTFramesetterCreateWithAttributedString(
            attributedString as CFAttributedString
        )
        
        // Calcular dimensiones de las columnas
        let contentRect = bounds.insetBy(dx: 16, dy: 16)
        let columnWidth = (contentRect.width - columnSpacing * CGFloat(numberOfColumns - 1))
            / CGFloat(numberOfColumns)
        
        var textOffset: CFIndex = 0
        let totalLength = attributedString.length
        
        // Iterar sobre cada columna y renderizar la porción correspondiente
        for column in 0..<numberOfColumns {
            guard textOffset < totalLength else { break }
            
            // Calcular el rectángulo de la columna
            let columnX = contentRect.origin.x + CGFloat(column) * (columnWidth + columnSpacing)
            let columnRect = CGRect(
                x: columnX,
                y: contentRect.origin.y,
                width: columnWidth,
                height: contentRect.height
            )
            
            let columnPath = CGMutablePath()
            columnPath.addRect(columnRect)
            
            // Crear el frame para esta columna
            let frameRange = CFRange(location: textOffset, length: 0) // 0 = hasta donde quepa
            let frame = CTFramesetterCreateFrame(framesetter, frameRange, columnPath, nil)
            
            // Dibujar el frame
            CTFrameDraw(frame, context)
            
            // Obtener el rango visible para saber dónde continuar en la siguiente columna
            let visibleRange = CTFrameGetVisibleStringRange(frame)
            textOffset += visibleRange.length
        }
    }
}
```

## Ejemplo avanzado

Este ejemplo implementa un sistema completo con arquitectura MVVM para renderizar texto enriquecido con detección de enlaces y métricas tipográficas:

```swift
import UIKit
import CoreText
import Combine

// MARK: - Modelo

/// Representa un bloque de contenido con metadatos tipográficos
struct RichTextContent {
    let attributedString: NSAttributedString
    let links: [TextLink]
    
    struct TextLink {
        let url: URL
        let range: NSRange
        let displayText: String
    }
}

/// Métricas calculadas del texto renderizado
struct TextLayoutMetrics {
    let totalLines: Int
    let totalHeight: CGFloat
    let lineMetrics