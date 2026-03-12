---
sidebar_position: 1
title: CreateML
---

# CreateML

## ¿Qué es CreateML?

CreateML es el framework de Apple diseñado para que los desarrolladores puedan **crear, entrenar y evaluar modelos de Machine Learning** directamente dentro del ecosistema Apple, sin necesidad de ser expertos en inteligencia artificial. Introducido en WWDC 2018 y mejorado significativamente en cada iteración posterior, CreateML permite generar modelos CoreML (.mlmodel) que se integran de forma nativa con las aplicaciones de iOS, macOS, watchOS y tvOS.

La filosofía detrás de CreateML es la **democratización del aprendizaje automático**. En lugar de requerir frameworks complejos como TensorFlow o PyTorch, y luego convertir los modelos a un formato compatible, CreateML ofrece APIs de alto nivel que abstraen la complejidad del entrenamiento. Utiliza técnicas como **transfer learning** (aprendizaje por transferencia), lo que permite obtener modelos precisos con conjuntos de datos relativamente pequeños y tiempos de entrenamiento significativamente reducidos.

CreateML soporta múltiples tipos de tareas de Machine Learning: **clasificación de imágenes, detección de objetos, clasificación de texto, análisis de sentimiento, clasificación de sonidos, predicción tabular, recomendaciones, detección de actividad corporal y análisis de series temporales**, entre otros. Puede utilizarse tanto a través de la app CreateML (interfaz gráfica incluida en Xcode) como mediante su API programática (`CreateML` framework), lo que lo hace ideal tanto para prototipado rápido como para pipelines de entrenamiento automatizado.

## Casos de uso principales

- **Clasificación de imágenes**: Entrenar un modelo que distinga entre diferentes categorías de objetos, como tipos de plantas, razas de animales o defectos en productos de manufactura. Ideal para apps de fotografía, agricultura o control de calidad.

- **Detección de objetos en imágenes**: Identificar y localizar múltiples objetos dentro de una imagen con sus coordenadas (bounding boxes). Útil en aplicaciones de realidad aumentada, inventarios automatizados o asistencia visual.

- **Análisis de texto y sentimiento**: Clasificar reseñas de usuarios como positivas o negativas, categorizar tickets de soporte automáticamente o filtrar contenido inapropiado en tiempo real dentro de la aplicación.

- **Clasificación de sonidos**: Reconocer sonidos ambientales como ladridos, sirenas, aplausos o comandos específicos. Aplicable en apps de accesibilidad, monitoreo del hogar o experiencias de audio interactivas.

- **Predicción tabular (regresión y clasificación)**: Predecir valores numéricos o categorías a partir de datos estructurados, como estimar precios de propiedades, predecir rotación de clientes (churn) o clasificar niveles de riesgo.

- **Sistemas de recomendación**: Generar recomendaciones personalizadas de productos, contenido o experiencias basándose en el comportamiento histórico del usuario, similar a lo que hacen plataformas de streaming o e-commerce.

## Instalación y configuración

### Requisitos del sistema

CreateML requiere **macOS** para el entrenamiento de modelos (no se puede entrenar en iOS). Los modelos resultantes sí pueden desplegarse en cualquier plataforma Apple.

- **Xcode 11+** (recomendado Xcode 15 o superior)
- **macOS Catalina 10.15+** (recomendado macOS Sonoma 14+ para las últimas funcionalidades)
- Para entrenamiento acelerado por GPU: Mac con chip Apple Silicon (M1 o superior)

### Agregar el framework al proyecto

No es necesario instalar dependencias externas. CreateML viene integrado en el SDK de macOS:

```swift
// En tu archivo Swift de entrenamiento (proyecto macOS)
import CreateML

// Para usar el modelo resultante en iOS/macOS
import CoreML
```

### Configuración del proyecto

1. **Para entrenamiento**: Crea un proyecto macOS (Command Line Tool o App) o usa un Swift Playground en Xcode.
2. **Para inferencia**: En tu app iOS/iPadOS, simplemente arrastra el archivo `.mlmodel` generado al proyecto Xcode.

```
📁 MiProyectoDeEntrenamiento (macOS)
├── main.swift          // Lógica de entrenamiento
├── DatosEntrenamiento/ // Carpeta con datasets
│   ├── Gatos/
│   ├── Perros/
│   └── Pájaros/
└── ModelosExportados/  // Carpeta de salida
```

### Permisos en Info.plist

CreateML en sí no requiere permisos especiales. Sin embargo, si tu app que **consume** el modelo necesita acceder a cámara, micrófono o fotos, deberás agregar las claves correspondientes:

