---
sidebar_position: 1
title: ModelIO
---

# ModelIO

## ¿Qué es ModelIO?

ModelIO es un framework de Apple diseñado para importar, exportar, manipular y renderizar modelos 3D y sus recursos asociados. Proporciona una infraestructura robusta para trabajar con mallas poligonales, materiales, iluminación, texturas y escenas tridimensionales completas. Es el puente fundamental entre los archivos de modelos 3D creados en herramientas externas (como Blender, Maya o 3ds Max) y los motores de renderizado de Apple como SceneKit, MetalKit y ARKit.

El framework soporta una amplia variedad de formatos de archivo estándar de la industria, incluyendo **USD (Universal Scene Description)**, **OBJ**, **PLY**, **STL** y **Alembic (ABC)**. Además de la importación y exportación, ModelIO permite generar geometría procedural (esferas, cubos, planos, etc.), realizar operaciones de subdivisión de mallas, hornear texturas (*baking*), configurar sistemas de iluminación basados en física (PBR) y realizar voxelización de modelos.

Es especialmente útil cuando necesitas preprocesar assets 3D antes de renderizarlos, cuando deseas generar contenido 3D de forma programática, o cuando necesitas convertir entre formatos de modelos 3D. Si tu aplicación involucra realidad aumentada, juegos, visualización de productos en 3D o cualquier tipo de renderizado tridimensional, ModelIO será una pieza clave en tu pipeline de assets.

## Casos de uso principales

- **Importación y conversión de modelos 3D**: Cargar modelos en formatos como OBJ, USD o STL desde archivos locales o remotos y convertirlos al formato que necesite tu motor de renderizado.

- **Generación de geometría procedural**: Crear primitivas 3D como esferas, cajas, cilindros, conos y planos de forma programática, con control total sobre los parámetros de subdivisión, dimensiones y segmentos.

- **Configuración de materiales PBR**: Definir materiales basados en física con propiedades como albedo, metalicidad, rugosidad y mapa normal para lograr renderizados fotorrealistas.

- **Preparación de assets para ARKit y RealityKit**: Preprocesar y optimizar modelos 3D que se utilizarán en experiencias de realidad aumentada, incluyendo la generación de mapas de iluminación.

- **Voxelización de modelos**: Convertir mallas poligonales en representaciones volumétricas (voxels) para simulaciones físicas, detección de colisiones avanzada o efectos visuales especiales.

- **Pipeline de horneado de texturas (Texture Baking)**: Hornear información de iluminación, oclusión ambiental y otros datos complejos directamente en texturas para mejorar el rendimiento en tiempo de ejecución.

## Instalación y configuración

ModelIO es un framework nativo de Apple disponible en **iOS 8+**, **macOS 10.11+**, **tvOS 9+** y **visionOS 1.0+**. No requiere instalación adicional mediante gestores de paquetes ya que viene incluido en el SDK del sistema.

### Import necesario

```swift
import ModelIO
```

### Imports complementarios frecuentes

```swift
import MetalKit       // Para integración con Metal
import SceneKit       // Para integración con SceneKit
import ARKit          // Para uso en realidad aumentada
import RealityKit     // Para uso en visionOS y AR avanzado
```

### Configuración en el proyecto

No se requieren permisos especiales en `Info.plist` para usar ModelIO. Sin embargo, si vas a cargar modelos desde archivos del usuario o desde la red, asegúrate de configurar los permisos correspondientes:

```xml
<!-- Solo si cargas archivos desde el almacenamiento del usuario (macOS) -->
<key>com.apple.security.files.user-selected.read-only</key>
<true/>

<!-- Solo si descargas modelos desde Internet -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

En tu archivo de proyecto en Xcode, ve a **Build Phases → Link Binary With Libraries** y verifica que `ModelIO.framework` esté vinculado. En la mayoría de los casos, Xcode lo agrega automáticamente al detectar el `import`.

## Conceptos clave

### 1. MDLAsset (Recurso / Asset)

Es el contenedor de nivel superior que representa toda una escena 3D. Un `MDLAsset` puede contener múltiples objetos, mallas, cámaras y luces. Es el punto de entrada principal cuando cargas un archivo 3D.

```swift
// Un MDLAsset encapsula todo el contenido de un archivo 3D
let asset = MDLAsset(url: modelURL)
```

### 2. MDLMesh (Malla)

Representa la geometría de un objeto 3D. Contiene los vértices, las normales, las coordenadas de textura y los índices que definen la forma tridimensional. ModelIO incluye métodos de fábrica para crear mallas primitivas.

### 3. MDLVertexDescriptor (Descriptor de Vértices)

Define la disposición (*layout*) de los datos de vértices en memoria: qué atributos están presentes (posición, normal, UV, etc.), su formato y cómo están organizados en los buffers. Es fundamental para la interoperabilidad con Metal.

### 4. MDLMaterial y MDLMaterialProperty (Materiales)

Representan las propiedades visuales de una superficie: color base, metalicidad, rugosidad, mapas normales, emisión, etc. Siguen el modelo de sombreado basado en física (PBR) y pueden incluir texturas o valores escalares.

### 5. MDLTexture (Texturas)

Encapsula datos de textura que pueden ser imágenes cargadas desde archivo, texturas procedurales generadas por código o texturas horneadas. Soporta texturas 2D, cúbicas (cubemaps) y de tipo URL.

### 6. MDLVoxelArray (Array de Vóxeles)

Permite convertir mallas poligonales en representaciones volumétricas discretas. Cada vóxel representa una celda en el espacio 3D que indica si está ocupada o no por la geometría del modelo.

## Ejemplo básico

```swift
import ModelIO
import SceneKit

