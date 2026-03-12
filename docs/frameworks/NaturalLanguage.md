---
sidebar_position: 1
title: NaturalLanguage
---

# NaturalLanguage

## ¿Qué es NaturalLanguage?

**NaturalLanguage** es un framework de Apple que proporciona herramientas de procesamiento de lenguaje natural (NLP) para analizar, comprender y generar texto en múltiples idiomas. Fue introducido en iOS 12 y macOS 10.14, y desde entonces ha evolucionado significativamente, permitiendo a los desarrolladores integrar capacidades lingüísticas avanzadas sin depender de servicios externos ni de bibliotecas de terceros.

El framework ofrece funcionalidades que van desde la identificación del idioma de un texto y la tokenización (segmentación en palabras, oraciones o párrafos), hasta el análisis de sentimiento, el reconocimiento de entidades nombradas (personas, lugares, organizaciones), la lematización y la generación de embeddings de palabras y oraciones. Todo esto se ejecuta de forma local en el dispositivo, lo que garantiza la privacidad del usuario y un rendimiento consistente incluso sin conexión a internet.

NaturalLanguage resulta especialmente útil cuando necesitas construir aplicaciones que procesen texto introducido por el usuario, clasifiquen contenido, implementen búsquedas inteligentes, filtren mensajes, ofrezcan sugerencias contextuales o cualquier otra funcionalidad que requiera una comprensión semántica o sintáctica del lenguaje. Además, permite entrenar modelos personalizados con **Create ML** e integrarlos directamente a través de las clases `NLModel` y `NLGazetteer`, lo que abre la puerta a casos de uso altamente especializados.

## Casos de uso principales

### 1. Detección automática de idioma
Identifica en qué idioma está escrito un texto para adaptar la interfaz, seleccionar el modelo de análisis correcto o enrutar contenido a traductores específicos. Soporta más de 60 idiomas.

### 2. Análisis de sentimiento
Determina si un texto tiene una connotación positiva, negativa o neutra. Es ideal para analizar reseñas de productos, comentarios en redes sociales o retroalimentación de usuarios dentro de la aplicación.

### 3. Reconocimiento de entidades nombradas (NER)
Extrae automáticamente nombres de personas, organizaciones, lugares y otros tipos de entidades de un texto. Muy útil para apps de noticias, asistentes personales o herramientas de productividad.

### 4. Tokenización avanzada
Segmenta texto en palabras, oraciones o párrafos respetando las reglas lingüísticas de cada idioma, incluyendo idiomas complejos como el chino, japonés o tailandés donde no hay espacios entre palabras.

### 5. Clasificación de texto personalizada
Entrena modelos con Create ML para clasificar texto en categorías definidas por ti (spam/no spam, temáticas, intenciones del usuario) e intégralos directamente con `NLModel`.

### 6. Búsqueda semántica con embeddings
Utiliza los embeddings de palabras y oraciones para calcular similitudes semánticas entre textos, permitiendo búsquedas inteligentes que van más allá de la coincidencia exacta de palabras.

## Instalación y configuración

### Importación del framework

NaturalLanguage viene incluido de forma nativa en las plataformas de Apple. No necesitas instalar ningún paquete externo ni usar CocoaPods, SPM o Carthage.

```swift
import NaturalLanguage
```

### Compatibilidad de plataformas

| Plataforma | Versión mínima |
|------------|---------------|
| iOS        | 12.0          |
| macOS      | 10.14         |
| tvOS       | 12.0          |
| watchOS    | 5.0           |
| Mac Catalyst | 13.0       |
| visionOS   | 1.0           |

### Permisos en Info.plist

NaturalLanguage **no requiere permisos especiales** en el archivo `Info.plist`, ya que todo el procesamiento se realiza localmente en el dispositivo sin acceder a datos sensibles del usuario como la ubicación, cámara o contactos.

### Configuración en Xcode

1. Abre tu proyecto en Xcode.
2. Selecciona el target de tu aplicación.
3. Ve a **General** → **Frameworks, Libraries, and Embedded Content**.
4. Normalmente no necesitas agregar nada manualmente; basta con `import NaturalLanguage` en tu código.
5. Si deseas usar modelos personalizados, entrena un modelo con **Create ML** y arrastra el archivo `.mlmodel` al proyecto.

```swift
// Imports típicos para un proyecto que usa NaturalLanguage
import Foundation
import NaturalLanguage

// Si vas a integrar con SwiftUI
import SwiftUI

// Si usas modelos personalizados de Create ML
import CoreML
```

## Conceptos clave

### 1. NLLanguageRecognizer

