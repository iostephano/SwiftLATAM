---
sidebar_position: 1
title: Machine Learning
---

# Machine Learning en iOS

## ¿Qué es Machine Learning?

Machine Learning (ML) es una rama de la inteligencia artificial que permite a las aplicaciones **aprender patrones a partir de datos** y tomar decisiones sin ser programadas explícitamente para cada caso. En lugar de escribir reglas manuales del tipo "si X entonces Y", entrenas un modelo con miles de ejemplos y este aprende a generalizar.

En el ecosistema Apple, Machine Learning se integra de forma nativa a través de **Core ML**, un framework que permite ejecutar modelos de ML directamente en el dispositivo del usuario, sin necesidad de conexión a internet ni servidores externos.

---

## ¿Por qué es importante para un desarrollador iOS en LATAM?

La adopción de ML en aplicaciones móviles está creciendo exponencialmente, y Latinoamérica no es la excepción. Estas son razones concretas por las que deberías dominar este tema:

1. **Diferenciación profesional**: Muy pocos desarrolladores iOS en la región dominan Core ML. Esto te posiciona como un perfil altamente competitivo para empresas locales e internacionales.

2. **Demanda real en la industria**: Fintechs como Nubank, Mercado Libre y Rappi integran ML para detección de fraude, recomendaciones personalizadas y procesamiento de documentos. Estas empresas buscan activamente talento en LATAM.

3. **Privacidad como ventaja**: Core ML ejecuta todo **on-device**. En un contexto donde las regulaciones de datos (como la Ley de Protección de Datos en México, Brasil y Colombia) son cada vez más estrictas, procesar datos localmente es una ventaja enorme.

4. **Resolución de problemas locales**: Clasificación de cultivos agrícolas, detección de enfermedades en zonas rurales, traducción de lenguas indígenas... ML abre puertas para resolver problemas específicos de nuestra región.

5. **Trabajo remoto internacional**: Empresas en Estados Unidos y Europa pagan salarios premium por desarrolladores iOS que integren capacidades de ML. Dominar esta habilidad amplía tus oportunidades de trabajo remoto significativamente.

---

## El ecosistema de ML en Apple

Apple ofrece un stack completo para trabajar con Machine Learning:

```
┌─────────────────────────────────────────────┐
│           Tu Aplicación iOS                 │
├─────────────────────────────────────────────┤
│  Vision  │  Natural Language  │  Speech     │  ← Frameworks de alto nivel
├─────────────────────────────────────────────┤
│              Core ML                        │  ← Motor de inferencia
├─────────────────────────────────────────────┤
│    Accelerate   │   Metal Performance       │  ← Hardware optimizado
│                 │   Shaders (MPS)           │
├─────────────────────────────────────────────┤
│    CPU    │    GPU    │    Neural Engine     │  ← Hardware del dispositivo
└─────────────────────────────────────────────┘
```

### Frameworks principales

| Framework | Uso principal | Ejemplo |
|-----------|--------------|---------|
| **Core ML** | Ejecutar modelos de ML en el dispositivo | Clasificación de imágenes, predicciones |
| **Vision** | Análisis de imágenes y video | Detección de rostros, texto en imágenes |
| **Natural Language** | Procesamiento de texto | Análisis de sentimiento, idioma |
| **Speech** | Reconocimiento de voz | Transcripción de audio a texto |
| **Sound Analysis** | Clasificación de sonidos | Detectar llanto de bebé, alarmas |
| **Create ML** | Entrenar modelos sin código | Crear modelos personalizados en Mac |

---

## Tu primer modelo con Core ML

Vamos a construir un clasificador de imágenes paso a paso.

### Paso 1: Obtener un modelo

