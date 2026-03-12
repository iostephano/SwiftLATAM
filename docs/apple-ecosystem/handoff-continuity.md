---
sidebar_position: 1
title: Handoff Continuity
---

# Handoff y Continuity: Experiencias Fluidas en el Ecosistema Apple

## ¿Qué es Handoff?

Handoff es una característica del ecosistema Apple que permite a los usuarios **comenzar una actividad en un dispositivo y continuarla en otro** de manera transparente. Imagina que un usuario está leyendo un artículo en tu app en su iPhone mientras viaja en el metro en Ciudad de México, y al llegar a casa abre su Mac y continúa exactamente donde lo dejó. Eso es Handoff.

Handoff forma parte de un conjunto más amplio de tecnologías llamado **Continuity**, que incluye:

- **Handoff**: Transferir actividades entre dispositivos
- **Universal Clipboard**: Copiar en un dispositivo, pegar en otro
- **Auto Unlock**: Desbloquear la Mac con el Apple Watch
- **Continuity Camera**: Usar el iPhone como cámara del Mac
- **Sidecar**: Usar el iPad como segunda pantalla
- **AirDrop**: Compartir archivos entre dispositivos cercanos

Como desarrolladores, nuestra responsabilidad directa recae principalmente en **Handoff**, ya que requiere implementación explícita en nuestras apps.

## ¿Por qué es importante para devs iOS en LATAM?

En Latinoamérica, el ecosistema Apple está creciendo de manera sostenida. Cada vez más usuarios poseen múltiples dispositivos Apple — un iPhone y un Mac, o un iPhone y un iPad. Implementar Handoff en tus aplicaciones ofrece varias ventajas competitivas:

1. **Diferenciación profesional**: La mayoría de las apps en el mercado latinoamericano NO implementan Handoff. Hacerlo te posiciona como un desarrollador que domina el ecosistema completo.

2. **Experiencia de usuario superior**: Las apps de banca, e-commerce y productividad que dominan el mercado LATAM rara vez aprovechan esta funcionalidad. Es una oportunidad enorme.

3. **Requisito en empresas de primer nivel**: Empresas como Rappi, Mercado Libre, Nubank o Kavak que buscan ingenieros iOS senior valoran el conocimiento profundo del ecosistema Apple.

4. **Preparación para visionOS**: Con la llegada del Apple Vision Pro, Continuity será aún más relevante. Los desarrolladores que dominen estas APIs estarán mejor preparados.

## Requisitos Previos del Sistema

Para que Handoff funcione, los dispositivos deben cumplir:

- Estar conectados con el **mismo Apple ID** en iCloud
- Tener **Bluetooth LE** activado
- Tener **Wi-Fi** activado
- Estar en **proximidad física** (Bluetooth range)
- Tener Handoff habilitado en Configuración

## Arquitectura de Handoff

El flujo de Handoff se basa en `NSUserActivity`, un objeto que encapsula el **estado de lo que el usuario está haciendo**:

```
┌─────────────────────┐         Bluetooth LE          ┌─────────────────────┐
│   DISPOSITIVO A     │  ─────────────────────────▶   │   DISPOSITIVO B     │
│   (Origen)          │    Anuncia actividad           │   (Destino)         │
│                     │                                │                     │
│  NSUserActivity     │         Wi-Fi/iCloud           │  NSUserActivity     │
│  - activityType     │  ◀─────────────────────────    │  - Restaura estado  │
│  - userInfo         │    Solicita datos completos    │  - Continúa tarea   │
│  - webpageURL       │                                │                     │
└─────────────────────┘                                └─────────────────────┘
```

1. El **dispositivo origen** crea y anuncia una `NSUserActivity`
2. El anuncio viaja por **Bluetooth LE** (solo metadatos mínimos)
3. El **dispositivo destino** detecta la actividad y muestra el ícono de Handoff
4. Cuando el usuario acepta, los datos completos se transfieren por **Wi-Fi o iCloud**

## Implementación Paso a Paso

### Paso 1: Configurar el Info.plist

Primero, debes declarar los tipos de actividad que tu app soporta. Agrega la clave `NSUserActivityTypes` en tu `Info.plist`:

```xml
<key>NSUserActivityTypes</key>
<array>
    <string>com.tuempresa.tuapp.viewing-article</string>
    <string>com.tuempresa.tuapp.editing-document</string>
    <string>com.tuempresa.tuapp.browsing-catalog</string>
</array>
```

> ⚠️ **Importante**: Los tipos de actividad deben usar **notación de dominio reverso** y ser idénticos en todas las apps que participen en el Handoff (iOS, macOS, iPadOS).