Es la clase encargada de identificar el idioma predominante en un texto. Puede devolver tanto el idioma más probable como un diccionario de hipótesis con sus respectivas probabilidades. Esto es fundamental cuando tu app necesita manejar contenido multilingüe.

```swift
let recognizer = NLLanguageRecognizer()
recognizer.processString("Hola, ¿cómo estás?")
let idioma = recognizer.dominantLanguage // .spanish
```

### 2. NLTokenizer

Segmenta texto en unidades lingüísticas: palabras, oraciones o párrafos. A diferencia de simplemente dividir por espacios, esta clase respeta las reglas gramaticales y sintácticas del idioma detectado, manejando correctamente puntuación, contracciones y scripts sin espacios.

### 3. NLTagger

Es la clase más versátil del framework. Permite etiquetar cada token de un texto con diferentes esquemas de etiquetado: tipo de palabra (sustantivo, verbo, adjetivo), entidad nombrada (persona, lugar, organización), lema, análisis de sentimiento y más. Se pueden aplicar múltiples esquemas simultáneamente.

### 4. NLEmbedding

Representa palabras u oraciones como vectores numéricos en un espacio de alta dimensión. Estos embeddings capturan relaciones semánticas: palabras con significados similares tendrán vectores cercanos. Apple proporciona embeddings preentrenados para varios idiomas y también permite usar embeddings personalizados.

### 5. NLModel

Permite cargar y usar modelos de clasificación de texto o etiquetado entrenados con **Create ML** (o exportados en formato compatible). Es el puente entre el aprendizaje automático personalizado y el procesamiento de lenguaje natural en producción.

### 6. NLGazetteer

Es un diccionario especializado que mapea términos a etiquetas. Se utiliza junto con `NLTagger` para forzar el reconocimiento de entidades específicas de tu dominio (por ejemplo, nombres de productos propios, terminología médica o jurídica) que los modelos genéricos podrían no reconocer.

## Ejemplo básico

```swift
import NaturalLanguage

// =============================================
// EJEMPLO BÁSICO: Detección de idioma y tokenización
// =============================================

/// Detecta el idioma dominante de un texto dado
func detectarIdioma(de texto: String) -> String {
    let recognizer = NLLanguageRecognizer()
    recognizer.processString(texto)
    
    // Obtener el idioma dominante
    guard let idioma = recognizer.dominantLanguage else {
        return "Idioma no identificado"
    }
    
    // Mapear el código de idioma a un nombre legible
    switch idioma {
    case .spanish: return "Español"
    case .english: return "Inglés"
    case .french: return "Francés"
    case .german: return "Alemán"
    case .portuguese: return "Portugués"
    case .italian: return "Italiano"
    default: return "Idioma detectado: \(idioma.rawValue)"
    }
}

/// Divide un texto en palabras individuales usando NLTokenizer
func tokenizarPalabras(de texto: String) -> [String] {
    let tokenizer = NLTokenizer(unit: .word)
    tokenizer.string = texto
    
    var palabras: [String] = []
    
    // Enumerar todos los tokens (palabras) del texto
    tokenizer.enumerateTokens(in: texto.startIndex..<texto.endIndex) { rango, _ in
        let palabra = String(texto[rango])
        palabras.append(palabra)
        return true // Continuar enumerando
    }
    
    return palabras
}

// --- Uso ---
let texto = "El procesamiento de lenguaje natural es fascinante y muy útil."

let idioma = detectarIdioma(de: texto)
print("Idioma detectado: \(idioma)")
// Salida: Idioma detectado: Español

let palabras = tokenizarPalabras(de: texto)
print("Palabras encontradas: \(palabras)")
// Salida: ["El", "procesamiento", "de", "lenguaje", "natural", "es", "fascinante", "y", "muy", "útil"]

// También podemos obtener las probabilidades de múltiples idiomas
let recognizer = NLLanguageRecognizer()
recognizer.processString("This is a test. Esto es una prueba.")
let hipotesis = recognizer.languageHypotheses(withMaximum: 3)
for (idioma, probabilidad) in hipotesis {
    print("\(idioma.rawValue): \(String(format: "%.2f%%", probabilidad * 100))")
}
```

## Ejemplo intermedio