/// Ejemplo básico: Cargar un modelo 3D desde un archivo y mostrarlo en SceneKit
class BasicModelLoader {
    
    /// Carga un modelo OBJ desde el bundle de la aplicación
    /// - Parameter filename: Nombre del archivo sin extensión
    /// - Returns: Un nodo de SceneKit listo para agregar a la escena
    func loadModel(named filename: String) -> SCNNode? {
        // 1. Obtener la URL del archivo en el bundle
        guard let url = Bundle.main.url(
            forResource: filename,
            withExtension: "obj"
        ) else {
            print("❌ No se encontró el archivo \(filename).obj en el bundle")
            return nil
        }
        
        // 2. Crear el MDLAsset a partir de la URL
        let asset = MDLAsset(url: url)
        
        // 3. Cargar todos los objetos del asset en memoria
        asset.loadTextures()
        
        // 4. Extraer el primer objeto (malla) del asset
        guard let mdlObject = asset.object(at: 0) as? MDLMesh else {
            print("❌ No se pudo extraer la malla del asset")
            return nil
        }
        
        // 5. Convertir la malla de ModelIO a un nodo de SceneKit
        let node = SCNNode(mdlObject: mdlObject)
        
        print("✅ Modelo '\(filename)' cargado correctamente")
        print("   - Vértices: \(mdlObject.vertexCount)")
        print("   - Submallas: \(mdlObject.submeshes?.count ?? 0)")
        
        return node
    }
}

// Uso:
// let loader = BasicModelLoader()
// if let modelNode = loader.loadModel(named: "mi_modelo") {
//     sceneView.scene?.rootNode.addChildNode(modelNode)
// }
```

## Ejemplo intermedio

```swift
import ModelIO
import MetalKit

/// Ejemplo intermedio: Generación de geometría procedural con materiales PBR
/// y preparación para renderizado con Metal
class ProceduralMeshGenerator {
    
    private let device: MTLDevice
    private let vertexDescriptor: MDLVertexDescriptor
    
    init?(device: MTLDevice? = MTLCreateSystemDefaultDevice()) {
        guard let device = device else {
            print("❌ Metal no está disponible en este dispositivo")
            return nil
        }
        self.device = device
        self.vertexDescriptor = ProceduralMeshGenerator.createVertexDescriptor()
    }
    
    /// Crea un descriptor de vértices compatible con Metal
    private static func createVertexDescriptor() -> MDLVertexDescriptor {
        let descriptor = MDLVertexDescriptor()
        
        // Atributo 0: Posición (float3)
        descriptor.attributes[0] = MDLVertexAttribute(
            name: MDLVertexAttributePosition,
            format: .float3,
            offset: 0,
            bufferIndex: 0
        )
        
        // Atributo 1: Normal (float3)
        descriptor.attributes[1] = MDLVertexAttribute(
            name: MDLVertexAttributeNormal,
            format: .float3,
            offset: MemoryLayout<Float>.size * 3,
            bufferIndex: 0
        )
        
        // Atributo 2: Coordenadas de textura (float2)
        descriptor.attributes[2] = MDLVertexAttribute(
            name: MDLVertexAttributeTextureCoordinate,
            format: .float2,
            offset: MemoryLayout<Float>.size * 6,
            bufferIndex: 0
        )
        
        // Layout del buffer: stride total por vértice
        descriptor.layouts[0] = MDLVertexBufferLayout(
            stride: MemoryLayout<Float>.size * 8 // 3+3+2 = 8 floats
        )
        
        return descriptor
    }
    