### Paso 2: Crear y Anunciar una Actividad

Veamos un ejemplo práctico — una app de recetas mexicanas donde el usuario puede continuar viendo una receta en otro dispositivo:

```swift
import UIKit

class RecipeDetailViewController: UIViewController {

    // MARK: - Properties
    private var recipe: Recipe
    private var currentActivity: NSUserActivity?

    // MARK: - Activity Type Constants
    private enum ActivityType {
        static let viewingRecipe = "com.cocinalatam.app.viewing-recipe"
    }

    // MARK: - Initialization
    init(recipe: Recipe) {
        self.recipe = recipe
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupUserActivity()
    }

    override func viewDidDisappear(_ animated: Bool) {
        super.viewDidDisappear(animated)
        // Invalidar la actividad cuando el usuario sale de la pantalla
        currentActivity?.invalidate()
        currentActivity = nil
    }

    // MARK: - Handoff Setup
    private func setupUserActivity() {
        let activity = NSUserActivity(activityType: ActivityType.viewingRecipe)

        // Título visible en el dispositivo destino
        activity.title = "Viendo: \(recipe.name)"

        // Datos necesarios para restaurar el estado
        activity.userInfo = [
            "recipeID": recipe.id,
            "recipeName": recipe.name,
            "scrollPosition": 0.0
        ]

        // Habilitar Handoff
        activity.isEligibleForHandoff = true

        // Habilitar búsqueda en Spotlight (bonus)
        activity.isEligibleForSearch = true

        // Habilitar sugerencias de Siri (bonus)
        activity.isEligibleForPrediction = true

        // URL web como fallback si la app no está instalada
        // en el dispositivo destino
        activity.webpageURL = URL(string: "https://cocinalatam.com/recetas/\(recipe.slug)")

        // Metadatos para Spotlight
        let attributes = CSSearchableItemAttributeSet(contentType: .content)
        attributes.displayName = recipe.name
        attributes.contentDescription = recipe.shortDescription
        attributes.thumbnailURL = recipe.thumbnailURL
        activity.contentAttributeSet = attributes

        // Asignar como actividad actual del view controller
        self.userActivity = activity
        currentActivity = activity

        // Notificar al sistema que la actividad necesita actualización
        activity.needsSave = true
    }
}
```

### Paso 3: Actualizar la Actividad Dinámicamente

Cuando el estado del usuario cambia (por ejemplo, hace scroll en la receta), debes actualizar la actividad:

```swift
extension RecipeDetailViewController {

    // Este método es llamado por el sistema cuando necesita
    // los datos más recientes de la actividad
    override func updateUserActivityState(_ activity: NSUserActivity) {
        super.updateUserActivityState(activity)

        // Actualizar con el estado más reciente
        activity.userInfo = [
            "recipeID": recipe.id,
            "recipeName": recipe.name,
            "scrollPosition": scrollView.contentOffset.y,
            "selectedTabIndex": segmentedControl.selectedSegmentIndex,
            "servingsCount": currentServings
        ]
    }

    // Llamar esto cuando el usuario interactúa
    func scrollViewDidScroll(_ scrollView: UIScrollView) {
        // Marcar que la actividad necesita guardar su estado
        userActivity?.needsSave = true
    }

    func servingsDidChange(to count: Int) {
        currentServings = count
        userActivity?.needsSave = true
    }
}
```

### Paso 4: Recibir y Restaurar la Actividad

En el **dispositivo destino**, debes manejar la actividad entrante. Hay dos lugares principales donde hacerlo:

#### En el AppDelegate (UIKit):

