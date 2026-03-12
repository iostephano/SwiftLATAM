---
sidebar_position: 1
title: ARKit
---

# ARKit

## ¿Qué es ARKit?

ARKit es el framework de Apple diseñado para crear experiencias de **realidad aumentada (RA)** en dispositivos iOS y iPadOS. Introducido en 2017 con iOS 11, ARKit aprovecha el hardware del dispositivo —cámara, sensores de movimiento, procesadores y escáner LiDAR (en modelos compatibles)— para fusionar contenido digital tridimensional con el entorno físico del usuario de forma fluida y realista.

El framework se encarga de las tareas más complejas de la realidad aumentada: el **seguimiento del mundo** (world tracking), la **detección de superficies** (planos horizontales y verticales), la **estimación de iluminación**, el **reconocimiento de imágenes y objetos 3D**, la **segmentación de personas**, el **raycasting** y mucho más. Todo esto permite al desarrollador centrarse en la experiencia creativa sin necesidad de implementar algoritmos de visión por computadora desde cero.

ARKit es ideal cuando se desea superponer modelos 3D sobre superficies reales, crear juegos inmersivos, desarrollar aplicaciones de decoración o arquitectura, implementar herramientas de medición espacial o construir experiencias educativas interactivas. A partir de iOS 17, Apple ha evolucionado parte de su stack de RA hacia **RealityKit** y **visionOS**, pero ARKit sigue siendo la piedra angular para experiencias de realidad aumentada en iPhone y iPad.

## Casos de uso principales

1. **Decoración y mobiliario virtual**: Aplicaciones como IKEA Place permiten colocar muebles virtuales en una habitación real para visualizar cómo quedarían antes de comprarlos. ARKit detecta el plano del suelo y posiciona el modelo 3D con escala real.

2. **Juegos de realidad aumentada**: Desde juegos de mesa virtuales sobre una mesa real hasta experiencias tipo Pokémon GO, ARKit proporciona el seguimiento necesario para que los elementos del juego permanezcan anclados al mundo físico.

3. **Medición y arquitectura**: Herramientas que miden distancias, áreas y volúmenes reales usando la cámara. Profesionales de la construcción y el diseño de interiores utilizan estas aplicaciones a diario para obtener medidas rápidas.

4. **Educación interactiva**: Visualizar el sistema solar, explorar la anatomía humana en 3D o recorrer monumentos históricos superpuestos en el aula. La RA transforma el aprendizaje en una experiencia tangible.

5. **Comercio electrónico y marketing**: Probarse gafas, maquillaje o zapatillas de forma virtual antes de comprar. Las marcas integran experiencias RA en sus apps para aumentar la conversión y reducir devoluciones.

6. **Navegación en interiores**: Superponer flechas y señales de dirección sobre el entorno real para guiar al usuario dentro de aeropuertos, centros comerciales u hospitales, donde el GPS convencional pierde precisión.

## Instalación y configuración

### Requisitos del proyecto

ARKit requiere un dispositivo con chip **A9 o superior** (iPhone 6s en adelante) y **iOS 11+**. Las funciones avanzadas como *Scene Reconstruction* o *Object Occlusion* requieren dispositivos con escáner **LiDAR** (iPhone 12 Pro en adelante / iPad Pro 2020+).

### Agregar ARKit al proyecto

ARKit viene incluido en el SDK de iOS, por lo que **no necesitas agregar ninguna dependencia externa** ni CocoaPod. Simplemente importa el framework:

```swift
import ARKit
```

Si vas a utilizar **RealityKit** para el renderizado (recomendado en proyectos modernos):

```swift
import ARKit
import RealityKit
```

### Permisos en Info.plist

ARKit necesita acceso a la cámara. Agrega la siguiente clave en tu archivo `Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>Esta aplicación necesita acceso a la cámara para mostrar experiencias de realidad aumentada.</string>
```

Si además utilizas la ubicación del usuario para geo-anclas:

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>Se necesita tu ubicación para anclar contenido RA en coordenadas geográficas.</string>
```

### Verificar compatibilidad en tiempo de ejecución

```swift
// Verificar si el dispositivo soporta ARKit con world tracking
if ARWorldTrackingConfiguration.isSupported {
    print("✅ ARKit World Tracking disponible")
} else {
    print("❌ Este dispositivo no soporta ARKit")
}
```

### Capacidad requerida en Info.plist (App Store)

Para que tu app solo aparezca en dispositivos compatibles:

```xml
<key>UIRequiredDeviceCapabilities</key>
<array>
    <string>arkit</string>