    /// Genera una esfera con material PBR configurado
    /// - Parameters:
    ///   - radius: Radio de la esfera
    ///   - segments: Número de segmentos (mayor = más detalle)
    ///   - color: Color base del material (RGBA)
    ///   - metallic: Nivel de metalicidad (0.0 a 1.0)
    ///   - roughness: Nivel de rugosidad (0.0 a 1.0)
    /// - Returns: MDLMesh con material PBR aplicado
    func generateSphere(
        radius: Float = 1.0,
        segments: UInt32 = 48,
        color: SIMD4<Float> = SIMD4<Float>(0.8, 0.2, 0.2, 1.0),
        metallic: Float = 0.5,
        roughness: Float = 0.3
    ) -> MDLMesh {
        // Crear allocator de Metal para gestión eficiente de memoria
        let allocator = MTKMeshBufferAllocator(device: device)
        
        // Generar la esfera procedural
        let sphere = MDLMesh.newEllipsoid(
            withRadii: SIMD3<Float>(repeating: radius),
            radialSegments: Int(segments),
            verticalSegments: Int(segments),
            geometryType: .triangles,
            inwardNormals: false,
            hemisphere: false,
            allocator: allocator
        )
        
        // Aplicar el descriptor de vértices
        sphere.vertexDescriptor = vertexDescriptor
        
        // Crear y configurar el material PBR
        let material = createPBRMaterial(
            color: color,
            metallic: metallic,
            roughness: roughness
        )
        
        // Asignar el material a todas las submallas
        if let submeshes = sphere.submeshes as? [MDLSubmesh] {
            for submesh in submeshes {
                submesh.material = material
            }
        }
        
        return sphere
    }
    
    /// Genera un terreno a partir de un mapa de altura
    /// - Parameters:
    ///   - heightMapURL: URL de la imagen del mapa de altura
    ///   - dimensions: Dimensiones del terreno (ancho, alto, profundidad)
    ///   - segments: Segmentos en cada eje
    /// - Returns: MDLMesh del terreno generado
    func generateTerrain(
        heightMapURL: URL,
        dimensions: SIMD3<Float> = SIMD3<Float>(10, 2, 10),
        segments: SIMD2<UInt32> = SIMD2<UInt32>(64, 64)
    ) -> MDLMesh? {
        let allocator = MTKMeshBufferAllocator(device: device)
        
        // Crear terreno a partir de un mapa de altura
        let terrain = MDLMesh(
            planeWithExtent: dimensions,
            segments: segments,
            geometryType: .triangles,
            allocator: allocator
        )
        
        // Aplicar desplazamiento basado en la textura del mapa de altura
        if let heightTexture = MDLTexture(named: heightMapURL.lastPathComponent) {
            // Generar normales suavizadas para iluminación correcta
            terrain.addNormals(
                withAttributeNamed: MDLVertexAttributeNormal,
                creaseThreshold: 0.5
            )
            
            print("✅ Terreno generado con \(terrain.vertexCount) vértices")
            print("   Textura de altura: \(heightTexture.dimensions)")
        }
        
        terrain.vertexDescriptor = vertexDescriptor
        return terrain
    }
    
    /// Crea un material PBR (Physically Based Rendering)
    private func createPBRMaterial(
        color: SIMD4<Float>,
        metallic: Float,
        roughness: Float
    ) -> MDLMaterial {
        // Crear función de dispersión (scattering function) PBR
        let scatteringFunction = MDLPhysicallyPlausibleScatteringFunction()
        let material = MDLMaterial(
            name: "PBRMaterial",
            scatteringFunction: scatteringFunction
        )
        
        // Color base (albedo)
        let baseColorProperty = MDLMaterialProperty(
            name: "baseColor",
            semantic: .baseColor,
            color: CGColor(
                red: CGFloat(color.x),
                green: CGFloat(color.y),
                blue: CGFloat(color.z),
                alpha: CGFloat(color.w)
            )
        )
        material.setProperty(baseColorProperty)
        
        // Metalicidad
        let metallicProperty = MDLMaterialProperty(
            name: "metallic",
            semantic: .metallic,
            float: metallic
        )
        material.setProperty(metallicProperty)
        
        // Rugosidad
        let roughnessProperty = MDLMaterialProperty(
            name: "roughness",
            semantic: .roughness,
            float: roughness
        )
        material.setProperty(roughnessProperty)
        
        return material
    }
    
    /// Convierte un MDLMesh a MTKMesh para renderizado directo con Metal
    func convertToMetalMesh(_ mdlM