```swift
class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(
        _ application: UIApplication,
        willContinueUserActivityWithType userActivityType: String
    ) -> Bool {
        // El sistema nos notifica que va a llegar una actividad
        // Puedes mostrar un indicador de carga aquí
        print("📡 Preparando para recibir actividad: \(userActivityType)")
        showLoadingIndicator(message: "Continuando desde otro dispositivo...")
        return true
    }

    func application(
        _ application: UIApplication,
        continue userActivity: NSUserActivity,
        restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void
    ) -> Bool {

        guard userActivity.activityType == "com.cocinalatam.app.viewing-recipe" else {
            return false
        }

        guard let userInfo = userActivity.userInfo,
              let recipeID = userInfo["recipeID"] as? String else {
            return false
        }

        print("✅ Continuando receta: \(recipeID)")

        // Opción 1: Navegar directamente
        navigateToRecipe(
            id: recipeID,
            scrollPosition: userInfo["scrollPosition"] as? CGFloat ?? 0,
            servingsCount: userInfo["servingsCount"] as? Int ?? 4
        )

        // Opción 2: Usar el restoration handler para delegar
        // al view controller correspondiente
        // restorationHandler([recipeDetailVC])

        return true
    }

    func application(
        _ application: UIApplication,
        didFailToContinueUserActivityWithType userActivityType: String,
        error: Error
    ) {
        // Manejar errores gracefully
        print("❌ Error al continuar actividad: \(error.localizedDescription)")
        hideLoadingIndicator()
        showErrorAlert(
            title: "No se pudo continuar",
            message: "Hubo un problema al transferir la actividad. Intenta de nuevo."
        )
    }

    // MARK: - Navigation Helper
    private func navigateToRecipe(
        id: String,
        scrollPosition: CGFloat,
        servingsCount: Int
    ) {
        Task {
            do {
                let recipe = try await RecipeService.shared.fetchRecipe(byID: id)
                await MainActor.run {
                    let detailVC = RecipeDetailViewController(recipe: recipe)
                    detailVC.initialScrollPosition = scrollPosition
                    detailVC.initialServingsCount = servingsCount

                    let navController = window?.rootViewController as? UINavigationController
                    navController?.pushViewController(detailVC, animated: true)
                    hideLoadingIndicator()
                }
            } catch {
                await MainActor.run {
                    hideLoadingIndicator()
                    showErrorAlert(
                        title: "Receta no encontrada",
                        message: "No pudimos cargar la receta. Verifica tu conexión."
                    )
                }
            }
        }
    }
}
```

#### En SceneDelegate (para apps con escenas):

```swift
class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    func scene(
        _ scene: UIScene,
        willContinueUserActivityWithType userActivityType: String
    ) {
        print("📡 Escena preparando para actividad: \(userActivityType)")
    }

    func scene(
        _ scene: UIScene,
        continue userActivity: NSUserActivity
    ) {
        handleIncomingActivity(userActivity)
    }

    func scene(
        _ scene: UIScene,
        didFailToContinueUserActivityWithType userActivityType: String,
        error: Error
    ) {
        print("❌ Fallo en escena: \(error)")
    }
}
```

### Paso 5: Implementación con SwiftUI

Si trabajas con SwiftUI (que es lo más probable en proyectos nuevos), la implementación es considerablemente más limpia:

```swift
import SwiftUI

struct RecipeDetailView: View {
    let recipe: Recipe
    @State private var scrollPosition: CGFloat = 0
    @State private var servingsCount: Int = 4
    @State private var selectedTab: Int = 0

    // Definir el tipo de actividad
    private let activityType = "com.cocinalatam.app.viewing-recipe"

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                RecipeHeaderView(recipe: recipe)

                Picker("Sección", selection: $selectedTab) {
                    Text("Ingredientes").tag(0)
                    Text("Preparación").tag(1)
                    Text("Tips").tag(2)
                }
                .pickerStyle(.segmented)

                ServingsStepperView(count: $servingsCount)

                switch selectedTab {
                case 0:
                    IngredientsListView(
                        ingredients: recipe.ingredients,
                        servings: servingsCount
                    )
                case 1:
                    StepsListView(steps: recipe.steps)
                default:
                    TipsListView(tips: recipe.tips)
                }
            }
            .padding()
        }
        .navigationTitle(recipe.name)
        // ✨ La magia de Handoff en SwiftUI
        .userActivity(activityType) { activity in
            activity.title = "Viendo: \(recipe.name)"
            activity.isEligibleForHandoff = true
            activity.isEligibleForSearch = true
            activity.isEligibleForPrediction = true
            activity.webpageURL = URL(
                string: "https://cocinalatam.com/recetas/\(recipe.slug)"
            )
            activity.userInfo = [
                "recipeID": recipe.id,
                "recipeName": recipe.name,
                "scrollPosition": scrollPosition,
                "selectedTab": selectedTab,
                "servingsCount": servingsCount
            ]
        }
        // Recibir actividades entrantes
        .onContinueUserActivity(activityType) { activity in
            handleIncomingActivity(activity)
        }
    }

    private func handleIncomingActivity(_ activity: NSUserActivity) {
        guard let userInfo = activity.userInfo else { return }

        if let position = userInfo["scrollPosition"] as? CGFloat {
            scrollPosition = position
        }
        if let tab = userInfo["selectedTab"] as? Int {
            selectedTab = tab
        }
        if let servings = userInfo["servingsCount"] as? Int {
            servingsCount = servings
        }
    }
}
```

### Manejo Centralizado con un Router en SwiftUI:

```swift
import SwiftUI

@main
struct CocinaLATAMApp: App {
    @StateObject private var router = AppRouter()