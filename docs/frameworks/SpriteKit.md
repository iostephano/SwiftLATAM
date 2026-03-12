---
sidebar_position: 1
title: SpriteKit
---

# SpriteKit

## ¿Qué es SpriteKit?

SpriteKit es el framework nativo de Apple diseñado específicamente para la creación de juegos 2D de alto rendimiento. Proporciona un motor de renderizado completo basado en un sistema de nodos jerárquico (scene graph), que permite gestionar sprites, animaciones, física, partículas, audio y mucho más, todo de forma integrada y optimizada para el hardware de los dispositivos Apple. Está disponible en iOS, macOS, tvOS y watchOS.

A diferencia de motores de terceros como Unity o Godot, SpriteKit se integra de forma nativa con el ecosistema de Apple, lo que significa que aprovecha Metal para el renderizado gráfico sin necesidad de configuración adicional, consume menos recursos del sistema y ofrece una interoperabilidad perfecta con UIKit, SwiftUI y el resto de frameworks nativos. Esto lo convierte en una opción ideal para juegos casuales, prototipos rápidos y experiencias interactivas que no requieren capacidades 3D complejas.

¿Cuándo usar SpriteKit? Es la elección adecuada cuando necesitas desarrollar un juego 2D exclusivamente para plataformas Apple, cuando deseas mantener el tamaño de tu aplicación reducido (sin dependencias externas pesadas), cuando buscas una integración directa con funcionalidades del sistema como Game Center, iCloud o StoreKit, o cuando necesitas incorporar elementos interactivos 2D animados dentro de una aplicación convencional (por ejemplo, animaciones complejas en una app educativa o efectos de partículas en una app de entretenimiento).

## Casos de uso principales

- **Juegos 2D casuales y arcade**: Plataformas, puzzles, runners infinitos, juegos de cartas o juegos de mesa. SpriteKit maneja eficientemente cientos de sprites en pantalla con físicas y colisiones.

- **Juegos educativos para niños**: Gracias a su simplicidad y la integración nativa con el sistema operativo, es perfecto para crear experiencias interactivas educativas con animaciones atractivas y controles táctiles intuitivos.

- **Prototipos rápidos de juegos**: Su curva de aprendizaje moderada y la integración con Xcode (incluido un editor visual de escenas con extensión `.sks`) permiten iterar rápidamente sobre ideas de diseño de juegos.

- **Visualizaciones interactivas y animaciones complejas**: Más allá de los juegos, SpriteKit es excelente para crear visualizaciones de datos animadas, simulaciones de partículas, fondos interactivos o efectos visuales dentro de aplicaciones convencionales.

- **Juegos multijugador locales en Apple TV**: Combinado con los controles remotos y gamepads en tvOS, permite crear experiencias multijugador locales con un rendimiento excelente.

- **Aplicaciones con efectos de partículas y física**: Cuando una app necesita simular gravedad, colisiones, explosiones o sistemas de partículas (nieve, fuego, humo) sin recurrir a un motor de juego completo.

## Instalación y configuración

SpriteKit viene integrado en el SDK de Apple, por lo que **no requiere instalación adicional** mediante CocoaPods, SPM u otro gestor de dependencias.

### Crear un proyecto desde cero

1. Abre Xcode y selecciona **File → New → Project**.
2. Elige la plantilla **Game** dentro de la sección iOS (o macOS/tvOS).
3. En **Game Technology**, selecciona **SpriteKit**.
4. Xcode generará automáticamente una `GameScene.sks` (archivo visual de escena) y un `GameScene.swift`.

### Agregar a un proyecto existente

Simplemente importa el framework en los archivos donde lo necesites:

```swift
import SpriteKit
```

### Permisos en Info.plist

SpriteKit **no requiere permisos especiales** en `Info.plist`. Sin embargo, si tu juego usa funcionalidades adicionales, podrías necesitar:

```xml
<!-- Solo si usas Game Center -->
<key>GKGameCenterEnabled</key>
<true/>

<!-- Solo si grabas gameplay con ReplayKit -->
<key>NSMicrophoneUsageDescription</key>
<string>Se necesita acceso al micrófono para grabar gameplay con audio</string>
```

### Configuración del View Controller (UIKit)

```swift
import UIKit
import SpriteKit

class GameViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        // Configurar la vista como SKView
        guard let skView = self.view as? SKView else { return }

        // Crear y presentar la escena
        let scene = GameScene(size: skView.bounds.size)
        scene.scaleMode = .aspectFill

        // Herramientas de depuración (desactivar en producción)
        skView.showsFPS = true
        skView.showsNodeCount = true
        skView.showsPhysics = true

        skView.presentScene(scene)
    }

    override var prefersStatusBarHidden: Bool { true }
}
```

