---
sidebar_position: 1
title: Ar Vr
---

# Realidad Aumentada y Realidad Virtual en iOS

## ¿Qué son AR y VR?

La **Realidad Aumentada (AR)** superpone contenido digital sobre el mundo real utilizando la cámara y los sensores del dispositivo. La **Realidad Virtual (VR)** crea un entorno completamente inmersivo que reemplaza el mundo real. Apple ha apostado fuertemente por estas tecnologías con frameworks como **ARKit**, **RealityKit** y, más recientemente, **visionOS** para el Apple Vision Pro.

En el ecosistema iOS, AR es la tecnología dominante. Desde el iPhone 6s en adelante, prácticamente todos los dispositivos Apple son capaces de ejecutar experiencias de realidad aumentada, lo que representa una base instalada de **cientos de millones de dispositivos** a nivel global.

## ¿Por qué es importante para un dev iOS en LATAM?

La demanda de experiencias AR/VR está creciendo exponencialmente en Latinoamérica:

- **E-commerce**: Empresas como Mercado Libre, Falabella y Liverpool están explorando AR para que los usuarios "prueben" productos antes de comprarlos.
- **Educación**: Instituciones educativas en México, Colombia, Argentina y Chile implementan experiencias inmersivas para mejorar el aprendizaje.
- **Real Estate**: Inmobiliarias en toda la región utilizan AR para mostrar propiedades con recorridos virtuales.
- **Industria**: Manufactura y minería en países como Chile, Perú y Brasil adoptan AR para mantenimiento y capacitación.
- **Turismo**: Museos, sitios arqueológicos y destinos turísticos ofrecen experiencias aumentadas (piensa en Teotihuacán, Machu Picchu o Cartagena).
- **Diferenciación profesional**: Muy pocos desarrolladores en la región dominan estas tecnologías, lo que te posiciona como un perfil altamente valioso y con salarios significativamente superiores al promedio.

Con el lanzamiento del **Apple Vision Pro** y visionOS, dominar AR/VR te prepara para la próxima era de la computación espacial.

## Frameworks fundamentales

### Ecosistema AR/VR de Apple

```
┌─────────────────────────────────────────────────────┐
│                   visionOS (2024+)                   │
│              Computación Espacial Completa            │
├─────────────────────────────────────────────────────┤
│                                                       │
│   ┌─────────────┐  ┌──────────────┐  ┌───────────┐  │
│   │   ARKit      │  │  RealityKit  │  │  SceneKit │  │
│   │ (Tracking &  │  │ (Rendering & │  │ (3D Legacy│  │
│   │  Detection)  │  │  Simulation) │  │  Support) │  │
│   └──────┬──────┘  └──────┬───────┘  └─────┬─────┘  │
│          │                │                 │         │
│   ┌──────┴────────────────┴─────────────────┴─────┐  │
│   │              RealityComposer Pro               │  │
│   │         (Herramienta de diseño 3D)             │  │
│   └────────────────────────────────────────────────┘  │
│                                                       │
│   ┌────────────────────────────────────────────────┐  │
│   │                  Metal / MetalFX                │  │
│   │            (GPU & Rendering de bajo nivel)      │  │
│   └────────────────────────────────────────────────┘  │
│                                                       │
└─────────────────────────────────────────────────────┘
```

| Framework | Uso principal | Disponibilidad |
|-----------|--------------|----------------|
| **ARKit** | Tracking, detección de planos, rostros, cuerpos, imágenes | iOS 11+ |
| **RealityKit** | Renderizado 3D, física, animaciones, audio espacial | iOS 13+ |
| **SceneKit** | Renderizado 3D (legacy, pero aún útil) | iOS 8+ |
| **Metal** | Renderizado GPU de bajo nivel | iOS 8+ |
| **visionOS SDK** | Experiencias espaciales completas | visionOS 1.0+ |

## Ejemplo práctico 1: Tu primera escena AR con RealityKit

Vamos a crear una aplicación que coloca un objeto 3D sobre una superficie horizontal detectada.

### Paso 1: Configurar el proyecto

Crea un nuevo proyecto en Xcode seleccionando **Augmented Reality App** con **RealityKit** como Content Technology.

