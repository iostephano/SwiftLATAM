---
sidebar_position: 1
title: SceneKit
---

# SceneKit

## ¿Qué es SceneKit?

SceneKit es el framework de Apple diseñado para crear y renderizar contenido 3D de alto rendimiento en aplicaciones iOS, macOS, tvOS y watchOS. Proporciona un motor de renderizado completo basado en un grafo de escena (*scene graph*), lo que permite a los desarrolladores construir escenas tridimensionales complejas mediante la composición jerárquica de nodos, geometrías, materiales, luces y cámaras, sin necesidad de interactuar directamente con APIs de bajo nivel como OpenGL o Metal.

A diferencia de otros motores 3D que requieren una curva de aprendizaje pronunciada, SceneKit abstrae gran parte de la complejidad del renderizado 3D ofreciendo una API declarativa y accesible. Incluye soporte nativo para física, animaciones, sistemas de partículas, sombras, reflejos, renderizado basado en física (PBR) y la carga de modelos 3D en formatos estándar como `.dae` (Collada), `.obj`, `.usdz` y `.scn`. Además, se integra de forma natural con UIKit, SwiftUI y ARKit, lo que lo convierte en una pieza fundamental del ecosistema de Apple para experiencias inmersivas.

SceneKit es la elección ideal cuando necesitas incorporar visualizaciones 3D en tu aplicación sin adoptar un motor de juegos completo como Unity o Unreal. Es perfecto para prototipos rápidos, visualizadores de productos, aplicaciones educativas, juegos casuales 3D, experiencias de realidad aumentada y cualquier escenario donde el contenido tridimensional deba coexistir armónicamente con la interfaz nativa de la plataforma Apple.

## Casos de uso principales

- **Visualizadores de productos 3D**: Permite a los usuarios rotar, hacer zoom e inspeccionar modelos tridimensionales de productos (muebles, dispositivos electrónicos, joyas) directamente en la aplicación, potenciando la experiencia de compra en e-commerce.

- **Juegos casuales 3D**: SceneKit ofrece un motor de física integrado, detección de colisiones y un sistema de partículas, lo que lo hace adecuado para juegos 3D de complejidad moderada sin necesidad de un motor externo.

- **Aplicaciones educativas y científicas**: Representación de moléculas, sistemas solares, modelos anatómicos o cualquier estructura tridimensional que requiera interacción y animación para facilitar el aprendizaje.

- **Experiencias de Realidad Aumentada con ARKit**: SceneKit es el renderizador predeterminado de `ARSCNView`, lo que permite colocar objetos virtuales 3D en el mundo real con detección de superficies, iluminación realista y oclusión.

- **Visualización de datos en 3D**: Gráficos tridimensionales, mapas topográficos, visualizaciones arquitectónicas y dashboards con profundidad que van más allá de las gráficas 2D convencionales.

- **Prototipos y herramientas de diseño**: Creación rápida de escenas 3D interactivas para validar conceptos de diseño, animaciones de interfaz con profundidad o transiciones tridimensionales entre vistas.

## Instalación y configuración

SceneKit viene incluido de forma nativa en el SDK de Apple, por lo que **no requiere instalación adicional** mediante gestores de dependencias como CocoaPods o Swift Package Manager.

### Importación en tu proyecto

```swift
import SceneKit
```

Si deseas usar SceneKit dentro de SwiftUI:

```swift
import SwiftUI
import SceneKit
```

Si trabajas con Realidad Aumentada:

```swift
import ARKit // ARSCNView ya incluye SceneKit internamente
```

### Configuración del proyecto

1. **Crear un nuevo proyecto** en Xcode seleccionando la plantilla "App" o "Game" (con tecnología SceneKit).
2. **No se requieren permisos especiales** en `Info.plist` para SceneKit por sí solo. Sin embargo, si lo combinas con ARKit necesitarás:

```xml
<key>NSCameraUsageDescription</key>
<string>Se necesita acceso a la cámara para la experiencia de realidad aumentada.</string>
```

3. **Formatos de modelos 3D soportados**: Añade tus archivos `.usdz`, `.dae`, `.obj` o `.scn` al catálogo de assets o directamente al bundle del proyecto. Xcode incluye un editor de escenas integrado para archivos `.scn`.

4. **Catálogo de assets para texturas**: Coloca las imágenes de texturas, mapas normales y mapas de entorno dentro del catálogo `Assets.xcassets` o en carpetas `.scnassets` para optimización automática por plataforma.

### Estructura recomendada del proyecto