## Conceptos clave

### 1. SKScene — La escena

La escena (`SKScene`) es el contenedor raíz de todo el contenido visible. Funciona como el "canvas" donde ocurre la acción. Cada escena tiene su propio ciclo de vida con métodos como `didMove(to:)`, `update(_:)` y `didSimulatePhysics()`. Puedes tener múltiples escenas (menú principal, nivel de juego, pantalla de game over) y transicionar entre ellas con animaciones.

### 2. SKNode — El nodo

Todo en SpriteKit es un nodo. `SKNode` es la clase base que forma la jerarquía de la escena (scene graph). Los nodos tienen posición, rotación, escala y pueden contener hijos. Los tipos más comunes son:
- **`SKSpriteNode`**: Muestra imágenes/texturas.
- **`SKLabelNode`**: Muestra texto.
- **`SKShapeNode`**: Dibuja formas geométricas.
- **`SKEmitterNode`**: Genera partículas.
- **`SKCameraNode`**: Controla la cámara.

### 3. SKAction — Las acciones

Las acciones son instrucciones animadas que los nodos ejecutan: mover, rotar, escalar, desvanecer, reproducir sonido, ejecutar código, etc. Se pueden componer en secuencias, grupos y repeticiones. Son el mecanismo principal para crear animaciones y comportamientos.

### 4. SKPhysicsBody — La física

SpriteKit incluye un motor de física 2D completo (basado en Box2D). Puedes asignar cuerpos físicos a los nodos para que respondan a gravedad, fuerzas, colisiones e impulsos. Los cuerpos se definen por su forma (círculo, rectángulo, polígono o basados en la textura del sprite).

### 5. SKPhysicsContact y categorías de colisión

El sistema de colisiones usa **bitmasks** para determinar qué objetos colisionan entre sí y cuáles generan notificaciones. Hay tres máscaras fundamentales: `categoryBitMask` (qué es este objeto), `collisionBitMask` (con qué objetos rebota) y `contactTestBitMask` (qué colisiones notifica al delegate).

### 6. Game Loop — El ciclo de juego

SpriteKit ejecuta un ciclo continuo por cada frame (~60 fps). El orden es: `update(_:)` → evaluar acciones → `didEvaluateActions()` → simular física → `didSimulatePhysics()` → aplicar restricciones → `didApplyConstraints()` → renderizar. Comprender este ciclo es esencial para ubicar correctamente la lógica del juego.

## Ejemplo básico

```swift
import SpriteKit

/// Escena básica que muestra un sprite en pantalla y lo mueve al tocar
class BasicScene: SKScene {

    // MARK: - Propiedades
    private var player: SKSpriteNode!

    // MARK: - Ciclo de vida de la escena
    override func didMove(to view: SKView) {
        // Configurar el fondo de la escena
        backgroundColor = .darkGray

        // Crear el sprite del jugador usando un color sólido
        player = SKSpriteNode(color: .systemBlue, size: CGSize(width: 50, height: 50))
        player.position = CGPoint(x: frame.midX, y: frame.midY)
        player.name = "jugador"
        addChild(player)

        // Crear una etiqueta informativa
        let etiqueta = SKLabelNode(text: "Toca la pantalla para mover")
        etiqueta.fontSize = 20
        etiqueta.fontColor = .white
        etiqueta.position = CGPoint(x: frame.midX, y: frame.maxY - 60)
        addChild(etiqueta)
    }

    // MARK: - Manejo de toques
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let toque = touches.first else { return }

        let posicionDestino = toque.location(in: self)

        // Calcular la distancia para ajustar la duración del movimiento
        let distancia = hypot(
            posicionDestino.x - player.position.x,
            posicionDestino.y - player.position.y
        )
        let duracion = TimeInterval(distancia / 300) // 300 puntos por segundo

        // Crear acción de movimiento con easing
        let mover = SKAction.move(to: posicionDestino, duration: duracion)
        mover.timingMode = .easeInEaseOut

        // Ejecutar la acción cancelando cualquier movimiento previo
        player.removeAllActions()
        player.run(mover)
    }

    // MARK: - Game Loop
    override func update(_ currentTime: TimeInterval) {
        // Este método se llama en cada frame (~60 veces por segundo)
        // Aquí va la lógica principal del juego
    }
}
```

## Ejemplo intermedio

