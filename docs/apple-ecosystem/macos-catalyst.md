---
sidebar_position: 1
title: Macos Catalyst
---

# Mac Catalyst: Lleva tus Apps de iPad a macOS

## ¿Qué es Mac Catalyst?

Mac Catalyst es una tecnología introducida por Apple en WWDC 2019 (originalmente conocida como "Project Marzipan") que permite a los desarrolladores **portar sus aplicaciones de iPad a macOS** con cambios mínimos en el código fuente. En esencia, Mac Catalyst traduce las APIs de UIKit para que funcionen de forma nativa en el entorno de escritorio de macOS.

Esto significa que si ya tienes una aplicación para iPad, puedes compilarla como una aplicación nativa de Mac **marcando una simple casilla en Xcode**, aunque la realidad de crear una experiencia de escritorio verdaderamente pulida requiere trabajo adicional significativo.

```
┌─────────────────────────────────────────────────┐
│              Tu código Swift + UIKit             │
├─────────────────────────────────────────────────┤
│                  Mac Catalyst                    │
│         (Capa de traducción UIKit → AppKit)      │
├──────────┬──────────────┬───────────────────────┤
│   iOS    │   iPadOS     │       macOS            │
└──────────┴──────────────┴───────────────────────┘
```

## ¿Por qué es importante para desarrolladores iOS en LATAM?

### 1. Multiplicar tu alcance de mercado sin multiplicar tu equipo

En Latinoamérica, muchos equipos de desarrollo son pequeños — a veces de una sola persona. Mac Catalyst permite que **un solo desarrollador iOS cubra también el mercado de Mac** sin necesidad de aprender AppKit desde cero ni contratar un especialista en macOS.

### 2. Oportunidad de diferenciación

El mercado de aplicaciones para macOS está **considerablemente menos saturado** que el de iOS. Mientras miles de desarrolladores compiten en la App Store de iPhone, la Mac App Store tiene menos competencia, lo cual representa una oportunidad real de visibilidad y monetización.

### 3. Clientes empresariales lo demandan

En el sector corporativo latinoamericano, especialmente en banca, fintech y gobierno, cada vez más organizaciones adoptan flotas de Mac. Poder ofrecer una versión de escritorio a partir de tu app de iPad es un **argumento de venta poderoso** para proyectos B2B.

### 4. Trabajo remoto y freelance internacional

Dominar Mac Catalyst te posiciona como un desarrollador multiplataforma Apple, algo muy valorado en plataformas de freelance internacional donde clientes de EE.UU. y Europa buscan developers que puedan entregar apps para todo el ecosistema.

## Configuración inicial

### Paso 1: Habilitar Mac Catalyst en tu proyecto

En Xcode, selecciona tu target principal, ve a la pestaña **General** y en la sección **Supported Destinations**, marca **Mac (Mac Catalyst)**.

También puedes hacerlo desde **Signing & Capabilities**:

1. Abre tu proyecto en Xcode 15 o superior
2. Selecciona tu target
3. Ve a **General → Supported Destinations**
4. Haz clic en **+** y selecciona **Mac (Mac Catalyst)**

### Paso 2: Primera compilación

Selecciona **"My Mac (Mac Catalyst)"** como destino de compilación y presiona `Cmd + R`. Tu app debería ejecutarse como una aplicación de Mac.

> ⚠️ **Nota importante**: No todo el código que funciona en iOS compilará automáticamente para Mac Catalyst. Las APIs que dependen de hardware exclusivo del iPhone (como `ARKit`, `CoreNFC` o `HealthKit`) no están disponibles.

## Adaptaciones esenciales para una buena experiencia de escritorio

### Verificar la plataforma en tiempo de ejecución

Hay situaciones donde necesitas ejecutar código específico para cada plataforma. Usa compilación condicional:

```swift
#if targetEnvironment(macCatalyst)
    // Código exclusivo para Mac Catalyst
    print("Ejecutando en macOS vía Catalyst")
#else
    // Código para iOS/iPadOS
    print("Ejecutando en iOS o iPadOS")
#endif
```

### Configurar el tamaño de ventana

En macOS, los usuarios esperan poder redimensionar ventanas. Configura restricciones de tamaño apropiadas:

```swift
import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    func scene(
        _ scene: UIScene,
        willConnectTo session: UISceneSession,
        options connectionOptions: UIScene.ConnectionOptions
    ) {
        guard let windowScene = scene as? UIWindowScene else { return }

        #if targetEnvironment(macCatalyst)
        // Configurar tamaño mínimo y máximo de la ventana
        if let sizeRestrictions = windowScene.sizeRestrictions {
            sizeRestrictions.minimumSize = CGSize(width: 800, height: 600)
            sizeRestrictions.maximumSize = CGSize(width: 1920, height: 1080)
        }

        // Configurar el título de la ventana
        windowScene.title = "Mi App Catalyst"
        #endif
    }
}
```

