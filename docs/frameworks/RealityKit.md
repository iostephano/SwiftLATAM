---
sidebar_position: 1
title: RealityKit
---

# RealityKit

## ¿Qué es RealityKit?

RealityKit es el framework de alto rendimiento de Apple diseñado específicamente para crear experiencias de **realidad aumentada (AR)** y **contenido 3D** de manera nativa en plataformas Apple. Introducido en WWDC 2019, RealityKit fue construido desde cero con tecnologías modernas como Swift, aprovechando renderizado basado en física (PBR), simulación de físicas, audio espacial y animaciones avanzadas. A diferencia de SceneKit, RealityKit está optimizado exclusivamente para experiencias inmersivas que combinan el mundo real con contenido digital.

El framework utiliza un sistema de **Entidad-Componente-Sistema (ECS)** como su arquitectura central, lo que permite una composición flexible y eficiente de objetos 3D. Cada elemento de la escena es una `Entity` a la que se le agregan `Component`s que definen su comportamiento, apariencia y propiedades físicas. Este patrón arquitectónico facilita enormemente la creación de escenas complejas manteniendo un código limpio y reutilizable.

RealityKit es especialmente relevante con la llegada de **visionOS** y Apple Vision Pro, donde se convierte en el framework principal para construir experiencias espaciales. Además, se integra de forma nativa con **SwiftUI** a través de `RealityView`, con **ARKit** para el seguimiento del mundo real, y con **Reality Composer Pro** para la creación visual de escenas 3D. Si estás desarrollando cualquier tipo de experiencia AR, contenido 3D interactivo o aplicaciones para Vision Pro, RealityKit es la herramienta fundamental que necesitas dominar.

## Casos de uso principales

### 1. Realidad Aumentada en iOS
Colocar objetos virtuales en el mundo real a través de la cámara del iPhone o iPad. Desde muebles virtuales para aplicaciones de comercio electrónico hasta herramientas de medición que interactúan con superficies detectadas.

### 2. Experiencias espaciales en visionOS
Crear aplicaciones inmersivas para Apple Vision Pro, incluyendo volúmenes 3D, espacios inmersivos completos y elementos interactivos que responden a gestos de mano y seguimiento ocular.

### 3. Visualización de productos 3D
Renderizar modelos 3D de productos con materiales realistas basados en física (PBR), permitiendo a los usuarios inspeccionar objetos desde todos los ángulos con iluminación realista y reflejos dinámicos.

### 4. Juegos y entretenimiento interactivo
Desarrollar juegos que combinen el mundo real con elementos virtuales, aprovechando el motor de físicas integrado, detección de colisiones y animaciones procedurales.

### 5. Aplicaciones educativas y de entrenamiento
Crear simulaciones interactivas donde los usuarios pueden manipular modelos anatómicos, arquitectónicos o mecánicos en 3D, con animaciones y comportamientos realistas.

### 6. Filtros y efectos faciales
Utilizar el seguimiento facial de ARKit combinado con RealityKit para aplicar mallas 3D, texturas y efectos en tiempo real sobre el rostro del usuario.

## Instalación y configuración

### Agregar RealityKit al proyecto

RealityKit viene incluido como framework del sistema en Xcode. No necesitas agregar ninguna dependencia externa mediante SPM o CocoaPods. Simplemente importa el framework donde lo necesites:

```swift
import RealityKit
import ARKit // Necesario para funcionalidades AR en iOS
```

### Configuración en Info.plist (iOS con cámara AR)

Para experiencias de realidad aumentada que utilizan la cámara, debes agregar la descripción de uso correspondiente en tu archivo `Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>Necesitamos acceso a la cámara para mostrar contenido de realidad aumentada.</string>
```