```xml
<!-- Solo si la app de inferencia usa cámara -->
<key>NSCameraUsageDescription</key>
<string>Necesitamos acceso a la cámara para clasificar objetos en tiempo real</string>

<!-- Solo si la app de inferencia usa micrófono -->
<key>NSMicrophoneUsageDescription</key>
<string>Necesitamos acceso al micrófono para clasificar sonidos</string>

<!-- Solo si la app accede a la galería de fotos -->
<key>NSPhotoLibraryUsageDescription</key>
<string>Necesitamos acceso a tus fotos para analizarlas</string>
```

## Conceptos clave

### 1. Transfer Learning (Aprendizaje por transferencia)

Es la técnica fundamental que CreateML utiliza internamente. En lugar de entrenar una red neuronal desde cero (lo cual requiere millones de imágenes y días de cómputo), se parte de un modelo pre-entrenado por Apple con millones de datos y se **ajustan las capas superiores** con tus datos específicos. Esto permite obtener modelos precisos con tan solo **decenas o cientos de ejemplos por categoría** y tiempos de entrenamiento de minutos en lugar de horas.

### 2. Datasets y Data Sources

CreateML trabaja con diferentes fuentes de datos según el tipo de tarea. Para imágenes, utiliza carpetas organizadas donde **cada subcarpeta representa una clase**. Para datos tabulares, acepta archivos CSV o JSON. Para texto, arrays de cadenas con sus etiquetas. La clase `MLDataTable` es la estructura central para datos tabulares, permitiendo operaciones de filtrado, transformación y partición de datos.

### 3. Modelo CoreML (.mlmodel)

Es el formato de archivo de salida que genera CreateML. Este archivo encapsula la arquitectura de la red neuronal, los pesos entrenados y los metadatos necesarios. Los archivos `.mlmodel` son **compilados por Xcode** en tiempo de build a un formato optimizado (`.mlmodelc`) que se ejecuta de manera eficiente en el dispositivo usando el framework CoreML con aceleración de Neural Engine, GPU o CPU según disponibilidad.

### 4. Métricas de evaluación

CreateML proporciona automáticamente métricas de rendimiento durante y después del entrenamiento. Las más importantes son: **accuracy** (precisión general), **precision** (de las predicciones positivas, cuántas son correctas), **recall** (de los positivos reales, cuántos se detectaron) y **F1-score** (media armónica de precision y recall). Es fundamental evaluar estas métricas con datos de **validación** que el modelo no haya visto durante el entrenamiento.

### 5. Augmentación de datos (Data Augmentation)

Técnica que CreateML soporta de forma nativa para imágenes, donde se generan variaciones artificiales de los datos de entrenamiento (rotaciones, recortes, cambios de brillo, volteos) para **aumentar la diversidad del dataset sin necesidad de recolectar más datos**. Esto mejora significativamente la capacidad de generalización del modelo y reduce el sobreajuste (overfitting).

### 6. Training Session y Checkpoints

CreateML permite **pausar, reanudar y monitorear sesiones de entrenamiento**. Durante el proceso, se generan checkpoints que guardan el estado del modelo en diferentes etapas. Esto es especialmente útil en entrenamientos largos, permitiendo recuperarse de interrupciones y seleccionar el mejor modelo de entre todas las épocas de entrenamiento.

## Ejemplo básico

Este ejemplo muestra cómo entrenar un clasificador de imágenes desde un script macOS:

```swift
import CreateML
import Foundation

// MARK: - Clasificador de imágenes básico
// Este script entrena un modelo que distingue entre gatos, perros y pájaros
// usando carpetas de imágenes organizadas por categoría

// 1. Definir las rutas de datos
// La estructura esperada es:
// DatosEntrenamiento/
//   ├── Gatos/     (imágenes de gatos)
//   ├── Perros/    (imágenes de perros)
//   └── Pájaros/   (imágenes de pájaros)
let directorioEntrenamiento = URL(fileURLWithPath: "/Users/tu_usuario/DatosEntrenamiento")
let directorioPrueba = URL(fileURLWithPath: "/Users/tu_usuario/DatosPrueba")

// 2. Crear el origen de datos para entrenamiento
// CreateML infiere las etiquetas automáticamente del nombre de las carpetas
let datosEntrenamiento = MLImageClassifier.DataSource.labeledDirectories(
    at: directorioEntrenamiento
)

// 3. Configurar los parámetros de entrenamiento
let parametros = MLImageClassifier.ModelParameters(
    validation: .split(strategy: .automatic), // 80% entrenamiento, 20% validación
    maxIterations: 25,                         // Número máximo de épocas
    augmentation: [.crop, .blur, .flip(axis: .horizontal), .rotation()] // Aumentación
)

// 4. Entrenar el modelo
do {
    let clasificador = try MLImageClassifier(
        trainingData: datosEntrenamiento,
        parameters: parametros
    )
    
    // 5. Evaluar el modelo con datos de prueba
    let metricasEvaluacion = clasificador.evaluation(
        on: .labeledDirectories(at: directorioPrueba)
    )
    
    print("✅ Entrenamiento completado")
    print("📊 Precisión en datos de prueba: \(metricasEvaluacion.classificationError)")
    
    // 6. Configurar metadatos del modelo
    let metadatos = MLModelMetadata(
        author: "Tu Nombre",
        shortDescription: "Clasificador de mascotas: gatos, perros y pájaros",
        version: "1.0"
    )
    
    // 7. Guardar el modelo entrenado
    let rutaSalida = URL(fileURLWithPath: "/Users/tu_usuario/ClasificadorMascotas.mlmodel")
    try clasificador.write(to: rutaSalida, metadata: metadatos)
    
    print("💾 Modelo guardado en: \(rutaSalida.path)")
    
} catch {
    print("❌ Error durante el entrenamiento: \(error.localizedDescription)")
}
```

