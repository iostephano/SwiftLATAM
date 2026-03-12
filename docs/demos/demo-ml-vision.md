---
sidebar_position: 1
title: Demo Ml Vision
---

# Demo ML Vision: Reconocimiento de Imágenes con Core ML y Vision en iOS

## ¿Qué es ML Vision?

**ML Vision** se refiere a la combinación de dos frameworks nativos de Apple: **Core ML** y **Vision**. Juntos permiten integrar modelos de aprendizaje automático para analizar imágenes y video en tiempo real, directamente en el dispositivo del usuario, sin necesidad de conexión a internet ni servidores externos.

- **Vision**: Framework que proporciona APIs de alto nivel para detección de rostros, texto, códigos de barras, objetos y más.
- **Core ML**: Motor de inferencia que ejecuta modelos de machine learning optimizados para hardware Apple (Neural Engine, GPU, CPU).

La combinación de ambos te permite construir experiencias como:

- Clasificación de imágenes (¿qué hay en esta foto?)
- Detección y reconocimiento de objetos
- Reconocimiento de texto (OCR)
- Detección de rostros y landmarks faciales
- Análisis de escenas en tiempo real con la cámara

## ¿Por qué es importante para un dev iOS en LATAM?

En Latinoamérica, la conectividad a internet no siempre es estable ni rápida. **Procesar inteligencia artificial directamente en el dispositivo** (on-device ML) elimina la dependencia de servidores remotos y reduce costos de infraestructura. Esto abre oportunidades enormes:

- **Agro-tech**: Aplicaciones que identifiquen plagas en cultivos tomando una foto, sin necesidad de cobertura 4G en zonas rurales.
- **Fintech**: Verificación de identidad mediante reconocimiento facial y lectura de documentos (INE, CURP, cédula, DNI).
- **Salud**: Análisis preliminar de imágenes médicas (dermatología, oftalmología) en regiones con acceso limitado a especialistas.
- **Retail**: Escaneo de productos, lectura de códigos y clasificación visual de inventario.
- **Educación**: Apps que identifiquen plantas, animales u objetos del entorno como herramienta de aprendizaje.

Además, dominar Core ML y Vision te posiciona como un desarrollador de alto valor en el mercado, ya que la demanda de aplicaciones con IA integrada crece exponencialmente en toda la región.

## Arquitectura de la Demo

```
┌─────────────────────────────────────────────┐
│              Vista (SwiftUI)                 │
│         Selector de imagen / Cámara         │
├─────────────────────────────────────────────┤
│           ImageClassifierService            │
│  ┌───────────────┐  ┌───────────────────┐   │
│  │  Vision API   │──│  Core ML Model    │   │
│  │ VNClassifica- │  │ (MobileNetV2.ml   │   │
│  │ tionRequest   │  │  model)           │   │
│  └───────────────┘  └───────────────────┘   │
├─────────────────────────────────────────────┤
│          Resultado: [(label, confidence)]    │
└─────────────────────────────────────────────┘
```

## Paso a Paso: Construyendo la Demo Completa

### Paso 1: Obtener un modelo Core ML