### Paso 2: Configurar permisos

En tu `Info.plist`, asegúrate de incluir:

```xml
<key>NSCameraUsageDescription</key>
<string>Necesitamos acceso a la cámara para mostrar contenido en realidad aumentada</string>
```

### Paso 3: Vista AR básica con UIKit

```swift
import UIKit
import RealityKit
import ARKit

class ARViewController: UIViewController {
    
    // MARK: - Properties
    var arView: ARView!
    let coachingOverlay = ARCoachingOverlayView()
    
    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupARView()
        setupCoachingOverlay()
        configureARSession()
        addTapGesture()
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        arView.session.pause()
    }
    
    // MARK: - Setup
    private func setupARView() {
        arView = ARView(frame: view.bounds)
        arView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        view.addSubview(arView)
        
        // Habilitar estadísticas de debug durante desarrollo
        #if DEBUG
        arView.debugOptions = [.showFeaturePoints, .showWorldOrigin]
        #endif
    }
    
    private func setupCoachingOverlay() {
        // El coaching overlay guía al usuario para escanear superficies
        coachingOverlay.session = arView.session
        coachingOverlay.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        coachingOverlay.goal = .horizontalPlane
        coachingOverlay.activatesAutomatically = true
        arView.addSubview(coachingOverlay)
    }
    
    private func configureARSession() {
        let configuration = ARWorldTrackingConfiguration()
        configuration.planeDetection = [.horizontal, .vertical]
        configuration.environmentTexturing = .automatic
        
        // Habilitar oclusión de personas si el dispositivo lo soporta
        if ARWorldTrackingConfiguration.supportsFrameSemantics(.personSegmentationWithDepth) {
            configuration.frameSemantics.insert(.personSegmentationWithDepth)
        }
        
        arView.session.run(configuration, options: [.resetTracking, .removeExistingAnchors])
    }
    
    private func addTapGesture() {
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(handleTap(_:)))
        arView.addGestureRecognizer(tapGesture)
    }
    
    // MARK: - Actions
    @objc private func handleTap(_ recognizer: UITapGestureRecognizer) {
        let location = recognizer.location(in: arView)
        
        // Realizar raycast para encontrar una superficie
        let results = arView.raycast(
            from: location,
            allowing: .estimatedPlane,
            alignment: .horizontal
        )
        
        guard let firstResult = results.first else {
            print("No se detectó ninguna superficie horizontal")
            return
        }
        
        // Colocar un objeto 3D en la posición detectada
        placeObject(at: firstResult)
    }
    
    private func placeObject(at raycastResult: ARRaycastResult) {
        // Crear un anchor en la posición del raycast
        let anchor = AnchorEntity(raycastResult: raycastResult)
        
        // Crear una caja 3D con material realista
        let boxMesh = MeshResource.generateBox(
            size: 0.1,
            cornerRadius: 0.005
        )
        
        var material = SimpleMaterial()
        material.color = .init(tint: .systemBlue.withAlphaComponent(0.8))
        material.metallic = .float(0.8)
        material.roughness = .float(0.2)
        
        let boxEntity = ModelEntity(mesh: boxMesh, materials: [material])
        
        // Agregar colisión para interactividad
        boxEntity.generateCollisionShapes(recursive: true)
        
        // Permitir que el usuario mueva el objeto
        arView.installGestures(
            [.translation, .rotation, .scale],
            for: boxEntity
        )
        
        // Agregar sombra al objeto
        boxEntity.components[GroundingShadowComponent.self] = GroundingShadowComponent(
            castsShadow: true
        )
        
        anchor.addChild(boxEntity)
        arView.scene.addAnchor(anchor)
        
        // Animación de aparición
        boxEntity.scale = SIMD3<Float>(0.001, 0.001, 0.001)
        boxEntity.move(
            to: Transform(scale: SIMD3<Float>(1, 1, 1)),
            relativeTo: boxEntity.parent,
            duration: 0.5,
            timingFunction: .easeInOut
        )
    }
}
```

### Paso 4: Versión con SwiftUI (iOS 15+)