</array>
```

## Conceptos clave

### 1. ARSession

La `ARSession` es el objeto central que coordina todos los procesos de realidad aumentada. Se encarga de capturar imágenes de la cámara, ejecutar los algoritmos de seguimiento, detectar superficies y gestionar los anclas. Toda experiencia de RA comienza ejecutando `session.run(configuration)` y se detiene con `session.pause()`.

### 2. ARConfiguration

Define **qué tipo de experiencia** de RA quieres ejecutar. Existen varias subclases:

- **`ARWorldTrackingConfiguration`**: La más completa. Seguimiento 6DoF (seis grados de libertad), detección de planos, imágenes, objetos y más.
- **`ARFaceTrackingConfiguration`**: Seguimiento facial con la cámara TrueDepth (frontal).
- **`ARBodyTrackingConfiguration`**: Seguimiento del cuerpo humano completo.
- **`ARGeoTrackingConfiguration`**: Anclas geográficas basadas en coordenadas GPS.
- **`ARImageTrackingConfiguration`**: Seguimiento exclusivo de imágenes de referencia.

### 3. ARAnchor

Un `ARAnchor` representa una **posición y orientación fija en el mundo real**. Cuando ARKit detecta un plano, una cara o una imagen, crea un ancla que puedes usar para posicionar contenido 3D. Los anclas persisten mientras la sesión esté activa y pueden ser compartidos entre dispositivos para experiencias colaborativas.

### 4. ARPlaneAnchor

Subclase específica de `ARAnchor` que representa una **superficie plana detectada** (suelo, mesa, pared). Contiene información sobre la extensión, la geometría y la alineación (horizontal o vertical) del plano.

### 5. Raycasting (ARRaycastQuery)

El raycasting es el mecanismo para **proyectar un rayo desde un punto 2D de la pantalla hacia el mundo 3D**. Cuando el usuario toca la pantalla, se lanza un raycast para determinar dónde intersecta con las superficies detectadas y así colocar objetos virtuales con precisión.

### 6. Scene Understanding

Conjunto de capacidades avanzadas que permiten a ARKit **comprender la geometría del entorno**:
- **Mesh reconstruction**: Genera un modelo 3D del entorno (requiere LiDAR).
- **Scene classification**: Identifica si una superficie es suelo, pared, techo, mesa, asiento, etc.
- **Object occlusion**: Hace que los objetos reales tapen a los virtuales de forma natural.

## Ejemplo básico

Este ejemplo muestra cómo configurar una vista de RA mínima con `ARSCNView` (SceneKit) y detectar un plano horizontal:

```swift
import UIKit
import ARKit

/// ViewController básico que inicia una sesión AR y detecta planos horizontales
class BasicARViewController: UIViewController, ARSCNViewDelegate {
    
    // MARK: - Propiedades
    
    /// Vista de SceneKit preparada para renderizar contenido AR
    private let sceneView = ARSCNView()
    
    // MARK: - Ciclo de vida
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Configurar la vista AR
        sceneView.frame = view.bounds
        sceneView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        sceneView.delegate = self
        
        // Mostrar estadísticas de depuración (FPS, número de nodos)
        sceneView.showsStatistics = true
        
        // Mostrar los puntos de detección de features
        sceneView.debugOptions = [.showFeaturePoints, .showWorldOrigin]
        
        view.addSubview(sceneView)
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        
        // Crear configuración de world tracking
        let configuration = ARWorldTrackingConfiguration()
        
        // Habilitar detección de planos horizontales
        configuration.planeDetection = [.horizontal]
        
        // Habilitar estimación de luz ambiental
        configuration.isLightEstimationEnabled = true
        
