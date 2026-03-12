---
sidebar_position: 1
title: Code Review
---

# Code Review: El arte de revisar (y recibir revisiones de) código en iOS

## ¿Qué es un Code Review?

Un **Code Review** (revisión de código) es el proceso sistemático en el que uno o más desarrolladores examinan el código escrito por un compañero antes de que este se integre a la rama principal del proyecto. No es simplemente "buscar errores": es una conversación técnica, un acto de mentoría bidireccional y una de las prácticas más poderosas para elevar la calidad de un equipo.

En el contexto de desarrollo iOS, un code review implica analizar Pull Requests (PRs) que pueden contener desde nuevos `UIViewController`, `ViewModels`, configuraciones de `SwiftUI`, hasta cambios en el `Info.plist` o en las reglas de `SwiftLint`.

---

## ¿Por qué es crítico para un dev iOS en LATAM?

La industria tech en Latinoamérica ha crecido exponencialmente. Miles de desarrolladores iOS trabajan de forma remota para empresas en Estados Unidos, Canadá y Europa. En este contexto:

1. **Tu código será revisado en inglés por equipos distribuidos.** Saber dar y recibir feedback profesionalmente te diferencia inmediatamente.
2. **Es tu carta de presentación silenciosa.** La calidad de tus PRs y la profundidad de tus reviews hablan más que tu CV.
3. **Acelera tu crecimiento técnico.** En LATAM no siempre hay acceso a conferencias presenciales o mentores senior locales. El code review con equipos internacionales compensa esa brecha.
4. **Reduce costos de bugs en producción.** En startups latinoamericanas con recursos limitados, un bug en producción puede significar la pérdida de usuarios que costó mucho adquirir.
5. **Construye confianza en equipos remotos.** Cuando trabajas desde Ciudad de México, Bogotá, Buenos Aires o Lima para un equipo en San Francisco, la confianza se construye commit a commit, review a review.

---

## Anatomía de un buen Code Review en iOS

### Lo que SÍ debes revisar

| Aspecto | Preguntas clave |
|---|---|
| **Arquitectura** | ¿Respeta el patrón del proyecto (MVVM, VIPER, TCA)? ¿Hay responsabilidades mezcladas? |
| **Naming** | ¿Los nombres comunican intención? ¿Siguen las convenciones de Swift API Design Guidelines? |
| **Manejo de memoria** | ¿Hay retain cycles? ¿Se usa `[weak self]` correctamente? |
| **Concurrencia** | ¿Se accede a datos desde el hilo correcto? ¿Se usa `@MainActor` donde corresponde? |
| **Accesibilidad** | ¿Tiene `accessibilityLabel`? ¿Funciona con VoiceOver? |
| **Testing** | ¿Incluye tests unitarios? ¿Los tests son legibles y prueban comportamiento, no implementación? |
| **Edge cases** | ¿Qué pasa si la red falla? ¿Y si el array viene vacío? ¿Y si el usuario no da permisos? |

### Lo que NO es un Code Review

- **No es un examen.** No estás calificando al otro desarrollador.
- **No es una competencia de ego.** "Yo lo habría hecho diferente" no es feedback útil por sí solo.
- **No es solo buscar errores de sintaxis.** Para eso existen los linters.

---

## Ejemplo práctico: Revisando un PR real

Imagina que un compañero envía este código en un PR para una pantalla de perfil de usuario:

```swift
class ProfileViewController: UIViewController {

    var userId: String = ""
    var userName: String = ""
    var userEmail: String = ""
    var profileImage: UIImage?
    var isLoading: Bool = false

    let networkManager = NetworkManager()

    override func viewDidLoad() {
        super.viewDidLoad()
        loadProfile()
    }

    func loadProfile() {
        isLoading = true
        networkManager.fetchUser(id: userId) { result in
            switch result {
            case .success(let user):
                self.userName = user.name
                self.userEmail = user.email
                self.updateUI()
                self.isLoading = false
            case .failure(let error):
                print(error)
                self.isLoading = false
            }
        }
    }

    func updateUI() {
        // actualizar labels...
    }
}
```

### ¿Qué comentarios dejarías?

Aquí van ejemplos de feedback constructivo, ordenados por severidad:

#### 🔴 Crítico: Retain cycle potencial