Si tu aplicación utiliza reconocimiento de ubicación geográfica (ARGeoTrackingConfiguration):

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>Necesitamos tu ubicación para anclar contenido AR en el mundo real.</string>
```

### Requisitos del proyecto

| Requisito | Valor mínimo |
|---|---|
| **iOS** | 13.0+ (recomendado 17.0+) |
| **visionOS** | 1.0+ |
| **macOS** | 10.15+ |
| **Xcode** | 15.0+ (para las APIs más recientes) |
| **Swift** | 5.9+ |

### Configuración para visionOS

En proyectos para visionOS, asegúrate de agregar en `Info.plist` las capacidades de espacio inmersivo si las necesitas:

```xml
<key>UIApplicationPreferredDefaultSceneSessionRole</key>
<string>UIWindowSceneSessionRoleVolumetricApplication</string>
```

Y en el archivo de capacidades del proyecto, habilita **Immersive Space** según el tipo de experiencia (Mixed, Full o Progressive).

## Conceptos clave

### 1. Entity (Entidad)

La `Entity` es el bloque de construcción fundamental de RealityKit. Representa cualquier objeto dentro de una escena 3D: un modelo, una luz, un ancla o incluso un contenedor vacío para organizar la jerarquía. Las entidades forman un **árbol jerárquico** donde las transformaciones (posición, rotación, escala) de una entidad padre afectan a todas sus entidades hijas.

```swift
// Una entidad es simplemente un contenedor al que se agregan componentes
let miEntidad = Entity()
miEntidad.name = "contenedor-principal"
miEntidad.position = [0, 1.5, -2] // x, y, z en metros
```

### 2. Component (Componente)

Los componentes definen las **propiedades y comportamientos** de una entidad. RealityKit proporciona numerosos componentes integrados como `ModelComponent` (apariencia visual), `CollisionComponent` (colisiones), `PhysicsBodyComponent` (simulación de físicas) y `Transform` (posición/rotación/escala). También puedes crear componentes personalizados para encapsular lógica específica de tu aplicación.

### 3. System (Sistema)

Los sistemas procesan entidades que poseen combinaciones específicas de componentes en cada frame de renderizado. Siguiendo la arquitectura ECS, los sistemas contienen la **lógica de actualización** y operan sobre conjuntos de entidades de manera eficiente. En versiones recientes de RealityKit, puedes crear `System` personalizados que se ejecutan automáticamente en el bucle de renderizado.

### 4. AnchorEntity (Entidad Ancla)

Las `AnchorEntity` son entidades especiales que vinculan tu contenido 3D al **mundo real**. Pueden anclarse a superficies horizontales o verticales, a imágenes detectadas, a rostros, a posiciones de cuerpo o a coordenadas específicas del mundo. Son el puente fundamental entre la realidad y lo virtual.

### 5. Material y Mesh (Malla)

Una **malla** (`MeshResource`) define la geometría 3D del objeto (su forma), mientras que un **material** (`Material`) define su apariencia visual (color, textura, rugosidad, metalicidad). RealityKit ofrece varios tipos de materiales: `SimpleMaterial`, `PhysicallyBasedMaterial`, `UnlitMaterial`, `ShaderGraphMaterial` y `VideoMaterial`.

### 6. Scene y ARView/RealityView

La **escena** (`Scene`) es el contenedor raíz que alberga todas las entidades. En iOS, se presenta a través de `ARView` (UIKit) o `RealityView` (SwiftUI). En visionOS, `RealityView` es el componente principal para integrar contenido 3D en tu interfaz de usuario. La escena gestiona automáticamente el renderizado, las actualizaciones de físicas y las animaciones.

## Ejemplo básico

```swift
import SwiftUI
import RealityKit

/// Vista básica que muestra un cubo 3D con material metálico en realidad aumentada.
/// Compatible con iOS 17+ usando RealityView.
struct CuboBasicoView: View {
    var body: some View {
        RealityView { content in
            // 1. Crear la geometría: un cubo de 10cm por lado
            let mesh = MeshResource.generateBox(size: 0.1)
            
            // 2. Crear el material con apariencia metálica azul
            var material = SimpleMaterial()
            material.color = .init(tint: .systemBlue)
            material.metallic = .float(0.8)
            material.roughness = .float(0.2)
            
            // 3. Crear la entidad modelo combinando malla y material
            let cubo = ModelEntity(mesh: mesh, materials: [material])
            
            // 4. Posicionar el cubo: 1.5 metros frente al usuario, a la altura de los ojos
            cubo.position = SIMD3<Float>(0, 1.5, -1.5)
            
            // 5. Agregar componente de colisión para permitir interacción
            cubo.generateCollisionShapes(recursive: false)
            
            // 6. Habilitar que el usuario pueda interactuar con el cubo
            cubo.components.set(InputTargetComponent())
            
            // 7. Agregar el cubo a la escena
            content.add(cubo)
        }
        .navigationTitle("Cubo Básico")
    }
}

#Preview {
    CuboBasicoView()
}
```

## Ejemplo intermedio

```swift
import SwiftUI
import RealityKit
import Combine

/// Vista intermedia que carga un modelo USDZ, aplica animaciones,
/// gestiona gestos de interacción y actualiza la escena de forma reactiva.
struct GaleriaProductoView: View {
    
    // Estado para controlar la rotación del modelo
    @State private var anguloRotacion: Float = 0.0
    @State private var modeloCargado: Bool = false
    @State private var entidadProducto: ModelEntity?
    