```swift
import NaturalLanguage

// =============================================
// EJEMPLO INTERMEDIO: Análisis completo de texto
// Incluye NER, análisis de sentimiento, lematización
// y clasificación de partes del discurso (POS tagging)
// =============================================

/// Estructura que encapsula los resultados del análisis de un texto
struct AnalisisTexto {
    let idioma: NLLanguage?
    let sentimiento: Double
    let entidades: [EntidadReconocida]
    let partesDelDiscurso: [PalabraClasificada]
    let lemas: [String: String] // palabra -> lema
}

/// Representa una entidad reconocida en el texto
struct EntidadReconocida {
    let texto: String
    let tipo: String // Persona, Lugar, Organización
    let rango: Range<String.Index>
}

/// Representa una palabra con su clasificación gramatical
struct PalabraClasificada {
    let palabra: String
    let categoria: String
}

/// Motor de análisis de lenguaje natural
class MotorNLP {
    
    // MARK: - Análisis de sentimiento
    
    /// Analiza el sentimiento de un texto completo
    /// Retorna un valor entre -1.0 (muy negativo) y 1.0 (muy positivo)
    func analizarSentimiento(de texto: String) -> Double {
        let tagger = NLTagger(tagSchemes: [.sentimentScore])
        tagger.string = texto
        
        // Obtener la puntuación de sentimiento para todo el texto
        let (sentimiento, _) = tagger.tag(
            at: texto.startIndex,
            unit: .paragraph,
            scheme: .sentimentScore
        )
        
        return Double(sentimiento?.rawValue ?? "0") ?? 0.0
    }
    
    // MARK: - Reconocimiento de entidades nombradas
    
    /// Extrae personas, lugares y organizaciones del texto
    func reconocerEntidades(en texto: String) -> [EntidadReconocida] {
        let tagger = NLTagger(tagSchemes: [.nameType])
        tagger.string = texto
        
        // Configurar opciones: omitir puntuación y espacios en blanco
        let opciones: NLTagger.Options = [
            .omitPunctuation,
            .omitWhitespace,
            .joinNames // Unir nombres compuestos como "Nueva York"
        ]
        
        // Definir los tipos de entidades que nos interesan
        let tiposDeInteres: [NLTag] = [
            .personalName,
            .placeName,
            .organizationName
        ]
        
        var entidades: [EntidadReconocida] = []
        
        tagger.enumerateTags(
            in: texto.startIndex..<texto.endIndex,
            unit: .word,
            scheme: .nameType,
            options: opciones
        ) { tag, rango in
            
            guard let tag = tag, tiposDeInteres.contains(tag) else {
                return true // Continuar
            }
            
            let tipoLegible: String
            switch tag {
            case .personalName: tipoLegible = "Persona"
            case .placeName: tipoLegible = "Lugar"
            case .organizationName: tipoLegible = "Organización"
            default: tipoLegible = "Otro"
            }
            
            let entidad = EntidadReconocida(
                texto: String(texto[rango]),
                tipo: tipoLegible,
                rango: rango
            )
            entidades.append(entidad)
            
            return true
        }
        
        return entidades
    }
    
    // MARK: - Clasificación gramatical (POS Tagging)
    
    /// Clasifica cada palabra según su categoría gramatical
    func clasificarPalabras(en texto: String) -> [PalabraClasificada] {
        let tagger = NLTagger(tagSchemes: [.lexicalClass])
        tagger.string = texto
        
        let opciones: NLTagger.Options = [
            .omitPunctuation,
            .omitWhitespace
        ]
        
        var resultado: [PalabraClasificada] = []
        
        tagger.enumerateTags(
            in: texto.startIndex..<texto.endIndex,
            unit: .word,
            scheme: .lexicalClass,
            options: opciones
        ) { tag, rango in
            
            let categoria: String
            switch tag {
            case .noun: categoria = "Sustantivo"
            case .verb: categoria = "Verbo"
            case .adjective: categoria = "Adjetivo"
            case .adverb: categoria = "Adverbio"
            case .pronoun: categoria = "Pronombre"
            case .determiner: categoria = "Determinante"
            case .preposition: categoria = "Preposición"
            case .conjunction: categoria = "Conjunción"
            default: categoria = tag?.rawValue ?? "Desconocido"
            }
            
            resultado.append(PalabraClasificada(
                palabra: String(texto[rango]),
                categoria: categoria
            ))
            
            return true
        }
        
        return resultado
    }
    
    // MARK: - Lematización
    
    /// Obtiene el lema (forma base) de cada palabra del texto
    func lematizar(texto: String) -> [String: String] {
        let tagger = NLTagger(tagSchemes: [.lemma])
        tagger.string = texto
        
        var lemas: [String: String] = [:]
        
        tagger.enumerateTags(
            in: texto.startIndex..<texto.endIndex,
            unit: .word,
            scheme: .lemma,
            options: [.omitPunctuation, .omitWhitespace]
        ) { tag, rango in
            
            let palabra = String(texto[rango])
            if let lema = tag?.rawValue {
                lemas[palabra] = lema
            }
            
            