## Ejemplo intermedio

Este ejemplo muestra un clasificador de texto para análisis de sentimiento con datos tabulares:

```swift
import CreateML
import Foundation

// MARK: - Clasificador de texto para análisis de sentimiento
// Entrena un modelo que clasifica reseñas de usuarios como positivas o negativas

// 1. Cargar datos desde un archivo CSV
// El CSV debe tener columnas: "texto" y "sentimiento"
// Ejemplo:
// texto,sentimiento
// "Excelente producto, muy recomendado",positivo
// "Pésimo servicio, no volvería",negativo
let archivoCSV = URL(fileURLWithPath: "/Users/tu_usuario/resenas.csv")

do {
    // 2. Crear una tabla de datos desde el CSV
    let tablaDatos = try MLDataTable(contentsOf: archivoCSV)
    
    // 3. Dividir en datos de entrenamiento y prueba (80/20)
    let (datosEntrenamiento, datosPrueba) = tablaDatos.randomSplit(
        by: 0.8,
        seed: 42 // Semilla para reproducibilidad
    )
    
    print("📋 Total de registros: \(tablaDatos.rows.count)")
    print("📚 Registros de entrenamiento: \(datosEntrenamiento.rows.count)")
    print("🧪 Registros de prueba: \(datosPrueba.rows.count)")
    
    // 4. Configurar parámetros del clasificador de texto
    let parametros = MLTextClassifier.ModelParameters(
        validation: .dataSource(.table(datosPrueba)),
        algorithm: .maxEnt(revision: 1),  // Maximum Entropy
        language: .spanish                  // ¡Importante para texto en español!
    )
    
    // 5. Entrenar el clasificador de texto
    let clasificadorTexto = try MLTextClassifier(
        trainingData: datosEntrenamiento,
        textColumn: "texto",         // Nombre de la columna con el texto
        labelColumn: "sentimiento",  // Nombre de la columna con las etiquetas
        parameters: parametros
    )
    
    // 6. Evaluar el modelo
    let metricas = clasificadorTexto.evaluation(on: datosPrueba, textColumn: "texto", labelColumn: "sentimiento")
    
    print("\n📊 Métricas de evaluación:")
    print("   Precisión: \(metricas.classificationError)")
    print("   Matriz de confusión: \(metricas.confusion)")
    
    // 7. Probar predicciones individuales
    let textosDePrueba = [
        "Me encanta esta aplicación, funciona perfecto",
        "Horrible experiencia, se cierra constantemente",
        "Buen diseño pero le faltan funciones",
        "La mejor compra que he hecho en años"
    ]
    
    print("\n🔮 Predicciones de ejemplo:")
    for texto in textosDePrueba {
        let prediccion = try clasificadorTexto.prediction(from: texto)
        print("   \"\(texto)\" → \(prediccion)")
    }
    
    // 8. Guardar el modelo
    let metadatos = MLModelMetadata(
        author: "Tu Nombre",
        shortDescription: "Clasificador de sentimiento para reseñas en español",
        version: "1.0"
    )
    
    try clasificadorTexto.write(
        to: URL(fileURLWithPath: "/Users/tu_usuario/AnalizadorSentimiento.mlmodel"),
        metadata: metadatos
    )
    
    print("\n✅ Modelo guardado exitosamente")
    
} catch {
    print("❌ Error: \(error.localizedDescription)")
}

// MARK: - Predictor tabular (Regresión)
// Ejemplo adicional: predecir el precio de una propiedad

func entrenarPredictorPrecios() throws {
    let archivoCSV = URL(fileURLWithPath: "/Users/tu_usuario/propiedades.csv")
    let tabla = try MLDataTable(contentsOf: archivoCSV)
    let (entrenamiento, prueba) = tabla.randomSplit(by: 0.8, seed: 42)
    
    // Entrenar un regresor para predecir precios
    let regresor = try MLRegressor(
        trainingData: entrenamiento,
        targetColumn: "precio" // Columna numérica a predecir
    )
    
    // Evaluar con métricas de regresión
    let metricas = regresor.evaluation(on: prueba)
    print("