```swift
import SpriteKit

/// Categorías de colisión usando bitmasks
struct CategoriaFisica {
    static let ninguna:    UInt32 = 0
    static let jugador:    UInt32 = 0b0001  // 1
    static let enemigo:    UInt32 = 0b0010  // 2
    static let proyectil:  UInt32 = 0b0100  // 4
    static let borde:      UInt32 = 0b1000  // 8
}

/// Juego tipo "Space Shooter" simplificado con física y colisiones
class ShooterScene: SKScene, SKPhysicsContactDelegate {

    // MARK: - Propiedades
    private var nave: SKSpriteNode!
    private var puntuacion: Int = 0
    private var etiquetaPuntuacion: SKLabelNode!
    private var ultimoTiempoGeneracion: TimeInterval = 0

    // MARK: - Configuración de la escena
    override func didMove(to view: SKView) {
        backgroundColor = .black
        configurarFisicaMundo()
        crearNave()
        crearHUD()
        crearFondoEstrellado()
    }

    private func configurarFisicaMundo() {
        // Configurar gravedad cero (juego espacial)
        physicsWorld.gravity = CGVector(dx: 0, dy: 0)
        physicsWorld.contactDelegate = self

        // Crear bordes de la pantalla como cuerpo físico
        let borde = SKPhysicsBody(edgeLoopFrom: frame)
        borde.categoryBitMask = CategoriaFisica.borde
        self.physicsBody = borde
    }

    private func crearNave() {
        nave = SKSpriteNode(color: .cyan, size: CGSize(width: 40, height: 50))
        nave.position = CGPoint(x: frame.midX, y: frame.minY + 100)
        nave.name = "nave"

        // Configurar cuerpo físico de la nave
        nave.physicsBody = SKPhysicsBody(rectangleOf: nave.size)
        nave.physicsBody?.isDynamic = true
        nave.physicsBody?.categoryBitMask = CategoriaFisica.jugador
        nave.physicsBody?.contactTestBitMask = CategoriaFisica.enemigo
        nave.physicsBody?.collisionBitMask = CategoriaFisica.borde
        nave.physicsBody?.allowsRotation = false

        addChild(nave)

        // Agregar efecto de propulsión con partículas
        if let propulsion = SKEmitterNode(fileNamed: "Propulsion") {
            propulsion.position = CGPoint(x: 0, y: -nave.size.height / 2)
            propulsion.targetNode = self
            nave.addChild(propulsion)
        }
    }

    private func crearHUD() {
        etiquetaPuntuacion = SKLabelNode(fontNamed: "Menlo-Bold")
        etiquetaPuntuacion.text = "Puntos: 0"
        etiquetaPuntuacion.fontSize = 18
        etiquetaPuntuacion.fontColor = .white
        etiquetaPuntuacion.horizontalAlignmentMode = .left
        etiquetaPuntuacion.position = CGPoint(x: 20, y: frame.maxY - 50)
        etiquetaPuntuacion.zPosition = 100
        addChild(etiquetaPuntuacion)
    }

    private func crearFondoEstrellado() {
        // Crear partículas de estrellas como fondo animado
        if let estrellas = SKEmitterNode(fileNamed: "Estrellas") {
            estrellas.position = CGPoint(x: frame.midX, y: frame.maxY)
            estrellas.advanceSimulationTime(10)
            estrellas.zPosition = -1
            addChild(estrellas)
        }
    }

    // MARK: - Generación de enemigos
    private func generarEnemigo() {
        let tamano = CGSize(width: 30, height: 30)
        let enemigo = SKSpriteNode(color: .red, size: tamano)

        // Posición aleatoria en la parte superior
        let xAleatorio = CGFloat.random(
            in: tamano.width...frame.width - tamano.width
        )
        enemigo.position = CGPoint(x: xAleatorio, y: frame.maxY + tamano.height)
        enemigo.name = "enemigo"

        // Física del enemigo
        enemigo.physicsBody = SKPhysicsBody(rectangleOf: tamano)
        enemigo.physicsBody?.isDynamic = true
        enemigo.physicsBody?.categoryBitMask = CategoriaFisica.enemigo
        enemigo.physicsBody?.contactTestBitMask = CategoriaFisica.proyectil
        enemigo.physicsBody?.collisionBitMask = CategoriaFisica.ninguna
        enemigo.physicsBody?.affectedByGravity = false

        addChild(enemigo)

        // Movimiento hacia abajo con velocidad aleatoria
        let duracion = TimeInterval.random(in: 3.0...6.0)
        let mover = SKAction.moveTo(y: -tamano.height, duration: duracion)
        let eliminar = SKAction.removeFromParent()
        enemigo.run(SKAction.sequence([mover, eliminar]))
    }

    // MARK: - Disparo
    