        // Iniciar la sesión AR
        sceneView.session.run(configuration)
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        
        // Pausar la sesión al salir de la vista
        sceneView.session.pause()
    }
    
    // MARK: - ARSCNViewDelegate
    
    /// Se llama cuando ARKit detecta un nuevo ancla (por ejemplo, un plano)
    func renderer(_ renderer: SCNSceneRenderer,
                  didAdd node: SCNNode,
                  for anchor: ARAnchor) {
        // Verificar que el ancla sea un plano
        guard let planeAnchor = anchor as? ARPlaneAnchor else { return }
        
        // Crear una visualización del plano detectado
        let planeGeometry = SCNPlane(
            width: CGFloat(planeAnchor.extent.x),
            height: CGFloat(planeAnchor.extent.z)
        )
        
        // Material semitransparente azul para visualizar el plano
        let material = SCNMaterial()
        material.diffuse.contents = UIColor.systemBlue.withAlphaComponent(0.3)
        planeGeometry.materials = [material]
        
        // Crear nodo y rotarlo para que sea horizontal
        let planeNode = SCNNode(geometry: planeGeometry)
        planeNode.eulerAngles.x = -.pi / 2
        planeNode.position = SCNVector3(
            planeAnchor.center.x,
            0,
            planeAnchor.center.z
        )
        
        node.addChildNode(planeNode)
        
        print("✅ Plano horizontal detectado: \(planeAnchor.extent)")
    }
    
    /// Se llama cuando un plano existente se actualiza (crece o se ajusta)
    func renderer(_ renderer: SCNSceneRenderer,
                  didUpdate node: SCNNode,
                  for anchor: ARAnchor) {
        guard let planeAnchor = anchor as? ARPlaneAnchor,
              let planeNode = node.childNodes.first,
              let planeGeometry = planeNode.geometry as? SCNPlane else { return }
        
        // Actualizar dimensiones del plano
        planeGeometry.width = CGFloat(planeAnchor.extent.x)
        planeGeometry.height = CGFloat(planeAnchor.extent.z)
        
        // Actualizar posición del plano
        planeNode.position = SCNVector3(
            planeAnchor.center.x,
            0,
            planeAnchor.center.z
        )
    }
}
```

## Ejemplo intermedio

Este ejemplo permite al usuario **tocar la pantalla para colocar un modelo 3D** sobre una superficie detectada, utilizando raycasting:

```swift
import UIKit
import ARKit
import RealityKit

/// ViewController que permite colocar objetos 3D tocando superficies detectadas
class PlaceObjectARViewController: UIViewController {
    
    // MARK: - Propiedades
    
    /// Vista de RealityKit para renderizar contenido AR
    private let arView = ARView(frame: .zero)
    
    /// Ancla del plano donde se colocan los objetos
    private var planeAnchor: AnchorEntity?
    
    /// Contador de objetos colocados
    private var objectCount = 0
    
    /// Colores disponibles para los objetos
    private let colores: [UIColor] = [
        .systemRed, .systemBlue, .systemGreen,
        .systemOrange, .systemPurple, .systemYellow
    ]
    
    // MARK: - Ciclo de vida
    
    override func viewDidLoad() {
        super.viewDidLoad()
        configurarVistaAR()
        configurarGestos()
        configurarCoaching()
    }
    
    // MARK: - Configuración
    
    private func configurarVistaAR() {
        arView.frame = view.bounds
        arView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        view.addSubview(arView)
        
        // Configuración de world tracking con detección de planos
        let configuration = ARWorldTrackingConfiguration()
        configuration.planeDetection = [.horizontal, .vertical]
        configuration.environmentTexturing = .automatic
        
        // Habilitar oclusión de personas si está disponible
        if ARWorldTrackingConfiguration.supportsFrameSemantics(.personSegmentationWithDepth) {
            configuration.frameSemantics.insert(.personSegmentationWithDepth)
        }
        
        arView.session.run(configuration)
    }
    
    private func configurarGestos() {
        // Gesto de tap para colocar objetos
        let tapGesture = UITapGestureRecognizer(
            target: self,
            action: #selector(manejarTap(_:))
        )
        arView.addGestureRecognizer(tapGesture)
        
        // Gesto de doble tap para eliminar el último objeto
        let doubleTapGesture = UITapGestureRecognizer(
            target: self,
            action: #selector(manejarDoubleTap(_:))
        )
        doubleTapGesture.numberOfTapsRequired = 2
        arView.addGestureRecognizer(doubleTapGesture)
        
        // Evitar conflicto entre gestos
        tapGesture.require(toFail: doubleTapGesture)
    }
    
    /// Añade un overlay de coaching que guía al usuario para escanear el entorno
    private func configurarCoaching() {
        let coachingOverlay = ARCoachingOverlayView()
        coachingOverlay.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        coachingOverlay.session = arView.session
        coachingOverlay.goal = .horizontalPlane
        coachingOverlay.activatesAutomatically = true
        arView.addSubview(coachingOverlay)
    }
    
    // MARK: - Gestión de gestos
    
    @objc private func manejarTap(_ gesture: UITapGestureRecognizer) {
        let ubicacion = gesture.location(in: arView)
        
        // Realizar raycast desde el punto tocado hacia las superficies detectadas
        guard let resultado = arView.raycast(
            from: ubicacion,