```
MyApp/
├── Models.scnassets/       // Modelos 3D y texturas (optimización automática)
│   ├── spaceship.scn
│   ├── textures/
│   │   ├── diffuse.png
│   │   └── normal.png
├── Scenes/
│   ├── GameScene.swift
│   └── SceneConfigurator.swift
├── ViewModels/
│   └── SceneViewModel.swift
└── Views/
    └── SceneView.swift
```

## Conceptos clave

### 1. SCNScene (La escena)

La escena es el contenedor raíz de todo el contenido 3D. Representa el mundo virtual completo y contiene un nodo raíz (`rootNode`) del cual cuelgan todos los demás elementos. Puedes crear escenas programáticamente o cargarlas desde archivos `.scn` o `.usdz`.

```swift
let scene = SCNScene()
// O desde un archivo:
let scene = SCNScene(named: "Models.scnassets/spaceship.scn")
```

### 2. SCNNode (Los nodos)

Los nodos son los bloques fundamentales del grafo de escena. Cada nodo posee una transformación 3D (posición, rotación, escala) y puede contener geometría, luces, cámaras u otros nodos hijos. La jerarquía de nodos define las relaciones padre-hijo, donde las transformaciones se heredan.

### 3. SCNGeometry (Las geometrías)

Las geometrías definen la forma visual de un objeto 3D. SceneKit proporciona primitivas integradas (`SCNBox`, `SCNSphere`, `SCNCylinder`, `SCNPlane`, `SCNTorus`, etc.) y permite cargar geometrías personalizadas desde archivos o crearlas mediante vértices.

### 4. SCNMaterial (Los materiales)

Los materiales controlan la apariencia visual de las geometrías. Cada material tiene propiedades como `diffuse` (color base), `specular` (brillo), `normal` (relieve), `emission` (autoiluminación), `metalness` y `roughness` (para renderizado PBR). Un material puede usar colores sólidos, imágenes o incluso contenido dinámico como `SpriteKit` scenes.

### 5. SCNLight y SCNCamera (Iluminación y cámara)

Las luces determinan cómo se ilumina la escena. SceneKit soporta luces omnidireccionales, direccionales, spots, ambiente e IES. La cámara define el punto de vista del usuario, con control sobre la perspectiva, profundidad de campo, HDR, bloom y otros efectos de postprocesado.

### 6. SCNPhysicsBody (Sistema de física)

El motor de física integrado permite simular gravedad, colisiones, fuerzas, articulaciones y campos de fuerza. Cada nodo puede tener un cuerpo físico estático, dinámico o cinemático, y el sistema se encarga automáticamente de la detección de colisiones y la respuesta física.

## Ejemplo básico

Este ejemplo crea una escena mínima con una esfera iluminada y una cámara, presentada en un `SCNView`:

```swift
import UIKit
import SceneKit

class BasicSceneViewController: UIViewController {
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // 1. Crear la vista de SceneKit que ocupará toda la pantalla
        let sceneView = SCNView(frame: view.bounds)
        sceneView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        sceneView.allowsCameraControl = true  // Permite rotar/zoom con gestos
        sceneView.autoenablesDefaultLighting = true  // Iluminación automática básica
        sceneView.backgroundColor = .black
        view.addSubview(sceneView)
        
        // 2. Crear una escena vacía
        let scene = SCNScene()
        sceneView.scene = scene
        
        // 3. Crear una esfera con material PBR
        let esfera = SCNSphere(radius: 1.0)
        let material = SCNMaterial()
        material.diffuse.contents = UIColor.systemBlue
        material.metalness.contents = 0.3    // Aspecto ligeramente metálico
        material.roughness.contents = 0.4    // Rugosidad moderada
        material.lightingModel = .physicallyBased
        esfera.materials = [material]
        
        // 4. Crear un nodo y añadirlo a la escena
        let nodoEsfera = SCNNode(geometry: esfera)
        nodoEsfera.position = SCNVector3(0, 0, 0)  // Centro de la escena
        scene.rootNode.addChildNode(nodoEsfera)
        
        // 5. Añadir una animación de rotación continua
        let rotacion = SCNAction.rotateBy(
            x: 0,
            y: CGFloat.pi * 2,  // Rotación completa en Y
            z: 0,
            duration: 4.0
        )
        nodoEsfera.runAction(SCNAction.repeatForever(rotacion))
        
        // 6. Configurar la cámara
        let nodoCamara = SCNNode()
        nodoCamara.camera = SCNCamera()
        nodoCamara.position = SCNVector3(0, 1, 5)  // Ligeramente arriba y atrás
        nodoCamara.look(at: SCNVector3Zero)          // Mirar al centro
        scene.rootNode.addChildNode(nodoCamara)
        
        // 7. Añadir luz direccional para sombras
        let nodoLuz = SCNNode()
        nodoLuz.light = SCNLight()
        nodoLuz.light?.type = .directional
        nodoLuz.light?.color = UIColor.white
        nodoLuz.light?.intensity = 1000
        nodoLuz.light?.castsShadow = true
        nodoLuz.eulerAngles = SCNVector3(-Float.pi / 4, Float.pi / 4, 0)
        scene.rootNode.addChildNode(nodoLuz)
    }
}
```