### Agregar una barra de herramientas (Toolbar) nativa de macOS

Una toolbar le da a tu app un aspecto profesional y nativo en macOS:

```swift
#if targetEnvironment(macCatalyst)
extension SceneDelegate: NSToolbarDelegate {

    func configureToolbar(for windowScene: UIWindowScene) {
        let toolbar = NSToolbar(identifier: "MainToolbar")
        toolbar.delegate = self
        toolbar.displayMode = .iconAndLabel
        toolbar.allowsUserCustomization = true

        if let titlebar = windowScene.titlebar {
            titlebar.toolbar = toolbar
            titlebar.toolbarStyle = .automatic
        }
    }

    func toolbar(
        _ toolbar: NSToolbar,
        itemForItemIdentifier itemIdentifier: NSToolbarItem.Identifier,
        willBeInsertedIntoToolbar flag: Bool
    ) -> NSToolbarItem? {

        if itemIdentifier == NSToolbarItem.Identifier("addItem") {
            let item = NSToolbarItem(itemIdentifier: itemIdentifier)
            item.image = UIImage(systemName: "plus.circle.fill")
            item.label = "Agregar"
            item.toolTip = "Agregar nuevo elemento"
            item.target = self
            item.action = #selector(addItemTapped)
            return item
        }
        return nil
    }

    func toolbarDefaultItemIdentifiers(_ toolbar: NSToolbar) -> [NSToolbarItem.Identifier] {
        return [
            .flexibleSpace,
            NSToolbarItem.Identifier("addItem"),
            .flexibleSpace
        ]
    }

    func toolbarAllowedItemIdentifiers(_ toolbar: NSToolbar) -> [NSToolbarItem.Identifier] {
        return toolbarDefaultItemIdentifiers(toolbar)
    }

    @objc func addItemTapped() {
        print("Botón de agregar presionado en la toolbar")
    }
}
#endif
```

### Soporte para menús del sistema

Los usuarios de Mac esperan un menú completo en la barra superior. Implementa esto en tu `AppDelegate`:

```swift
override func buildMenu(with builder: UIMenuBuilder) {
    super.buildMenu(with: builder)

    // Solo modificar el menú principal del sistema
    guard builder.system == .main else { return }

    // Remover menús que no aplican
    builder.remove(menu: .format)

    // Agregar menú personalizado
    let exportAction = UIAction(
        title: "Exportar datos",
        image: UIImage(systemName: "square.and.arrow.up")
    ) { _ in
        self.exportData()
    }

    // Agregar atajo de teclado
    let importAction = UIKeyCommand(
        title: "Importar datos",
        image: UIImage(systemName: "square.and.arrow.down"),
        action: #selector(importData),
        input: "I",
        modifierFlags: [.command, .shift]
    )

    let fileMenu = UIMenu(
        title: "Archivo",
        children: [exportAction, importAction]
    )

    builder.insertChild(fileMenu, atStartOfMenu: .file)
}

@objc func importData() {
    print("Importando datos...")
}

func exportData() {
    print("Exportando datos...")
}
```

### Soporte para atajos de teclado

Los usuarios de Mac viven con el teclado. Agrega atajos en tus `UIViewController`:

```swift
class MainViewController: UIViewController {

    override var keyCommands: [UIKeyCommand]? {
        return [
            UIKeyCommand(
                title: "Buscar",
                action: #selector(performSearch),
                input: "F",
                modifierFlags: .command
            ),
            UIKeyCommand(
                title: "Nuevo documento",
                action: #selector(createNewDocument),
                input: "N",
                modifierFlags: .command
            ),
            UIKeyCommand(
                title: "Recargar",
                action: #selector(reloadContent),
                input: "R",
                modifierFlags: .command
            )
        ]
    }

    @objc func performSearch() {
        // Mostrar interfaz de búsqueda
        let searchController = UISearchController(searchResultsController: nil)
        present(searchController, animated: true)
    }

    @objc func createNewDocument() {
        print("Creando nuevo documento...")
    }

    @objc func reloadContent() {
        print("Recargando contenido...")
    }
}
```

### Soporte para Hover (cursor del mouse)

En macOS, el usuario tiene un cursor. Aprovéchalo para dar retroalimentación visual:

```swift
class HoverableButton: UIButton {

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupHoverInteraction()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupHoverInteraction()
    }

    private func setupHoverInteraction() {
        let hoverGesture = UIHoverGestureRecognizer(
            target: self,
            action: #selector(handleHover(_:))
        )
        addGestureRecognizer(hoverGesture)
    }

    @objc private func handleHover(_ recognizer: UIHoverGestureRecognizer) {
        switch recognizer.state {
        case .began:
            // El cursor entró al área del botón
            UIView.animate(withDuration: 0.2) {
                self.transform = CGAffineTransform(scaleX: 1.05, y: 1.05)
                self.backgroundColor = .systemGray5
            }
        case .ended, .cancelled:
            // El cursor salió del área del botón
            UIView.animate(withDuration: 0.2) {
                self.transform = .identity
                self.backgroundColor = .clear
            }
        default:
            break
        }
    }
}
```

## Soporte para múltiples ventanas

Una de las ventajas más importantes en macOS es el soporte de múltiples ventanas:

```swift
class DocumentViewController: UIViewController {

    @objc func openNewWindow() {
        // Crear una nueva actividad de escena
        let activity = NSUserActivity(activityType: "com.miapp.newdocument")
        activity.title = "Nuevo Documento"
        activity.userInfo = ["documentId": UUID().uuidString]

        UIApplication.shared.requestSceneSessionActivation(
            nil,                    // Nueva escena
            userActivity: activity, // Actividad asociada
            options: nil,
            errorHandler: { error in
                print("Error al abrir nueva ventana: \(error.localizedDescription)")
            }
        )
    }
}
```

Configura el soporte en `Info.plist`:

```xml
<key>UIApplicationSceneManifest</key>
<dict>
    <key>UIApplicationSupportsMultipleScenes</key>
    <true/>
    <key>UISceneConfigurations</key>
    <dict>
        <key>UIWindowSceneSessionRoleApplication</key>
        <array>
            <dict>
                <key>UISceneConfigurationName</key>
                <string>Default Configuration</string>
                <key>UISceneDelegateClassName</key>
                <string>$(PRODUCT_MODULE_NAME).SceneDelegate</string>
            </dict>
        </array>
    </dict>
</dict>
```

## Manejo de APIs no disponibles

Algunas APIs de iOS no están disponibles en Mac Catalyst. Manéjalas con gracia:

```swift
class CameraManager {

    enum CameraError: Error {
        case notAvailableOnMac
        case permissionDenied
        case unknown
    }

    func capturePhoto(
        from viewController: UIViewController,
        completion: @escaping (Result<UIImage, CameraError>) -> Void
    ) {
        #if targetEnvironment(macCatalyst)
        // En Mac, ofrecer alternativa: seleccionar archivo
        let picker = UIDocumentPickerViewController(
            forOpeningContentTypes: [.image]
        )
        viewController.present(picker, animated: true)
        #else
        // En iOS, usar la cámara normalmente
        guard UIImagePickerController.isSourceTypeAvailable(.camera) else {
            completion(.failure(.notAvailableOnMac))
            return
        }

        let imagePicker = UIImagePickerController()
        imagePicker.sourceType = .camera
        viewController.present(imagePicker, animated: true)
        #endif
    }
}
```

## Acceder a APIs de AppKit (Avanzado)

En algunos casos, necesitas acceder directamente a AppKit. Esto se logra mediante un plugin de bundle:

### Paso 1: Crear el protocolo puente

```swift
// Archivo compartido: MacBridge.swift
@objc protocol MacBridgeProtocol: NSObjectProtocol {
    func showNativeSavePanel(
        filename: String,
        completion: @escaping (String?) -> Void
    )
    func setWindowAppearance(isDark: Bool)
}
```

### Paso 2: Crear un Bundle target para macOS

Crea un nuevo target en Xcode de tipo **"Bundle"** con destino **macOS**:

```swift
// MacBridgePlugin.swift (en el target del bundle macOS)
import AppKit

class MacBridgePlugin: NSObject, MacBridgeProtocol {

    func showNativeSavePanel(
        filename: String,
        completion: @escaping (String?) -> Void
    ) {
        let savePanel = NSSavePanel()
        savePanel.nameFieldStringValue = filename
        savePanel.allowedContentTypes = [.pdf, .png]
        savePanel.canCreateDirectories = true

        savePanel.begin { response in
            if response == .OK {
                completion(savePanel.url?.path)
            } else {
                completion(nil)
            }
        }
    }

    func setWindowAppearance(isDark: Bool) {
        NSApp.appearance = NSAppearance(
            named: isDark ? .darkAqua : .aqua
        )
    }
}
```

### Paso 3: Cargar el plugin desde tu app Catalyst

```swift
class MacPluginLoader {

    static let shared = MacPluginLoader()

    private var plugin: MacBridgeProtocol?

    func loadPlugin() {
        #if targetEnvironment(macCatalyst)
        guard let bundleURL = Bundle.main.builtInPlugInsURL?
            .appendingPathComponent("MacBridgePlugin.bundle"),
              let bundle = Bundle(url: bundleURL),