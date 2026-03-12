---
sidebar_position: 1
title: UIKit
---

# UIKit

## ¿Qué es UIKit?

UIKit es el framework fundamental de Apple para construir interfaces de usuario en aplicaciones iOS, iPadOS y tvOS. Introducido junto con el primer iPhone SDK en 2008, UIKit proporciona la infraestructura necesaria para gestionar el ciclo de vida de la aplicación, manejar eventos táctiles, renderizar vistas, gestionar animaciones y coordinar la interacción del usuario con la pantalla. Es, en esencia, la columna vertebral sobre la que se han construido millones de aplicaciones durante más de una década.

UIKit sigue un patrón de arquitectura basado en eventos y utiliza un modelo imperativo para la construcción de interfaces. A diferencia de SwiftUI, que adopta un paradigma declarativo, UIKit requiere que el desarrollador gestione explícitamente el estado de las vistas, las transiciones entre pantallas y las actualizaciones de la interfaz. Esto otorga un control granular sobre cada aspecto visual y de comportamiento, lo cual es especialmente valioso en aplicaciones complejas con requisitos de personalización avanzada.

Aunque SwiftUI ha ganado popularidad desde su lanzamiento en 2019, UIKit sigue siendo indispensable. Muchas APIs de Apple solo están disponibles a través de UIKit, gran parte del código empresarial existente está escrito con este framework, y ciertas funcionalidades avanzadas — como controladores de navegación personalizados, transiciones complejas o manejo detallado del teclado — siguen siendo más maduras y confiables en UIKit. Cualquier desarrollador iOS serio debe dominar UIKit a fondo.

## Casos de uso principales

- **Aplicaciones empresariales con interfaces complejas**: UIKit es ideal para apps con formularios extensos, tablas dinámicas, navegación profundamente anidada y flujos de trabajo multi-paso donde se necesita control total sobre el comportamiento de cada componente.

- **Aplicaciones con navegación avanzada**: Flujos de navegación con controladores modales, tab bars personalizados, split views para iPad y transiciones animadas personalizadas entre pantallas se gestionan de forma más robusta con UIKit.

- **Proyectos que requieren compatibilidad con versiones anteriores de iOS**: UIKit funciona desde iOS 2, mientras que SwiftUI requiere iOS 13 como mínimo (y muchas funcionalidades requieren iOS 15+). Para apps que deben soportar versiones antiguas, UIKit es la única opción viable.

- **Interfaces con alto grado de personalización visual**: Celdas de tabla completamente personalizadas, layouts de colección complejos con `UICollectionViewCompositionalLayout`, animaciones interactivas con `UIDynamicAnimator` o gestos personalizados con `UIGestureRecognizer`.

- **Integración con código legacy de Objective-C**: Muchas bases de código empresariales tienen componentes en Objective-C que interactúan directamente con UIKit. Mantener y extender estas aplicaciones requiere conocimiento profundo del framework.

- **Aplicaciones con manejo intensivo de texto**: Editores de texto enriquecido, campos de entrada con validación en tiempo real y layouts de texto complejos usando `NSAttributedString` y `UITextView`.

## Instalación y configuración

UIKit viene integrado por defecto en cualquier proyecto iOS. No requiere instalación adicional mediante Swift Package Manager, CocoaPods ni ningún gestor de dependencias.

### Import necesario

```swift
import UIKit
```

### Configuración del proyecto

Al crear un nuevo proyecto en Xcode con la plantilla **App**, puedes elegir entre **Storyboard** (UIKit) o **SwiftUI** como interfaz. Para proyectos puramente UIKit, selecciona **Storyboard**.

Si prefieres trabajar **sin Storyboards** (enfoque programático), debes:

1. Eliminar `Main.storyboard` del proyecto.
2. Eliminar la referencia a "Main" en `Info.plist` bajo la clave `UIMainStoryboardFile`.
3. Eliminar la referencia en el `Info.plist` del Scene Manifest:

```xml
<!-- Eliminar o vaciar el valor de UISceneStoryboardFile -->
<key>UISceneStoryboardFile</key>
<string></string>
```

4. Configurar la ventana principal manualmente en `SceneDelegate.swift`:

```swift
import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    func scene(
        _ scene: UIScene,
        willConnectTo session: UISceneSession,
        options connectionOptions: UIScene.ConnectionOptions
    ) {
        guard let windowScene = (scene as? UIWindowScene) else { return }

        window = UIWindow(windowScene: windowScene)
        window?.rootViewController = UINavigationController(
            rootViewController: HomeViewController()
        )
        window?.makeKeyAndVisible()
    }
}
```

### Permisos en Info.plist

UIKit en sí no requiere permisos especiales, pero muchos componentes que se usan junto con él sí los necesitan:

```xml
<!-- Acceso a la cámara (UIImagePickerController) -->
<key>NSCameraUsageDescription</key>
<string>Necesitamos acceso a la cámara para tomar fotos de perfil</string>

<!-- Acceso a la galería de fotos -->
<key>NSPhotoLibraryUsageDescription</key>
<string>Necesitamos acceso a tus fotos para seleccionar una imagen</string>
```

## Conceptos clave

### 1. UIViewController — El controlador de vista

Es la unidad fundamental de organización en UIKit. Cada pantalla de tu aplicación típicamente corresponde a un `UIViewController`. Gestiona una jerarquía de vistas (`view`), responde a eventos del ciclo de vida (`viewDidLoad`, `viewWillAppear`, `viewDidDisappear`, etc.) y coordina la lógica de presentación.

```swift
class MiViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        // Se llama una sola vez cuando la vista se carga en memoria
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        // Se llama cada vez que la vista está a punto de mostrarse
    }
}
```

### 2. UIView — El bloque de construcción visual

Toda pieza visual en UIKit hereda de `UIView`. Los botones (`UIButton`), las etiquetas (`UILabel`), las imágenes (`UIImageView`) y cualquier componente personalizado son subclases de `UIView`. Cada vista tiene un `frame` (posición y tamaño), un `bounds` (sistema de coordenadas interno) y puede contener subvistas formando una jerarquía.

### 3. Auto Layout — El sistema de layout basado en restricciones

Auto Layout permite definir interfaces que se adaptan a diferentes tamaños de pantalla mediante **constraints** (restricciones). En lugar de posicionar vistas con coordenadas absolutas, defines relaciones entre ellas: "esta etiqueta debe estar 16 puntos debajo de la imagen" o "este botón debe estar centrado horizontalmente".

```swift
NSLayoutConstraint.activate([
    etiqueta.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
    etiqueta.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
    etiqueta.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16)
])
```

### 4. Delegación (Delegate Pattern)

UIKit utiliza el patrón de delegación de forma extensiva. Un objeto delega ciertas responsabilidades a otro objeto que conforma un protocolo. Por ejemplo, `UITableView` delega la configuración de celdas y la respuesta a selecciones a su `dataSource` y `delegate`.

### 5. UINavigationController y navegación

`UINavigationController` gestiona una pila de controladores de vista, permitiendo navegación hacia adelante (`pushViewController`) y hacia atrás (`popViewController`). Es el mecanismo principal para flujos de navegación jerárquica.

### 6. UITableView y UICollectionView — Listas y colecciones

Son los componentes más utilizados en UIKit para mostrar listas desplazables de datos. `UITableView` muestra filas verticales, mientras que `UICollectionView` permite layouts flexibles en cuadrículas, carruseles y cualquier disposición personalizada.

## Ejemplo básico

Este ejemplo muestra cómo crear una pantalla simple con una etiqueta y un botón, todo de forma programática:

```swift
import UIKit

/// Controlador básico que muestra una etiqueta y un botón
/// Demuestra la configuración programática de vistas y Auto Layout
class SaludoViewController: UIViewController {

    // MARK: - UI Components

    /// Etiqueta que muestra el mensaje de saludo
    private let etiquetaSaludo: UILabel = {
        let label = UILabel()
        label.text = "¡Hola, UIKit!"
        label.font = UIFont.systemFont(ofSize: 28, weight: .bold)
        label.textColor = .label
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    /// Botón que cambia el texto de la etiqueta al pulsarlo
    private let botonCambiar: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Cambiar saludo", for: .normal)
        button.titleLabel?.font = UIFont.systemFont(ofSize: 18, weight: .medium)
        button.backgroundColor = .systemBlue
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 12
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()

    // MARK: - Propiedades

    /// Contador para alternar entre saludos
    private var contadorSaludos = 0

    /// Lista de saludos disponibles
    private let saludos = [
        "¡Hola, UIKit!",
        "¡Bienvenido, desarrollador!",
        "¡Swift es genial!",
        "¡Sigue programando!"
    ]

    // MARK: - Ciclo de vida

    override func viewDidLoad() {
        super.viewDidLoad()
        configurarVista()
        configurarConstraints()
        configurarAcciones()
    }

    // MARK: - Configuración

    /// Configura la vista principal y agrega las subvistas
    private func configurarVista() {
        view.backgroundColor = .systemBackground
        title = "Ejemplo Básico"

        view.addSubview(etiquetaSaludo)
        view.addSubview(botonCambiar)
    }

    /// Define las restricciones de Auto Layout para posicionar los elementos
    private func configurarConstraints() {
        NSLayoutConstraint.activate([
            // Etiqueta centrada verticalmente, con un pequeño desplazamiento hacia arriba
            etiquetaSaludo.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            etiquetaSaludo.centerYAnchor.constraint(
                equalTo: view.centerYAnchor,
                constant: -40
            ),
            etiquetaSaludo.leadingAnchor.constraint(
                equalTo: view.leadingAnchor,
                constant: 20
            ),
            etiquetaSaludo.trailingAnchor.constraint(
                equalTo: view.trailingAnchor,
                constant: -20
            ),

            // Botón debajo de la etiqueta
            botonCambiar.topAnchor.constraint(
                equalTo: etiquetaSaludo.bottomAnchor,
                constant: 30
            ),
            botonCambiar.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            botonCambiar.widthAnchor.constraint(equalToConstant: 220),
            botonCambiar.heightAnchor.constraint(equalToConstant: 50)
        ])
    }

    /// Conecta las acciones de los botones
    private func configurarAcciones() {
        botonCambiar.addTarget(
            self,
            action: #selector(cambiarSaludo),
            for: .touchUpInside
        )
    }

    // MARK: - Acciones

    /// Cambia el texto de la etiqueta al siguiente saludo con una animación suave
    @objc private func cambiarSaludo() {
        contadorSaludos = (contadorSaludos + 1) % saludos.count

        UIView.animate(withDuration: 0.3) {
            self.etiquetaSaludo.alpha = 0
        } completion: { _ in
            self.etiquetaSaludo.text = self.saludos[self.contadorSaludos]
            UIView.animate(withDuration: 0.3) {
                self.etiquetaSaludo.alpha = 1
            }
        }
    }
}
```

## Ejemplo intermedio

Este ejemplo muestra una pantalla con una tabla que carga datos de una API simulada, con celdas personalizadas, pull-to-refresh y manejo de estados vacíos:

```swift
import UIKit

// MARK: - Modelo de datos

/// Representa un usuario en la lista
struct Usuario {
    let id: Int
    let nombre: String
    let email: String
    let avatar: String
}

// MARK: - Celda personalizada

/// Celda personalizada para mostrar información de un usuario
class UsuarioCelda: UITableViewCell {

    /// Identificador reutilizable para la celda
    static let identificador = "UsuarioCelda"

    // MARK: - UI Components

    private let avatarImageView: UIImageView = {
        let imageView = UIImageView()
        imageView.contentMode = .scaleAspectFill
        imageView.clipsToBounds = true
        imageView.layer.cornerRadius = 25
        imageView.backgroundColor = .systemGray5
        imageView.tintColor = .systemGray3
        imageView.image = UIImage(systemName: "person.circle.fill")
        imageView.translatesAutoresizingMaskIntoConstraints = false
        return imageView
    }()

    private let nombreLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 17, weight: .semibold)
        label.textColor = .label
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private let emailLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 14, weight: .regular)
        label.textColor = .secondaryLabel
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private let contenedorTexto: UIStackView = {
        let stack = UIStackView()
        stack.axis = .vertical
        stack.spacing = 4
        stack.translatesAutoresizingMaskIntoConstraints = false
        return stack
    }()

    // MARK: - Inicialización

    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        configurarLayout()
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) no ha sido implementado")
    }

    // MARK: - Configuración

    private func configurarLayout() {
        accessoryType = .disclosureIndicator

        contentView.addSubview(avatarImageView)
        contenedorTexto.addArrangedSubview(nombreLabel)
        contened