```swift
import SwiftUI
import RealityKit
import ARKit

struct ARContentView: View {
    @State private var objectCount = 0
    @State private var showInstructions = true
    
    var body: some View {
        ZStack(alignment: .bottom) {
            ARViewContainer(objectCount: $objectCount)
                .edgesIgnoringSafeArea(.all)
            
            VStack(spacing: 12) {
                if showInstructions {
                    InstructionCard()
                        .transition(.move(edge: .top).combined(with: .opacity))
                }
                
                HStack(spacing: 20) {
                    Label("\(objectCount) objetos", systemImage: "cube.fill")
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(.ultraThinMaterial)
                        .clipShape(Capsule())
                    
                    Button("Limpiar") {
                        NotificationCenter.default.post(
                            name: .clearARScene,
                            object: nil
                        )
                        objectCount = 0
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.red)
                }
                .padding(.bottom, 30)
            }
        }
        .onAppear {
            DispatchQueue.main.asyncAfter(deadline: .now() + 5) {
                withAnimation { showInstructions = false }
            }
        }
    }
}

struct InstructionCard: View {
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: "hand.tap.fill")
                .font(.title)
            Text("Toca una superficie para colocar un objeto")
                .font(.subheadline)
                .multilineTextAlignment(.center)
        }
        .padding()
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .padding(.horizontal)
    }
}

struct ARViewContainer: UIViewRepresentable {
    @Binding var objectCount: Int
    
    func makeUIView(context: Context) -> ARView {
        let arView = ARView(frame: .zero)
        
        let config = ARWorldTrackingConfiguration()
        config.planeDetection = [.horizontal]
        config.environmentTexturing = .automatic
        arView.session.run(config)
        
        let tapGesture = UITapGestureRecognizer(
            target: context.coordinator,
            action: #selector(Coordinator.handleTap(_:))
        )
        arView.addGestureRecognizer(tapGesture)
        
        // Observar notificación para limpiar escena
        context.coordinator.setupNotificationObserver()
        
        return arView
    }
    
    func updateUIView(_ uiView: ARView, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(objectCount: $objectCount)
    }
    
    class Coordinator: NSObject {
        @Binding var objectCount: Int
        weak var arView: ARView?
        
        init(objectCount: Binding<Int>) {
            _objectCount = objectCount
        }
        
        func setupNotificationObserver() {
            NotificationCenter.default.addObserver(
                self,
                selector: #selector(clearScene),
                name: .clearARScene,
                object: nil
            )
        }
        
        @objc func handleTap(_ recognizer: UITapGestureRecognizer) {
            guard let arView = recognizer.view as? ARView else { return }
            self.arView = arView
            
            let location = recognizer.location(in: arView)
            let results = arView.raycast(
                from: location,
                allowing: .estimatedPlane,
                alignment: .horizontal
            )
            
            guard let result = results.first else { return }
            
            let anchor = AnchorEntity(raycastResult: result)
            
            // Crear una esfera con material PBR
            let sphere = ModelEntity(
                mesh: .generateSphere(radius: 0.05),
                materials: [SimpleMaterial(
                    color: UIColor.random(),
                    isMetallic: Bool.random()
                )]
            )
            
            sphere.generateCollisionShapes(recursive: true)
            arView.installGestures([.all], for: sphere)
            
            anchor.addChild(sphere)
            arView.scene.addAnchor(anchor)
            
            DispatchQueue.main.async {
                self.objectCount += 1
            }
        }
        
        @objc func clearScene() {
            arView?.scene.anchors.removeAll()
        }
    }
}

// MARK: - Extensions
extension Notification.Name {
    static let clearARScene = Notification.Name("clearARScene")
}

extension UIColor {
    static func random() -> UIColor {
        UIColor(
            red: .random(in: 0.2...1),
            green: .random(in: 0.2...1),
            blue: .random(in: 0.2...1),
            alpha: 1
        )
    }
}
```

## Ejemplo práctico 2: Detección de imágenes AR

Un caso de uso muy popular en LATAM es la detección de imágenes para marketing, museos y educación:

```swift
import ARKit
import RealityKit

class ImageTrackingViewController: UIViewController, ARSessionDelegate {
    
    var arView: ARView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        arView = ARView(frame: view.bounds)
        arView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        arView.session.