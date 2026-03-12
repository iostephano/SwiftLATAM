---
sidebar_position: 1
title: Demo Ar Experience
---

# Demo AR Experience: Creando una Experiencia de Realidad Aumentada en iOS

## ¿Qué es una AR Experience?

Una **AR Experience** (experiencia de realidad aumentada) es una aplicación que superpone contenido digital — modelos 3D, textos, animaciones, partículas — sobre el mundo real capturado por la cámara del dispositivo. En iOS, Apple nos ofrece un ecosistema robusto compuesto por **ARKit**, **RealityKit** y **Reality Composer** para construir estas experiencias de manera nativa, eficiente y con un rendimiento excepcional.

Esta demo te guiará paso a paso para crear una experiencia AR completa: desde la configuración inicial del proyecto hasta la colocación de objetos 3D interactivos sobre superficies reales.

## ¿Por qué es importante para un dev iOS en LATAM?

La realidad aumentada está transformando industrias clave en Latinoamérica:

- **E-commerce**: Empresas como Mercado Libre, Falabella y Liverpool exploran la visualización de productos en 3D antes de comprar.
- **Educación**: Startups edtech en México, Colombia y Argentina usan AR para experiencias de aprendizaje inmersivo.
- **Bienes raíces**: Desarrolladoras inmobiliarias implementan recorridos virtuales con AR para preventa de departamentos.
- **Turismo y cultura**: Museos y sitios arqueológicos en Perú, Guatemala y México integran guías con realidad aumentada.
- **Marketing**: Agencias en toda la región crean experiencias AR para campañas de marcas globales.

Dominar ARKit te posiciona como un **desarrollador especializado** en un nicho con alta demanda y poca competencia en la región. Mientras muchos devs se concentran en CRUD apps, tú puedes diferenciarte ofreciendo experiencias que realmente sorprendan.

## Requisitos previos

Antes de comenzar, asegúrate de contar con:

- **Xcode 15+** (última versión estable recomendada)
- **Dispositivo físico** con chip A9 o superior (el simulador NO soporta ARKit)
- **iOS 16+** como target de deployment
- Conocimientos básicos de **SwiftUI** y **UIKit**
- Familiaridad con el patrón **Coordinator** (útil para integrar vistas de AR en SwiftUI)

## Paso 1: Configuración del proyecto

Crea un nuevo proyecto en Xcode seleccionando **Augmented Reality App**:

1. Abre Xcode → **File → New → Project**
2. Selecciona **Augmented Reality App**
3. Elige **RealityKit** como tecnología y **SwiftUI** como interfaz
4. Nombra tu proyecto `ARExperienceDemo`

### Configuración del Info.plist

ARKit requiere acceso a la cámara. Agrega la siguiente clave en tu `Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>Necesitamos acceder a la cámara para mostrar la experiencia de realidad aumentada.</string>
```

> ⚠️ **Importante**: Sin este permiso, tu app se cerrará inmediatamente al intentar iniciar la sesión AR. Apple rechazará tu app en review si el mensaje no es descriptivo.

## Paso 2: Estructura base del proyecto

Organizaremos el proyecto con una arquitectura limpia y mantenible:

```
ARExperienceDemo/
├── App/
│   └── ARExperienceDemoApp.swift
├── Features/
│   └── ARScene/
│       ├── Views/
│       │   ├── ARContentView.swift
│       │   └── ARViewContainer.swift
│       ├── ViewModels/
│       │   └── ARSceneViewModel.swift
│       └── Models/
│           └── ARPlaceable.swift
├── Services/
│   └── ARSessionService.swift
├── Resources/
│   └── Models.reality
└── Extensions/
    └── SIMD+Extensions.swift
```

## Paso 3: Creando el contenedor ARView

Este es el componente central. Usaremos `UIViewRepresentable` para integrar `ARView` de RealityKit dentro de SwiftUI:

```swift
import SwiftUI
import RealityKit
import ARKit

struct ARViewContainer: UIViewRepresentable {
    @ObservedObject var viewModel: ARSceneViewModel
    
    func makeUIView(context: Context) -> ARView {
        let arView = ARView(frame: .zero)
        
        // Configuración de la sesión AR
        let configuration = ARWorldTrackingConfiguration()
        configuration.planeDetection = [.horizontal, .vertical]
        configuration.environmentTexturing = .automatic
        
        // Habilitar oclusión de personas si el dispositivo lo soporta
        if ARWorldTrackingConfiguration.supportsFrameSemantics(.personSegmentationWithDepth) {
            configuration.frameSemantics.insert(.personSegmentationWithDepth)
        }
        
        arView.session.run(configuration)
        arView.session.delegate = context.coordinator
        
        // Agregar gesture recognizer para colocar objetos
        let tapGesture = UITapGestureRecognizer(
            target: context.coordinator,
            action: #selector(Coordinator.handleTap(_:))
        )
        arView.addGestureRecognizer(tapGesture)
        
        // Habilitar debugging visual durante desarrollo
        #if DEBUG
        arView.debugOptions = [.showFeaturePoints, .showAnchorOrigins]
        #endif
        
        return arView
    }
    
    func updateUIView(_ uiView: ARView, context: Context) {
        // Actualizaciones reactivas desde el ViewModel
        if viewModel.shouldClearScene {
            uiView.scene.anchors.removeAll()
            viewModel.shouldClearScene = false
        }
    }
    
    func makeCoordinator() -> Coordinator {
        Coordinator(viewModel: viewModel)
    }
}
```

## Paso 4: Implementando el Coordinator

El Coordinator maneja la interacción entre el usuario y la escena AR:

```swift
extension ARViewContainer {
    
    class Coordinator: NSObject, ARSessionDelegate {
        var viewModel: ARSceneViewModel
        
        init(viewModel: ARSceneViewModel) {
            self.viewModel = viewModel
        }
        
        // MARK: - Gesture Handling
        
        @objc func handleTap(_ recognizer: UITapGestureRecognizer) {
            guard let arView = recognizer.view as? ARView else { return }
            
            let tapLocation = recognizer.location(in: arView)
            
            // Raycast para detectar superficies reales
            let results = arView.raycast(
                from: tapLocation,
                allowing: .estimatedPlane,
                alignment: .horizontal
            )
            
            guard let firstResult = results.first else {
                viewModel.showMessage("No se detectó una superficie. Mueve el dispositivo lentamente.")
                return
            }
            
            placeObject(in: arView, at: firstResult)
        }
        
        // MARK: - Object Placement
        
        private func placeObject(in arView: ARView, at raycastResult: ARRaycastResult) {
            let selectedModel = viewModel.selectedModel
            
            // Crear anchor en la posición detectada
            let anchor = AnchorEntity(raycastResult: raycastResult)
            
            // Generar el modelo 3D según el tipo seleccionado
            let entity = createEntity(for: selectedModel)
            
            // Agregar animación de aparición
            entity.scale = SIMD3<Float>(0.001, 0.001, 0.001)
            anchor.addChild(entity)
            arView.scene.addAnchor(anchor)
            
            // Animar la escala con efecto "pop"
            var transform = entity.transform
            transform.scale = SIMD3<Float>(
                selectedModel.scale,
                selectedModel.scale,
                selectedModel.scale
            )
            entity.move(
                to: transform,
                relativeTo: entity.parent,
                duration: 0.4,
                timingFunction: .easeInOut
            )
            
            // Generar feedback háptico
            let impactFeedback = UIImpactFeedbackGenerator(style: .medium)
            impactFeedback.impactOccurred()
            
            viewModel.objectCount += 1
            viewModel.showMessage("¡Objeto colocado! Total: \(viewModel.objectCount)")
        }
        
        private func createEntity(for model: ARPlaceable) -> ModelEntity {
            switch model.type {
            case .box:
                let mesh = MeshResource.generateBox(size: 0.1, cornerRadius: 0.005)
                let material = SimpleMaterial(
                    color: model.color,
                    roughness: 0.3,
                    isMetallic: true
                )
                let entity = ModelEntity(mesh: mesh, materials: [material])
                entity.generateCollisionShapes(recursive: true)
                return entity
                
            case .sphere:
                let mesh = MeshResource.generateSphere(radius: 0.05)
                let material = SimpleMaterial(
                    color: model.color,
                    roughness: 0.1,
                    isMetallic: true
                )
                let entity = ModelEntity(mesh: mesh, materials: [material])
                entity.generateCollisionShapes(recursive: true)
                return entity
                
            case .text:
                let mesh = MeshResource.generateText(
                    model.text ?? "Hola LATAM!",
                    extrusionDepth: 0.02,
                    font: .systemFont(ofSize: 0.05, weight: .bold),
                    containerFrame: .zero,
                    alignment: .center,
                    lineBreakMode: .byWordWrapping
                )
                let material = SimpleMaterial(
                    color: model.color,
                    isMetallic: false
                )
                let entity = ModelEntity(mesh: mesh, materials: [material])
                entity.generateCollisionShapes(recursive: true)
                return entity
                
            case .custom:
                // Cargar modelo USDZ personalizado
                guard let modelEntity = try? ModelEntity.loadModel(named: model.modelName ?? "default") else {
                    // Fallback a un cubo si el modelo no se encuentra
                    let mesh = MeshResource.generateBox(size: 0.1)
                    let material = SimpleMaterial(color: .gray, isMetallic: false)
                    return ModelEntity(mesh: mesh, materials: [material])
                }
                modelEntity.generateCollisionShapes(recursive: true)
                return modelEntity
            }
        }
        
        // MARK: - ARSessionDelegate
        
        func session(_ session: ARSession, didAdd anchors: [ARAnchor]) {
            for anchor in anchors {
                if let planeAnchor = anchor as? ARPlaneAnchor {
                    let surfaceType = planeAnchor.alignment == .horizontal ? "horizontal" : "vertical"
                    DispatchQueue.main.async {
                        self.viewModel.detectedSurfaces += 1
                        self.viewModel.showMessage("Superficie \(surfaceType) detectada ✓")
                    }
                }
            }
        }
        
        func session(_ session: ARSession, didFailWithError error: Error) {
            DispatchQueue.main.async {
                self.viewModel.showMessage("Error AR: \(error.localizedDescription)")
            }
        }
        
        func sessionWasInterrupted(_ session: ARSession) {
            DispatchQueue.main.async {
                self.viewModel.showMessage("Sesión interrumpida. Vuelve a la app para continuar.")
            }
        }
    }
}
```