```
// Comentario en el PR:
// ⚠️ Aquí hay un retain cycle potencial. El closure captura `self`
// de forma fuerte. Sugiero usar `[weak self]`:

networkManager.fetchUser(id: userId) { [weak self] result in
    guard let self else { return }
    switch result {
    case .success(let user):
        self.userName = user.name
        self.userEmail = user.email
        self.updateUI()
        self.isLoading = false
    case .failure(let error):
        print(error)
        self.isLoading = false
    }
}
```

#### 🔴 Crítico: Actualización de UI fuera del hilo principal

```swift
// Comentario en el PR:
// El callback de `fetchUser` probablemente viene en un hilo de background.
// Actualizar UI desde ahí puede causar crashes o comportamiento errático.

networkManager.fetchUser(id: userId) { [weak self] result in
    DispatchQueue.main.async {
        guard let self else { return }
        // ... manejar resultado
    }
}

// O mejor aún, si el proyecto usa async/await:

@MainActor
func loadProfile() async {
    isLoading = true
    do {
        let user = try await networkManager.fetchUser(id: userId)
        self.userName = user.name
        self.userEmail = user.email
        self.updateUI()
    } catch {
        // Manejar error apropiadamente
    }
    isLoading = false
}
```

#### 🟡 Importante: Manejo de errores pobre

```
// Comentario en el PR:
// `print(error)` no es manejo de errores 😅. El usuario no recibe
// ninguna retroalimentación si falla la carga. ¿Podemos mostrar
// un alert o un estado de error en la UI?
//
// Además, en producción estos `print()` no nos sirven.
// ¿Consideramos usar nuestro logger o enviarlo a Crashlytics?
```

#### 🟡 Importante: Demasiadas propiedades expuestas como `var`

```swift
// Comentario en el PR:
// Estas propiedades son todas `var` internas y públicas.
// Esto permite que cualquier parte del código las modifique sin control.
// Sugiero considerar un ViewModel que encapsule este estado:

struct ProfileViewModel {
    let userId: String
    private(set) var userName: String = ""
    private(set) var userEmail: String = ""
    private(set) var profileImage: UIImage?
    private(set) var isLoading: Bool = false

    mutating func update(with user: User) {
        userName = user.name
        userEmail = user.email
    }
}
```

#### 🟢 Sugerencia (no bloquea aprobación): Naming

```
// Comentario en el PR (nit):
// Nit: `loadProfile()` podría ser más descriptivo.
// ¿Qué tal `fetchAndDisplayUserProfile()`?
// No bloqueo el PR por esto, solo una idea 🤷‍♂️
```

---

## El código refactorizado

Después de aplicar el feedback del review, el código podría verse así:

```swift
import os

final class ProfileViewController: UIViewController {

    // MARK: - Dependencies

    private let networkManager: NetworkManaging
    private let userId: String
    private let logger = Logger(subsystem: "com.app.profile", category: "ProfileVC")

    // MARK: - State

    private var viewModel = ProfileViewModel()

    // MARK: - Init

    init(userId: String, networkManager: NetworkManaging = NetworkManager()) {
        self.userId = userId
        self.networkManager = networkManager
        super.init(nibName: nil, bundle: nil)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        Task {
            await fetchAndDisplayUserProfile()
        }
    }

    // MARK: - Data Loading

    @MainActor
    private func fetchAndDisplayUserProfile() async {
        viewModel.isLoading = true
        updateUI()

        do {
            let user = try await networkManager.fetchUser(id: userId)
            viewModel.update(with: user)
            updateUI()
        } catch {
            logger.error("Failed to fetch user profile: \(error.localizedDescription)")
            showErrorAlert(message: "No pudimos cargar tu perfil. Intenta de nuevo.")
        }

        viewModel.isLoading = false
        updateUI()
    }

    // MARK: - UI Updates

    private func updateUI() {
        // Actualizar labels, imagen, estado de loading...
    }

    private func showErrorAlert(message: String) {
        let alert = UIAlertController(
            title: "Error",
            message: message,
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}
```

Nota cómo el código pasó de tener **6 problemas identificables** a ser un componente con inyección de dependencias, manejo correcto de concurrencia, logging apropiado y feedback al usuario. **Eso es el poder de un buen code review.**

---

## Cómo dar feedback que no destruya relaciones

El tono de tus comentarios importa tanto como su contenido técnico. Esto es especialmente relevante en equipos multiculturales donde trabajamos como devs LATAM.

### Fórmulas probadas

| ❌ Evitar | ✅ Preferir |
|---|---|
| "Esto está mal" | "¿Consideraste hacer X? Creo que podría prevenir Y" |
| "¿Por qué hiciste esto?" | "Me ayuda entender la razón detrás de este approach. ¿Fue por Z?" |
| "Esto no tiene sentido" | "Me cuesta seguir esta lógica. ¿Podemos simplificarla así...?" |
| "Siempre deberías usar X" | "En mi experiencia, X funciona bien aquí porque..." |
| *No decir nada positivo* | "Me gusta cómo manejaste el caso de error aquí 👏" |

### El framework ASK

Antes de dejar un comentario, pregúntate:

- **A**ccional: ¿El dev puede hacer algo concreto con mi feedback?
- **S**pecífico: ¿Señalo exactamente dónde y qué cambiar?
- **K**ind (amable): ¿Lo diría de esta forma cara a cara tomando un café?

---

## Cómo recibir feedback sin tomarlo personal

Este es quizás el skill más difícil y el menos enseñado.

### Mentalidad clave

> "El review es sobre el **código**, no sobre **ti**."

### Pasos prácticos cuando recibes un comentario que te incomoda

1. **Respira.** Lee el comentario completo antes de responder.
2. **Asume buena intención.** El 95% de las veces, la persona quiere ayudar.
3. **Separa el ego del código.** Tú no eres tu código. Escribirás miles de líneas más.
4. **Agradece el feedback.** Un simple "Good catch, thanks!" construye puentes enormes.
5. **Si no entiendes, pregunta.** "¿Puedes elaborar un poco más?" es siempre válido.
6. **Si no estás de acuerdo, argumenta con datos.** "Entiendo el punto, pero en este caso preferí X porque [documentación/benchmark/contexto]."

### Señales de que estás reaccionando con ego

- Sientes la urgencia de responder **inmediatamente**
- Empiezas tu respuesta con "Pero..."
- Sientes que están atacando tu competencia profesional
- Quieres defender tu código a toda costa aunque el feedback tenga mérito

Si detectas alguna de estas señales, cierra el PR, levántate, toma agua, y vuelve en 15 minutos.

---

## Checklist para antes de enviar tu PR

Antes de pedir review, revisa tú mismo:

- [ ] Releí todo mi diff como si fuera de otra persona
- [ ] El PR tiene un título claro y descriptivo
- [ ] Incluí una descripción que explica **qué** y **por qué** (no solo el **cómo**)
- [ ] Los commits tienen mensajes significativos
- [ ] El PR no tiene más de ~400 líneas de cambios (si tiene más, ¿puedo dividirlo?)
- [ ] Los tests pasan localmente
- [ ] No hay `print()` olvidados, código comentado ni `TODO` sin ticket
- [ ] Agregué screenshots o video si hay cambios de UI
- [ ] Señalé las partes donde tengo dudas o quiero feedback específico

### Ejemplo de buena descripción de PR

```markdown
## Qué hace este PR
Agrega la pantalla de perfil de usuario con carga async del API.

## Por qué
Es parte del epic PROJ-234. El diseño fue aprobado en Figma [link].

## Decisiones técnicas
- Usé async/await en lugar de closures para simplificar el flujo
- Inyecté `NetworkManaging` como protocolo para facilitar testing
- No agregué cache por ahora (se hará en PROJ-235)

## Screenshots
| Estado normal | Estado de error | Loading |
|---|---|---|
| ![img1] | ![img2] | ![img3] |

## Testing
- [x] Unit tests para ProfileViewModel
- [x] Probado en iPhone SE (pantalla pequeña)
- [x] Probado con VoiceOver
- [ ] UI tests (pendiente para siguiente sprint)

## ¿Dónde quiero feedback especial?
El manejo del estado de loading en línea 45-60. No estoy seguro
si es la mejor approach.
```

---

## Métricas de un proceso de Code Review saludable

Si lideras un equipo o quieres proponer mejoras, estas métricas te ayudan:

| Métrica | Objetivo saludable |
|---|---|
| **Tiempo hasta primera revisión** | < 4 horas laborales |
| **Tiempo total hasta merge** | < 24 horas |
| **Tamaño promedio del PR** | < 400 líneas cambiadas |
| **Cantidad de rondas de revisión** | 1-2 (si pasa de 3, algo falló antes) |
| **PRs rechazados completamente** | < 5% (si es más alto, falta alineación previa) |

---

## Herramientas recomendadas para el ecosistema iOS

### Para el proceso de review
- **GitHub Pull Requests** — El estándar, con inline comments y suggested changes
- **Bit