    var body: some View {
        VStack {
            // Encabezado informativo
            Text(modeloCargado ? "Toca el modelo para animarlo" : "Cargando modelo...")
                .font(.headline)
                .padding()
            
            // Vista 3D con interacción mediante gestos
            RealityView { content in
                // Crear un entorno de iluminación basado en imagen
                await configurarEscena(content: content)
            } update: { content in
                // Se ejecuta cada vez que cambia el @State
                // Aplicar rotación actualizada al modelo
                if let entidad = entidadProducto {
                    let rotacion = simd_quatf(angle: anguloRotacion, axis: [0, 1, 0])
                    entidad.transform.rotation = rotacion
                }
            }
            .gesture(gestoRotacion)
            .gesture(gestoTap)
            
            // Controles de la interfaz
            HStack(spacing: 20) {
                Button("Reiniciar Posición") {
                    withAnimation {
                        anguloRotacion = 0
                    }
                }
                .buttonStyle(.bordered)
                
                Button("Girar 90°") {
                    anguloRotacion += .pi / 2
                }
                .buttonStyle(.borderedProminent)
            }
            .padding()
        }
    }
    
    // MARK: - Configuración de la escena
    
    /// Configura la escena cargando el modelo 3D y estableciendo iluminación.
    private func configurarEscena(content: RealityViewContent) async {
        // Crear una plataforma base circular
        let plataforma = ModelEntity(
            mesh: .generateCylinder(height: 0.02, radius: 0.15),
            materials: [SimpleMaterial(color: .darkGray, isMetallic: true)]
        )
        plataforma.position = SIMD3<Float>(0, 0, -1.0)
        
        // Intentar cargar un modelo USDZ del bundle
        do {
            let modelo = try await ModelEntity(named: "zapato_deportivo")
            
            // Escalar el modelo para que se ajuste a la escena
            let boundingBox = modelo.visualBounds(relativeTo: nil)
            let tamanoMaximo = max(
                boundingBox.extents.x,
                boundingBox.extents.y,
                boundingBox.extents.z
            )
            let escalaDeseada: Float = 0.2 / tamanoMaximo
            modelo.scale = SIMD3<Float>(repeating: escalaDeseada)
            
            // Posicionar sobre la plataforma
            modelo.position = SIMD3<Float>(0, 0.02, 0)
            
            // Habilitar interacción
            modelo.generateCollisionShapes(recursive: true)
            modelo.components.set(InputTargetComponent())
            
            // Agregar sombra de contacto con el suelo
            modelo.components.set(GroundingShadowComponent(castsShadow: true))
            
            // Hacer hijo de la plataforma para que se mueva con ella
            plataforma.addChild(modelo)
            
            // Guardar referencia para actualizaciones
            await MainActor.run {
                self.entidadProducto = modelo
                self.modeloCargado = true
            }
            
        } catch {
            print("Error al cargar el modelo: \(error.localizedDescription)")
            
            // Modelo de respaldo: una esfera con material PBR
            let esfera = ModelEntity(
                mesh: .generateSphere(radius: 0.08),
                materials: [crearMaterialPBR()]
            )
            esfera.position = SIMD3<Float>(0, 0.1, 0)
            esfera.generateCollisionShapes(recursive: false)
            esfera.components.set(InputTargetComponent())
            plataforma.addChild(esfera)
            
            await MainActor.run {
                self.entidadProducto = esfera
                self.modeloCargado = true
            }
        }
        
        content.add(plataforma)
    }
    
    // MARK: - Materiales
    
    /// Crea un material PBR (Physically Based Rendering) personalizado.
    private func crearMaterialPBR() -> PhysicallyBasedMaterial {
        var material = PhysicallyBasedMaterial()
        material.baseColor = .init(tint: .init(red: 0.9, green: 0.3, blue: 0.1, alpha: 1.0))
        material.metallic = .init(floatLiteral: 0.9)
        material.roughness = .init(floatLiteral: 0.15)
        material.clearcoat = .init(floatLiteral: 0.5) // Capa de barniz
        return material
    }
    
    // MARK: - Gestos de interacción
    
    /// Gesto de rotación arrastrando sobre el modelo.
    private var gestoRotacion: some Gesture {
        DragGesture()
            .onChanged { valor in
                // Convertir desplazamiento horizontal a rotación
                let deltaX = Float(valor.translation.width)
                anguloRotacion = deltaX * 0.01
            }
    }
    
    /// Gesto de toque que activa una animación de rebote.
    private var gestoTap: some Gesture {
        TapGesture()
            .targetedToAnyEntity