Apple proporciona modelos preentrenados en [su sitio oficial](https://developer.apple.com/machine-learning/models/). Descarga **MobileNetV2**, un modelo liviano para clasificación de imágenes.

El archivo tendrá la extensión `.mlmodel`. Simplemente arrástralo a tu proyecto en Xcode.

### Paso 2: Explorar el modelo generado

Cuando agregas un `.mlmodel` a tu proyecto, Xcode genera automáticamente una clase Swift. Haz clic en el archivo para ver sus entradas y salidas:

- **Entrada**: Una imagen de 224×224 píxeles
- **Salida**: La clasificación (etiqueta) y las probabilidades de cada categoría

### Paso 3: Implementar la clasificación

```swift
import UIKit
import CoreML
import Vision

class ImageClassifierViewController: UIViewController {

    @IBOutlet weak var imageView: UIImageView!
    @IBOutlet weak var resultLabel: UILabel!

    // MARK: - Modelo Core ML

    private lazy var classificationRequest: VNCoreMLRequest = {
        do {
            // Cargar el modelo MobileNetV2
            let configuration = MLModelConfiguration()
            configuration.computeUnits = .all // Usa CPU, GPU y Neural Engine

            let model = try MobileNetV2(configuration: configuration)
            let vnModel = try VNCoreMLModel(for: model.model)

            let request = VNCoreMLRequest(model: vnModel) { [weak self] request, error in
                self?.processClassificationResults(request: request, error: error)
            }

            // Ajustar la imagen al tamaño que espera el modelo
            request.imageCropAndScaleOption = .centerCrop

            return request
        } catch {
            fatalError("Error al cargar el modelo: \(error)")
        }
    }()

    // MARK: - Clasificar imagen

    func classifyImage(_ image: UIImage) {
        guard let ciImage = CIImage(image: image) else {
            resultLabel.text = "No se pudo procesar la imagen"
            return
        }

        // Ejecutar la inferencia en un hilo secundario
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }

            let handler = VNImageRequestHandler(ciImage: ciImage, options: [:])

            do {
                try handler.perform([self.classificationRequest])
            } catch {
                print("Error al clasificar: \(error)")
            }
        }
    }

    // MARK: - Procesar resultados

    private func processClassificationResults(request: VNRequest, error: Error?) {
        guard let results = request.results as? [VNClassificationObservation] else {
            return
        }

        // Obtener los 3 resultados más probables
        let topResults = results.prefix(3)

        let resultText = topResults.map { observation in
            let confidence = (observation.confidence * 100).rounded()
            return "\(observation.identifier): \(confidence)%"
        }.joined(separator: "\n")

        // Actualizar la UI en el hilo principal
        DispatchQueue.main.async { [weak self] in
            self?.resultLabel.text = resultText
        }
    }
}
```

### Paso 4: Integrar con la cámara

```swift
import UIKit

extension ImageClassifierViewController: UIImagePickerControllerDelegate,
                                         UINavigationControllerDelegate {

    @IBAction func takePhotoTapped(_ sender: UIButton) {
        let picker = UIImagePickerController()
        picker.delegate = self
        picker.sourceType = .camera // O .photoLibrary para galería
        picker.allowsEditing = true
        present(picker, animated: true)
    }

    func imagePickerController(
        _ picker: UIImagePickerController,
        didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]
    ) {
        dismiss(animated: true)

        guard let image = info[.editedImage] as? UIImage ?? info[.originalImage] as? UIImage else {
            return
        }

        imageView.image = image
        resultLabel.text = "Analizando..."

        // Clasificar la imagen seleccionada
        classifyImage(image)
    }
}
```

---

## Ejemplo práctico: Análisis de sentimiento en texto

Este ejemplo es especialmente útil para apps de redes sociales, encuestas o análisis de reseñas:

```swift
import NaturalLanguage

struct SentimentAnalyzer {

    enum Sentiment: String {
        case positive = "😊 Positivo"
        case negative = "😞 Negativo"
        case neutral = "😐 Neutro"
    }

    /// Analiza el sentimiento de un texto dado
    /// - Parameter text: El texto a analizar
    /// - Returns: El sentimiento detectado con su puntuación
    func analyze(_ text: String) -> (sentiment: Sentiment, score: Double) {
        let tagger = NLTagger(tagSchemes: [.sentimentScore])
        tagger.string = text

        let (tag, _) = tagger.tag(
            at: text.startIndex,
            unit: .paragraph,
            scheme: .sentimentScore
        )

        // El score va de -1.0 (muy negativo) a 1.0 (muy positivo)
        let score = Double(tag?.rawValue ?? "0") ?? 0.0

        let sentiment: Sentiment
        switch score {
        case 0.1...:
            sentiment = .positive
        case ..<(-0.1):
            sentiment = .negative
        default:
            sentiment = .neutral
        }

        return (sentiment, score)
    }
}

// Uso
let analyzer = SentimentAnalyzer()

let reviews = [
    "¡Esta app es increíble! La mejor que he usado",
    "Pésimo servicio, nunca más vuelvo a comprar aquí",
    "El producto llegó en buen estado",
    "Me encanta la comida de este restaurante, totalmente recomendado",
    "Muy malo, no funciona para nada"
]

for review in reviews {
    let result = analyzer.analyze(review)
    print("\(result.sentiment.rawValue) (\(result.score)): \(review)")
}
```

---

## Crear tu propio modelo con Create ML

No siempre necesitas modelos preentrenados. Con **Create ML** puedes entrenar modelos personalizados directamente en tu Mac.

### Ejemplo: Clasificador de frutas

```swift
import CreateML
import Foundation

// Este código se ejecuta en un Playground de macOS o en un script

// 1. Definir las rutas de datos de entrenamiento
// La estructura de carpetas debe ser:
// TrainingData/
//   ├── manzana/
//   │   ├── img001.jpg
//   │   ├── img002.jpg
//   │   └── ...
//   ├── banana/
//   │   ├── img001.jpg
//   │   └── ...
//   └── naranja/
//       ├── img001.jpg
//       └── ...

let trainingDataURL = URL(fileURLWithPath: "/path/to/TrainingData")
let testingDataURL = URL(fileURLWithPath: "/path/to/TestingData")

do {
    // 2. Crear las fuentes de datos
    let trainingData = MLImageClassifier.DataSource.labeledDirectories(at: trainingDataURL)
    let testingData = MLImageClassifier.DataSource.labeledDirectories(at: testingDataURL)

    // 3. Configurar y entrenar el modelo
    let parameters = MLImageClassifier.ModelParameters(
        validation: .split(strategy: .automatic),
        maxIterations: 20,
        augmentation: [.crop, .blur, .exposure, .flip, .rotation, .noise]
    )

    let classifier = try MLImageClassifier(
        trainingData: trainingData,
        parameters: parameters
    )

    // 4. Evaluar el modelo
    let evaluation = classifier.evaluation(on: testingData)
    print("Precisión del modelo: \(evaluation)")

    // 5. Guardar el modelo como .mlmodel
    let metadata = MLModelMetadata(
        author: "Tu Nombre",
        shortDescription: "Clasificador de frutas tropicales",
        version: "1.0"
    )

    try classifier.write(
        to: URL(fileURLWithPath: "/path/to/FruitClassifier.mlmodel"),
        metadata: metadata
    )

    print("✅ Modelo guardado exitosamente")
} catch {
    print("❌ Error: \(error)")
}
```

### Alternativa visual: Create ML App

Si prefieres no escribir código para entrenar, abre **Create ML** desde Xcode (Xcode → Open Developer Tool → Create ML) y usa la interfaz gráfica:

1. Crea un nuevo proyecto de tipo **Image Classifier**
2. Arrastra tu carpeta de imágenes de entrenamiento
3. Haz clic en **Train**
4. Prueba el modelo con la pestaña **Preview**
5. Exporta el `.mlmodel` y agrégalo a tu proyecto

---

## Detección de objetos en tiempo real con Vision

Un caso de uso avanzado es detectar objetos usando la cámara en tiempo real:

```swift
import AVFoundation
import Vision
import UIKit

class RealtimeDetectionViewController: UIViewController {

    private let captureSession = AVCaptureSession()
    private var previewLayer: AVCaptureVideoPreviewLayer!
    private var detectionOverlay: CALayer!

    // MARK: - Configuración del modelo

    private lazy var detectionRequest: VNCoreMLRequest = {
        guard let model = try? VNCoreMLModel(for: YOLOv3Tiny(configuration: .init()).model) else {
            fatalError("No se pudo cargar el modelo de detección")
        }

        let request = VNCoreMLRequest(model: model) { [weak self] request, error in
            self?.handleDetectionResults(request: request)
        }

        request.imageCropAndScaleOption = .scaleFill
        return request
    }()

    // MARK: - Ciclo de vida

    override func viewDidLoad() {
        super.viewDidLoad()
        setupCamera()
        setupOverlay()
    }

    // MARK: - Configuración de la cámara

    private func setupCamera() {
        guard let camera = AVCaptureDevice.default(.builtInWideAngleCamera,
                                                    for: .video,
                                                    position: .back),
              let input = try? AVCaptureDeviceInput(device: camera) else {
            return
        }

        captureSession.addInput(input)

        let output = AVCaptureVideoDataOutput()
        output.setSampleBufferDelegate(self, queue: DispatchQueue(label: "ml.detection"))
        captureSession.addOutput(output)

        previewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
        previewLayer.frame = view.bounds
        previewLayer.videoGravity = .resizeAspectFill
        view.layer.addSublayer(previewLayer)

        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            self?.captureSession.startRunning()
        }
    }

    private func setupOverlay() {
        detectionOverlay = CALayer()
        detectionOverlay.frame = view.bounds
        view.layer.addSublayer(detectionOverlay)
    }

    // MARK: - Procesar detecciones

    private func handleDetectionResults(request: VNRequest) {
        guard let results = request.results as? [VNRecognizedObjectObservation] else { return }

        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }

            // Limpiar las cajas anteriores
            self.detectionOverlay.sublayers?.forEach { $0