## Paso 5: El ViewModel

```swift
import SwiftUI
import Combine

enum ARModelType: String, CaseIterable {
    case box = "Cubo"
    case sphere = "Esfera"
    case text = "Texto 3D"
    case custom = "Modelo USDZ"
}

struct ARPlaceable: Identifiable {
    let id = UUID()
    let type: ARModelType
    var color: UIColor
    var scale: Float
    var text: String?
    var modelName: String?
    
    static let defaultModels: [ARPlaceable] = [
        ARPlaceable(type: .box, color: .systemBlue, scale: 1.0),
        ARPlaceable(type: .sphere, color: .systemRed, scale: 1.0),
        ARPlaceable(type: .text, color: .systemGreen, scale: 1.0, text: "¡Hola AR!"),
        ARPlaceable(type: .box, color: .systemPurple, scale: 1.5),
    ]
}

class ARSceneViewModel: ObservableObject {
    @Published var selectedModel: ARPlaceable = ARPlaceable.defaultModels[0]
    @Published var objectCount: Int = 0
    @Published var detectedSurfaces: Int = 0
    @Published var shouldClearScene: Bool = false
    @Published var statusMessage: String = "Apunta la cámara hacia una superficie plana"
    @Published var showStatus: Bool = false
    
    private var messageCancellable: AnyCancellable?
    
    func showMessage(_ message: String) {
        statusMessage = message
        showStatus = true
        
        messageCancellable?.cancel()
        messageCancellable = Just(())
            .delay(for: .seconds(3), scheduler: RunLoop.main)
            .sink { [weak self] _ in
                withAnimation {
                    self?.showStatus = false
                }
            }
    }
    
    func clearScene() {
        shouldClearScene = true
        objectCount = 0
        showMessage("Escena limpia 🧹")
    }
    
    func selectModel(_ model: ARPlaceable) {
        selectedModel = model
        showMessage("Seleccionado: \(model.type.rawValue)")
    }
}
```

## Paso 6: La vista principal con controles

```swift
import SwiftUI

struct ARContentView: View {
    @StateObject private var viewModel = ARSceneViewModel()
    @State private var showModelPicker = false
    
    var body: some View {
        ZStack {
            // Vista AR de fondo (pantalla completa)
            ARViewContainer(viewModel: viewModel)
                .ignoresSafeArea()
            
            // Overlay de controles
            VStack {
                // Barra de estado superior
                if viewModel.showStatus {
                    StatusBanner(message: viewModel.statusMessage)
                        .transition(.move(edge: .top).combined(with: .opacity))
                        .animation(.spring(response: 0.4), value: viewModel.showStatus)
                }
                
                Spacer()
                
                // Panel de información
                HStack {
                    InfoPill(
                        icon: "cube.fill",
                        text: "\(viewModel.objectCount) objetos"
                    )
                    InfoPill(
                        icon: "square.grid.3x3.fill",
                        text: "\(viewModel.detectedSurfaces) superficies"
                    )
                }
                .padding(.bottom, 8)
                
                // Barra de herramientas inferior
                HStack(spacing: 20) {
                    // Botón limpiar escena
                    ToolButton(icon: "trash.fill", label: "Limpiar") {
                        viewModel.clearScene()
                    }
                    
                    // Selector de modelos
                    ToolButton(icon: