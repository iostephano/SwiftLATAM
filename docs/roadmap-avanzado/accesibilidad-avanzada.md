---
sidebar_position: 1
title: Accesibilidad Avanzada
---

# Accesibilidad Avanzada en iOS

## ¿Qué es la accesibilidad avanzada?

La accesibilidad avanzada va mucho más allá de agregar `accessibilityLabel` a tus botones. Se trata de construir experiencias verdaderamente inclusivas que funcionen para **todas las personas**, independientemente de sus capacidades visuales, auditivas, motoras o cognitivas. Implica dominar las APIs profundas de `UIAccessibility`, construir componentes personalizados que se comporten correctamente con tecnologías asistivas y auditar tu aplicación de forma sistemática.

Cuando hablamos de nivel avanzado, nos referimos a:

- Crear **elementos de accesibilidad personalizados** para vistas complejas (gráficas, mapas, controles custom).
- Implementar **rotores personalizados** para navegación eficiente.
- Manejar **notificaciones de accesibilidad** dinámicas.
- Soportar correctamente **Dynamic Type** en layouts complejos.
- Adaptar la UI según las **preferencias del usuario** (reducir movimiento, aumentar contraste, etc.).
- Integrar **pruebas automatizadas de accesibilidad** en tu pipeline de CI/CD.

---

## ¿Por qué es crucial para devs iOS en LATAM?

### El contexto latinoamericano

En Latinoamérica, **más de 85 millones de personas viven con algún tipo de discapacidad** según la CEPAL. En México, Brasil, Colombia y Argentina existen leyes específicas que exigen accesibilidad digital:

- **México**: Ley General para la Inclusión de las Personas con Discapacidad.
- **Brasil**: Lei Brasileira de Inclusão (LBI - Lei 13.146/2015).
- **Colombia**: Ley 1618 de 2013.
- **Argentina**: Ley 26.653 de Accesibilidad Web.

Muchas apps del sector fintech, gobierno digital y salud en la región **están obligadas legalmente** a ser accesibles. Ignorar la accesibilidad no es solo un problema ético: es un riesgo legal y de negocio.

### La ventaja competitiva

La realidad es que **muy pocos desarrolladores iOS en LATAM dominan accesibilidad avanzada**. Esto representa una oportunidad enorme. Si te especializas en este campo, te diferencias inmediatamente en el mercado laboral y puedes acceder a posiciones senior y de consultoría tanto en empresas locales como remotas internacionales.

---

## Elementos de accesibilidad personalizados

Cuando tienes una vista compleja (como una gráfica de barras o un tablero personalizado), VoiceOver no puede interpretar automáticamente cada elemento visual. Necesitas crear **elementos de accesibilidad virtuales**.

### Ejemplo: Gráfica de barras accesible

```swift
import UIKit

class BarChartView: UIView {

    struct BarData {
        let label: String
        let value: Double
        let frame: CGRect
    }

    var bars: [BarData] = []

    // MARK: - Accesibilidad

    override var isAccessibilityElement: Bool {
        get { return false } // El contenedor NO es un elemento
        set {}
    }

    override var accessibilityElements: [Any]? {
        get {
            return bars.enumerated().map { index, bar in
                let element = UIAccessibilityElement(accessibilityContainer: self)
                element.accessibilityLabel = bar.label
                element.accessibilityValue = "\(Int(bar.value)) unidades"
                element.accessibilityFrameInContainerSpace = bar.frame
                element.accessibilityTraits = .staticText
                element.accessibilityHint = "Barra \(index + 1) de \(bars.count)"
                return element
            }
        }
        set {}
    }
}
```

### ¿Qué hace este código?

1. Marca el contenedor como **no accesible** directamente (`isAccessibilityElement = false`).
2. Crea un `UIAccessibilityElement` virtual por cada barra.
3. Cada elemento tiene su propio `label`, `value`, `hint` y **frame** para que VoiceOver posicione el cursor correctamente.
4. El usuario puede navegar barra por barra con swipe izquierda/derecha.

---

## Rotores personalizados

El **rotor** es una de las herramientas más poderosas de VoiceOver. Permite al usuario navegar por categorías (encabezados, enlaces, imágenes). Puedes crear **rotores personalizados** para ofrecer navegación contextual.

### Ejemplo: Rotor para navegar entre secciones de un feed

```swift
import UIKit

class FeedViewController: UIViewController {

    var sectionHeaders: [UIView] = []
    private var currentSectionIndex = 0

    override func viewDidLoad() {
        super.viewDidLoad()
        configureCustomRotor()
    }

    private func configureCustomRotor() {
        let sectionRotor = UIAccessibilityCustomRotor(name: "Secciones") { [weak self] predicate in
            guard let self = self else { return nil }

            let forward = predicate.searchDirection == .next
            let currentIndex = self.currentSectionIndex

            let nextIndex: Int
            if forward {
                nextIndex = min(currentIndex + 1, self.sectionHeaders.count - 1)
            } else {
                nextIndex = max(currentIndex - 1, 0)
            }

            self.currentSectionIndex = nextIndex

            guard nextIndex < self.sectionHeaders.count else { return nil }

            let targetElement = self.sectionHeaders[nextIndex]
            return UIAccessibilityCustomRotorItemResult(
                targetElement: targetElement,
                targetRange: nil
            )
        }

        self.accessibilityCustomRotors = [sectionRotor]
    }
}
```

Con este rotor, un usuario de VoiceOver puede girar el rotor para seleccionar "Secciones" y luego deslizar arriba/abajo para **saltar directamente entre secciones** sin pasar por cada celda individual.

---

## Adaptación dinámica a preferencias del usuario

Un desarrollador avanzado no solo hace que VoiceOver funcione; adapta **toda la experiencia** según las preferencias de accesibilidad del sistema.

### Ejemplo: Responder a múltiples preferencias

```swift
import UIKit
import SwiftUI

class AdaptiveViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        configureForAccessibility()
        registerForNotifications()
    }

    private func configureForAccessibility() {
        // Reducir movimiento
        if UIAccessibility.isReduceMotionEnabled {
            // Reemplazar animaciones complejas con transiciones simples
            disableParallaxEffects()
            useSimpleFadeTransitions()
        }

        // Aumentar contraste
        if UIAccessibility.isDarkerSystemColorsEnabled {
            applyHighContrastTheme()
        }

        // Transparencia reducida
        if UIAccessibility.isReduceTransparencyEnabled {
            removeBlurEffects()
        }

        // VoiceOver activo
        if UIAccessibility.isVoiceOverRunning {
            simplifyLayoutForScreenReader()
        }

        // Tamaño de texto preferido
        let contentSize = traitCollection.preferredContentSizeCategory
        if contentSize.isAccessibilityCategory {
            // El usuario usa tamaños XXL - adaptar layout
            switchToVerticalLayout()
        }
    }

    private func registerForNotifications() {
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(voiceOverStatusChanged),
            name: UIAccessibility.voiceOverStatusDidChangeNotification,
            object: nil
        )

        NotificationCenter.default.addObserver(
            self,
            selector: #selector(reduceMotionStatusChanged),
            name: UIAccessibility.reduceMotionStatusDidChangeNotification,
            object: nil
        )

        NotificationCenter.default.addObserver(
            self,
            selector: #selector(boldTextStatusChanged),
            name: UIAccessibility.boldTextStatusDidChangeNotification,
            object: nil
        )
    }

    @objc private func voiceOverStatusChanged() {
        if UIAccessibility.isVoiceOverRunning {
            simplifyLayoutForScreenReader()
        } else {
            restoreFullLayout()
        }
    }

    @objc private func reduceMotionStatusChanged() {
        configureForAccessibility()
    }

    @objc private func boldTextStatusChanged() {
        updateFontsForBoldText()
    }

    // MARK: - Métodos auxiliares (implementar según tu UI)
    private func disableParallaxEffects() { /* ... */ }
    private func useSimpleFadeTransitions() { /* ... */ }
    private func applyHighContrastTheme() { /* ... */ }
    private func removeBlurEffects() { /* ... */ }
    private func simplifyLayoutForScreenReader() { /* ... */ }
    private func switchToVerticalLayout() { /* ... */ }
    private func restoreFullLayout() { /* ... */ }
    private func updateFontsForBoldText() { /* ... */ }
}
```

### En SwiftUI es más conciso

```swift
import SwiftUI

struct AdaptiveCardView: View {
    @Environment(\.sizeCategory) var sizeCategory
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    @Environment(\.accessibilityReduceTransparency) var reduceTransparency
    @Environment(\.accessibilityDifferentiateWithoutColor) var differentiateWithoutColor
    @Environment(\.legibilityWeight) var legibilityWeight

    var body: some View {
        VStack(spacing: sizeCategory.isAccessibilityCategory ? 20 : 12) {
            cardContent
        }
        .background(cardBackground)
        .animation(reduceMotion ? .none : .spring(), value: sizeCategory)
    }

    @ViewBuilder
    private var cardContent: some View {
        if sizeCategory.isAccessibilityCategory {
            // Layout vertical para textos muy grandes
            VStack(alignment: .leading, spacing: 8) {
                iconView
                textContent
            }
        } else {
            // Layout horizontal estándar
            HStack(spacing: 12) {
                iconView
                textContent
            }
        }
    }

    @ViewBuilder
    private var iconView: some View {
        Image(systemName: "checkmark.circle.fill")
            .foregroundColor(.green)
            .overlay {
                // Si el usuario no distingue colores, agregar forma adicional
                if differentiateWithoutColor {
                    Image(systemName: "checkmark")
                        .font(.caption2)
                        .bold()
                        .foregroundColor(.white)
                }
            }
    }

    private var textContent: some View {
        VStack(alignment: .leading) {
            Text("Pago completado")
                .font(.headline)
                .fontWeight(legibilityWeight == .bold ? .heavy : .semibold)
            Text("Tu transferencia fue procesada exitosamente")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
    }

    @ViewBuilder
    private var cardBackground: some View {
        if reduceTransparency {
            Color(.systemBackground)
        } else {
            Color(.systemBackground).opacity(0.85)
        }
    }
}
```

---

## Dynamic Type avanzado con layouts adaptativos

Uno de los errores más comunes es soportar Dynamic Type pero **romper el layout** cuando el texto crece. La técnica clave es detectar `.isAccessibilityCategory` y cambiar la disposición.

```swift
import SwiftUI

struct ProfileHeaderView: View {
    @Environment(\.sizeCategory) var sizeCategory

    let name: String
    let role: String
    let avatarURL: URL?

    var isAccessibilitySize: Bool {
        sizeCategory.isAccessibilityCategory
    }

    var body: some View {
        Group {
            if isAccessibilitySize {
                VStack(spacing: 16) {
                    avatar
                    info
                }
            } else {
                HStack(spacing: 16) {
                    avatar
                    info
                    Spacer()
                }
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(name), \(role)")
    }

    private var avatar: some View {
        AsyncImage(url: avatarURL) { image in
            image.resizable()
        } placeholder: {
            Circle().fill(Color.gray.opacity(0.3))
        }
        .frame(
            width: isAccessibilitySize ? 100 : 60,
            height: isAccessibilitySize ? 100 : 60
        )
        .clipShape(Circle())
        .accessibilityHidden(true) // La imagen es decorativa
    }

    private var info: some View {
        VStack(alignment: isAccessibilitySize ? .center : .leading, spacing: 4) {
            Text(name)
                .font(.headline)
            Text(role)
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
    }
}
```

---

## Acciones de accesibilidad personalizadas

Para elementos que tienen múltiples acciones (como una celda de email con archivar, eliminar, marcar como leído), evita que el usuario tenga que buscar botones ocultos.

```swift
import SwiftUI

struct EmailRowView: View {
    let email: Email

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(email.sender)
                .font(.headline)
            Text(email.subject)
                .font(.subheadline)
            Text(email.preview)
                .font(.caption)
                .foregroundColor(.secondary)
                .lineLimit(2)
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(accessibilityDescription)
        .accessibilityAction(named: "Archivar") {
            archiveEmail()
        }
        .accessibilityAction(named: "Eliminar") {
            deleteEmail()
        }
        .accessibilityAction(named: email.isRead ? "Marcar como no leído" : "Marcar como leído") {
            toggleReadStatus()
        }
        .accessibilityAction(named: "Responder") {
            replyToEmail()
        }
    }

    private var accessibilityDescription: String {
        let readStatus = email.isRead ? "" : "No leído. "
        return "\(readStatus)Correo de \(email.sender). Asunto: \(email.subject). \(email.preview)"
    }

    private func archiveEmail() { /* ... */ }
    private func deleteEmail() { /* ... */ }
    private func toggleReadStatus() { /* ... */ }
    private func replyToEmail() { /* ... */ }
}

struct Email {
    let sender: String
    let subject: String
    let preview: String
    var isRead: Bool
}
```

Con esto, el usuario de VoiceOver puede **deslizar hacia arriba y abajo** sobre el elemento para recorrer las acciones disponibles y activar la que necesite con doble tap.

---

## Notificaciones dinámicas de accesibilidad

Cuando el contenido cambia de forma asíncrona (carga de datos, errores, actualizaciones), debes **notificar a VoiceOver** explícitamente.

```swift
import UIKit

class PaymentViewController: UIViewController {

    func processPayment() {
        showLoadingIndicator()

        // Notificar que la pantalla cambió
        UIAccessibility.post(
            notification: .screenChanged,
            argument: loadingLabel //