Apple proporciona modelos pre-entrenados en [apple.com/machine-learning/models](https://developer.apple.com/machine-learning/models/). Para esta demo usaremos **MobileNetV2**, un modelo ligero de clasificación de imágenes.

1. Descarga `MobileNetV2.mlmodel` desde el sitio de Apple.
2. Arrastra el archivo `.mlmodel` a tu proyecto en Xcode.
3. Xcode generará automáticamente una clase Swift con la interfaz del modelo.

> **Tip**: Al seleccionar el archivo `.mlmodel` en Xcode, puedes ver la pestaña de metadatos con las entradas, salidas y el tamaño del modelo.

### Paso 2: Crear el servicio de clasificación

```swift
import Vision
import CoreML
import UIKit

/// Servicio que encapsula toda la lógica de clasificación de imágenes
/// utilizando Vision + Core ML.
final class ImageClassifierService {

    // MARK: - Properties

    private let model: VNCoreMLModel
    private let minimumConfidence: Float = 0.1

    // MARK: - Initialization

    init() throws {
        // Configuración del modelo para usar Neural Engine si está disponible
        let configuration = MLModelConfiguration()
        configuration.computeUnits = .all

        let mlModel = try MobileNetV2(configuration: configuration).model
        self.model = try VNCoreMLModel(for: mlModel)
    }

    // MARK: - Classification

    /// Resultado individual de una clasificación
    struct ClassificationResult: Identifiable {
        let id = UUID()
        let label: String
        let confidence: Float

        var confidencePercentage: String {
            String(format: "%.1f%%", confidence * 100)
        }
    }

    /// Clasifica una imagen y devuelve los resultados ordenados por confianza.
    /// - Parameters:
    ///   - image: La imagen UIImage a clasificar
    ///   - maxResults: Número máximo de resultados a devolver
    ///   - completion: Closure con los resultados o un error
    func classify(
        image: UIImage,
        maxResults: Int = 5,
        completion: @escaping (Result<[ClassificationResult], Error>) -> Void
    ) {
        guard let ciImage = CIImage(image: image) else {
            completion(.failure(ClassificationError.invalidImage))
            return
        }

        let request = VNCoreMLRequest(model: model) { [weak self] request, error in
            guard let self = self else { return }

            if let error = error {
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
                return
            }

            guard let observations = request.results as? [VNClassificationObservation] else {
                DispatchQueue.main.async {
                    completion(.failure(ClassificationError.noResults))
                }
                return
            }

            let results = observations
                .filter { $0.confidence >= self.minimumConfidence }
                .prefix(maxResults)
                .map { observation in
                    ClassificationResult(
                        label: observation.identifier.capitalized,
                        confidence: observation.confidence
                    )
                }

            DispatchQueue.main.async {
                completion(.success(Array(results)))
            }
        }

        // Configurar el crop y scale de la imagen de entrada
        request.imageCropAndScaleOption = .centerCrop

        // Ejecutar la solicitud en un hilo de background
        DispatchQueue.global(qos: .userInitiated).async {
            let handler = VNImageRequestHandler(ciImage: ciImage, options: [:])
            do {
                try handler.perform([request])
            } catch {
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
            }
        }
    }

    // MARK: - Errors

    enum ClassificationError: LocalizedError {
        case invalidImage
        case noResults

        var errorDescription: String? {
            switch self {
            case .invalidImage:
                return "No se pudo procesar la imagen proporcionada."
            case .noResults:
                return "No se obtuvieron resultados de la clasificación."
            }
        }
    }
}
```

### Paso 3: Versión con async/await (iOS 15+)

```swift
extension ImageClassifierService {

    /// Versión moderna con async/await para clasificar imágenes.
    func classify(image: UIImage, maxResults: Int = 5) async throws -> [ClassificationResult] {
        try await withCheckedThrowingContinuation { continuation in
            classify(image: image, maxResults: maxResults) { result in
                continuation.resume(with: result)
            }
        }
    }
}
```

### Paso 4: Construir la interfaz con SwiftUI

```swift
import SwiftUI
import PhotosUI

struct MLVisionDemoView: View {

    // MARK: - State

    @State private var selectedImage: UIImage?
    @State private var results: [ImageClassifierService.ClassificationResult] = []
    @State private var isClassifying = false
    @State private var errorMessage: String?
    @State private var showImagePicker = false
    @State private var selectedPhotoItem: PhotosPickerItem?

    // MARK: - Services

    private let classifier: ImageClassifierService? = try? ImageClassifierService()

    // MARK: - Body

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    imageSection
                    actionButtons
                    resultsSection
                }
                .padding()
            }
            .navigationTitle("ML Vision Demo")
            .alert("Error", isPresented: .constant(errorMessage != nil)) {
                Button("OK") { errorMessage = nil }
            } message: {
                Text(errorMessage ?? "")
            }
        }
    }

    // MARK: - Image Section

    private var imageSection: some View {
        Group {
            if let selectedImage {
                Image(uiImage: selectedImage)
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(maxHeight: 300)
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                    .shadow(radius: 5)
                    .overlay(alignment: .topTrailing) {
                        Button {
                            withAnimation {
                                self.selectedImage = nil
                                self.results = []
                            }
                        } label: {
                            Image(systemName: "xmark.circle.fill")
                                .font(.title2)
                                .foregroundStyle(.white)
                                .shadow(radius: 3)
                        }
                        .padding(8)
                    }
            } else {
                placeholderView
            }
        }
    }

    private var placeholderView: some View {
        RoundedRectangle(cornerRadius: 16)
            .fill(Color(.systemGray6))
            .frame(height: 250)
            .overlay {
                VStack(spacing: 12) {
                    Image(systemName: "photo.on.rectangle.angled")
                        .font(.system(size: 50))
                        .foregroundStyle(.secondary)
                    Text("Selecciona una imagen para analizar")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
            }
    }

    // MARK: - Action Buttons

    private var actionButtons: some View {
        VStack(spacing: 12) {
            PhotosPicker(
                selection: $selectedPhotoItem,
                matching: .images,
                photoLibrary: .shared()
            ) {
                Label("Seleccionar Imagen", systemImage: "photo.fill")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundStyle(.white)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
            }
            .onChange(of: selectedPhotoItem) { _, newItem in
                Task {
                    await loadImage(from: newItem)
                }
            }

            if selectedImage != nil {
                Button {
                    Task { await classifyImage() }
                } label: {
                    HStack {
                        if isClassifying {
                            ProgressView()
                                .tint(.white)
                        }
                        Text(isClassifying ? "Analizando..." : "🧠 Clasificar Imagen")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(isClassifying ? Color.gray : Color.green)
                    .foregroundStyle(.white)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .disabled(isClassifying)
            }
        }
    }

    // MARK: - Results Section

    private var resultsSection: some View {
        Group {
            if !results.isEmpty {
                VStack(alignment: .leading, spacing: 16) {
                    Text("Resultados")
                        .font(.title2.bold())

                    ForEach(results) { result in
                        ResultRow(result: result)
                    }
                }
                .padding()
                .background(Color(.systemGray6))
                .clipShape(RoundedRectangle(cornerRadius: 16))
            }
        }
    }

    // MARK: - Methods

    private func loadImage(from item: PhotosPickerItem?) async {
        guard let item else { return }

        do {
            if let data = try await item.loadTransferable(type: Data.self),
               let uiImage = UIImage(data: data) {
                await MainActor.run {
                    withAnimation {
                        selectedImage = uiImage
                        results = []
                    }
                }
            }
        } catch {
            await MainActor.run {
                errorMessage = "Error al cargar la imagen: \(error.localizedDescription)"
            }
        }
    }

    private func classifyImage() async {
        guard let image = selectedImage, let classifier else { return }

        isClassifying = true
        defer { isClassifying = false }

        do {
            let classificationResults = try await classifier.classify(image: image)
            withAnimation(.spring()) {
                results = classificationResults
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

// MARK: - Result Row Component

struct ResultRow: View {
    let result: ImageClassifierService.ClassificationResult

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(result.label)
                    .font(.headline)
                Spacer()
                Text(result.confidencePercentage)
                    .font(.subheadline.bold())
                    .foregroundStyle(confidenceColor)
            }

            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 4)
                        .fill(Color(.systemGray4))
                        .frame(height: 8)

                    RoundedRectangle(cornerRadius: 4)
                        .fill(confidenceColor)
                        .frame(
                            width: geometry.size.width * CGFloat(result.confidence),
                            height: 8
                        )
                }
            }
            .frame(height: 8)
        }
        .padding(.vertical, 4)
    }

    private var confidenceColor: Color {
        switch result.confidence {
        case 0.7...:
            return .green
        case 0.4..<0.7:
            return .orange
        default:
            return .red
        }
    }
}
```

### Paso 5: Vista de cámara en tiempo real (Bonus avanzado)

Para clasificar imágenes desde la cámara en tiempo real, necesitas combinar `AVCaptureSession` con Vision:

```swift
import AVFoundation
import Vision

/// Coordinador que conecta la cámara con el clasificador de Vision.
final class CameraClassifierCoordinator: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {

    private let classifier: ImageClassifierService
    private let session = AVCaptureSession()
    private var request: VNCoreMLRequest?
    var onResults: (([ImageClassifierService.ClassificationResult]) -> Void)?

    // Throttle: clasificar máximo cada 500ms para no saturar el dispositivo
    private var lastClassificationTime: Date = .distantPast
    private let classificationInterval: TimeInterval = 0.5

    