## Ejemplo intermedio

Este ejemplo construye un sistema solar simplificado con múltiples planetas orbitando alrededor de un sol, usando física, texturas y animaciones:

```swift
import UIKit
import SceneKit

class SistemaSolarViewController: UIViewController {
    
    private var sceneView: SCNView!
    private var scene: SCNScene!
    
    // MARK: - Datos de los planetas
    struct DatosPlaneta {
        let nombre: String
        let radio: CGFloat
        let distanciaAlSol: Float
        let color: UIColor
        let duracionOrbita: TimeInterval
        let duracionRotacion: TimeInterval
    }
    
    private let planetas: [DatosPlaneta] = [
        DatosPlaneta(nombre: "Mercurio", radio: 0.15, distanciaAlSol: 2.5,
                     color: .gray, duracionOrbita: 4, duracionRotacion: 2),
        DatosPlaneta(nombre: "Venus", radio: 0.25, distanciaAlSol: 3.5,
                     color: .orange, duracionOrbita: 7, duracionRotacion: 5),
        DatosPlaneta(nombre: "Tierra", radio: 0.3, distanciaAlSol: 5.0,
                     color: .systemBlue, duracionOrbita: 10, duracionRotacion: 1),
        DatosPlaneta(nombre: "Marte", radio: 0.2, distanciaAlSol: 6.5,
                     color: .systemRed, duracionOrbita: 15, duracionRotacion: 1.1),
        DatosPlaneta(nombre: "Júpiter", radio: 0.7, distanciaAlSol: 9.0,
                     color: .systemBrown, duracionOrbita: 25, duracionRotacion: 0.5)
    ]
    
    override func viewDidLoad() {
        super.viewDidLoad()
        configurarEscena()
        crearSol()
        crearPlanetas()
        configurarCamara()
        configurarIluminacion()
        agregarFondoEstrellado()
    }
    
    // MARK: - Configuración de la escena
    private func configurarEscena() {
        sceneView = SCNView(frame: view.bounds)
        sceneView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        sceneView.allowsCameraControl = true
        sceneView.backgroundColor = .black
        sceneView.showsStatistics = true  // Muestra FPS y estadísticas de debug
        sceneView.antialiasingMode = .multisampling4X
        view.addSubview(sceneView)
        
        scene = SCNScene()
        sceneView.scene = scene
    }
    
    // MARK: - Creación del Sol
    private func crearSol() {
        let geometriaSol = SCNSphere(radius: 1.0)
        let materialSol = SCNMaterial()
        materialSol.diffuse.contents = UIColor.yellow
        materialSol.emission.contents = UIColor.orange  // El sol emite luz propia
        materialSol.lightingModel = .constant           // No afectado por luces externas
        geometriaSol.materials = [materialSol]
        
        let nodoSol = SCNNode(geometry: geometriaSol)
        nodoSol.name = "Sol"
        nodoSol.position = SCNVector3Zero
        scene.rootNode.addChildNode(nodoSol)
        
        // Añadir luz puntual al sol para iluminar los planetas
        let luzSol = SCNLight()
        luzSol.type = .omni
        luzSol.color = UIColor(white: 1.0, alpha: 1.0)
        luzSol.intensity = 2000
        luzSol.attenuationStartDistance = 0
        luzSol.attenuationEndDistance = 20
        nodoSol.light = luzSol
        
        // Animación de pulso del sol
        let escalarArriba = SCNAction.scale(to: 1.05, duration: 1.5)
        let escalarAbajo = SCNAction.scale(to: 0.95, duration: 1.5)
        escalarArriba.timingMode = .easeInEaseOut
        escalarAbajo.timingMode = .easeInEaseOut
        let pulso = SCNAction.sequence([escalarArriba, escalarAbajo])
        nodoSol.runAction(SCNAction.repeat